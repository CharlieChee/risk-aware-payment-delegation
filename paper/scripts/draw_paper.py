"""Publication figures from frozen evidence; main and ablation views separated."""
from pathlib import Path
import json
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap
from primary_profiles import display_primary
from reported_results import display_language, REPORT
from figure1_architecture import draw_architecture
from figure_mechanism import draw_ablations, draw_witnesses, draw_authorization, authorization_replay_values
from evaluation_figures import draw_completion, draw_robustness, draw_intent
R=Path(__file__).resolve().parents[1];F=R/'figures';F.mkdir(exist_ok=True)
def data(n):return json.loads((R/'data/derived'/f'{n}.json').read_text())
def diag(n):return json.loads((R/'data/diagnostics'/f'{n}.json').read_text())
INK='#1F2937';MUTED='#5E6C7B';LINE='#DCE2E7';DIRECT='#53677F';SET='#007F82';PALE='#E8F4F3';RED='#B34438';GREY='#8A96A5'
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':9,'axes.labelsize':9,'axes.titlesize':10,'xtick.labelsize':8.5,'ytick.labelsize':8.5,'legend.fontsize':8.5,'text.color':INK,'axes.labelcolor':INK,'xtick.color':MUTED,'ytick.color':MUTED,'axes.edgecolor':'#B7C1CB','axes.linewidth':.6,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.spines.bottom':False,'xtick.major.size':0,'ytick.major.size':0,'pdf.fonttype':42,'ps.fonttype':42,'savefig.facecolor':'white','legend.frameon':False,'lines.solid_capstyle':'round','axes.unicode_minus':False,'mathtext.fontset':'dejavusans'})
manifest=[]
selected_figures=set(sys.argv[2:]) if len(sys.argv)>1 and sys.argv[1]=='--only' else set()
def save(fig,n,sources,role):
 if not selected_figures or n in selected_figures:
  for ext in ['pdf','svg','png']:fig.savefig(F/f'{n}.{ext}',dpi=400,bbox_inches='tight',pad_inches=.065)
 manifest.append(dict(figure=n,sources=sources,placement=role,dpi=400));plt.close(fig)
def panel(ax,l,t):ax.set_title(f'({l})  {t}',loc='left',fontweight='bold',pad=13)
def grid(ax,axis='y'):ax.set_axisbelow(True);ax.grid(axis=axis,color=LINE,lw=.6);ax.tick_params(pad=5)
def legend(fig,left=.07):
 fig.legend(handles=[Line2D([0],[0],color=DIRECT,lw=5,label='Direct generation'),Line2D([0],[0],color=SET,lw=5,label='Risk-aware (Set)')],loc='upper left',bbox_to_anchor=(left,.995),ncol=2,handlelength=1.3,columnspacing=2.4,borderaxespad=0)
def rect(ax,x,y,w,h,face='white'):ax.add_patch(Rectangle((x,y),w,h,facecolor=face,edgecolor=LINE,lw=.8))
def arrow(ax,a,b):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=9,lw=1.2,color=MUTED))

# Main: original vector illustration, with the learned/executable boundary visible.
with plt.rc_context({'svg.fonttype':'none'}):
 fig=draw_architecture()
 save(fig,'01_contract_architecture',['historical schematic; superseded by Algorithm 1 in the manuscript'],'historical_unused')
main=data('main_summary');by={(r['profile'],r['arm']):r for r in main};ps=['ds_flash_low','ds_flash_high','astra_max'];short=['DS low','DS high','Astra max'];labels=['DeepSeek low','DeepSeek high','Astra max']

# Main: complete same-case Qwen additions; original evidence stays frozen.
primary=display_primary(R)
primary_by=primary['by'];primary_ps=primary['profiles'];primary_labels=primary['labels']
partial_ids={p['profile'] for p in primary['partials']}
reported_ids=set(primary['author_reported_profiles'])
primary_labels=[label+(' *' if p in reported_ids else (' †' if p in partial_ids else '')) for p,label in zip(primary_ps,primary_labels)]
height=1.05+.31*len(primary_ps)
fig,axes=plt.subplots(1,3,figsize=(7.15,height),sharey=True)
fig.subplots_adjust(left=.21,right=.99,bottom=.14,top=1-.65/height,wspace=.36)
legend(fig,.21)
unsafe_max=max(100*primary_by[p,a]['unsafe']/primary_by[p,a]['n'] for p in primary_ps for a in ['direct','set'] if primary_by[p,a]['unsafe'] is not None)
refusal_max=max(100*primary_by[p,a]['false_refusal']/primary_by[p,a]['n'] for p in primary_ps for a in ['direct','set'] if primary_by[p,a]['false_refusal'] is not None)
unsafe_limit=max(30,int(np.ceil(unsafe_max/10))*10)
refusal_limit=max(30,int(np.ceil(refusal_max/10))*10)
settings=[('exact','Exact decisions (%)',108,[0,25,50,75,100]),
          ('unsafe','Unsafe acceptance (%)',unsafe_limit+6,list(range(0,unsafe_limit+1,10))),
          ('false_refusal','False refusal (%)',refusal_limit+5,list(range(0,refusal_limit+1,10)))]
