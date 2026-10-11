"""Rebuild prompt and four-method controls from immutable per-trial rows."""
from collections import Counter
from pathlib import Path
import json

REL = Path('data/supplements/prompt_controls_20261011')
LABELS = {'ds_flash_low': 'DS low', 'ds_flash_high': 'DS high',
          'gpt56_sol_medium': 'Sol medium', 'gpt56_luna_medium': 'Luna medium',
          'gpt56_terra_medium': 'Terra medium'}


def aggregate(rows):
    counts = Counter(r['category'] for r in rows)
    assert set(counts) <= {'exact', 'unsafe', 'false_refusal', 'other'}
    return dict(n=len(rows), **{k: counts[k] for k in ['exact', 'unsafe', 'false_refusal', 'other']},
                feasible=sum(r['expected'] == 'accept' for r in rows),
                safe_completion=sum(r['expected'] == 'accept' and r['category'] == 'exact' for r in rows),
                exact_percent=100 * counts['exact'] / len(rows) if rows else None)


def analyze(root):
    root = Path(root)
    rows = json.loads((root / REL / 'rows.json').read_text())
    cohorts = json.loads((root / REL / 'cohorts.json').read_text())
    assert len(rows) == len({r['record_id'] for r in rows}) == 3520
    by = {(r['profile'], r['method'], r['case']): r for r in rows}
    assert len(by) == len(rows)
    prompt, four_way = [], []
    for profile in cohorts['profiles']:
        sides = {}
        for method in ['direct', 'prompt']:
            selected = [r for r in rows if r['profile'] == profile and r['method'] == method]
            assert len(selected) == len({r['case'] for r in selected}) == 200
            assert len({r['template'] for r in selected}) == 20
            sides[method] = aggregate(selected)
        cases = {r['case'] for r in rows if r['profile'] == profile and r['method'] == 'prompt'}
        flips = Counter()
        for case in cases:
            a, b = by[profile, 'direct', case], by[profile, 'prompt', case]
            assert a['public_sha256'] == b['public_sha256']
            assert (a['model'], a['effort'], a['timeout_seconds'], a['output_cap']) == (
                b['model'], b['effort'], b['timeout_seconds'], b['output_cap'])
            old, new = a['category'] == 'exact', b['category'] == 'exact'
            flips['both_exact' if old and new else 'exact_to_error' if old else
                  'error_to_exact' if new else 'both_error'] += 1
        prompt.append(dict(profile=profile, label=LABELS[profile], **sides,
                           delta_pp=sides['prompt']['exact_percent'] - sides['direct']['exact_percent'],
                           paired_transitions=dict(flips)))
        shared = cohorts['four_way_cases'][profile]
        assert len(shared) == (200 if profile.startswith('ds_') else 40)
        result = {method: aggregate([by[profile, method, case] for case in shared])
                  for method in ['direct', 'prompt', 'set', 'python']}
        assert all(v['n'] == len(shared) and v['feasible'] * 2 == v['n'] for v in result.values())
        for case in shared:
            assert len({by[profile, method, case]['public_sha256']
                        for method in ['direct', 'prompt', 'set', 'python']}) == 1
        four_way.append(dict(profile=profile, label=LABELS[profile], **result))
    return dict(prompt_calls=1000, archived_comparison_records=3520,
                prompt_comparisons=prompt, four_way_comparisons=four_way,
                full_four_way_evaluations=sum(r['direct']['n'] * 4 for r in four_way),
                all_failures_retained=True, cohorts_overlap=True,
                inputs='Retained per-trial outcomes; no external aggregate updates used in paired controls.')


def build(root, table_dir=None):
    root = Path(root)
    result = analyze(root)
    dest = Path(table_dir) if table_dir else root / ('tables' if (root / 'paper.tex').exists() else 'tex/tables')
    dest.mkdir(parents=True, exist_ok=True)
    (root / 'output').mkdir(exist_ok=True)
    (root / 'output/prompt_controls_values.json').write_text(json.dumps(result, indent=2) + '\n')
    lines = [r'\begin{tabular}{@{}lrrrrr@{}}', r'\toprule',
             r'Configuration & $n$ & Direct & Prompt & Prompt U/R/O & $\Delta$ (pp)\\', r'\midrule']
    for r in result['prompt_comparisons']:
        a, b = r['direct'], r['prompt']
        lines.append(f"{r['label']} & {a['n']} & {a['exact_percent']:.1f} & {b['exact_percent']:.1f} & "
                     f"{b['unsafe']}/{b['false_refusal']}/{b['other']} & ${r['delta_pp']:+.1f}$" + r'\\')
    lines += [r'\bottomrule', r'\end{tabular}']
    (dest / 'prompt_control.tex').write_text('\n'.join(lines) + '\n')
    lines = [r'\begin{tabular}{@{}llrrrr@{}}', r'\toprule',
             r'& & & & \multicolumn{2}{c}{Framework implementations}\\',
             r'\cmidrule(l){5-6}',
             r'Configuration & $n$ & Direct & Prompt & Set (DSL) & Set-Py\\', r'\midrule']
    for r in result['four_way_comparisons']:
        cells = []
        for method in ['direct', 'prompt', 'set', 'python']:
            a = r[method]
            cells.append(r'\shortstack[r]{' + f"{a['exact_percent']:.1f}" + r'\\{\scriptsize ' +
                         f"{a['unsafe']}/{a['false_refusal']}/{a['other']}" + '}}')
        lines.append(r['label'] + f" & {r['direct']['n']} & " + ' & '.join(cells) + r'\\[3pt]')
    lines += [r'\bottomrule', r'\end{tabular}']
    (dest / 'four_way_controls.tex').write_text('\n'.join(lines) + '\n')
    return result


if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1])
