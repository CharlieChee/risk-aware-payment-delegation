"""Report primary DeepSeek decisions from the complete-domain evaluator.

The retained responses and historical scoring files remain unchanged. Every
reported decision is joined to the saved Algorithm 1 replay by profile and case.
"""
from collections import Counter
from pathlib import Path
import json

REPLAY = 'data/supplements/primary_certification_20261011/replay.json'
PROFILES = ('ds_flash_low', 'ds_flash_high')


def load(root, name):
    return json.loads((Path(root) / name).read_text())


def replay_index(root):
    replay = load(root, REPLAY)
    assert replay['model_calls'] == 0 and not replay['historical_records_modified']
    by = {(r['profile'], r['case']): r for r in replay['outcomes']}
    assert len(by) == len(replay['outcomes']) == 400
    for profile in PROFILES:
        rows = [r for r in by.values() if r['profile'] == profile]
        assert len(rows) == 200
        assert all(r['current_exact'] == (r['current_outcome'] == 'exact') for r in rows)
        group = next(g for g in replay['groups'] if g['profile'] == profile)
        assert dict(Counter(r['current_outcome'] for r in rows)) == group['outcomes']
    return by


def main_rows(root):
    rows = load(root, 'data/derived/main_rows.json')
    current = replay_index(root)
    joined = set()
    for row in rows:
        key = row['profile'], row['case']
        if row['arm'] != 'set' or key not in current:
            continue
        decision = current[key]
        assert row['outcome'] == decision['archived_outcome']
        assert bool(row['exact']) == decision['archived_exact']
        row['archived_outcome'] = row['outcome']
        row['current_outcome'] = decision['current_outcome']
        if decision['current_exact'] != decision['archived_exact']:
            assert decision['status'] == 'failure' and decision['archived_exact']
            row['outcome'] = 'uncertified_execution'
        row['exact'] = decision['current_exact']
        row['unsafe_accept'] = decision['current_outcome'] == 'unsafe'
        row['false_reject'] = decision['current_outcome'] == 'false_refusal'
        row['invalid'] = decision['status'] == 'failure'
        row['decision_status'] = decision['status']
        row['decision_reason'] = decision['reason']
        row['scoring_source'] = REPLAY
        joined.add(key)
    assert joined == set(current)
    return rows


def summarize(rows):
    return dict(n=len(rows), exact=sum(r['exact'] for r in rows),
                unsafe=sum(r['unsafe_accept'] for r in rows),
                false_refusal=sum(r['false_reject'] for r in rows),
                expected_accept=sum(r['expected'] == 'accept' for r in rows),
                correct_accept=sum(r['expected'] == 'accept' and r['exact'] for r in rows),
                outcomes=dict(Counter(r['outcome'] for r in rows)))


def summary_rows(root, grouping=None):
    name = (grouping + '_summary') if grouping else 'main_summary'
    summaries = load(root, 'data/derived/' + name + '.json')
    rows = main_rows(root)
    for summary in summaries:
        if summary['profile'] not in PROFILES or summary['arm'] != 'set':
            continue
        selected = [r for r in rows if r['profile'] == summary['profile'] and r['arm'] == 'set'
                    and (grouping is None or r[grouping] == summary[grouping])]
        assert len(selected) == summary['n']
        summary.update(summarize(selected))
        summary['non_unsafe_failure'] = summary['n'] - summary['exact'] - summary['unsafe']
        summary['scoring_source'] = REPLAY
    return summaries


def intervals(root):
    import numpy as np
    rng = np.random.default_rng(20261008)
    rows = main_rows(root)
    results = []
    # Preserve the original resampling order, seed, clusters, and paired cases.
    for profile in ['astra_max', 'ds_flash_low', 'ds_flash_high', 'deepseek_pooled']:
        selected = [r for r in rows if r['profile'] == profile or
                    (profile == 'deepseek_pooled' and r['profile'] in PROFILES)]
        for baseline in ['direct', 'python_fresh']:
            for metric in ['exact', 'unsafe_accept']:
                diffs = []
                for template in sorted({r['template'] for r in selected}):
                    ours = [int(r[metric]) for r in selected if r['arm'] == 'set' and r['template'] == template]
                    base = [int(r[metric]) for r in selected if r['arm'] == baseline and r['template'] == template]
                    assert len(ours) == len(base)
                    diffs.append(np.mean(ours) - np.mean(base))
                boot = rng.choice(diffs, size=(20000, len(diffs)), replace=True).mean(axis=1)
                results.append(dict(profile=profile, baseline=baseline, metric=metric,
                    delta_percentage_points=float(np.mean(diffs) * 100),
                    cluster_bootstrap_95_interval_pp=[float(x * 100) for x in np.quantile(boot, [.025, .975])],
                    clusters=len(diffs), bootstrap_draws=20000))
    return results


def pooled(root):
    rows = main_rows(root)
    result = {}
    for arm in ['direct', 'set']:
        selected = [r for r in rows if r['profile'] in PROFILES and r['arm'] == arm]
        s = summarize(selected)
        result[arm] = dict(n=s['n'], distinct_tasks=len({r['case'] for r in selected}),
            profiles=2, exact=s['exact'], unsafe=s['unsafe'], false_refusal=s['false_refusal'],
            feasible_trials=s['expected_accept'], safe_exact_completion=s['correct_accept'],
            other_failures=s['n'] - s['exact'] - s['unsafe'] - s['false_refusal'])
    return result


def prompt_rows(root, rows):
    current = replay_index(root)
    joined = set()
    result = []
    for original in rows:
        row = dict(original)
        key = row['profile'], row['case']
        if row['method'] == 'set' and key in current:
            decision = current[key]
            assert (row['category'] == 'exact') == decision['archived_exact']
            row['category'] = decision['current_outcome']
            joined.add(key)
        result.append(row)
    assert joined == set(current)
    return result


def build(root):
    root = Path(root)
    result = dict(source=REPLAY, model_calls=0, historical_records_modified=False,
                  pooled_deepseek=pooled(root), intervals=intervals(root))
    result['decisions'] = [r for r in main_rows(root) if r['profile'] in PROFILES and r['arm'] == 'set']
    assert [result['pooled_deepseek'][a]['exact'] for a in ['direct', 'set']] == [248, 369]
    (root / 'output').mkdir(exist_ok=True)
    (root / 'output/final_primary_results.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1])
