"""Re-evaluate the retained DeepSeek primary specifications under Algorithm 1.

No model calls or changes to historical records. Pass --artifact to the
experimental artifact root containing risk_payment, benchmarks, and bilingual.
Original invalid outputs remain failures; valid compiled specifications are
evaluated on the same complete catalogues with the certification wrapper.
"""
from pathlib import Path
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import argparse
import gzip
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]


def replay(item):
    artifact_path, record = item
    artifact = Path(artifact_path)
    sys.path.insert(0, str(artifact))
    from risk_payment.decision import decide, score
    result = record['evaluation']['result']
    reference = json.loads((artifact / 'benchmarks/primary/reference' /
                            (record['case'] + '.json')).read_text())['reference']
    if not result['valid']:
        decision = dict(status='failure', reason='archived_invalid_output')
        current = dict(category='other', exact=False)
    else:
        archived_score = score(result['output'], reference)
        assert archived_score['exact'] == bool(record['evaluation']['metrics']['exact'])
        public = json.loads((artifact / 'benchmarks/primary/public' /
                             (record['case'] + '.json')).read_text())
        decision = decide(result['spec'], public['candidates'], catalogue_complete=True)
        if decision['status'] == 'failure':
            current = dict(category='other', exact=False)
        else:
            output = dict(decision='accept' if decision['status']=='accept' else 'reject',
                          allowed_ids=decision['allowed_ids'],
                          guaranteed_utility=decision['guaranteed_utility'])
            current = score(output, reference)
    return dict(profile=record['profile'], case=record['case'],
                archived_outcome=record['outcome'],
                archived_exact=bool(record['evaluation']['metrics']['exact']),
                current_outcome=current['category'], current_exact=current['exact'],
                status=decision['status'], reason=decision['reason'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact', type=Path,
                        default=ROOT.parent/'risk-aware-payment-delegation')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    records, hashes = [], {}
    for profile in ['ds_flash_low', 'ds_flash_high']:
        path = args.artifact/'bilingual/raw_records'/(profile+'_set.jsonl.gz')
        hashes[str(path.relative_to(args.artifact))] = hashlib.sha256(path.read_bytes()).hexdigest()
        with gzip.open(path, 'rt') as stream:
            rows = [json.loads(line) for line in stream]
        assert len(rows) == len({r['case'] for r in rows}) == 200
        records.extend(rows)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        outcomes = list(pool.map(replay, [(str(args.artifact), r) for r in records]))
    groups = []
    for profile in ['ds_flash_low', 'ds_flash_high']:
        rows = [r for r in outcomes if r['profile']==profile]
        groups.append(dict(profile=profile, n=len(rows),
                           archived_exact=sum(r['archived_exact'] for r in rows),
                           certified_exact=sum(r['current_exact'] for r in rows),
                           outcomes=dict(Counter(r['current_outcome'] for r in rows)),
                           statuses=dict(Counter(r['status'] for r in rows))))
    for name in ['engine.py', 'decision.py']:
        path = args.artifact/'risk_payment'/name
        hashes['risk_payment/'+name] = hashlib.sha256(path.read_bytes()).hexdigest()
    report = dict(status='completed', model_calls=0, historical_records_modified=False,
                  scope='Same retained DeepSeek specifications and complete primary catalogues; current Algorithm 1 certification.',
                  source_sha256=hashes, groups=groups, outcomes=outcomes)
    path = ROOT/'output/primary_certification_replay.json'
    path.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(groups, indent=2))


if __name__ == '__main__':
    main()
