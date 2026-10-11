"""Recompute benchmark references using the ledger and exact DSL interpreter."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import argparse, hashlib, json, time
from . import contracts, ledger
from .engine import solve
from .decision import decide

ROOT=Path(__file__).resolve().parents[1]

def check_case(case):
    folder=ROOT/'benchmarks/primary'
    public=json.loads((folder/case['public_path']).read_text())
    private=json.loads((folder/case['reference_path']).read_text())
    candidates=public['candidates'];maximum=case['stratum']['max_affected']
    reference=ledger.reference(case['template'],candidates,maximum)
    assert reference==private['reference'], case['id']
    spec=contracts.gold_spec(case['template'],maximum)
    assert spec==private['gold_spec'], case['id']
    evaluated=solve(spec,candidates)
    for key in ('decision','allowed_ids','guaranteed_utility'):
        assert evaluated[key]==reference[key], (case['id'],key)
    for left,right in zip(evaluated['matrix'],reference['matrix']):
        assert (left['id'],left['safe'],left['psi'])==(right['id'],right['safe'],right['psi'])
    # The stricter certification wrapper agrees on the benchmark's resolved inputs.
    decision=decide(spec,candidates)
    assert decision['status']==('accept' if reference['decision']=='accept' else 'refuse')
    assert decision['allowed_ids']==reference['allowed_ids']
    return dict(case=case['id'],template=case['template'],candidates=len(candidates),
                state_candidate_checks=len(candidates)*len(spec['states']),status='passed')

def check_language():
    folder=ROOT/'bilingual/language_panel/public'
    pairs=0
    for zh_path in folder.glob('*__zh.json'):
        en_path=zh_path.with_name(zh_path.name.replace('__zh.json','__en.json'))
        zh=json.loads(zh_path.read_text());en=json.loads(en_path.read_text())
        for value in (zh,en):
            for r in value['records']:r['text']='TEXT'
            value['attributes']={k:'DESCRIPTION' for k in value['attributes']}
            for v in value.get('attribute_schema',{}).values():v['description']='DESCRIPTION'
        assert zh==en,zh_path.name
        pairs+=1
    assert pairs==60
    return pairs

def check_feasibility_pairs(cases):
    pairs={}
    for c in cases:pairs.setdefault(c['pair_id'],[]).append(c)
    for pair in pairs.values():
        assert len(pair)==2 and {r['expected'] for r in pair}=={'accept','reject'}
        pair.sort(key=lambda r:r['expected'])
        a,b=[json.loads((ROOT/'benchmarks/primary'/r['public_path']).read_text()) for r in pair]
        index=pair[0]['designated_position']
        b['candidates'][index]['attrs']['admin']-=pair[0]['stratum']['margin']+1
        assert a==b,pair[0]['pair_id']
    return len(pairs)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--limit',type=int,default=200)
    p.add_argument('--workers',type=int,default=4)
    args=p.parse_args()
    cases=json.loads((ROOT/'benchmarks/primary/manifest.json').read_text())['cases']
    pairs=check_feasibility_pairs(cases)
    language=check_language()
    started=time.monotonic();rows=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for f in as_completed([pool.submit(check_case,c) for c in cases[:args.limit]]):
            rows.append(f.result())
            if len(rows)%10==0:print(f'{len(rows)}/{min(args.limit,len(cases))} reference cases verified',flush=True)
    report=dict(status='passed',model_calls=0,cases=len(rows),feasibility_pairs=pairs,
                bilingual_pairs=language,state_candidate_checks=sum(r['state_candidate_checks'] for r in rows),
                elapsed_seconds=time.monotonic()-started,results=sorted(rows,key=lambda r:r['case']))
    out=ROOT/'output';out.mkdir(exist_ok=True)
    (out/'reference_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='results'}))

if __name__=='__main__':main()
