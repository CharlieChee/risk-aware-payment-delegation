"""Main evaluation figures with explicit cohorts and readable denominators."""
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from primary_profiles import display_primary
from reported_results import display_language

INK='#1F2937'; MUTED='#5E6C7B'; LINE='#DCE2E7'
DIRECT='#53677F'; SET='#007F82'; RED='#B34438'


def read(root,path):
    return json.loads((Path(root)/path).read_text())


def draw_intent(root):
    """Percentage view of complete paired API cohorts; broader volume stays separate."""
    root=Path(root)
    folder='data/supplements/intent_ambiguity_20261011/'
    summary=read(root,folder+'parameter_summary.json')
    rows=read(root,folder+'parameter_rows.json')
    api=[r for r in rows if r['profile']!='gpt6_max']
    assert len(api)==544 and len({r['task_id'] for r in api})==544
    assert len({r['case_id'] for r in api})==42
    profiles=['ds_flash_low','ds_flash_max','glm53_low','qwen_max_low']
    labels=['DeepSeek low','DeepSeek max','GLM low','Qwen Max low']
    display={r['profile']:r for r in summary['displayed']}
    values={'source':folder+'parameter_rows.json', 'metric':'exact_decision_rate',
        'all_recorded_trials':len(rows), 'api_recorded_trials':len(api),
        'api_task_variants':42, 'plotted_trials':0, 'profiles':[],
        'selection':'Complete paired API cohorts from the historical intent study; other settings and all error categories remain in the appendix.',
        'api_task_ids':[r['task_id'] for r in api]}
    fig,ax=plt.subplots(figsize=(3.45,2.13))
    fig.subplots_adjust(left=.282,right=.983,bottom=.205,top=.805)
    for y,p,name in zip(range(3,-1,-1),profiles,labels):
        row=display[p];d,s=row['rule_direct'],row['set_mechanism']
        assert d['n']==s['n'] and set(d['case_ids'])==set(s['case_ids'])
        recorded=[r for r in api if r['profile']==p and r['partition'] in row['partitions']
                  and r['method'] in ('rule_direct','set_mechanism')]
        assert len(recorded)==d['n']+s['n']
        for method,counts in [('rule_direct',d),('set_mechanism',s)]:
            rr=[r for r in recorded if r['method']==method]
            assert len(rr)==counts['n'] and sum(r['exact'] for r in rr)==counts['exact']
        for offset,a,color in [(+.17,'rule_direct',DIRECT),(-.17,'set_mechanism',SET)]:
            count=row[a];pct=100*count['exact']/count['n']
            ax.barh(y+offset,pct,height=.255,color=color,zorder=3)
            ax.text(pct+1.7,y+offset,f'{pct:.1f}%' if pct!=100 else '100%',
                va='center',ha='left',fontsize=7.6,color=color,
                weight='bold' if a=='set_mechanism' else 'normal')
        values['plotted_trials']+=len(recorded)
        values['profiles'].append(dict(profile=p,label=name,n_per_method=d['n'],
            direct_exact=d['exact'],set_exact=s['exact'],
            direct_percent=100*d['exact']/d['n'],set_percent=100*s['exact']/s['n'],
            partitions=row['partitions'],task_ids=[r['task_id'] for r in recorded]))
    assert values['plotted_trials']==294
    ax.set(xlim=(0,124),ylim=(-.55,3.55),xticks=[0,25,50,75,100])
    ax.set_yticks(range(3,-1,-1),labels);ax.tick_params(labelsize=7.7)
    ax.set_xlabel('Exact decisions (%)',fontsize=8,labelpad=4)
    ax.grid(axis='x',color=LINE,lw=.6);ax.set_axisbelow(True)
    fig.legend(handles=[Rectangle((0,0),1,1,facecolor=DIRECT,label='Direct'),
                        Rectangle((0,0),1,1,facecolor=SET,label='Set')],
               loc='upper left',bbox_to_anchor=(.278,.97),ncol=2,
               fontsize=8,handlelength=1.1,handletextpad=.5,columnspacing=1.7,borderaxespad=0)
    fig.text(.282,.016,'Complete paired cohorts · 294 evaluations',fontsize=7,color=MUTED)
    (root/'figures/16_retained_intent_values.json').write_text(json.dumps(values,indent=2)+'\n')
    return fig


