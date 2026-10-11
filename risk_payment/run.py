"""Run an English primary cohort through an OpenAI-compatible chat endpoint.

Requests and responses are durably checkpointed separately. A completed
response is rescored without another API call after interruption. No payment
or other external action is performed. Credentials are read only from env.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import argparse, hashlib, json, os, tempfile, time

from .prompts import request, SCHEMAS
from .decision import decide, score
from .format_decode import decode as decode_carrier
from .schema_check import validate_schema

ROOT = Path(__file__).resolve().parents[1]

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, delete=False) as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n'); f.flush(); os.fsync(f.fileno()); name=f.name
    os.replace(name, path)
    if os.name == 'posix':
        fd=os.open(path.parent, os.O_RDONLY)
        try: os.fsync(fd)
        finally: os.close(fd)

def sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def decode(content, method='direct'):
    return decode_carrier(content, SCHEMAS[method], validate_schema)

def invoke(payload, base_url, api_key, timeout):
    req=Request(base_url.rstrip('/')+'/chat/completions',data=json.dumps(payload).encode(),
                headers={'Content-Type':'application/json','Authorization':'Bearer '+api_key})
    with urlopen(req,timeout=timeout) as response:
        return json.load(response)

def one(args, case, api_key, transport=invoke):
    public=json.loads((args.benchmark/case['public_path']).read_text())
    payload=dict(model=args.model,messages=request(args.method,public),max_tokens=args.output_cap)
    if args.effort:payload['reasoning_effort']=args.effort
    if args.temperature is not None:payload['temperature']=args.temperature
    if args.json_mode:payload['response_format']={'type':'json_object'}
    task=args.output/case['id']; task.mkdir(parents=True,exist_ok=True)
    identity={'payload':payload,'base_url':args.base_url,'protocol':'english-release-v1','method':args.method}
    fingerprint=sha(identity)
    request_path=task/'request.json'
    if request_path.exists():
        old=json.loads(request_path.read_text())
        if old['sha256']!=fingerprint:
            raise ValueError('Run configuration changed; use a new output directory.')
    else:save(request_path,dict(identity,sha256=fingerprint))
    result_path=task/'result.json'
    if result_path.exists():return json.loads(result_path.read_text())
    response_path=task/'response.json'
    if response_path.exists():
        observation=json.loads(response_path.read_text())
    else:
        start=time.monotonic()
        try:
            response=transport(payload,args.base_url,api_key,args.timeout)
            observation={'ok':True,'response':response,'seconds':time.monotonic()-start,
                         'completed_at':datetime.now(timezone.utc).isoformat()}
        except HTTPError as exc:
            observation={'ok':False,'error':f'HTTP {exc.code}','seconds':time.monotonic()-start}
        except (URLError, TimeoutError, OSError, ValueError):
            observation={'ok':False,'error':'transport_or_response_failure','seconds':time.monotonic()-start}
        # Save immediately, before decoding, execution, or reference access.
        save(response_path,observation)
    result=dict(case=case['id'],method=args.method,model=args.model,request_sha256=fingerprint,
                output=None,usage={},seconds=observation['seconds'])
    try:
        if not observation['ok']:raise ValueError(observation['error'])
        response=observation['response']; result['usage']=response.get('usage',{})
        result['response_model']=response.get('model')
        parsed,trace=decode(response['choices'][0]['message']['content'],args.method)
        result['parsed_output']=parsed;result['carrier_trace']=trace
        if args.method=='direct':result['output']=parsed
        else:
            outcome=decide(parsed,public['candidates'],public['catalog_complete'])
            result['execution']=outcome
            if outcome['status']=='failure':raise ValueError(outcome['reason'])
            result['output']={k:outcome[k] for k in ['allowed_ids','guaranteed_utility']}
            result['output']['decision']='accept' if outcome['status']=='accept' else 'reject'
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        result['error']=str(exc)[:250]
    # References are read only after response checkpoint and execution.
    reference=json.loads((args.benchmark/case['reference_path']).read_text())['reference']
    result['metrics']=score(result['output'] or {},reference)
    save(result_path,result)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',required=True)
    p.add_argument('--method',choices=['direct','set'],required=True)
    p.add_argument('--base-url',default=os.environ.get('PAYMENT_API_BASE_URL',''))
    p.add_argument('--api-key-env',default='PAYMENT_API_KEY')
    p.add_argument('--effort')
    p.add_argument('--output-cap',type=int,default=32768)
    p.add_argument('--temperature',type=float)
    p.add_argument('--json-mode',action='store_true')
    p.add_argument('--timeout',type=int,default=1800)
    p.add_argument('--concurrency',type=int,default=4)
    p.add_argument('--limit',type=int,default=200)
    p.add_argument('--benchmark',type=Path,default=ROOT/'benchmarks/primary')
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--dry-run',action='store_true',help='Write public requests only; no model calls.')
    args=p.parse_args()
    if min(args.limit,args.concurrency,args.output_cap,args.timeout)<1:p.error('Numeric settings must be positive.')
    cases=json.loads((args.benchmark/'manifest.json').read_text())['cases'][:args.limit]
    if args.dry_run:
        for case in cases:
            public=json.loads((args.benchmark/case['public_path']).read_text())
            save(args.output/'requests'/f"{case['id']}.json",{'model':args.model,'max_tokens':args.output_cap,
                  'messages':request(args.method,public)})
        print(f'{len(cases)} requests written; no model calls.');return
    key=os.environ.get(args.api_key_env)
    if not key or not args.base_url:p.error('Set PAYMENT_API_KEY and PAYMENT_API_BASE_URL (or --base-url).')
    if not args.base_url.startswith('https://'):p.error('Use an HTTPS endpoint.')
    # One local owner per run directory prevents duplicate paid calls on restart.
    args.output.mkdir(parents=True,exist_ok=True)
    import fcntl
    with (args.output/'.run.lock').open('w') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:p.error('This output directory already has an active runner.')
        completed=[]
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            futures=[pool.submit(one,args,c,key) for c in cases]
            for future in as_completed(futures):
                row=future.result();completed.append(row)
                summary={'n':len(completed),'planned':len(cases),'method':args.method,'model':args.model,
                         'counts':{k:sum(r['metrics'][k] for r in completed) for k in ['exact','unsafe','false_refusal','other']}}
                save(args.output/'summary.json',summary)
                print(f"{len(completed)}/{len(cases)} completed; {row['metrics']['category']}",flush=True)

if __name__=='__main__':main()
