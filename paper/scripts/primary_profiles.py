"""Complete, frozen primary cohorts in a fixed model-family display order."""
from pathlib import Path
import json

ORDER = [
    ('ds_flash_low', 'DeepSeek low'),
    ('ds_flash_high', 'DeepSeek high'),
    ('qwen_flash_low', 'Qwen Flash low'),
    ('qwen_max_low', 'Qwen Max low'),
    ('glm53_flash_low', 'GLM Flash low'),
    ('glm53_high', 'GLM high'),
    ('gpt56_luna_medium', '5.6 Luna medium'),
    ('gpt56_terra_medium', '5.6 Terra medium'),
    ('gpt56_sol_medium', '5.6 Sol medium'),
    ('astra_max', 'Astra max'),
    ('opus55_medium', 'Opus 5.5 medium'),
]


def complete_primary(root):
    root = Path(root)
    base = json.loads((root / 'data/derived/main_summary.json').read_text())
    sources = ['data/derived/main_summary.json', 'data/supplements/qwen_primary200/summary.json']
    rows = base + json.loads((root / sources[1]).read_text())
    extensions = []
    for folder in sorted((root / 'data/supplements').glob('primary200_*')):
        path = folder / 'summary.json'
        assert path.exists() and (folder / 'provenance.json').exists()
        data = json.loads(path.read_text())
        assert len(data) == 2 and all(v['n'] == 200 for v in data)
        assert {v['arm'] for v in data} == {'direct', 'set'}
        rows.extend(data)
        sources.append(str(path.relative_to(root)))
        extensions.append(folder)
    by = {(r['profile'], r['arm']): r for r in rows}
    assert len(by) == len(rows), 'Duplicate frozen primary profile'
    selected = [(p, label) for p, label in ORDER if (p, 'direct') in by]
    assert len(selected) * 2 == sum(r['arm'] in ('direct', 'set') for r in rows)
    return dict(by=by, profiles=[p for p, _ in selected], labels=[label for _, label in selected],
                sources=sources, extensions=extensions, trials=400*len(selected))


def display_primary(root, include_author_reports=True):
    """Add labelled observed partial pairs without changing complete-cohort counts."""
    root = Path(root)
    complete = complete_primary(root)
    by = dict(complete['by'])
    sources = list(complete['sources'])
    partials = []
    for folder in sorted((root / 'data/supplements').glob('partial_primary_*')):
        provenance = json.loads((folder / 'provenance.json').read_text())
        profile = provenance['profiles'][0]['id']
        if profile in complete['profiles']:
            continue
        summaries = json.loads((folder / 'summary.json').read_text())
        assert len(summaries) == 2 and {r['arm'] for r in summaries} == {'direct', 'set'}
        assert all(r['n'] == provenance['paired_cases'] < 200 for r in summaries)
        assert provenance['partial'] and not provenance['extrapolated_counts']
        assert all((r['profile'], r['arm']) not in by for r in summaries)
        by.update({(r['profile'], r['arm']): r for r in summaries})
        sources.append(str((folder / 'summary.json').relative_to(root)))
        partials.append(dict(profile=profile, folder=folder, n=provenance['paired_cases'],
                             provenance=provenance))
    author_profiles = []
    reviewed_profiles = []
    if include_author_reports:
        from reported_results import author_report, REPORT, PRIMARY_COMPLETION, opus_output_review, OPUS_REVIEW
        for row in author_report(root)['primary']:
            by[row['profile'], row['arm']] = row
            if row['profile'] not in author_profiles:
                author_profiles.append(row['profile'])
        partials = [p for p in partials if p['profile'] not in author_profiles]
        sources.extend([REPORT, PRIMARY_COMPLETION])
        review = opus_output_review(root)
        for row in review['paired_summary']:
            if row['profile'] in author_profiles:
                continue  # A complete primary update supersedes this earlier pilot.
            assert by[row['profile'], row['arm']]['n'] == row['n']
            by[row['profile'], row['arm']] = row
            if row['profile'] not in reviewed_profiles:
                reviewed_profiles.append(row['profile'])
        if reviewed_profiles:
            sources.append(OPUS_REVIEW)
    selected = [(p, label) for p, label in ORDER if (p, 'direct') in by]
    return dict(by=by, profiles=[p for p, _ in selected], labels=[l for _, l in selected],
                author_reported_profiles=author_profiles,
                author_reviewed_profiles=reviewed_profiles,
                sources=sources, partials=partials, complete=complete,
                partial_trials=sum(2*p['n'] for p in partials),
                display_trials=sum(by[p,a]['n'] for p,_ in selected for a in ('direct','set')))