def draw_completion(root):
    """Grouped bars: model accuracy, classified outcomes, and contract families.

    Aggregation is over explicitly labelled task/configuration outcomes. Missing
    joint counts are never inferred from accuracy-only updates. Per-template and
    per-configuration counts remain in the machine-readable figure data.
    """
    root=Path(root)
    primary=display_primary(root)
    by,profiles=primary['by'],primary['profiles']
    reported=set(primary['author_reported_profiles'])
    reviewed=set(primary['author_reviewed_profiles'])
    partials={p['profile']:p['n'] for p in primary['partials']}
    full=[p for p in profiles if p not in partials]
    pooled=read(root,'data/supplements/evaluation_redesign_20261010/verified_claims.json')['pooled_deepseek']
    tb={(r['profile'],r['arm'],r['template']):r
        for r in read(root,'data/derived/template_summary.json')}
    templates=[f'{family}{i}' for family in 'abcd' for i in range(1,6)]
    joint=[p for p in full if all(by[p,a].get(k) is not None
           for a in ('direct','set') for k in ('correct_accept','expected_accept','unsafe'))]
    values={'primary':[], 'joint':[], 'templates':[],
        'joint_inclusion':'All 200-task configurations with reported safe completion and unsafe acceptance. No imputation.',
        'complete_configurations':len(full),'partial_configurations':len(partials),
        'template_cohort':'Original DeepSeek low/high, all 20 templates, 10 tasks per template and method.',
        'primary_sources':primary['sources'],
        'template_source':'data/derived/template_summary.json',
        'pooled_deepseek':pooled}
    for i,p in enumerate(profiles,1):
        n=by[p,'direct']['n']
        assert n==by[p,'set']['n'] and (n==200 or partials.get(p)==n)
        values['primary'].append(dict(id=i,profile=p,author_reported=p in reported,
            author_reviewed=p in reviewed,partial=p in partials,n=n,
            direct_exact=by[p,'direct']['exact'],set_exact=by[p,'set']['exact']))
        if p in joint:
            assert by[p,'direct']['expected_accept']==by[p,'set']['expected_accept']==100
            values['joint'].append(dict(id=i,profile=p,n=200,feasible_n=100,
                direct=dict(unsafe=by[p,'direct']['unsafe'],correct_accept=by[p,'direct']['correct_accept']),
                set=dict(unsafe=by[p,'set']['unsafe'],correct_accept=by[p,'set']['correct_accept'])))
    for t in templates:
        for p in ('ds_flash_low','ds_flash_high'):
            d,s=[tb[p,arm,t] for arm in ('direct','set')]
            assert d['n']==s['n']==10
            values['templates'].append(dict(profile=p,template=t,n=10,
                direct=d['exact'],set=s['exact'],gain=s['exact']-d['exact']))
    joint_pooled={'profiles':joint,'n_per_method':sum(r['n'] for r in values['joint']),
                  'feasible_per_method':sum(r['feasible_n'] for r in values['joint'])}
    for arm in ('direct','set'):
        joint_pooled[arm]={metric:sum(r[arm][metric] for r in values['joint'])
                           for metric in ('unsafe','correct_accept')}
    values['joint_pooled']=joint_pooled
    family_pooled=[]
    for code,label in [('a','Coupon'),('b','Insurance'),('c','Returns'),('d','Service')]:
        rs=[r for r in values['templates'] if r['template'].startswith(code)]
        row=dict(family=code,label=label,n_per_method=sum(r['n'] for r in rs),
                 direct_exact=sum(r['direct'] for r in rs),set_exact=sum(r['set'] for r in rs))
        assert row['n_per_method']==100
        family_pooled.append(row)
    values['family_pooled']=family_pooled

    fig=plt.figure(figsize=(7.15,4.55))
    a=fig.add_axes([.075,.615,.910,.310])
    b=fig.add_axes([.075,.107,.370,.322])
    c=fig.add_axes([.575,.107,.410,.322])
    fig.text(.005,.973,'(a)  Exact decisions across model configurations',fontsize=9.4,weight='bold')
    fig.text(.005,.485,'(b)  Safety and useful completion',fontsize=9.0,weight='bold')
    fig.text(.505,.485,'(c)  Results across contract families',fontsize=9.0,weight='bold')
    fig.legend(handles=[Rectangle((0,0),1,1,facecolor=DIRECT,label='Direct'),
                        Rectangle((0,0),1,1,facecolor=SET,label='Set')],
               loc='upper right',bbox_to_anchor=(.987,1.001),ncol=2,
               fontsize=8.2,handlelength=1.2,handletextpad=.5,columnspacing=1.4,borderaxespad=0)
    def setup(ax,ylabel):
        ax.set(ylim=(0,112),yticks=[0,25,50,75,100])
        ax.set_ylabel(ylabel,fontsize=8.0,labelpad=5)
        ax.tick_params(axis='y',labelsize=7.5,pad=4)
        ax.tick_params(axis='x',labelsize=7.5,pad=6,length=0)
        ax.grid(axis='y',color='#DDE3E7',lw=.55)
        ax.set_axisbelow(True)
        for spine in ax.spines.values():spine.set_visible(False)
    def grouped(ax,direct,result,labels,width=.34,labelsize=7.6,integer_labels=()):
        centers=np.arange(len(labels))
        for delta,ys,color in [(-width/2,direct,DIRECT),(width/2,result,SET)]:
            bars=ax.bar(centers+delta,ys,width=width*.92,color=color,zorder=3)
            for j,(bar,val) in enumerate(zip(bars,ys)):
                text=(f'{val:.0f}' if j in integer_labels else
                      (f'{val:.1f}'.rstrip('0').rstrip('.') if val%1 else str(int(val))))
                ax.text(bar.get_x()+bar.get_width()/2,val+2.0,text,
                        ha='center',va='bottom',fontsize=labelsize,color=INK)
        ax.set_xticks(centers,labels)
        ax.set_xlim(-.62,len(labels)-.38)
    setup(a,'Exact decisions (%)')
    labels=['DS\nlow','DS\nhigh','Qwen\nFlash low','Qwen\nMax low',
            'GLM\nFlash low','GLM\nhigh','Luna\nmedium','Terra\nmedium',
            'Sol\nmedium','Astra\nmax','Opus 5.5\nmedium']
    assert len(labels)==len(profiles)
    grouped(a,[100*by[p,'direct']['exact']/by[p,'direct']['n'] for p in profiles],
              [100*by[p,'set']['exact']/by[p,'set']['n'] for p in profiles],labels,
              width=.35,labelsize=7.1,integer_labels=(len(profiles)-1,))
    setup(b,'Outcomes (%)')
    def joint_rates(arm):
        return [100*joint_pooled[arm]['unsafe']/joint_pooled['n_per_method'],
                100*joint_pooled[arm]['correct_accept']/joint_pooled['feasible_per_method']]
    grouped(b,joint_rates('direct'),joint_rates('set'),
              ['Unsafe acceptance ↓','Safe completion ↑'],width=.32,labelsize=8.2)
    setup(c,'Exact decisions (%)')
    grouped(c,[100*r['direct_exact']/r['n_per_method'] for r in family_pooled],
              [100*r['set_exact']/r['n_per_method'] for r in family_pooled],
              [r['label'] for r in family_pooled],width=.34,labelsize=7.8)
    joint_label=(f"{len(joint)} configurations\n{joint_pooled['n_per_method']:,} outcomes; "
                 f"{joint_pooled['feasible_per_method']:,} feasible per method")
    fig.text(.260,.009,joint_label,
             ha='center',fontsize=6.8,color=MUTED,linespacing=1.35)
    fig.text(.780,.009,'DeepSeek low/high\n100 outcomes per family and method',
             ha='center',fontsize=6.8,color=MUTED,linespacing=1.35)
    values['visualization']={
        'design':'Conventional grouped bars: model accuracy, pooled classified outcomes, contract-family accuracy',
        'joint_display':f'Unsafe acceptance and safe completion pooled over {len(joint)} fully classified configurations',
        'joint_denominators':{'unsafe_acceptance':joint_pooled['n_per_method'],
                              'safe_completion':joint_pooled['feasible_per_method']},
        'rate_axis_ticks':[0,25,50,75,100],
        'jitter':False,'imputation':False,'bar_value_labels':True,
        'reported_percentage_decimal_places':1,
        'value_label_decimal_overrides':{'opus55_medium':0},
        'sample_sizes_in_caption_and_appendix':False,
        'sample_size_locations':['Appendix B', 'Appendix C'],
        'family_denominator':100,'all_template_counts_retained':True,
        'publication_workflow_annotations':False,
        'all_preexisting_data_preserved':True,'new_model_calls':0}
    (root/'figures/14_safe_completion_values.json').write_text(json.dumps(values,indent=2)+'\n')
    return fig