yy=np.arange(len(primary_ps))[::-1]
for ax,(metric,title,lim,ticks),letter in zip(axes,settings,'abc'):
 for y,p in zip(yy,primary_ps):
  if any(primary_by[p,a][metric] is None for a in ('direct','set')):
   ax.text(.04,y,'not reported',transform=ax.get_yaxis_transform(),va='center',fontsize=7.5,color=MUTED)
   continue
  d=100*primary_by[p,'direct'][metric]/primary_by[p,'direct']['n']
  s=100*primary_by[p,'set'][metric]/primary_by[p,'set']['n']
  if p in partial_ids:ax.axhspan(y-.49,y+.49,color='#FFF5E5',zorder=0)
  if metric=='exact':
   ax.plot([d,s],[y,y],color=LINE,lw=2.4,zorder=2)
   for value,color,marker,offset,va in [(d,DIRECT,'o',.11,'bottom'),(s,SET,'s',-.11,'top')]:
    ax.scatter([value],[y],s=22,c=color,marker=marker,zorder=4)
    label=f'{value:.1f}'.rstrip('0').rstrip('.')
    ax.text(value,y+offset,label,ha='center',va=va,fontsize=7.8,color=color,
            fontweight='bold' if color==SET else 'normal')
  else:
   for value,color,offset in [(d,DIRECT,.24),(s,SET,-.24)]:
    ax.barh(y+offset,value,height=.32,color=color,zorder=3)
    label=f'{value:.1f}'.rstrip('0').rstrip('.')
    ax.text(value+.65,y+offset,label,va='center',fontsize=8.0,color=color,
            fontweight='bold' if color==SET else 'normal')
 ax.set_xlim(-3 if metric=='exact' else 0,lim)
 ax.set_xticks(ticks);ax.set_ylim(-.55,len(primary_ps)-.40)
 ax.set_yticks(yy,primary_labels);grid(ax,'x')
 ax.set_title(f'({letter})  {title}',loc='left',fontweight='bold',fontsize=9.1,pad=11)
 for y in np.arange(.5,len(primary_ps)-1,.1*10):ax.axhline(y,color=LINE,lw=.4,zorder=0)
footnote='; '.join(f"{primary['labels'][primary_ps.index(p['profile'])]}: {p['n']} completed pairs" for p in primary['partials'])
fig.text(.21,.052,'Complete rows: 200 cases. † Opus: 16 pairs, author-reviewed decisions.',fontsize=7.3,color=MUTED)
fig.text(.21,.018,'Observed percentages, not projected counts. Within-profile comparisons; budgets differ.',fontsize=7.3,color=MUTED)
save(fig,'02_primary_results',primary['sources'],'archived_unused')

# Main: every common effort level in all four GPT families; separate language panel.
gs=data('grid_summary');gb={(r['profile'],r['arm']):r for r in gs if r['group']=='all'};lb=display_language(R)
fig=plt.figure(figsize=(7.15,2.72));a=fig.add_axes([.005,.15,.61,.58]);b=fig.add_axes([.765,.15,.225,.58]);legend(fig,.015)
fig.text(.015,.865,'(a)  Model family and reasoning effort',fontweight='bold',fontsize=10)
fig.text(.685,.865,'(b)  Task language',fontweight='bold',fontsize=10)
efforts=['low','medium','high','xhigh','max'];families_grid=[('astra','Astra'),('gpt56_sol','5.6 Sol'),('gpt56_terra','5.6 Terra'),('gpt56_luna','5.6 Luna')]
a.set(xlim=(-1.70,4.50),ylim=(-.50,3.50));a.axis('off')
for x,label in enumerate(['low','med.','high','xhigh','max']):a.text(x,3.80,label,ha='center',va='center',fontsize=8.5,color=MUTED)
for row,(prefix,label) in enumerate(families_grid):
 y=3-row;a.add_patch(Rectangle((-1.7,y-.48),6.2,.96,facecolor=PALE if row%2==0 else '#F7F9FA',edgecolor='none'))
 a.text(-1.56,y,label,va='center',fontsize=9,fontweight='bold')
 for x,e in enumerate(efforts):
  d,s=gb[prefix+'_'+e,'direct'],gb[prefix+'_'+e,'set'];assert d['n']==s['n']==60
  a.text(x-.15,y,str(d['exact']),ha='right',va='center',fontsize=9,color=DIRECT)
  a.text(x,y,'→',ha='center',va='center',fontsize=8.5,color=MUTED)
  a.text(x+.15,y,str(s['exact']),ha='left',va='center',fontsize=9,color=SET,fontweight='bold')
