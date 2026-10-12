"""Single offline entry for the manuscript's reporting and contract checks.

Install requirements.txt, then run ``python reproduce.py --pdf`` from the
source package. The optional PDF step requires latexmk and pdfLaTeX. Frozen
reporting inputs are read as supplied; this entry does not call model APIs
or replace externally supplied aggregates with newly scored observations.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))


def input_hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / 'data').rglob('*')) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', action='store_true', help='Also compile paper.tex with latexmk.')
    parser.add_argument('--latexmk', default='latexmk', help='latexmk executable or path.')
    args = parser.parse_args()
    out = ROOT / 'output/reproduction'
    out.mkdir(parents=True, exist_ok=True)
    before = input_hashes()
    env = dict(os.environ, MPLBACKEND='Agg', PYTHONDONTWRITEBYTECODE='1')
    commands = []

    def run(name, command, cwd=ROOT):
        log = out / (name + '.log')
        print(name + ' ...', flush=True)
        with log.open('w') as stream:
            process = subprocess.run(command, cwd=cwd, env=env, stdout=stream,
                                     stderr=subprocess.STDOUT)
        if process.returncode:
            raise SystemExit(name + ' failed; see ' + str(log.relative_to(ROOT)))
        commands.append(name)

    run('tables', [sys.executable, str(ROOT / 'scripts/make_tables.py')])
    run('figures', [sys.executable, str(ROOT / 'scripts/draw_paper.py'), '--only',
                   '13_authorization_diagnostics', '14_safe_completion',
                   '15_configuration_robustness', '16_retained_intent'])
    run('decision_contract', [sys.executable, str(ROOT / 'scripts/check_decision_contract.py')])
    run('primary_trace', [sys.executable, str(ROOT / 'scripts/verify_primary_trace.py')])

    from intent_ambiguity_reporting import figure3_results
    from primary_profiles import display_primary
    from prompt_control_reporting import analyze as analyze_prompt_controls
    prompt_controls = analyze_prompt_controls(ROOT)
    assert prompt_controls['prompt_calls'] == 1000
    assert prompt_controls['full_four_way_evaluations'] == 2080
    paired = figure3_results(ROOT)
    plotted = json.loads((ROOT / 'figures/16_retained_intent_values.json').read_text())
    plot_by = {r['profile']: r for r in plotted['profiles']}
    assert len(plot_by) == len(paired) == 4
    for row in paired:
        plot = plot_by[row['profile']]
        for arm in ['direct', 'set']:
            c = row[arm]
            assert c['n'] == plot['n_per_method']
            assert c['exact'] == plot[arm + '_exact']
            assert sum(c[k] for k in ['exact', 'unsafe', 'false_refusal', 'other']) == c['n']
            assert abs(100 * c['exact'] / c['n'] - plot[arm + '_percent']) < 1e-10
    contract = json.loads((ROOT / 'output/algorithm_contract_check.json').read_text())
    assert contract['status'] == 'passed' and contract['cases'] == 10
    primary = display_primary(ROOT)
    final_primary = json.loads((ROOT / 'output/final_primary_results.json').read_text())
    assert final_primary['pooled_deepseek']['set']['exact'] == 369
    assert len(final_primary['decisions']) == 400
    for row in primary['by'].values():
        if row['arm'] in ['direct', 'set'] and all(row.get(k) is not None for k in ['exact', 'unsafe', 'false_refusal']):
            assert sum(row[k] for k in ['exact', 'unsafe', 'false_refusal']) <= row['n']

    generated_pdf = None
    if args.pdf:
        latexmk = shutil.which(args.latexmk)
        if not latexmk:
            raise SystemExit('Install latexmk and pdfLaTeX, or omit --pdf for analysis only.')
        source = ROOT if (ROOT / 'paper.tex').exists() else ROOT / 'tex'
        build = out / 'latex'
        build.mkdir(exist_ok=True)
        run('paper', [latexmk, '-pdf', '-interaction=nonstopmode', '-halt-on-error',
                      '-outdir=' + str(build), 'paper.tex'], cwd=source)
        generated_pdf = str((build / 'paper.pdf').relative_to(ROOT))

    after = input_hashes()
    assert before == after, 'Frozen reporting inputs changed during reproduction.'
    report = {
        'status': 'passed', 'model_calls': 0, 'input_files_unchanged': len(before),
        'input_sha256': before, 'steps': commands,
        'scope': 'Offline reconstruction of reported tables and figures from frozen reporting inputs; no new model inference.',
        'primary_profiles': primary['profiles'], 'primary_reported_outcomes': primary['display_trials'],
        'primary_deepseek_results': final_primary['pooled_deepseek'],
        'figure3_evaluations': sum(r[a]['n'] for r in paired for a in ['direct', 'set']),
        'figure3_complete_results': paired, 'decision_contract_checks': contract['cases'],
        'primary_trace_event_candidate_checks': 14592,
        'prompt_engineering_calls': prompt_controls['prompt_calls'],
        'four_method_control_outcomes': prompt_controls['full_four_way_evaluations'],
        'pdf': generated_pdf,
        'outputs': ['tables/' if (ROOT / 'paper.tex').exists() else 'tex/tables/', 'figures/',
                    'output/figure3_complete_results.json', 'output/algorithm_contract_check.json']
    }
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Passed. Report: output/reproduction/report.json', flush=True)


if __name__ == '__main__':
    main()