def draw_robustness(root):
    """Absolute rates: three GPT-5.6 effort facets and DeepSeek language bars.

    Settings are requested categorical levels, not measured compute. Missing or
    incomplete settings are represented by NaN so no point or connecting segment
    is synthesized. The language panel retains its own reported denominators.
    """
    root=Path(root)
    grid=read(root,'data/derived/grid_summary.json')
    gb={(r['profile'],r['arm']):r for r in grid if r['group']=='all'}
    lb=display_language(root)
    efforts=['none','low','medium','high','xhigh','max','ultra']
    settings=['Off','L','M','H','XH','Max','U']
    families=[('gpt56_sol','Sol'),('gpt56_terra','Terra'),('gpt56_luna','Luna')]
    values=dict(metric='Exact decisions (%)',y_axis_limits=[0,100],
        effort_source='data/derived/grid_summary.json',
        language_sources=['data/derived/language_all_methods_matched.json'],
        effort_order=efforts,setting_labels=settings,effort=[],language=[],
        interpolation='None; straight segments only between adjacent complete requested settings',
        point_or_bar_value_labels=False,cohorts_pooled=False,new_model_calls=0)
    values['family_setting_order']={}
    fig=plt.figure(figsize=(7.15,3.05))
    fig.text(.01,.967,'(a)  Sensitivity to reasoning settings',fontsize=9.2,weight='bold')
    fig.text(.684,.967,'(b)  Task language',fontsize=9.2,weight='bold')
    styles=[('direct',DIRECT,'o','--'),('set',SET,'s','-')]
    fig.legend(handles=[Line2D([0],[0],color=color,marker=marker,ls=ls,
                    markersize=4,lw=1.4,markerfacecolor='white' if arm=='direct' else color,
                    label='Direct' if arm=='direct' else 'Set') for arm,color,marker,ls in styles],
               loc='upper center',bbox_to_anchor=(.51,.938),ncol=2,
               fontsize=8.2,handlelength=2.4,columnspacing=2.3,borderaxespad=0)
    positions=[(.058,.250,.177,.555),(.255,.250,.177,.555),
               (.452,.250,.177,.555)]
    changes=[]
    for (prefix,label),pos in zip(families,positions):
        ax=fig.add_axes(pos)
        series={arm:[] for arm,_,_,_ in styles}
        available_efforts=[effort for effort in efforts if all(
            gb.get((prefix+'_'+effort,arm),{}).get('profile_complete',False)
            and gb.get((prefix+'_'+effort,arm),{}).get('n')==60
            for arm,_,_,_ in styles)]
        values['family_setting_order'][prefix]=available_efforts
        for effort in available_efforts:
            profile=prefix+'_'+effort
            available={arm:gb.get((profile,arm)) for arm,_,_,_ in styles}
            complete=all(row and row['profile_complete'] and row['n']==60
                         for row in available.values())
            entry=dict(family=prefix,label=label,profile=profile,setting=effort,
                       plotted=complete,status='complete' if complete else
                       ('incomplete' if any(available.values()) else 'missing'))
            for arm,_,_,_ in styles:
                row=available[arm]
                entry[arm]=dict(n=row['n'],exact=row['exact'],
                    percent=100*row['exact']/row['n'] if complete else None) if row else None
                series[arm].append(entry[arm]['percent'] if complete else np.nan)
            values['effort'].append(entry)
            if complete:changes.append(available['set']['exact']-available['direct']['exact'])
        for arm,color,marker,ls in styles:
            ax.plot(range(len(available_efforts)),series[arm],color=color,marker=marker,ls=ls,
                    lw=1.35,ms=3.2,mew=.8,mfc='white' if arm=='direct' else color,
                    clip_on=False,zorder=3 if arm=='direct' else 4)
        ax.set(xlim=(-.30,len(available_efforts)-.70),ylim=(0,100),yticks=[0,50,100])
        ax.set_xticks(range(len(available_efforts)),[settings[efforts.index(e)] for e in available_efforts])
        ax.tick_params(axis='x',labelsize=6.7,pad=4)
        ax.tick_params(axis='y',labelsize=7.1,pad=3)
        if prefix!='gpt56_sol':ax.tick_params(axis='y',labelleft=False)
        ax.set_title(label,loc='left',fontsize=8.7,weight='bold',pad=7)
        ax.grid(axis='y',color=LINE,lw=.6);ax.set_axisbelow(True)
    assert len(changes)==19 and sum(d>0 for d in changes)==18 and sum(d<0 for d in changes)==1
    values['complete_effort_configurations']=len(changes)
    fig.text(.008,.530,'Exact decisions (%)',rotation=90,va='center',ha='center',fontsize=8.2)
    fig.text(.343,.133,'Requested reasoning setting',ha='center',fontsize=8.2)
    # Two language subgroups per configuration; within each, Direct and Set.
    ax=fig.add_axes([.721,.250,.274,.555])
    ps=['ds_flash_low','ds_flash_high','ds_flash_max']
    names=['DS\nlow','DS\nhigh','DS\nmax']
    centers=np.arange(3)*1.5
    ticks=[];ticklabels=[]
    for i,(p,name,center) in enumerate(zip(ps,names,centers)):
        if i%2==0:ax.axvspan(center-.69,center+.69,color='#F3F6F8',zorder=0)
        for language,offset in [('zh',-.30),('en',.30)]:
            ticks.append(center+offset);ticklabels.append(language.upper())
            for arm,shift,color in [('direct',-.105,DIRECT),('set',.105,SET)]:
                row=lb[p,arm,language];pct=100*row['exact']/row['n']
                assert row['n']==60
                ax.bar(center+offset+shift,pct,width=.185,color=color,
                       edgecolor='white',linewidth=.3,zorder=3)
                values['language'].append(dict(profile=p,arm=arm,language=language,
                    n=row['n'],exact=row['exact'],percent=pct,
                    author_reported=bool(row.get('author_reported',False))))
        ax.text(center,-.15,name,transform=ax.get_xaxis_transform(),ha='center',
                va='top',fontsize=7.6,linespacing=1.15)
    ax.set(xlim=(-.75,3.75),ylim=(0,100),yticks=[0,25,50,75,100])
    ax.set_xticks(ticks,ticklabels)
    ax.tick_params(axis='x',labelsize=7.0,pad=4)
    ax.tick_params(axis='y',labelsize=7.1,pad=3)
    ax.set_ylabel('Exact decisions (%)',fontsize=8.2,labelpad=5)
    ax.grid(axis='y',color=LINE,lw=.6);ax.set_axisbelow(True)
    fig.text(.01,.057,'Effort: 60 tasks per setting; 19 complete settings. Requested settings are not measured compute.',
             fontsize=7.0,color=MUTED)
    fig.text(.01,.014,'Language: 60 tasks per language and method. Exact counts and the complete configuration controls are in the appendix.',
             fontsize=7.0,color=MUTED)
    (root/'figures/15_configuration_robustness_values.json').write_text(json.dumps(values,indent=2)+'\n')
    return fig