fig.text(.015,.035,'Exact / 60: Direct → Set  |  All 20 common model–effort settings',fontsize=8.2,color=MUTED)
lps=['ds_flash_low','ds_flash_high','ds_flash_max','astra_max'];mat=np.array([[100*lb[p,m,l]['exact']/lb[p,m,l]['n'] for m,l in [('direct','zh'),('direct','en'),('set','zh'),('set','en')]] for p in lps]);cmap=LinearSegmentedColormap.from_list('language',['#F6F8FA','#C9E5E2',SET]);b.imshow(mat,cmap=cmap,vmin=0,vmax=100,aspect='auto')
for yy in range(4):
 for xx in range(4):b.text(xx,yy,f'{mat[yy,xx]:.1f}'.rstrip('0').rstrip('.'),ha='center',va='center',fontsize=8,color='white' if mat[yy,xx]>=81 else INK,fontweight='bold' if xx>=2 else 'normal')
b.axvline(1.5,color='white',lw=4)
for yy in [.5,1.5,2.5]:b.axhline(yy,color='white',lw=1)
b.set_xticks(range(4),['ZH','EN','ZH','EN']);b.set_yticks(range(4),['DS low','DS high','DS max','Astra *']);b.tick_params(length=0);b.text(.25,1.06,'Direct',transform=b.transAxes,ha='center',fontsize=8.5,color=DIRECT);b.text(.75,1.06,'Set',transform=b.transAxes,ha='center',fontsize=8.5,color=SET)
fig.text(.66,.035,'Exact %; DS n=60, Astra* n=200',fontsize=7.3,color=MUTED)
save(fig,'03_effort_language',['data/derived/grid_summary.json','data/derived/language_all_methods_matched.json',REPORT],'archived_unused')

# Appendix: complete problem/output/reference traces, not isolated score callouts.
fig=draw_witnesses()
save(fig,'04_boundary_witnesses',['data/worked_examples'],'archived_unused')

# Main: all four prespecified families and every primary task retained.
families=data('family_summary');fb={(r['profile'],r['arm'],r['family']):r for r in families};fig,axes=plt.subplots(2,2,figsize=(7.15,3.48));fig.subplots_adjust(left=.155,right=.985,bottom=.15,top=.80,wspace=.42,hspace=.85);legend(fig,.155)
fl=[('coupon_cancellation','Coupon cancellation'),('insured_cancellation','Insured cancellation'),('threshold_returns','Threshold-based returns'),('service_replacement','Service replacement')]
for ax,(fam,title),letter in zip(axes.flat,fl,'abcd'):
 for yy,p in zip([2,1,0],ps):
  d=fb[p,'direct',fam]['exact'];s=fb[p,'set',fam]['exact'];ax.plot([d,s],[yy,yy],color='#C7D2DB',lw=3,zorder=1);ax.scatter(d,yy,s=28,facecolor='white',edgecolor=DIRECT,lw=1.3,zorder=3);ax.scatter(s,yy,s=30,color=SET,marker='s',zorder=4);ax.text(d-.9,yy-.20,str(d),ha='right',va='top',fontsize=8.3,color=DIRECT);ax.text(s+.9,yy+.06,str(s),ha='left',va='bottom',fontsize=8.3,color=SET,fontweight='bold')
 ax.set_yticks([2,1,0],short);ax.set_xlim(0,56);ax.set_ylim(-.75,2.7);ax.set_xticks([0,10,20,30,40,50]);grid(ax,'x');panel(ax,letter,title)
 if letter in 'cd':ax.set_xlabel('Exact decisions / 50')
