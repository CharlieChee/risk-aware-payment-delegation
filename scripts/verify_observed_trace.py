"""Verify the two already recorded ticket traces without model calls."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from risk_payment.engine import solve


def main():
    manifest = json.loads((ROOT / 'bilingual/observed_trace/manifest.json').read_text())
    results = []
    for row in manifest['records']:
        path = ROOT / row['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
        record = json.loads(path.read_text())
        spec = record['response']
        public = record['public_input']
        expected = record['evaluation']['decision_output']
        result = solve(spec, public['candidates'])
        assert record['model'] == 'gpt-6-astra' and record['effort'] == 'max'
        assert spec == record['evaluation']['parsed_output']
        assert record['evaluation']['full_success']
        for key in ['decision', 'allowed_ids', 'guaranteed_utility']:
            assert result[key] == expected[key], (row['task_id'], key)
        assert len(spec['states']) == 2
        assert all(s['risk'] == 'True' and s['utility'] == '(3000-price)/1000'
                   for s in spec['states'])
        results.append(dict(task=row['task_id'], decision=result['decision'],
                            allowed_ids=result['allowed_ids'], value=result['guaranteed_utility']))
    assert {r['decision'] for r in results} == {'accept', 'reject'}
    out = ROOT / 'output'
    out.mkdir(exist_ok=True)
    (out / 'observed_trace_check.json').write_text(json.dumps(
        dict(status='passed', model_calls=0, results=results), indent=2)+'\n')
    print('Verified both archived request-to-decision traces; no model calls.')


if __name__ == '__main__':
    main()
