"""Dense mechanism diagnostics and complete witness traces from frozen evidence."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

INK = '#1F2937'
MUTED = '#5E6C7B'
LINE = '#DCE2E7'
TEAL = '#007F82'
BLUE = '#53677F'
RED = '#B34438'


def authorization_replay_values(stress):
    """The complete DeepSeek subset of the frozen replay diagnostic."""
    profiles = ['ds_flash_low', 'ds_flash_high', 'ds_flash_max']
    metrics = ['n', 'grid_unsafe_domain', 'grid_unsafe_selection',
               'single_unsafe_selection', 'grid_invalid', 'single_invalid']
    rows = []
    for profile, label in zip(profiles, ['Low', 'High', 'Max']):
        groups = [g for g in stress['groups'] if g['profile'] == profile]
        assert len(groups) == 3 and all(g['n'] == 72 for g in groups)
        row = dict(profile=profile, label=label,
                   **{k: sum(g[k] for g in groups) for k in metrics})
        assert row['n'] == 216 and row['grid_unsafe_selection'] == 0
        assert row['grid_invalid'] == row['single_invalid']
        rows.append(row)
    return dict(source='data/diagnostics/stress_chart_data.json',
        scope='Pooled diagnostic collection across three DeepSeek settings; preparation strata remain indexed in the artifact',
        unit='Frozen rule artifacts, not independent natural-language requests',
        base_tasks=72, artifacts=sum(r['n'] for r in rows),
        catalogue_replays=2*sum(r['n'] for r in rows), profiles=rows,
        invalid_per_catalogue=sum(r['grid_invalid'] for r in rows),
        original_responses_modified=False, new_model_calls=0)


def draw_authorization(stress):
    """Compact grouped bars for a supplementary DeepSeek replay diagnostic."""
    values = authorization_replay_values(stress)
    rows = values['profiles']
    fig, ax = plt.subplots(figsize=(3.45, 2.95))
    fig.subplots_adjust(left=.160, right=.965, bottom=.270, top=.645)
    x = np.arange(len(rows)); width = .28
    series = [('grid_unsafe_domain', '#FFFFFF', '', -.17,
               'Unsafe admission - mixed catalogue'),
              ('single_unsafe_selection', '#BFBFBF', '///', .17,
               'Unsafe selection - unsafe-only catalogue')]
    for key, color, hatch, offset, label in series:
        bars = ax.bar(x+offset, [r[key] for r in rows], width=width,
                      color=color, edgecolor='black', hatch=hatch, label=label, zorder=3)
        ax.bar_label(bars, padding=3, fontsize=9, weight='bold', color='black')
    ax.set(xlim=(-.65, 2.65), ylim=(0, 13), yticks=[0, 4, 8, 12])
    ax.set_xticks(x, [r['label'] for r in rows])
    ax.tick_params(axis='x', labelsize=8.5, pad=5)
    ax.tick_params(axis='y', labelsize=8)
    ax.set_ylabel('Rules with errors', fontsize=8.5, labelpad=5)
    ax.grid(axis='y', color='#D9D9D9', lw=.6); ax.set_axisbelow(True)
    fig.legend(handles=[Rectangle((0, 0), 1, 1, facecolor=c, edgecolor='black', hatch=hatch, label=label)
                        for _, c, hatch, _, label in series],
               loc='upper left', bbox_to_anchor=(.035, .833),
               fontsize=7.8, handlelength=1.15, handletextpad=.55,
               labelspacing=.6, borderaxespad=0)
    return fig


def draw_ablations(stress, oracle_rows, risk, reuse):
    fig = plt.figure(figsize=(7.15, 4.42))
    header = lambda x, y, title, sub: (
        fig.text(x, y, title, weight='bold', fontsize=10),
        fig.text(x, y-.040, sub, color=MUTED, fontsize=8.1))
    header(.005, .976, '(a)  A safe choice can hide unsafe rules',
           'Frozen-artifact replay · n = 1,296 · no new calls')
    header(.525, .976, '(b)  Permission and value are separate',
           'Reference component interventions · n = 16')
    header(.005, .486, '(c)  Error consequences change the trade-off',
           'All DeepSeek primary trials · n = 400 per route')
    header(.525, .486, '(d)  Stable rules amortize language work',
           'Two families × eight catalogues · cold cost included')
    # A: distinguish a permitted domain from the actually selected witness.
    a = fig.add_axes([.207, .667, .262, .200])
    agg = stress['aggregate']
    values = [sum(g[k] for g in agg) for k in
              ['grid_unsafe_domain', 'grid_unsafe_selection', 'single_unsafe_selection']]
    assert values == [23, 0, 8]
    a.barh([2, 1, 0], values, height=.48, color=[BLUE, TEAL, RED])
    for y, v, c in zip([2, 1, 0], values, [BLUE, TEAL, RED]):
        a.text(v+.7, y, str(v), va='center', color=c, weight='bold', fontsize=10)
    a.set(xlim=(0, 28), ylim=(-.6, 2.6), xticks=[0, 10, 20], xlabel='Affected artifacts')
    a.set_yticks([2, 1, 0], ['Unsafe domain', 'Unsafe choice:\nmixed catalogue',
                            'Unsafe choice:\nunsafe-only'])
    a.tick_params(axis='y', labelsize=8.4)
    a.grid(axis='x', color=LINE, lw=.6); a.set_axisbelow(True)
    invalid = sum(g['single_invalid'] for g in agg)
    assert invalid == sum(g['grid_invalid'] for g in agg) == 13
    fig.text(.005, .553, 'All routes retained; 13 invalid executions per replay condition.',
             fontsize=7.9, color=MUTED)
    # B: four interventions, and three non-interchangeable correctness targets.
    b = fig.add_axes([.715, .637, .274, .221])
    b.set(xlim=(-.5, 2.5), ylim=(-.5, 3.5)); b.axis('off')
    oracle = {r['variant']: r for r in oracle_rows}
    variants = ['original', 'oracle_utility_only', 'oracle_admissibility_only', 'oracle_both']
    for y, key, label in zip([3, 2, 1, 0], variants,
                             ['Original', 'Ref. utility', 'Ref. permission', 'Both']):
        b.text(-.70, y, label, ha='right', va='center', fontsize=8.5)
        for x, metric in enumerate(['overpermissive', 'unsafe', 'exact']):
            v = int(oracle[key][metric]); good = metric == 'exact'
            b.add_patch(Rectangle((x-.47, y-.45), .94, .9,
                        facecolor=('#E4F2EE' if good else '#F7E8E4') if v else '#F3F5F7',
                        edgecolor='none'))
            b.text(x, y, str(v), ha='center', va='center', fontsize=10,
                   weight='bold' if v else 'normal', color=(TEAL if good else RED) if v else MUTED)
    for x, label in enumerate(['Unsafe\ndomain', 'Unsafe\nchoice', 'Exact\ndecision']):
        b.text(x, 3.72, label, ha='center', va='bottom', fontsize=8.0)
    fig.text(.525, .553, 'Selected faulty outputs; these are diagnostic oracle changes.',
             fontsize=7.9, color=MUTED)
    # C: the full observed preference trade-off, including its reversal at lambda=1.
    c = fig.add_axes([.075, .117, .385, .264])
    xs = np.linspace(1, 5, 201)
    for arm, color, label in [('python_fresh', BLUE, 'Python'), ('set', TEAL, 'Set')]:
        rr = risk[arm]
        ys = (rr['unsafe'] * xs + rr['other_failures']) / 400
        c.plot(xs, ys, color=color, lw=2, label=label)
        c.scatter([1, 5], [ys[0], ys[-1]], s=16, color=color, zorder=3)
    c.axvline(5/3, color=MUTED, lw=.8, ls=(0, (3, 3)))
    c.text(1.80, .226, r'$\lambda = 5/3$', color=MUTED, fontsize=8.5)
    c.set(xlim=(.9, 5.1), ylim=(0, .26), xticks=[1, 2, 3, 4, 5],
          yticks=[0, .1, .2], xlabel=r'Unsafe-error cost $\lambda$ (other error = 1)',
          ylabel='Empirical weighted loss')
    c.grid(axis='y', color=LINE, lw=.6); c.legend(loc='lower right', fontsize=8.3)
    fig.text(.005, .010, 'Exploratory cost sensitivity; no estimated deployment loss.',
             fontsize=7.9, color=MUTED)
    # D: normalize only within a profile, retain all executable caching controls.
    d = fig.add_axes([.690, .117, .294, .264])
    arms = ['direct', 'python_fresh', 'python_cached', 'flat_a', 'set']
    labels = ['Direct', 'Python / new', 'Python / cached', 'Merged / cached', 'Set / cached']
    records = {(r['profile'], r['method']): r for r in reuse}
    for profile, off, color, label in [('ds_flash_low', .18, BLUE, 'DS low'),
                                      ('gpt6_max', -.18, TEAL, 'Astra max')]:
        base = records[profile, 'direct']
        base_tokens = base['input_tokens'] + base['output_tokens']
        for y, arm in zip(range(4, -1, -1), arms):
            r = records[profile, arm]
            value = 100 * (r['input_tokens'] + r['output_tokens']) / base_tokens
            d.barh(y+off, value, height=.30, color=color,
                   label=label if arm == 'direct' else None)
            d.text(value+2.4, y+off, f'{value:.0f}', va='center', fontsize=7.7, color=color)
    d.set(xlim=(0, 140), ylim=(-.65, 4.7), xticks=[0, 50, 100],
          xlabel='Tokens (% of direct, within model)')
    d.set_yticks(range(4, -1, -1), labels); d.tick_params(axis='y', labelsize=8.3)
    d.grid(axis='x', color=LINE, lw=.6); d.set_axisbelow(True)
    d.legend(loc='lower left', bbox_to_anchor=(-.04, .99), ncol=2,
             fontsize=7.9, columnspacing=1.0, handlelength=1.2)
    fig.text(.525, .010, 'New calls: 16 per route; cached calls: 2 per route.',
             fontsize=7.9, color=MUTED)
    # Subtle separators, no boxes or decorative gradients around the data.
    fig.add_artist(plt.Line2D([.50, .50], [.01, .98], transform=fig.transFigure,
                              color=LINE, lw=.7))
    fig.add_artist(plt.Line2D([.005, .99], [.527, .527], transform=fig.transFigure,
                              color=LINE, lw=.7))
    return fig


def draw_witnesses():
    """Numerical values are checked against the saved primary ledger witnesses."""
    assert sum([34800, 13300, 25400, 7500, 124433]) == 205433
    assert 41300 + 21000 + 137699 == 199999
    fig, ax = plt.subplots(figsize=(7.15, 4.3))
    fig.subplots_adjust(left=.01, right=.99, bottom=.02, top=.99)
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis('off')
    ax.text(.00, .976, 'Two Astra max boundary errors, traced from request to exact check',
            fontsize=10.5, weight='bold')
    ax.text(.00, .929, 'Observed primary cases; monetary amounts are in MU. No additional trials.',
            fontsize=8.6, color=MUTED)
    columns = [.00, .35, .68]
    for x, title in zip(columns, ['01  Required behavior', '02  Direct final output', '03  Reference verification']):
        ax.text(x, .851, title, weight='bold', fontsize=9.4)
    ax.plot([0, 1], [.825, .825], color=LINE, lw=.8)
    def txt(x, y, s, color=INK, size=9.0, weight='normal'):
        ax.text(x, y, s, va='top', fontsize=size, linespacing=1.40, color=color, weight=weight)
    txt(.00, .783, '(a)  Threshold-dependent returns', weight='bold')
    txt(.00, .724, 'At most four of six items return.\nEvery event must cost ≤ 2,000 MU.\nBoth retained-value and retained-\nweight thresholds trigger clawbacks.')
    txt(.35, .783, 'ACCEPT', RED, 10.5, 'bold')
    txt(.35, .713, 'Worst loss reported: 1,954.33\nSelected offer: bbb115a088d0\nReported margin: 45.67 below cap.')
    txt(.68, .783, 'Witness event: {0, 3, 4, 5}', weight='bold')
    txt(.68, .723, '348 + 133 + 254 + 75\n+ 1,244.33 = 2,054.33 MU\nRestocking, freight, two clawbacks,\nand one administrative charge.', size=8.8)
    txt(.68, .531, '54.33 ABOVE CAP → REFUSE', RED, 9.1, 'bold')
    ax.plot([0, 1], [.467, .467], color=LINE, lw=.8)
    txt(.00, .426, '(b)  Capped coupon cancellation', weight='bold')
    txt(.00, .368, 'Same 2,000 MU loss cap.\n1,024 offers; at most four cancels.\nGroup clawbacks are capped.\nA conditional order charge may apply.')
    txt(.35, .426, 'REFUSE', RED, 10.5, 'bold')
    txt(.35, .356, 'No candidate accepted.\nThe decision overlooks the feasible\noffer 7f5a456392d5.')
    txt(.68, .426, 'Maximizing event: {0, 2, 3, 5}', weight='bold')
    txt(.68, .366, '413 + 210 + 1,376.99\n= 1,999.99 MU\nGroup charge < 218 cap;\nno additional order clawback.', size=8.8)
    txt(.68, .174, '0.01 BELOW CAP → ACCEPT', TEAL, 9.1, 'bold')
    for y in [.662, .305]:
        for a, b in [(.303, .334), (.632, .665)]:
            ax.add_patch(FancyArrowPatch((a, y), (b, y), arrowstyle='-|>',
                         mutation_scale=10, color=MUTED, linewidth=.9))
    ax.plot([0, 1], [.113, .113], color=LINE, lw=.8)
    txt(.00, .080, 'Independent finite checks: all 57 allowed events and every catalogue candidate.\nSet returns the correct decision in both cases. Full terms, arithmetic, and utility are in the appendix text.',
        MUTED, 8.8)
    return fig