save(fig,'11_contract_families',['data/derived/family_summary.json'],'archived_unused')

# Python and other execution controls appear only in ablation figures below.
st=diag('stress_chart_data');fig,(a,b)=plt.subplots(1,2,figsize=(7.15,2.58),gridspec_kw={'width_ratios':[1.18,1]});fig.subplots_adjust(left=.16,right=.99,bottom=.21,top=.75,wspace=.45)
a.axvspan(2000,4500,color='#FBEFEC');a.barh([1,0],[4000,2000],height=.32,color=[DIRECT,SET]);a.axvline(2000,color=RED,ls=(0,(4,3)),lw=1);a.text(2140,1.62,'User limit',ha='left',fontsize=8.3,color=RED)
for yy,v,c in [(1,4000,DIRECT),(0,2000,SET)]:a.text(v+80,yy,f'{v:,}',va='center',fontsize=9,color=c,fontweight='bold')
a.set(xlim=(0,4650),ylim=(-.55,1.9),xlabel='Largest admitted loss (MU)');a.set_xticks([0,2000,4000]);a.set_yticks([1,0],['Python','Set contract']);grid(a,'x');panel(a,'a','Permission boundary')
b.axis('off');panel(b,'b','One new, unsafe offer');b.text(.02,.79,'Actual loss: 4,000 MU',fontsize=11,fontweight='bold');b.text(.02,.61,'Generated rules remain unchanged.',fontsize=8.7,color=MUTED);b.text(.02,.36,'Python',fontsize=10);b.text(.53,.36,'ACCEPT',fontsize=10,fontweight='bold',color=RED);b.text(.02,.12,'Set contract',fontsize=10);b.text(.53,.12,'REJECT',fontsize=10,fontweight='bold',color=SET);fig.text(.16,.98,'Selected DeepSeek high pair  |  Identical compilation input  |  No new model calls',fontsize=8.3,color=MUTED)
save(fig,'05_permission_probe',['data/diagnostics/stress_chart_data.json','data/diagnostics/stress_story.json'],'execution_ablation')
ts=data('template_summary');tb={(r['profile'],r['arm'],r['template']):r for r in ts}
tids=[f'{a}{i}' for a in 'abcd' for i in range(1,6)]
fig=plt.figure(figsize=(7.15,4.15));grids=fig.add_gridspec(1,3,left=.105,right=.975,bottom=.09,top=.85,width_ratios=[1,1,1.06],wspace=.48)
axes=[fig.add_subplot(grids[0,i]) for i in range(3)]
cmap=LinearSegmentedColormap.from_list('exact',['#F6F8FA','#CEE5E0',SET])
template_values=dict(template_denominator=10,template_profiles=[],aggregate_source=primary['sources'],astra={})
for ax,p,label in zip(axes[:2],['ds_flash_low','ds_flash_high'],['DeepSeek low','DeepSeek high']):
 mat=np.array([[tb[p,m,t]['exact'] for m in ['direct','python_fresh','set']] for t in tids])
 ax.imshow(mat,vmin=0,vmax=10,cmap=cmap,aspect='auto')
 for yy in range(20):
  for xx in range(3):ax.text(xx,yy,str(mat[yy,xx]),ha='center',va='center',fontsize=8.5,color='white' if mat[yy,xx]>=8 else INK,fontweight='bold' if xx==2 else 'normal')
 ax.set_xticks([0,1,2],['Direct','Python','Set']);ax.set_yticks(range(20),tids);ax.tick_params(length=0)
 ax.set_title(label+'\nPer template / 10',fontsize=9.2,fontweight='bold',pad=10)
 for yy in [4.5,9.5,14.5]:ax.axhline(yy,color='white',lw=3)
 template_values['template_profiles'].append(dict(profile=p,templates=tids,methods=['direct','python_fresh','set'],exact=mat.tolist()))
for y,title in [(.755,'Coupons'),(.56,'Insurance'),(.37,'Returns'),(.175,'Replacement')]:fig.text(.006,y,title,rotation=90,va='center',color=MUTED,fontsize=8.3)
ax=axes[2]
for i,(arm,color) in enumerate([('direct',DIRECT),('set',SET)]):
 r=primary_by['astra_max',arm]
 assert r['n']==200 and r['exact']==(180 if arm=='direct' else 196)
 ax.bar(i,r['exact'],color=color,width=.56,zorder=3)
 ax.text(i,r['exact']+3,str(r['exact']),ha='center',va='bottom',fontsize=10,fontweight='bold',color=color)
 template_values['astra'][arm]=dict(n=r['n'],exact=r['exact'])
