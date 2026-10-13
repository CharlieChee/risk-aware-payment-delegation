"""Rebuild Figure 3 and appendix tables from the closed availability cohort."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/supplements/availability_20261013'
TABLES=ROOT/('tables' if (ROOT/'paper.tex').exists() else 'tex/tables')
PROFILES=['deepseek_low','glm_low','qwen_low']
LABELS={'deepseek_low':'DeepSeek','glm_low':'GLM','qwen_low':'Qwen'}

def read(name):return json.loads((DATA/name).read_text())
def pct(n,d):return f'{100*n/d:.2f}' if d else '--'

def build():
    s=read('summary.json');rows=read('rows.json');w=read('witnesses.json')
    assert len(rows)==2400 and s['total']['certified']==2373
    main=[r for r in w if r['main_exposure']]
    total=s['total'];e=total['endpoints'];cover=total['event_coverage']['rank_le8_safe_to_unsafe_strict_backup']
    assert len(main)==e['rank_le8_safe_to_unsafe_strict_backup']==48
    assert len({r['case_id'] for r in main})==48
    assert all(r['strict_backups'] and r['minimum_deletions']<=8 for r in main)
    stats={'AvailSafeDS':s['by_model']['deepseek_low']['endpoints']['original_safe'],
        'AvailSafeGLM':s['by_model']['glm_low']['endpoints']['original_safe'],
        'AvailSafeQwen':s['by_model']['qwen_low']['endpoints']['original_safe'],
        'AvailHiddenPct':pct(e['latent_safe'],e['original_safe']),
        'AvailExposedPct':pct(len(main),e['original_safe']),
        'AvailExposedRequests':cover['requests'],'AvailExposedTemplates':len(cover['templates']),
        'AvailBackupMin':min(x['strict_backups'] for x in main),
        'AvailBackupMax':max(x['strict_backups'] for x in main),
        'AvailExactExposed':sum(x['original_exact'] for x in main)}
    (TABLES/'availability_stats.tex').write_text('% Generated from the closed availability cohort.\n'+''.join('\\newcommand{\\'+k+'}{'+str(v)+'}\n' for k,v in stats.items()))
    lines=[r'\begin{tabular}{@{}lrrrrrr@{}}',r'\toprule',
        r'Model & Evaluable & Safe $n$ & Hidden (\%) & Exposed (\%) & Requests & Templates\\',r'\midrule']
    for p in PROFILES:
        c=s['by_model'][p];q=c['endpoints'];cov=c['event_coverage']['rank_le8_safe_to_unsafe_strict_backup']
        lines.append(f"{LABELS[p]} & {c['certified']} & {q['original_safe']} & {pct(q['latent_safe'],q['original_safe'])} & {pct(q['rank_le8_safe_to_unsafe_strict_backup'],q['original_safe'])} & {cov['requests']} & {len(cov['templates'])}"+r'\\')
    lines += [r'\midrule',f"All & {total['certified']} & {e['original_safe']} & {stats['AvailHiddenPct']} & {stats['AvailExposedPct']} & {cover['requests']} & {len(cover['templates'])}"+r'\\',r'\bottomrule',r'\end{tabular}']
    (TABLES/'availability_models.tex').write_text('\n'.join(lines)+'\n')
    lines=[r'\begin{tabular}{@{}lrrrr@{}}',r'\toprule',r'Template & Safe $n$ & Hidden (\%) & Exposed (\%) & Requests\\',r'\midrule']
    for t,c in s['by_template'].items():
        q=c['endpoints'];cov=c['event_coverage']['rank_le8_safe_to_unsafe_strict_backup']
        lines.append(f"{t} & {q['original_safe']} & {pct(q['latent_safe'],q['original_safe'])} & {pct(q['rank_le8_safe_to_unsafe_strict_backup'],q['original_safe'])} & {cov['requests']}"+r'\\')
        if t in ['a5','b5','c5']:lines.append(r'\midrule')
    lines += [r'\bottomrule',r'\end{tabular}']
    (TABLES/'availability_templates.tex').write_text('\n'.join(lines)+'\n')
    lines=[r'\begin{tabular}{@{}lrrrr@{}}',r'\toprule',r'Budget $k$ & 1 & 4 & 8 & 16\\',r'\midrule']
    specs=[('Directed safe to unsafe','rank','safe_to_unsafe_strict_backup',e['original_safe']),
           ('Directed unsafe to safe','rank','unsafe_to_safe',e['original_unsafe']),
           ('Random safe to unsafe','random','safe_to_unsafe_strict_backup_mean_within_specification_rate',None),
           ('Random unsafe to safe','random','unsafe_to_safe_mean_within_specification_rate',None)]
    for label,kind,field,d in specs:
        vals=[pct(total['rank_cumulative'][str(k)][field],d) if kind=='rank' else f"{100*total['random'][str(k)][field]:.3f}" for k in [1,4,8,16]]
        lines.append(label+' & '+' & '.join(vals)+r'\\')
    lines += [r'\bottomrule',r'\end{tabular}']
    (TABLES/'availability_controls.tex').write_text('\n'.join(lines)+'\n')
    values={'cohort':'first fully evaluable completion cohort, closed 2026-10-13',
        'source':'data/supplements/availability_20261013/summary.json',
        'metric':'cumulative directed exposure with strict authorized backup',
        'planned':2400,'auditable':2373,'failed':27,'budgets':[1,4,8,16],
        'unit':'one retained specification per request and model; replay conditions are dependent',
        'profiles':[],'stats':stats}
    colors=['#244D6A','#A05D32','#739387'];markers=['o','s','^'];styles=['-','--',':']
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':8.5,'axes.labelsize':8.5,
                         'axes.labelweight':'bold','font.weight':'bold','pdf.fonttype':42,
                         'text.color':'black','axes.labelcolor':'black',
                         'xtick.color':'black','ytick.color':'black',
                         'axes.spines.top':True,'axes.spines.right':True,
                         'axes.spines.bottom':True,'axes.spines.left':True}):
        fig,ax=plt.subplots(figsize=(3.42,2.34));fig.subplots_adjust(left=.18,right=.965,bottom=.23,top=.72)
        for p,color,marker,ls in zip(PROFILES,colors,markers,styles):
            c=s['by_model'][p];n=c['endpoints']['original_safe']
            y=[100*c['rank_cumulative'][str(k)]['safe_to_unsafe_strict_backup']/n for k in [1,4,8,16]]
            ax.plot([1,4,8,16],y,color=color,marker=marker,linestyle=ls,lw=1.8,ms=5,label=f'{LABELS[p]} (n={n})')
            values['profiles'].append(dict(profile=p,label=LABELS[p],denominator=n,percentages=y,
                counts=[c['rank_cumulative'][str(k)]['safe_to_unsafe_strict_backup'] for k in [1,4,8,16]]))
        ax.set(xlim=(.4,16.6),ylim=(0,7),xticks=[1,4,8,16],yticks=[0,2,4,6],
               xlabel='Removal budget k (offers)',ylabel='Initially safe purchases\nexposed (%)')
        ax.grid(axis='y',color='#D9D9D9',lw=.6);ax.set_axisbelow(True)
        for spine in ax.spines.values():spine.set_color('black');spine.set_linewidth(1.1)
        ax.tick_params(width=1.1,length=3,colors='black')
        legend=ax.legend(loc='lower left',bbox_to_anchor=(-.05,1.02),fontsize=8.1,frameon=True,
                         borderpad=.4,labelspacing=.3,handlelength=2.6)
        legend.get_frame().set_edgecolor('black');legend.get_frame().set_facecolor('white');legend.get_frame().set_alpha(1)
        for ext in ['pdf','png']:
            fig.savefig(ROOT/'figures'/f'13_authorization_diagnostics.{ext}',dpi=400,bbox_inches='tight',pad_inches=.04)
        plt.close(fig)
    (ROOT/'figures/13_authorization_diagnostics_values.json').write_text(json.dumps(values,indent=2)+'\n')
    print(json.dumps(stats))

if __name__=='__main__':build()
