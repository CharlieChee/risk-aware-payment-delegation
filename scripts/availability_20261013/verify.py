"""Offline replay of the closed availability cohort. No model calls."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import argparse
import gzip
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/availability_20261013'
RAW=ROOT/'bilingual/availability_20261013'
import availability_audit as audit
import frozen_engine as engine

def read(name):return json.loads((DATA/name).read_text())
def records(path):
    with gzip.open(path,'rt') as f:
        for line in f:yield json.loads(line)
def normalized(matrix):
    return [(r['id'],r['safe'],r.get('proven_unsafe'),
             None if r['psi'] is None else Fraction(r['psi']))for r in matrix]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native-witnesses',action='store_true',help='Also recompute every primary witness from its saved expressions.')
    args=p.parse_args()
    manifest=read('manifest.json')
    for shard in manifest['shards']:
        path=ROOT/shard['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==shard['sha256'],shard['path']
        assert sum(1 for _ in records(path))==shard['records'],shard['path']
    tasks={r['case_id']:r['private']for r in records(RAW/'tasks.jsonl.gz')}
    expected=read('summary.json');witnesses={(r['profile'],r['case_id']):r for r in read('witnesses.json')if r['main_exposure']}
    totals=Counter(); models={};primary=[];certified=0;native_count=0
    for i,r in enumerate(records(RAW/'retained.jsonl.gz'),1):
        task=tasks[r['case_id']]; row=r['row']; ok=r['final_status']=='AUDITABLE'
        a=audit.audit_availability(r['case_id'],[x['id']for x in task['candidates']],
            r['generated_matrix']if ok else [],task['reference_matrix'],task['availability_random_plan'],
            generated_valid=ok,generated_error=None if ok else 'retained failure',
            catalogue_complete=bool(r['spec'] and r['spec'].get('catalog_complete')))
        for field in ['endpoints','rank_cumulative','random_summaries']:
            assert a[field]==row[field],(r['profile'],r['case_id'],field)
        assert a['certification']['status']==row['certification']['status']
        certified+=a['certification']['status']=='PASS'
        totals.update(a['endpoints']);models.setdefault(r['profile'],Counter()).update(a['endpoints'])
        if a['endpoints']['rank_le8_safe_to_unsafe_strict_backup']:
            primary.append((r['profile'],r['case_id'],row['template']))
            w=witnesses[(r['profile'],r['case_id'])]
            if args.native_witnesses:
                native=engine.solve(r['spec'],task['candidates'])
                assert normalized(native['matrix'])==normalized(r['generated_matrix'])
                remaining=[c for c in task['candidates']if c['id']not in w['removed_ids']]
                changed=engine.solve(r['spec'],remaining)
                subset=[m for m in r['generated_matrix']if m['id']not in w['removed_ids']]
                assert normalized(changed['matrix'])==normalized(subset)
                ref={x['id']:x for x in task['reference_matrix']}
                candidates=[x for x in changed['matrix']if x['safe'] and Fraction(x['psi'])>0]
                v=max(Fraction(x['psi'])for x in candidates)
                selected=[x['id']for x in candidates if Fraction(x['psi'])==v]
                backups=[x['id']for x in candidates if ref[x['id']]['safe'] and Fraction(ref[x['id']]['psi'])>0]
                assert selected==w['selected_ids'] and all(not ref[x]['safe']for x in selected)
                assert len(backups)==w['strict_backups']>0
                native_count+=1
        if i%400==0:print(f'Replayed {i}/2400 retained slots',flush=True)
    assert i==2400 and certified==2373
    assert dict(totals)==expected['total']['endpoints']
    for profile,counts in models.items():assert dict(counts)==expected['by_model'][profile]['endpoints']
    assert len(primary)==48 and len({x[1]for x in primary})==48 and len({x[2]for x in primary})==15
    failed=list(records(RAW/'failures.jsonl.gz'));assert len(failed)==27
    assert all(not x['inference']['ok']for x in failed)
    result=dict(status='passed',model_calls=0,planned=i,evaluable=certified,
                primary_exposures=len(primary),requests=len({x[1]for x in primary}),
                templates=len({x[2]for x in primary}),native_witnesses=native_count,
                scope='Hash verification, full matrix-based paired catalogue replay, endpoint reconstruction'+
                      (' and native expression checks for all primary witnesses.'if args.native_witnesses else '.'))
    out=ROOT/'output/availability_20261013_verification.json';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