ax.set_title('Astra max\nWhole benchmark / 200',fontsize=9.2,fontweight='bold',pad=10)
ax.set_xticks([0,1],['Direct','Set']);ax.set_ylim(0,218);ax.set_yticks([0,50,100,150,200]);ax.set_xlim(-.6,1.6);ax.set_ylabel('Exact decisions',fontsize=8.7);grid(ax,'y')
fig.text(.105,.97,'Contract-template coverage and the Astra aggregate',fontsize=9.3,color=INK,fontweight='bold')
(F/'06_all_templates_values.json').write_text(json.dumps(template_values,indent=2)+'\n')
save(fig,'06_all_templates',['data/derived/template_summary.json']+primary['sources'],'execution_ablation')
risk=data('risk_tradeoff')['counts'];fig,(a,b)=plt.subplots(1,2,figsize=(7.15,2.64));fig.subplots_adjust(left=.105,right=.99,bottom=.22,top=.75,wspace=.5)
for yy,m in [(1,'python_fresh'),(0,'set')]:
 u=risk[m]['unsafe'];o=risk[m]['other_failures'];a.barh(yy,u,height=.34,color=RED);a.barh(yy,o,left=u,height=.34,color=GREY);a.text(u/2,yy,str(u),va='center',ha='center',color='white',fontsize=10,fontweight='bold');a.text(u+o/2,yy,str(o),va='center',ha='center',color='white',fontsize=10)
a.set(xlim=(0,34),ylim=(-.55,1.65),xlabel='Failed decisions / 400');a.set_yticks([1,0],['Python','Set']);a.set_xticks([0,10,20,30]);grid(a,'x');panel(a,'a','Error consequences')
xs=np.linspace(1,5,201)
for m,col,label in [('python_fresh',DIRECT,'Python'),('set',SET,'Set contract')]:b.plot(xs,(risk[m]['unsafe']*xs+risk[m]['other_failures'])/400,color=col,lw=2,label=label)
b.axvline(5/3,color=MUTED,lw=.8,ls=':');b.text(1.79,.219,r'$\lambda=5/3$',fontsize=9,color=MUTED);b.set(xlim=(1,5),ylim=(0,.26),xlabel='Unsafe cost (other failure = 1)',ylabel='Empirical weighted loss');b.set_yticks([0,.05,.1,.15,.2,.25]);grid(b);b.legend(loc='lower right');panel(b,'b','Cost sensitivity');fig.legend(handles=[Line2D([0],[0],color=RED,lw=6,label='Unsafe acceptance'),Line2D([0],[0],color=GREY,lw=6,label='Other failures')],loc='upper left',bbox_to_anchor=(.105,.997),ncol=2,handlelength=1.3)
save(fig,'07_risk_sensitivity',['data/derived/risk_tradeoff.json'],'execution_ablation')
reuse=data('reuse_summary');rs={r['method']:r for r in reuse if r['profile']=='gpt6_max'};fig,ax=plt.subplots(figsize=(7.15,2.72));fig.subplots_adjust(left=.265,right=.98,bottom=.20,top=.9);ms=['direct','python_fresh','python_cached','flat_a','set'];names=['Direct per catalogue','Python per catalogue','Cached Python','Flat contract','Set contract']
for yy,m in zip(range(4,-1,-1),ms):
 r=rs[m];v=(r['input_tokens']+r['output_tokens'])/1000;col=SET if m=='set' else DIRECT if m=='direct' else GREY;ax.barh(yy,v,height=.48,color=col);ax.text(v+4,yy,f'{v:.1f}k  /  {r["calls"]} calls',va='center',fontsize=9,color=col)
