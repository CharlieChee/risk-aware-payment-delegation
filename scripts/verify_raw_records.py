"""Verify retained request/response records against published outcome rows."""
from collections import Counter
from pathlib import Path
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'bilingual/raw_records/manifest.json').read_text())
    rows = json.loads((ROOT / 'paper/data/derived/main_rows.json').read_text())
    by_task = {r['task']: r for r in rows}
    archived_content = {}
    with gzip.open(ROOT / 'data/artifacts/derived_main_rows.jsonl.gz', 'rt') as stream:
        for line in stream:
            row = json.loads(line)
            archived_content[row['task']] = row['source_content_sha256']
    seen = set()
    cohorts = []
    for shard in manifest['files']:
        path = ROOT / shard['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == shard['sha256'], shard['path']
        counts = Counter()
        cases = set()
        with gzip.open(path, 'rt', encoding='utf-8') as stream:
            for line in stream:
                record = json.loads(line)
                task = record['task']
                assert task not in seen
                seen.add(task)
                source = by_task[task]
                assert (record['profile'], record['arm']) == (shard['profile'], shard['arm'])
                assert record['request']['key'] == task
                assert (ROOT / record['english_task']).is_file()
                for field in ['case', 'profile', 'arm', 'template', 'pair_id', 'outcome']:
                    assert record[field] == source[field], (task, field)
                assert record['evaluation']['outcome'] == source['outcome']
                for field in ['exact', 'unsafe_accept', 'false_reject']:
                    assert record['evaluation']['metrics'][field] == source[field], (task, field)
                content = record['observation']['content']
                assert hashlib.sha256(content.encode()).hexdigest() == archived_content[task]
                assert not any(p.startswith(('request/messages', 'response/output'))
                               for p in record['sanitized_fields'])
                assert set(record['source_sha256']) == {'request', 'response', 'observation', 'evaluation'}
                cases.add(record['case'])
                counts[record['outcome']] += 1
        assert len(cases) == sum(counts.values()) == shard['records'] == 200
        assert dict(counts) == shard['outcomes']
        cohorts.append(dict(profile=shard['profile'], arm=shard['arm'], n=200, outcomes=dict(counts)))
    assert len(seen) == manifest['records'] == 800
    report = dict(status='passed', records=len(seen), cohorts=cohorts,
                  checks=['shard hashes', 'task identifiers', 'full cohort membership',
                          'recorded scoring alignment', 'unaltered response content',
                          'English task links'])
    (ROOT / 'output').mkdir(exist_ok=True)
    (ROOT / 'output/raw_records_check.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Verified 800 retained trials across four complete primary cohorts.')


if __name__ == '__main__':
    main()
