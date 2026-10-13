"""Main evaluation figures with explicit cohorts and readable denominators."""
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from primary_profiles import display_primary
from reported_results import display_language

INK='#000000'; MUTED='#595959'; LINE='#D9D9D9'
# Muted sand and slate blue retain a clear lightness difference in print.
DIRECT='#D8B78E'; SET='#5B7F99'
METHOD_LINE={'direct':'#956C3E', 'set':'#315E7D'}
LANGUAGE_COLOR={'zh':'#70998E', 'en':'#E0CAA8'}
METHOD_HATCH={'direct':'', 'set':'///'}


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
    fig,ax=plt.subplots(figsize=(3.45,2.42))
    fig.subplots_adjust(left=.345,right=.972,bottom=.290,top=.800)
    for y,p,name in zip(range(3,-1,-1),profiles,labels):
        row=display[p];d,s=row['rule_direct'],row['set_mechanism']
        assert d['n']==s['n'] and set(d['case_ids'])==set(s['case_ids'])
        recorded=[r for r in api if r['profile']==p and r['partition'] in row['partitions']
                  and r['method'] in ('rule_direct','set_mechanism')]
        assert len(recorded)==d['n']+s['n']
        for method,counts in [('rule_direct',d),('set_mechanism',s)]:
            rr=[r for r in recorded if r['method']==method]
            assert len(rr)==counts['n'] and sum(r['exact'] for r in rr)==counts['exact']
        for offset,a,color,hatch in [(+.235,'rule_direct',DIRECT,''),(-.235,'set_mechanism',SET,'///')]:
            count=row[a];pct=100*count['exact']/count['n']
            ax.barh(y+offset,pct,height=.32,color=color,edgecolor='black',hatch=hatch,zorder=3)
            ax.text(pct+1.7,y+offset,f'{pct:.1f}%' if pct!=100 else '100%',
                va='center',ha='left',fontsize=7.6,color=color,
                weight='bold' if a=='set_mechanism' else 'normal')
        values['plotted_trials']+=len(recorded)
        values['profiles'].append(dict(profile=p,label=name,n_per_method=d['n'],
            direct_exact=d['exact'],set_exact=s['exact'],
            direct_percent=100*d['exact']/d['n'],set_percent=100*s['exact']/s['n'],
            partitions=row['partitions'],task_ids=[r['task_id'] for r in recorded]))
    assert values['plotted_trials']==294
    ax.set(xlim=(0,136),ylim=(-.6,3.6),xticks=[0,25,50,75,100])
    ax.set_yticks(range(3,-1,-1),labels);ax.tick_params(labelsize=7.7)
    ax.set_xlabel('Exact decisions (%)',fontsize=8,labelpad=4)
    ax.grid(axis='x',color=LINE,lw=.6);ax.set_axisbelow(True)
    fig.legend(handles=[Rectangle((0,0),1,1,facecolor=DIRECT,edgecolor='black',label='Direct'),
                        Rectangle((0,0),1,1,facecolor=SET,edgecolor='black',hatch=METHOD_HATCH['set'],label='Set')],
               loc='upper center',bbox_to_anchor=(.54,.985),ncol=2,
               fontsize=8,handlelength=1.1,handletextpad=.5,columnspacing=1.7,borderaxespad=0)
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
    from certified_primary import pooled as final_pooled, summary_rows, REPLAY
    pooled=final_pooled(root)
    tb={(r['profile'],r['arm'],r['template']):r
        for r in summary_rows(root, 'template')}
    templates=[f'{family}{i}' for family in 'abcd' for i in range(1,6)]
    joint=[p for p in full if all(by[p,a].get(k) is not None
           for a in ('direct','set') for k in ('correct_accept','expected_accept','unsafe'))]
    values={'primary':[], 'joint':[], 'templates':[],
        'joint_inclusion':'All 200-task configurations with reported safe completion and unsafe acceptance. No imputation.',
        'complete_configurations':len(full),'partial_configurations':len(partials),
        'template_cohort':'DeepSeek low/high, all 20 templates, 10 tasks per template and method; Algorithm 1 decisions.',
        'primary_sources':primary['sources'],
        'template_source':REPLAY,
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

    fig=plt.figure(figsize=(7.15,4.85))
    a=fig.add_axes([.085,.635,.900,.285])
    b=fig.add_axes([.085,.170,.365,.255])
    c=fig.add_axes([.585,.170,.400,.255])
    fig.text(.005,.973,'(a)  Exact decisions across model configurations',fontsize=9.4,weight='bold')
    fig.text(.005,.478,'(b)  Safety and useful completion',fontsize=9.0,weight='bold')
    fig.text(.505,.478,'(c)  Results across contract families',fontsize=9.0,weight='bold')
    fig.legend(handles=[Rectangle((0,0),1,1,facecolor=DIRECT,edgecolor='black',label='Direct'),
                        Rectangle((0,0),1,1,facecolor=SET,edgecolor='black',hatch=METHOD_HATCH['set'],label='Set')],
               loc='upper right',bbox_to_anchor=(.987,1.001),ncol=2,
               fontsize=8.2,handlelength=1.2,handletextpad=.5,columnspacing=1.4,borderaxespad=0)
    def setup(ax,ylabel):
        ax.set(ylim=(0,112),yticks=[0,25,50,75,100])
        ax.set_ylabel(ylabel,fontsize=8.0,labelpad=5)
        ax.tick_params(axis='y',labelsize=7.5,pad=4)
        ax.tick_params(axis='x',labelsize=7.5,pad=6,length=0)
        ax.grid(axis='y',color=LINE,lw=.55)
        ax.set_axisbelow(True)
        for spine in ax.spines.values():spine.set_visible(False)
    bar_width_points=13.2
    bar_gap_points=4.8
    def grouped(ax,direct,result,labels,labelsize=7.6,integer_labels=()):
        centers=np.arange(len(labels))
        ax.set_xlim(-.62,len(labels)-.38)
        # Match the printed bar width, not the categorical data-coordinate width.
        # The three panels have different axis widths and category counts.
        axis_width_points=fig.get_figwidth()*ax.get_position().width*72
        data_units_per_point=(len(labels)+.24)/axis_width_points
        width=bar_width_points*data_units_per_point
        separation=(bar_width_points+bar_gap_points)*data_units_per_point
        for delta,ys,color,hatch in [(-separation/2,direct,DIRECT,''),(separation/2,result,SET,'///')]:
            bars=ax.bar(centers+delta,ys,width=width,color=color,edgecolor='black',hatch=hatch,zorder=3)
            for j,(bar,val) in enumerate(zip(bars,ys)):
                text=(f'{val:.0f}' if j in integer_labels else
                      (f'{val:.1f}'.rstrip('0').rstrip('.') if val%1 else str(int(val))))
                ax.text(bar.get_x()+bar.get_width()/2,val+2.0,text,
                        ha='center',va='bottom',
                        fontsize=labelsize,color=INK)
        ax.set_xticks(centers,labels)
    setup(a,'Exact decisions (%)')
    labels=['DS\nlow','DS\nhigh','Qwen\nFlash\nlow','Qwen\nMax\nlow',
            'GLM\nFlash\nlow','GLM\nhigh','Luna\nmedium','Terra\nmedium',
            'Sol\nmedium','Astra\nmax','Opus 5.5\nmedium']
    assert len(labels)==len(profiles)
    grouped(a,[100*by[p,'direct']['exact']/by[p,'direct']['n'] for p in profiles],
              [100*by[p,'set']['exact']/by[p,'set']['n'] for p in profiles],labels,
              labelsize=7.1,integer_labels=(len(profiles)-1,))
    setup(b,'Outcomes (%)')
    def joint_rates(arm):
        return [100*joint_pooled[arm]['unsafe']/joint_pooled['n_per_method'],
                100*joint_pooled[arm]['correct_accept']/joint_pooled['feasible_per_method']]
    grouped(b,joint_rates('direct'),joint_rates('set'),
              ['Unsafe\nacceptance ↓','Safe\ncompletion ↑'],labelsize=8.2)
    setup(c,'Exact decisions (%)')
    grouped(c,[100*r['direct_exact']/r['n_per_method'] for r in family_pooled],
              [100*r['set_exact']/r['n_per_method'] for r in family_pooled],
              [r['label'] for r in family_pooled],labelsize=7.8)
    printed_widths=[bar.get_width()/(ax.get_xlim()[1]-ax.get_xlim()[0])*
                    fig.get_figwidth()*ax.get_position().width*72
                    for ax in (a,b,c) for container in ax.containers
                    for bar in container.patches]
    assert np.allclose(printed_widths,bar_width_points,rtol=0,atol=1e-9)
    values['visualization']={
        'design':'Conventional grouped bars: model accuracy, pooled classified outcomes, contract-family accuracy',
        'joint_display':f'Unsafe acceptance and safe completion pooled over {len(joint)} fully classified configurations',
        'joint_denominators':{'unsafe_acceptance':joint_pooled['n_per_method'],
                              'safe_completion':joint_pooled['feasible_per_method']},
        'rate_axis_ticks':[0,25,50,75,100],
        'jitter':False,'imputation':False,'bar_value_labels':True,
        'bar_width_points':bar_width_points,'bar_gap_points':bar_gap_points,
        'equal_physical_bar_widths':True,
        'reported_percentage_decimal_places':1,
        'value_label_decimal_overrides':{'opus55_medium':0},
        'sample_sizes_in_caption_and_appendix':True,
        'sample_size_locations':['Figure caption', 'Appendix B', 'Appendix C'],
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
    from certified_reporting import summary_rows as certified_summaries, REPORT as SCORING_REPORT
    grid=certified_summaries(root,'data/derived/grid_summary.json')
    gb={(r['profile'],r['arm']):r for r in grid if r['group']=='all'}
    lb=display_language(root)
    efforts=['none','low','medium','high','xhigh','max']
    settings=['Off','L','M','H','XH','Max']
    families=[('gpt56_sol','Sol'),('gpt56_terra','Terra'),('gpt56_luna','Luna')]
    values=dict(metric='Exact decisions (%)',y_axis_limits=[0,100],
        effort_source=SCORING_REPORT,
        language_sources=[SCORING_REPORT],
        effort_order=efforts,setting_labels=settings,effort=[],language=[],
        interpolation='None; straight segments only between adjacent complete requested settings',
        point_or_bar_value_labels=False,cohorts_pooled=False,new_model_calls=0)
    values['family_setting_order']={}
    fig=plt.figure(figsize=(7.15,3.40))
    fig.text(.01,.967,'(a)  Sensitivity to reasoning settings',fontsize=9.2,weight='bold')
    fig.text(.684,.967,'(b)  Method comparison',fontsize=9.2,weight='bold')
    styles=[('direct',METHOD_LINE['direct'],'o','--'),
            ('set',METHOD_LINE['set'],'s','-')]
    fig.legend(handles=[Line2D([0],[0],color=color,marker=marker,ls=ls,
                    markersize=4,lw=1.4,markerfacecolor='white' if arm=='direct' else color,
                    label='Direct' if arm=='direct' else 'Set') for arm,color,marker,ls in styles],
               loc='upper center',bbox_to_anchor=(.42,.916),ncol=2,
               fontsize=8.2,handlelength=2.4,columnspacing=2.3,borderaxespad=0)
    fig.legend(handles=[Patch(facecolor=color,edgecolor='black',hatch=hatch,label=label)
                        for label,color,hatch in [('ZH',LANGUAGE_COLOR['zh'],''),
                                                  ('EN',LANGUAGE_COLOR['en'],'///')]],
               loc='upper center',bbox_to_anchor=(.858,.916),ncol=2,
               fontsize=8.2,handlelength=1.25,columnspacing=1.1,borderaxespad=0)
    positions=[(.072,.300,.180,.440),(.266,.300,.180,.440),
               (.460,.300,.180,.440)]
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
                    lw=1.8,ms=4.2,mew=1.0,mfc='white' if arm=='direct' else color,
                    clip_on=False,zorder=3 if arm=='direct' else 4)
        ax.set(xlim=(-.30,len(available_efforts)-.70),ylim=(0,100),yticks=[0,50,100])
        ax.set_xticks(range(len(available_efforts)),[settings[efforts.index(e)] for e in available_efforts])
        plt.setp(ax.get_xticklabels(), rotation=60, ha='right', rotation_mode='anchor')
        ax.tick_params(axis='x',labelsize=6.7,pad=4)
        ax.tick_params(axis='y',labelsize=7.1,pad=3)
        if prefix!='gpt56_sol':ax.tick_params(axis='y',labelleft=False)
        ax.set_title(label,loc='left',fontsize=8.7,weight='bold',pad=7)
        ax.grid(axis='y',color=LINE,lw=.6);ax.set_axisbelow(True)
    assert len(changes)==18 and sum(d>0 for d in changes)==17 and sum(d<0 for d in changes)==1
    values['complete_effort_configurations']=len(changes)
    fig.text(.008,.520,'Exact decisions (%)',rotation=90,va='center',ha='center',fontsize=9)
    fig.text(.350,.150,'Requested reasoning setting',ha='center',fontsize=9)
    # Methods are explicit on the x-axis. Language uses its own palette and
    # plain/hatched fills, independent of the method colors in panel (a).
    ax=fig.add_axes([.731,.300,.264,.440])
    ps=['ds_flash_low','ds_flash_high','ds_flash_max']
    names=['DS low','DS high','DS max']
    centers=np.arange(3)*1.5
    ticks=[];ticklabels=[]
    for i,(p,name,center) in enumerate(zip(ps,names,centers)):
        if i%2==0:ax.axvspan(center-.69,center+.69,color='#F3F3F3',zorder=0)
        for arm,offset in [('direct',-.30),('set',.30)]:
            ticks.append(center+offset);ticklabels.append('Direct' if arm=='direct' else 'Set')
            for language,shift,color,hatch in [('zh',-.105,LANGUAGE_COLOR['zh'],''),
                                               ('en',.105,LANGUAGE_COLOR['en'],'///')]:
                row=lb[p,arm,language];pct=100*row['exact']/row['n']
                assert row['n']==60
                ax.bar(center+offset+shift,pct,width=.185,color=color,
                       edgecolor='black',linewidth=.55,hatch=hatch,zorder=3)
                values['language'].append(dict(profile=p,arm=arm,language=language,
                    n=row['n'],exact=row['exact'],percent=pct,
                    author_reported=bool(row.get('author_reported',False))))
        ax.text(center,-.36,name,transform=ax.get_xaxis_transform(),ha='center',
                va='top',fontsize=7.6,linespacing=1.15)
    ax.set(xlim=(-.75,3.75),ylim=(0,100),yticks=[0,25,50,75,100])
    ax.set_xticks(ticks,ticklabels)
    plt.setp(ax.get_xticklabels(),rotation=55,ha='right',rotation_mode='anchor')
    ax.tick_params(axis='x',labelsize=7.0,pad=4)
    ax.tick_params(axis='y',labelsize=7.1,pad=3)
    ax.set_ylabel('Exact decisions (%)',fontsize=8.2,labelpad=5)
    ax.grid(axis='y',color=LINE,lw=.6);ax.set_axisbelow(True)
    values['language_visual_encoding']=dict(x_axis='Method',groups=ps,
        method_order=['direct','set'],language_order=['zh','en'],
        color=LANGUAGE_COLOR.copy(),hatch={'zh':'','en':'///'},
        palette='muted color with grayscale-distinguishable fills',
        method_encoding='x-axis labels and subgroup position')
    (root/'figures/15_configuration_robustness_values.json').write_text(json.dumps(values,indent=2)+'\n')
    return fig
