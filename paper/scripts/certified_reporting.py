"""One complete-domain scoring view over retained experimental records.

Original responses and archived scores remain unchanged. Publication consumers
read the same audited replacement summaries, including failure partitions.
"""
from copy import deepcopy
from pathlib import Path
import json

REPORT = 'data/supplements/complete_domain_scoring_20261013/report.json'


def summary_rows(root, source):
    root = Path(root)
    report = json.loads((root / REPORT).read_text())
    assert report['status'] == 'passed' and report['model_calls'] == 0
    return deepcopy(report['summaries'][source])


def intent_rows(root, filename='parameter_rows.json'):
    root = Path(root)
    rows = json.loads((root / 'data/supplements/intent_ambiguity_20261011' / filename).read_text())
    report = json.loads((root / REPORT).read_text())
    changes = {r['task_id']: r for r in report['intent_changes'] if r['file'] == filename}
    for row in rows:
        if row['task_id'] in changes:
            change = changes[row['task_id']]
            assert all(row[k] == v for k, v in change['before'].items())
            row.update(change['after'])
    return rows
