"""Tables and a human-readable index from the audited historical cohorts."""
from pathlib import Path
import csv, json


def figure3_results(root):
    """Recompute the four displayed pairs directly from their retained outcomes."""
    root = Path(root)
    data = root / 'data/supplements/intent_ambiguity_20261011'
    rows = json.loads((data / 'parameter_rows.json').read_text())
    summary = json.loads((data / 'parameter_summary.json').read_text())
    profiles = [('ds_flash_low', 'DeepSeek low'), ('ds_flash_max', 'DeepSeek max'),
                ('glm53_low', 'GLM low'), ('qwen_max_low', 'Qwen Max low')]
    displayed = {r['profile']: r for r in summary['displayed']}
    result = []
    for profile, label in profiles:
        reference = displayed[profile]
        entry = {'profile': profile, 'label': label}
        case_sets = []
        for arm, method in [('direct', 'rule_direct'), ('set', 'set_mechanism')]:
            selected = [r for r in rows if r['profile'] == profile
                        and r['partition'] in reference['partitions'] and r['method'] == method]
            assert len({r['case_id'] for r in selected}) == len(selected)
            assert all(sum(bool(r[k]) for k in ['exact', 'unsafe', 'false_refusal']) <= 1 for r in selected)
            counts = {'n': len(selected)}
            counts.update({k: sum(bool(r[k]) for r in selected)
                           for k in ['exact', 'unsafe', 'false_refusal']})
            counts['other'] = counts['n'] - sum(counts[k] for k in ['exact', 'unsafe', 'false_refusal'])
            assert all(counts[k] == reference[method][k] for k in ['n', 'exact', 'unsafe', 'false_refusal'])
            entry[arm] = counts
            case_sets.append({r['case_id'] for r in selected})
        assert case_sets[0] == case_sets[1]
        result.append(entry)
    assert sum(r[a]['n'] for r in result for a in ['direct', 'set']) == 294
    return result


def build(root):
    root=Path(root); data=root/'data/supplements/intent_ambiguity_20261011'
    (root/'output').mkdir(exist_ok=True)
    summary=json.loads((data/'parameter_summary.json').read_text())
    rows=json.loads((data/'parameter_rows.json').read_text())
    missing=json.loads((data/'parameter_missing.json').read_text())
    tables=root/'tables'
    tables.mkdir(parents=True, exist_ok=True)
    figure3 = figure3_results(root)
    lines = [r'\begin{tabular}{@{}lrrrrr@{}}', r'\toprule',
             r'Configuration & $n$ & Exact $\uparrow$ & Unsafe $\downarrow$ & False refusal $\downarrow$ & Other $\downarrow$\\', r'\midrule']
    for row in figure3:
        cells = [f"{row['direct'][k]}$\\to${row['set'][k]}"
                 for k in ['exact', 'unsafe', 'false_refusal', 'other']]
        lines.append(row['label'] + ' & ' + str(row['direct']['n']) + ' & ' + ' & '.join(cells) + r'\\')
    lines += [r'\bottomrule', r'\end{tabular}']
    (tables/'intent_figure3.tex').write_text('\n'.join(lines)+'\n')
    (root/'output/figure3_complete_results.json').write_text(json.dumps(figure3, indent=2)+'\n')
    labels={'ds_flash_low':'DeepSeek low','ds_flash_max':'DeepSeek max',
            'glm53_low':'GLM low','glm53_max':'GLM max',
            'qwen_max_low':'Qwen Max low','qwen_max_xhigh':'Qwen Max xhigh',
            'gpt6_max':'Astra max'}
    lines=[r'\begin{tabular}{@{}lrrr@{}}',r'\toprule',
           r'Configuration & $n$ & Exact D$\to$S & Unsafe D$\to$S\\',r'\midrule']
    for r in summary['displayed']:
        d,s=r['rule_direct'],r['set_mechanism']
        label=labels[r['profile']]+(r'$^\dagger$' if r['profile']=='qwen_max_low' else '')
        lines.append(f"{label} & {d['n']} & {d['exact']}$\\to${s['exact']} & {d['unsafe']}$\\to${s['unsafe']}"+r'\\')
    lines += [r'\bottomrule',r'\end{tabular}']
    (tables/'intent_main.tex').write_text('\n'.join(lines)+'\n')
    lines=[r'\begin{tabular}{@{}llrrrr@{}}',r'\toprule',
           r'Cohort & Configuration & Direct exact/$n$ & Merged exact/$n$ & Set exact/$n$ & Unsafe D/M/S\\',r'\midrule']
    for partition,label in [('discovery','Discovery'),('held_out_instances','Validation'),('boundary_search','Stress')]:
        profiles=['gpt6_max'] if partition=='boundary_search' else list(labels)[:-1]
        for profile in profiles:
            rr=[r for r in rows if r['partition']==partition and r['profile']==profile]
            methods=['rule_direct','flat_program','set_mechanism'];counts=[];unsafe=[]
            for m in methods:
                arm=[r for r in rr if r['method']==m]
                counts.append(f"{sum(r['exact'] for r in arm)}/{len(arm)}" if arm else '--')
                unsafe.append(str(sum(r['unsafe'] for r in arm)) if arm else '--')
            lines.append(f"{label} & {labels[profile]} & "+' & '.join(counts)+' & '+' / '.join(unsafe)+r'\\')
        if partition!='boundary_search':lines.append(r'\midrule')
    lines += [r'\bottomrule',r'\end{tabular}']
    (tables/'intent_all.tex').write_text('\n'.join(lines)+'\n')
    # An ordinary spreadsheet index, retaining every observed result and raw path.
    fields=['task_id','case_id','family_id','profile','method','partition','condition',
            'exact','unsafe','false_refusal','valid','overpermissive','category','source_path']
    # The archived index is immutable once created; presentation changes do not rewrite it.
    if not (data/'trial_index.csv').exists():
        with (data/'trial_index.csv').open('w',encoding='utf-8-sig',newline='') as fh:
            w=csv.DictWriter(fh,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    doc = "# Retained-intent evaluations\n\nComplete outcome counts are in the JSON inputs and generated tables. See docs/data.md in the repository for provenance and cohort definitions.\n"
    (root/'output/intent_audit.md').write_text(doc)

if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1])
