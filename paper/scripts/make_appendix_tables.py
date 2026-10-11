"""Compact evidence tables: combine denominators and error partitions once.

Only reporting fragments are written. Frozen records and author reports are
read-only; absent observations and unreported categories remain missing.
"""
from pathlib import Path
from collections import Counter
import json
from primary_profiles import display_primary
from reported_results import display_language, opus_output_review


def build(root, table_dir=None):
    root = Path(root)
    dest = Path(table_dir) if table_dir else root / 'tables'
    dest.mkdir(parents=True, exist_ok=True)
    def load(name):
        return json.loads((root / name).read_text())
    def put(name, lines):
        (dest / (name + '.tex')).write_text('\n'.join(lines) + '\n')
    def table(spec, header):
        return [r'\begin{tabular}{' + spec + '}', r'\toprule', header, r'\midrule']
    def finish(name, lines):
        put(name, lines + [r'\bottomrule', r'\end{tabular}'])
    def outcome_cells(row):
        if row is None:
            return ['--', '--']
        other = row['n'] - row['exact'] - row['unsafe'] - row['false_refusal']
        assert min(row['exact'], row['unsafe'], row['false_refusal'], other) >= 0
        return [f"{row['exact']}/{row['n']}",
                f"{row['unsafe']}/{row['false_refusal']}/{other}"]

    display = display_primary(root)
    partial = {p['profile'] for p in display['partials']}
    reported = set(display['author_reported_profiles'])
    lines = table('@{}llrrrrrr@{}',
        r'Configuration & Method & Budget & Timeout & Service & Invalid & Value & Unreported\\')
    for profile, label in zip(display['profiles'], display['labels']):
        mark = ''
        for i, arm in enumerate(('direct', 'set')):
            row = display['by'][profile, arm]
            if not row.get('failure_subtypes_reported', True):
                cells = ['--'] * 5 + [str(row['other'])]
            elif row.get('error_partition_reported', True):
                o = row['outcomes']
                counts = [o.get(k, 0) for k in ('output_budget', 'timeout',
                    'transport_or_provider_failure', 'invalid_output')]
                counts += [sum(o.get(k, 0) for k in ('certificate_underclaim',
                    'certificate_overclaim', 'suboptimal', 'other_error')), 0]
                assert sum(counts) == row['n']-row['exact']-row['unsafe']-row['false_refusal'], (profile, arm)
                cells = list(map(str, counts))
            else:
                cells = ['--'] * 5 + [str(row['n'] - row['exact'])]
            lines.append((label + mark if i == 0 else '') + ' & ' + arm.capitalize()
                         + ' & ' + ' & '.join(cells) + r'\\')
    finish('appendix_primary_other', lines)

    # Include all observed Opus outcomes without mixing them into paired rates.
    review = opus_output_review(root)
    lines = table('@{}llrrrrr@{}', r'Scope & Method & $n$ & Exact & Unsafe & Refusal & Other\\')
    for name, records in [('Paired', review['paired_summary']), ('All observed', review['all_observed_summary'])]:
        for i, row in enumerate(records):
            lines.append((name if i == 0 else '') + ' & ' + row['arm'].capitalize() + ' & '
                         + ' & '.join(str(row[k]) for k in ('n', 'exact', 'unsafe', 'false_refusal', 'other')) + r'\\')
    finish('appendix_opus', lines)

    grid = {(r['profile'], r['arm']): r for r in load('data/derived/grid_summary.json') if r['group'] == 'all'}
    arms = ('direct', 'set')
    lines = table('@{}llrrrr@{}',
        r'&&\multicolumn{2}{c}{Direct}&\multicolumn{2}{c}{Set}\\' + '\n' +
        r'Model & Setting & Exact/$n$ & U/R/O & Exact/$n$ & U/R/O\\')
    for model, label in [('gpt56_sol', 'Sol'), ('gpt56_terra', 'Terra'), ('gpt56_luna', 'Luna')]:
        first = True
        for effort in ('none', 'low', 'medium', 'high', 'xhigh', 'max'):
            profile = model + '_' + effort
            if (profile, 'direct') not in grid:
                continue
            rows = [grid[profile, a] for a in arms]
            if not all(r['profile_complete'] and r['n'] == 60 for r in rows):
                continue
            marker = ''
            cells = [cell for row in rows for cell in outcome_cells(row)]
            lines.append((label if first else '') + ' & ' + ('off' if effort == 'none' else effort) + marker
                         + ' & ' + ' & '.join(cells) + r'\\')
            first = False
        lines.append(r'\midrule')
    finish('appendix_grid', lines[:-1])

    language = display_language(root)
    original = {(r['profile'], r['arm'], r['language']): r
                for r in load('data/derived/language_all_methods_matched.json')}
    lines = table('@{}llrrrr@{}',
        r'&&\multicolumn{2}{c}{Direct}&\multicolumn{2}{c}{Set}\\' + '\n' +
        r'Configuration & Language & Exact/$n$ & U/R/O & Exact/$n$ & U/R/O\\')
    for profile, label, source in [('ds_flash_low','DS low', original), ('ds_flash_high','DS high', original),
            ('ds_flash_max','DS max', original), ('astra_max','Astra max (60)', original),
            ('astra_max','Astra max (200)', language)]:
        for i, lang in enumerate(('zh', 'en')):
            cells = [cell for a in arms for cell in outcome_cells(source.get((profile,a,lang)))]
            lines.append((label if i == 0 else '') + ' & ' + lang.upper() + ' & ' + ' & '.join(cells) + r'\\')
        lines.append(r'\midrule')
    finish('appendix_language', lines[:-1])

    # All three ambiguity routes, with explicit denominators and disjoint errors.
    records = load('data/supplements/intent_ambiguity_20261011/parameter_rows.json')
    labels = [('ds_flash_low','DS low'), ('ds_flash_max','DS max'), ('glm53_low','GLM low'),
              ('glm53_max','GLM max'), ('qwen_max_low','Qwen Max low'), ('qwen_max_xhigh','Qwen Max xhigh')]
    lines = table('@{}llrrrrrr@{}',
        r'&&\multicolumn{2}{c}{Direct}&\multicolumn{2}{c}{Merged}&\multicolumn{2}{c}{Set}\\' + '\n' +
        r'Cohort & Configuration & Exact/$n$ & U/R/O & Exact/$n$ & U/R/O & Exact/$n$ & U/R/O\\')
    for partition, label in [('discovery','Discovery'), ('held_out_instances','Validation'), ('boundary_search','Stress')]:
        profiles = [('gpt6_max','Astra max')] if partition == 'boundary_search' else labels
        for profile, model in profiles:
            cells = []
            for method in ('rule_direct','flat_program','set_mechanism'):
                rr = [r for r in records if (r['partition'],r['profile'],r['method']) == (partition,profile,method)]
                row = dict(n=len(rr), exact=sum(r['exact'] for r in rr), unsafe=sum(r['unsafe'] for r in rr),
                           false_refusal=sum(r['false_refusal'] for r in rr)) if rr else None
                cells.extend(outcome_cells(row))
            lines.append(label + ' & ' + model + ' & ' + ' & '.join(cells) + r'\\')
        lines.append(r'\midrule')
    finish('appendix_intent', lines[:-1])

    rows = load('data/diagnostics/stress_summary.json')['groups']
    by = {(r['profile'],r['arm'],r['variant']):r for r in rows}
    lines = table('@{}llrrrr@{}',
        r'Configuration & Frozen realization & Unsafe domain & Unsafe selection & Unsafe selection & Invalid\\' + '\n' +
        r'&& Mixed & Mixed & Unsafe-only & Mixed / only\\')
    for profile, label in [('ds_flash_low','DS low'), ('ds_flash_high','DS high'), ('ds_flash_max','DS max')]:
        for i, (arm, name) in enumerate([('python_cached','Python matched'), ('python_fresh','Python visible'), ('set','Set')]):
            m = by[profile,arm,'risk_grid']; s = by[profile,arm,'single_4000_yuan']
            assert m['n'] == s['n'] == 72
            lines.append((label if i == 0 else '') + ' & ' + name + ' & ' +
                f"{m['full_domain_unsafe']} & {m['unsafe_accept']} & {s['unsafe_accept']} & {m['invalid']}/{s['invalid']}" + r'\\')
        lines.append(r'\midrule')
    finish('appendix_replay', lines[:-1])


if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1])
