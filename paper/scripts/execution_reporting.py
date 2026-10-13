"""Concentrated execution controls, derived without changing frozen outcomes."""
from pathlib import Path
import json
from certified_primary import summary_rows, intervals as primary_intervals


def build(root, table_dir=None):
    root = Path(root)
    dest = Path(table_dir) if table_dir else root / ('tables' if (root/'paper.tex').exists() else 'tex/tables')
    dest.mkdir(parents=True, exist_ok=True)
    (root / 'output').mkdir(exist_ok=True)
    def load(name):
        return json.loads((root / name).read_text())
    def pooled(rows):
        assert rows
        out = {k: sum(r[k] for r in rows) for k in
               ('n', 'exact', 'unsafe', 'false_refusal', 'expected_accept')}
        out['correct_accept'] = sum(r.get('correct_accept', r.get('safe_exact_accept', 0)) for r in rows)
        out['other'] = out['n'] - out['exact'] - out['unsafe'] - out['false_refusal']
        assert out['other'] >= 0 and out['correct_accept'] <= out['expected_accept']
        return out
    main = summary_rows(root)
    grid = [r for r in load('data/derived/grid_summary.json')
            if r['group'] == 'all' and r['profile_complete']
            and not r['profile'].endswith('_ultra')]
    language = load('data/derived/language_all_methods_matched.json')
    auth = load('data/diagnostics/v43_evidence.json')['groups']
    rows = []
    def add(group, label, records, test, control='python_fresh'):
        sides = {name: pooled([r for r in records if test(r) and r['arm'] == arm])
                 for name, arm in [('procedural', control), ('state_wise', 'set')]}
        assert sides['procedural']['n'] == sides['state_wise']['n']
        assert sides['procedural']['expected_accept'] == sides['state_wise']['expected_accept']
        rows.append(dict(group=group, label=label, control=control, **sides))
    for profile, label in [('ds_flash_low', 'DS low'), ('ds_flash_high', 'DS high')]:
        add('Primary decisions', label, main, lambda r, p=profile: r['profile'] == p)
    for prefix, label in [('astra_', 'Astra (5 settings)'), ('gpt56_sol_', 'Sol (6 settings)'),
                          ('gpt56_terra_', 'Terra (6 settings)'), ('gpt56_luna_', 'Luna (6 settings)')]:
        add('Requested effort', label, grid, lambda r, p=prefix: r['profile'].startswith(p))
    for prefix, label in [('ds_', 'DS (3 profiles; ZH/EN)'), ('astra_', 'Astra (ZH/EN)')]:
        add('Task language', label, language, lambda r, p=prefix: r['profile'].startswith(p))
    for control, group in [('python_cached', 'Matched catalogue input'), ('python_fresh', 'Visible catalogue input')]:
        for prefix, label in [('ds_', 'DS (3 settings)'), ('astra_', 'Astra (3 settings)')]:
            add(group, label, auth, lambda r, p=prefix: r['profile'].startswith(p), control)
    by = {(r['profile'], r['arm']): r for r in main}
    resources = []
    for profile, label in [('ds_flash_low', 'DS low'), ('ds_flash_high', 'DS high'), ('astra_max', 'Astra max')]:
        rr = {}
        for name, arm in [('procedural', 'python_fresh'), ('state_wise', 'set')]:
            r = by[profile, arm]
            assert r['input_tokens']['missing'] == r['output_tokens']['missing'] == 0
            rr[name] = dict(n=r['n'], mean_tokens=r['input_tokens']['mean'] + r['output_tokens']['mean'],
                            median_request_seconds=r['seconds']['median'])
        resources.append(dict(profile=profile, label=label, token_reduction_percent=
            100 * (1 - rr['state_wise']['mean_tokens'] / rr['procedural']['mean_tokens']), **rr))
    intervals = [r for r in primary_intervals(root)
                 if r['profile'] == 'deepseek_pooled' and r['baseline'] == 'python_fresh']
    manuscript_rows = [r for r in rows if r['group'] in
                       ('Primary decisions', 'Requested effort', 'Matched catalogue input')]
    result = dict(direction='Set-Py -> Set (DSL)', decisions=rows, resources=resources,
        manuscript_decisions=manuscript_rows, manuscript_resource_comparison=False,
        bootstrap_intervals=intervals, cohorts_pooled=False, observations_changed=False,
        resource_cohort='Original measured calls; no decision outcomes inferred from resource measurements')
    (root / 'output/execution_controls_values.json').write_text(json.dumps(result, indent=2) + '\n')
    lines = [r'\begin{tabular}{@{}lrrrr@{}}', r'\toprule',
        r'Configuration & $n$ & Unsafe $\downarrow$ & Safe / feasible $\uparrow$ & Exact $\uparrow$\\', r'\midrule']
    last = None
    for row in manuscript_rows:
        if row['group'] != last:
            if last is not None: lines.append(r'\addlinespace[3pt]')
            lines.append(r'\multicolumn{5}{l}{\emph{' + row['group'] + r'}}\\')
            last = row['group']
        a, b = row['procedural'], row['state_wise']
        def arrow(key):
            return f"${a[key]}\\to{b[key]}$"
        safe = f"${a['correct_accept']}/{a['expected_accept']}\\to{b['correct_accept']}/{b['expected_accept']}$"
        lines.append(row['label'] + f" & {a['n']} & " + ' & '.join([
            arrow('unsafe'), safe, arrow('exact')]) + r'\\')
    lines += [r'\bottomrule', r'\end{tabular}']
    (dest / 'execution_controls.tex').write_text('\n'.join(lines) + '\n')
    templates = {(r['profile'],r['arm'],r['template']):r for r in summary_rows(root, 'template')}
    lines = [r'\begin{tabular}{@{}lrr@{}}',r'\toprule',
        r'Template & DS low & DS high\\',r'\midrule']
    for family in 'abcd':
        for i in range(1,6):
            key = family + str(i)
            cells = [f"${templates[p,'direct',key]['exact']}\\to{templates[p,'set',key]['exact']}$"
                     for p in ['ds_flash_low','ds_flash_high']]
            lines.append(key + ' & ' + ' & '.join(cells) + r'\\')
        if family != 'd': lines.append(r'\midrule')
    lines += [r'\bottomrule',r'\end{tabular}']
    (dest / 'primary_templates.tex').write_text('\n'.join(lines) + '\n')
    return result


if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1])