ax.set(xlim=(0,280),ylim=(-.65,4.65),xlabel='Total input + output tokens (thousands)');ax.set_xticks([0,50,100,150,200,250]);ax.set_yticks(range(4,-1,-1),names);grid(ax,'x');fig.text(.265,.96,'Astra  |  Two requirement families, eight catalogues each',fontsize=9,color=MUTED)
save(fig,'08_catalogue_reuse',['data/derived/reuse_summary.json'],'execution_ablation')
groups=st['groups'];profiles=st['profiles'];arms=['python_cached','python_fresh','set'];fig,axes=plt.subplots(1,3,figsize=(7.15,3.08),sharey=True);fig.subplots_adjust(left=.15,right=.99,bottom=.18,top=.76,wspace=.20);cmap=LinearSegmentedColormap.from_list('error',['#F5F7F9','#EDD3C9',RED])
for ax,metric,title,letter in zip(axes,['grid_unsafe_domain','single_unsafe_selection','single_invalid'],['Unsafe domains','Unsafe selections','Invalid executions'],'abc'):
 mat=np.array([[next(g[metric] for g in groups if g['profile']==p and g['arm']==m) for m in arms] for p in profiles]);ax.imshow(mat,cmap=cmap,vmin=0,vmax=5,aspect='auto')
 for yy in range(6):
  for xx in range(3):ax.text(xx,yy,str(mat[yy,xx]),ha='center',va='center',fontsize=10,color='white' if mat[yy,xx]>=4 else INK)
 ax.set_xticks(range(3),['Py\nmatched','Py\nvisible','Set']);ax.set_yticks(range(6),['DS low','DS high','DS max','Astra low','Astra high','Astra max']);ax.tick_params(length=0);panel(ax,letter,title)
fig.text(.15,.965,'All frozen outputs  |  72 artifacts per cell  |  Paired candidate-shift audit',fontsize=9,color=MUTED)
save(fig,'09_full_transfer_audit',['data/diagnostics/stress_chart_data.json'],'execution_ablation')
oracle={r['variant']:r for r in data('historical_oracle_ablation')};keys=['original','oracle_utility_only','oracle_admissibility_only','oracle_both'];fig,axes=plt.subplots(1,3,figsize=(7.15,2.82),sharey=True);fig.subplots_adjust(left=.285,right=.99,bottom=.17,top=.74,wspace=.18)
for ax,field,title,color in zip(axes,['overpermissive','unsafe','exact'],['Unsafe domain','Unsafe choice','Exact decision'],[RED,RED,SET]):
 values=[int(oracle[k][field]) for k in keys];ax.barh(range(3,-1,-1),values,height=.45,color=color)
 for yy,v in zip(range(3,-1,-1),values):ax.text(v+.35,yy,str(v),va='center',fontsize=9,color=color,fontweight='bold')
 ax.set_xlim(0,19);ax.set_xticks([0,8,16]);ax.set_yticks(range(3,-1,-1),['Original specification','Fix utility only','Fix admissibility only','Fix both']);ax.set_title(title,fontsize=9.5,fontweight='bold',pad=12);grid(ax,'x')
fig.text(.285,.96,'Reference-assisted interventions  |  16 selected faulty contracts',fontsize=9,color=MUTED)
save(fig,'10_oracle_decomposition',['data/derived/historical_oracle_ablation.json'],'mechanism_ablation')
# Full implementation controls remain together in the appendix.
fig=draw_ablations(st, data('historical_oracle_ablation'), data('risk_tradeoff')['counts'], reuse)
save(fig,'12_mechanism_ablations',[
 'data/diagnostics/stress_chart_data.json','data/derived/historical_oracle_ablation.json',
 'data/derived/risk_tradeoff.json','data/derived/reuse_summary.json'],'execution_ablation')
fig=draw_authorization(st)
(F/'13_authorization_diagnostics_values.json').write_text(json.dumps(authorization_replay_values(st),indent=2)+'\n')
save(fig,'13_authorization_diagnostics',[
 'data/diagnostics/stress_chart_data.json'],'main')
save(draw_completion(R),'14_safe_completion',primary['sources']+[
 'data/derived/template_summary.json',
 'data/supplements/evaluation_redesign_20261010/verified_claims.json'], 'main')
save(draw_robustness(R),'15_configuration_robustness',[
 'data/derived/grid_summary.json','data/derived/language_all_methods_matched.json',REPORT], 'appendix')
save(draw_intent(R),'16_retained_intent',[
 'data/supplements/intent_ambiguity_20261011/parameter_summary.json',
 'data/supplements/intent_ambiguity_20261011/parameter_rows.json'], 'main')
# Keep uncited historical plots available without marking them as manuscript figures.
for item in manifest:
 if item['placement'] not in ('main','appendix'):
  item['placement']='archived_unused'
(F/'figure_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'Generated {len(manifest)} figures; {sum(x["placement"]=="main" for x in manifest)} main figures.')
