"""Author-confirmed aggregates, kept separate from immutable per-trial evidence."""
from pathlib import Path
import json
from collections import Counter

REPORT = 'data/author_reports/20261011_confirmed_aggregates.json'
OPUS_REVIEW = 'data/author_reports/20261011_opus_output_review.json'
PRIMARY_COMPLETION = 'data/author_reports/20261011_primary200_completion.json'


def primary_completion(root):
    report = json.loads((Path(root) / PRIMARY_COMPLETION).read_text())
    assert report['new_model_calls'] == 0 and not report['raw_records_received']
    assert len(report['primary']) == 8 and not report['language']
    for row in report['primary']:
        assert row['n'] == 200 and row['expected_accept'] == 100
        assert sum(row[k] for k in ('exact', 'unsafe', 'false_refusal', 'other')) == row['n']
        assert sum(row['outcomes'].values()) == row['n']
        assert 0 <= row['correct_accept'] <= row['expected_accept']
        assert 0 <= row['exact'] - row['correct_accept'] <= row['n'] - row['expected_accept']
        assert row['correct_accept'] + row['false_refusal'] <= row['expected_accept']
    return report


def opus_output_review(root):
    """Apply the author's output adjudication; preserve the local runtime record.

    An invalid schema/execution flag and an author-reviewed correct decision are
    distinct measurements. This reporting overlay does not re-execute or repair
    responses, replace historical evaluations, or impute unobserved outcomes.
    """
    root = Path(root)
    review = json.loads((root / OPUS_REVIEW).read_text())
    assert review['status'] == 'author_confirmed_external_review_pending_raw_import'
    assert not review['external_raw_records_received']
    assert review['new_model_calls'] == 0 and not review['original_records_modified']
    original = json.loads((root / review['source_rows']).read_text())
    changes = {r['task']: r for r in review['corrections']}
    assert len(changes) == len(review['corrections'])
    assert set(changes) == {r['task'] for r in original if r['outcome'] == 'invalid_output'}
    rows = []
    for r in original:
        change = changes.get(r['task'])
        if change:
            assert change['original_outcome'] == r['outcome'] == 'invalid_output'
            assert change['reported_outcome'] == 'exact'
            assert change['arm'] == r['arm'] and change['case'] == r['case']
        rows.append(dict(task=r['task'], profile=r['profile'], arm=r['arm'],
            case=r['case'], expected=r['expected'],
            included_in_paired_display=r['included_in_paired_display'],
            original_outcome=r['outcome'],
            reported_outcome=change['reported_outcome'] if change else r['outcome'],
            author_reviewed=bool(change)))

    def summarize(subset):
        result = []
        for arm in ('direct', 'set'):
            rr = [r for r in subset if r['arm'] == arm]
            counts = Counter(r['reported_outcome'] for r in rr)
            exact, unsafe, refusal = (counts[k] for k in ('exact', 'unsafe_accept', 'false_refusal'))
            result.append(dict(profile='opus55_medium', arm=arm, n=len(rr),
                exact=exact, unsafe=unsafe, false_refusal=refusal,
                other=len(rr)-exact-unsafe-refusal,
                expected_accept=sum(r['expected'] == 'accept' for r in rr),
                correct_accept=sum(r['expected'] == 'accept' and r['reported_outcome'] == 'exact' for r in rr),
                outcomes=dict(counts), author_reviewed=True,
                reclassified=sum(r['author_reviewed'] for r in rr),
                review_source=OPUS_REVIEW,
                metric_basis='Original outcomes with author-confirmed decision reclassifications; local execution flags unchanged'))
        return result

    paired = summarize([r for r in rows if r['included_in_paired_display']])
    all_observed = summarize(rows)
    assert rows == review['reported_rows']
    assert paired == review['paired_summary'] and all_observed == review['all_observed_summary']
    return review


def author_report(root):
    report = json.loads((Path(root) / REPORT).read_text())
    assert report['status'] == 'author_confirmed_aggregates_pending_raw_import'
    assert not report['raw_records_received']
    completion = primary_completion(root)
    primary = {(r['profile'], r['arm']): r for r in report['primary']}
    primary.update({(r['profile'], r['arm']): r for r in completion['primary']})
    report['primary'] = list(primary.values())
    report['update_sources'] = [REPORT, PRIMARY_COMPLETION]
    report['unavailable'] = completion['missing']
    for row in report['primary'] + report['language']:
        assert row['n'] == 200 and 0 <= row['exact'] <= row['n']
        assert sum(row['outcomes'].values()) == row['n']
        if row['error_partition_reported']:
            assert row['unsafe'] == row['outcomes'].get('unsafe_accept', 0)
            assert row['false_refusal'] == row['outcomes'].get('false_refusal', 0)
        else:
            assert row['unsafe'] is None and row['false_refusal'] is None
    return report


def display_language(root):
    rows = json.loads((Path(root) / 'data/derived/language_all_methods_matched.json').read_text())
    by = {(r['profile'], r['arm'], r['language']): r for r in rows}
    report = author_report(root)
    # No 200-case Python outcomes accompanied the newly reported Astra results.
    for r in report['language']:
        by[r['profile'], r['arm'], r['language']] = r
        by.pop((r['profile'], 'python_fresh', r['language']), None)
    return by
