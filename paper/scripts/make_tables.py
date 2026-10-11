from pathlib import Path
import json
from primary_profiles import complete_primary, display_primary
from reported_results import display_language
from intent_ambiguity_reporting import build as build_intent_tables
R=Path(__file__).resolve().parents[1];D=R/'data/derived';T=R/'tables';T.mkdir(exist_ok=True)
build_intent_tables(R)
def load(n):return json.loads((D/(n+'.json')).read_text())
main=load('main_summary');by={(r['profile'],r['arm']):r for r in main}
profiles=['ds_flash_low','ds_flash_high','astra_max']; labels=['DeepSeek low','DeepSeek high','Astra max']
grid=load('grid_summary');gb={(r['profile'],r['arm']):r for r in grid if r['group']=='all'}
# Auto-generated LaTeX tables (Qwen supplements do not change old evidence).
def put(n,s):(T/(n+'.tex')).write_text(s+'\n')
primary=complete_primary(R)
primary_by=primary['by'];primary_profiles=primary['profiles'];primary_labels=primary['labels']
display=display_primary(R)
partial_ids={p['profile'] for p in display['partials']}
partial_note=' '.join(f"{display['labels'][display['profiles'].index(p['profile'])]} uses {p['n']} same-case pairs." for p in display['partials'])
extension_profiles=[p for p in primary_profiles if p.startswith(('glm','gpt56'))]
archived_extension_count=len(extension_profiles)
primary_by=display['by'];primary_profiles=display['profiles'];primary_labels=display['labels']
extension_profiles=[p for p in primary_profiles if p.startswith(('glm','gpt56'))]
reported_ids=set(display['author_reported_profiles'])
def fmt(v):return r'\text{--}' if v is None else str(v)
def marked(label,p):return label
put('primary_stats', '\n'.join([
 r'\newcommand{\PrimaryProfileCount}{'+str(len(primary_profiles))+'}',
 r'\newcommand{\PrimaryDisplayCount}{'+str(len(display['profiles']))+'}',
 r'\newcommand{\PrimaryCompleteDisplayCount}{'+str(len(display['profiles'])-len(display['partials']))+'}',
 r'\newcommand{\PrimaryPartialProfileCount}{'+str(len(display['partials']))+'}',
 r'\newcommand{\PrimaryPartialNote}{'+partial_note+'}',
 r'\newcommand{\PrimaryPartialTrials}{'+str(display['partial_trials'])+'}',
 r'\newcommand{\PrimaryTrialCount}{'+f'{display["display_trials"]:,}'.replace(',','{,}')+'}',
 r'\newcommand{\PrimaryExtensionCount}{'+str(len(extension_profiles)*400)+'}',
 r'\newcommand{\PrimaryExtensionProfiles}{'+str(len(extension_profiles))+'}',
]))
paragraphs=[]
for p,label in zip(primary_profiles,primary_labels):
 if not p.startswith('glm'):continue
 d,s=primary_by[p,'direct'],primary_by[p,'set']
 extra=f"; unsafe acceptances change from {d['unsafe']} to {s['unsafe']}" if d['unsafe'] is not None else '; its detailed failure categories await the original records'
 paragraphs.append(f"{marked(label,p)} obtains \\textbf{{{d['exact']}/200$\\to${s['exact']}/200}} exact decisions"+extra+'. ')
gpt=[(p,l) for p,l in zip(primary_profiles,primary_labels) if p.startswith('gpt56')]
if gpt:
 values=[]
 for p,label in gpt:
  d,s=primary_by[p,'direct'],primary_by[p,'set']
  values.append(label.replace('5.6 ','').replace(' medium','')+f" {d['exact']}$\\to${s['exact']}")
 paragraphs.append('At medium effort, GPT-5.6 exact counts are '+', '.join(values)+', each out of 200. ')
if extension_profiles:
 paragraphs.append(r'These complete extensions retain all operational and compilation failures (Appendix~\ref{app:primary-extensions}).')
put('primary_extension_results',''.join(paragraphs))
pending=[label for p,label in [('glm53_high','GLM high'),('gpt56_luna_medium','GPT-5.6 Luna medium'),
    ('gpt56_terra_medium','GPT-5.6 Terra medium'),('gpt56_sol_medium','GPT-5.6 Sol medium')]
    if p not in extension_profiles and p not in partial_ids]
status_parts=[]
if display['partials']:
 status_parts.append(partial_note+' These observed rates are displayed separately from the complete-cohort totals; they do not estimate a completed 200-case run.')
if pending:
 status_parts.append('At this snapshot, '+', '.join(pending)+' remain incomplete and are not displayed.')
if reported_ids:status_parts.append('The complete configurations report 200 tasks per method; dagger-marked rows use their observed paired denominators. Asterisks identify author-reported aggregate updates from another computer: GLM high, Astra max, and the Sol medium Set arm. Their original records await import. Unreported error categories and completion counts are left blank, and no new paired statistics are inferred from aggregates.')
if not status_parts:status_parts.append('All requested medium/high profiles are complete in this snapshot.')
put('primary_extension_status',' '.join(status_parts))
lines=[r'\begin{tabular}{lrrrrrr}',r'\toprule',
       r'Model & $n$ & Exact $\uparrow$ & Unsafe $\downarrow$ & Refusal $\downarrow$ & Other $\downarrow$ & Accept / feasible $\uparrow$ \\',r'\midrule']
for p,lab in zip(display['profiles'],display['labels']):
 values=[]
 for field in ['exact','unsafe','false_refusal','other','correct_accept']:
  nums=[]
  for arm in ['direct','set']:
   r=display['by'][p,arm]
   value=(r['n']-r['exact']-r['unsafe']-r['false_refusal'] if r['unsafe'] is not None and r['false_refusal'] is not None else None) if field=='other' else r.get(field)
   nums.append(f"{value}/{r['expected_accept']}" if field=='correct_accept' and value is not None else fmt(value))
  values.append(f'${nums[0]}\\to\\mathbf{{{nums[1]}}}$')
 marker=''
 lines.append(lab+marker+' & '+str(display['by'][p,'direct']['n'])+' & '+' & '.join(values)+r' \\')
lines += [r'\bottomrule',r'\end{tabular}'];put('main','\n'.join(lines))
partial_details=[]
for partial in display['partials']:
 p=partial['profile'];prov=partial['provenance'];folder=partial['folder']
 label=display['labels'][display['profiles'].index(p)]
 paired=[display['by'][p,a] for a in ['direct','set']]
 all_observed=json.loads((folder/'all_observed_summary.json').read_text())
 partial_details.append(r'\paragraph{Provisional paired results.} '+f"{label} retains {prov['observed_trials']}/400 first method outcomes. {prov['stopping_reason']} Both methods completed the same {partial['n']} cases; Figures~\\ref{{fig:completion}}a and~\\ref{{fig:primary}} use these {prov['displayed_trials']} paired observations, without filtering by correctness. The other {prov['observed_unpaired_trials']} observed outcomes remain archived. Pending outcomes are not imputed. Completion may depend on task difficulty, so these rates are provisional and are not full-cohort estimates. ")
 d,s=paired
 partial_details.append(f"On the paired subset, exact decisions are {d['exact']}$\\to${s['exact']}/{partial['n']}. Direct answering has {d['outcomes'].get('output_budget',0)} output-budget failures and {d['outcomes'].get('timeout',0)} timeouts; this operational contribution must be distinguished from semantic errors. ")
 if p=='opus55_medium':
  from reported_results import opus_output_review
  review=opus_output_review(R)
  all_observed=review['all_observed_summary']
  partial_details.append('The author reports external verification that outputs classified locally as invalid are correct: 20 Direct and 7 Set outcomes are reclassified, including 7 and 3 in the paired subset. These are author-reviewed decision scores; external raw records await import. Original schema/execution flags and outputs remain archived, so this adjudication does not establish new successful local executions. Timeouts and provider failures retain their original classifications. Before adjudication, paired exact counts were 5 and 12, and all-observed counts were 16/53 and 60/68. ')
  partial_details.append('Opus requests the local Claude CLI with model identifier \\texttt{claude-opus-5-5}, medium effort, a fresh isolated session, and the unchanged 1,800-second deadline. Its native output ceiling is unobserved. The configured gateway supplies the reported model identity; no independent upstream identity attestation or cross-provider compute matching is claimed. ')
  retest_path=folder/'selected_retest.json'
  if retest_path.exists():
   retest=json.loads(retest_path.read_text())
   partial_details.append(f"A separate repeat of {retest['n']} initially unsuccessful Set outcomes yields {retest['exact']}/{retest['n']} exact decisions. This failure-selected diagnostic retains the same frozen requests and scoring; its new responses do not replace the original responses in the paired comparison. ")
 partial_details.extend([r'\begin{table*}[t]',r'\centering\scriptsize',r'\begin{tabular}{llrrrrrrrrr}',r'\toprule',r'Subset & Method & $n$ & Exact & Unsafe & Refusal & Budget & Timeout & Transport & Invalid & Value \\',r'\midrule'])
 for subset,records in [('Matched pairs',paired),('All observed',all_observed)]:
  for i,r in enumerate(records):
   o=r['outcomes'];vals=[r['n'],r['exact'],r['unsafe'],r['false_refusal'],o.get('output_budget',0),o.get('timeout',0),o.get('transport_or_provider_failure',0),o.get('invalid_output',0),o.get('certificate_underclaim',0)+o.get('certificate_overclaim',0)+o.get('suboptimal',0)+o.get('other_error',0)]
   assert sum(vals[1:])==r['n']
   partial_details.append((subset if i==0 else '')+' & '+('Direct' if r['arm']=='direct' else 'Set')+' & '+' & '.join(map(str,vals))+r' \\')
  partial_details.append(r'\midrule')
 partial_details[-1]=r'\bottomrule'
 partial_details.extend([r'\end{tabular}',r'\caption{Provisional '+label+r' outcomes after author-reported external adjudication. Only matched pairs enter Figures~\ref{fig:completion}a and~\ref{fig:primary}; the all-observed rows contain different case sets. External raw records await import; original local execution flags are preserved. Pending trials are not imputed.}',r'\end{table*}'])
put('partial_primary_details','\n'.join(partial_details) if partial_details else '% No provisional profiles remain in the current display.')
lines=[r'\begin{tabular}{llrrrrrrrrr}',r'\toprule',
       r'Model & Method & Exact & Unsafe & Refusal & Budget & Timeout & Transport & Invalid & Value \\',r'\midrule']
for p,label in [('qwen_flash_low','Flash low'),('qwen_max_low','Max low')]:
 for i,arm in enumerate(['direct','set']):
  r=primary_by[p,arm];o=r['outcomes']
  values=[r['exact'],r['unsafe'],r['false_refusal'],o.get('output_budget',0),o.get('timeout',0),
          o.get('transport_or_provider_failure',0),o.get('invalid_output',0),
          o.get('certificate_underclaim',0)+o.get('certificate_overclaim',0)]
  assert sum(values)==200
  lines.append((label if i==0 else '')+' & '+('Direct' if arm=='direct' else 'Set')+' & '+' & '.join(map(str,values))+r' \\')
 if p=='qwen_flash_low':lines.append(r'\midrule')
lines += [r'\bottomrule',r'\end{tabular}'];put('qwen_errors','\n'.join(lines))
lines=[r'\begin{tabular}{llrrrrrrrrr}',r'\toprule',
       r'Model & Method & Exact & Unsafe & Refusal & Budget & Timeout & Transport & Invalid & Value \\',r'\midrule']
for pi,p in enumerate(extension_profiles):
 label=primary_labels[primary_profiles.index(p)]
 for i,arm in enumerate(['direct','set']):
  r=primary_by[p,arm];o=r['outcomes']
  values=[r['exact'],r['unsafe'],r['false_refusal'],o.get('output_budget',0),o.get('timeout',0),
          o.get('transport_or_provider_failure',0),o.get('invalid_output',0),
          o.get('certificate_underclaim',0)+o.get('certificate_overclaim',0)+o.get('suboptimal',0)+o.get('other_error',0)]
  if not r.get('error_partition_reported',True):values=[r['exact']]+[None]*7
  elif not r.get('failure_subtypes_reported',True):values=[r['exact'],r['unsafe'],r['false_refusal']]+[None]*5
  else:assert sum(values)==200,(p,arm,values)
  lines.append((marked(label,p) if i==0 else '')+' & '+('Direct' if arm=='direct' else 'Set')+' & '+' & '.join('--' if v is None else str(v) for v in values)+r' \\')
 if pi<len(extension_profiles)-1:lines.append(r'\midrule')
lines += [r'\bottomrule',r'\end{tabular}'];put('primary_extension_errors','\n'.join(lines))
notes=[]
for folder in primary['extensions']:
 p=json.loads((folder/'provenance.json').read_text())
 label=primary_labels[primary_profiles.index(p['profiles'][0]['id'])]
 notes.append(f"{label}: {p['reused_trials']}/400 exactly matched historical outcomes reused")
put('primary_extension_reuse','; '.join(notes)+'.')
for table_name,arms in [('execution_ablation',['direct','python_fresh','set'])]:
 lines=[r'\begin{tabular}{llrrrrr}',r'\toprule',r'Model & Method & Exact $\uparrow$ & Unsafe $\downarrow$ & Refusal $\downarrow$ & Other $\downarrow$ & Accept $\uparrow$ \\',r'\midrule']
 execution_profiles=[(p,lab) for p,lab in zip(profiles,labels) if p.startswith('ds_')]
 for p,lab in execution_profiles:
  for i,m in enumerate(arms):
   r=by[p,m];name={'direct':'Direct','python_fresh':'Set-Py','set':r'\textbf{Set contract}'}[m];other=r['n']-r['exact']-r['unsafe']-r['false_refusal']
   exact=f"{r['exact']}/200";exact=(r'\textbf{'+exact+'}') if m=='set' else exact
   lines.append(f"{lab if i==0 else ''} & {name} & {exact} & {r['unsafe']} & {r['false_refusal']} & {other} & {r['correct_accept']}/100 "+r'\\')
  if p!=execution_profiles[-1][0]:lines.append(r'\midrule')
 lines+=[r'\bottomrule',r'\end{tabular}'];put(table_name, '\n'.join(lines))
# Complete grid with partial rows explicitly separated.
lines=[r'\begin{tabular}{llrrr}',r'\toprule',r'Model & Effort & Direct & Set-Py & Set \\',r'\midrule']
mods=['astra','gpt56_sol','gpt56_luna','gpt56_terra'];names={'astra':'Astra','gpt56_sol':'5.6 Sol','gpt56_luna':'5.6 Luna','gpt56_terra':'5.6 Terra'}
for mod in mods:
 for e in ['none','low','medium','high','xhigh','max','ultra']:
  p=mod+'_'+e
  if (p,'direct') not in gb or not gb[p,'direct']['profile_complete']:continue
  a=[gb[p,m] for m in ['direct','python_fresh','set']];marker=r'$^\dagger$' if not a[0]['profile_complete'] else ''
  lines.append(names[mod]+' & '+e+marker+' & '+' & '.join(f"{r['exact']}/{r['n']}" for r in a)+r' \\')
 if mod!=mods[-1]:lines.append(r'\midrule')
lines+=[r'\bottomrule',r'\end{tabular}'];put('grid', '\n'.join(lines))
# Failure grid, useful for distinguishing service / output errors.
lines=[r'\begin{tabular}{llrrrrrrrrr}',r'\toprule',r'&&\multicolumn{3}{c}{Direct} & \multicolumn{3}{c}{Set-Py} & \multicolumn{3}{c}{Set} \\',r'Model & Effort & U & R & O & U & R & O & U & R & O \\',r'\midrule']
for mod in mods:
 for e in ['none','low','medium','high','xhigh','max','ultra']:
  p=mod+'_'+e
  if (p,'direct') not in gb or not gb[p,'direct']['profile_complete']:continue
  rs=[gb[p,m] for m in ['direct','python_fresh','set']];mark=r'$^\dagger$' if not rs[0]['profile_complete'] else ''
  vals=[str(v) for r in rs for v in [r['unsafe'],r['false_refusal'],r['n']-r['exact']-r['unsafe']-r['false_refusal']]]
  lines.append(names[mod]+' & '+e+mark+' & '+' & '.join(vals)+r' \\')
 if mod!=mods[-1]:lines.append(r'\midrule')
lines+=[r'\bottomrule',r'\end{tabular}'];put('grid_errors','\n'.join(lines))
# Current language display; the original 60-case, three-method cohort is archived.
lb=display_language(R);lines=[r'\begin{tabular}{llrrr}',r'\toprule',r'Model & Language & Direct & Set-Py & Set \\',r'\midrule']
for p,lab in [('ds_flash_low','DS low'),('ds_flash_high','DS high'),('ds_flash_max','DS max'),('astra_max','Astra max')]:
 for language,ln in [('zh','Chinese'),('en','English')]:
  rs=[lb.get((p,m,language)) for m in ['direct','python_fresh','set']];mark=''
  lines.append(f'{lab}{mark} & {ln} & '+' & '.join(f"{r['exact']}/{r['n']}" if r else '--' for r in rs)+r' \\')
 if p!='astra_max':lines.append(r'\midrule')
lines+=[r'\bottomrule',r'\end{tabular}'];put('language','\n'.join(lines))
# Preserve the original language-control tables verbatim as a distinct cohort.
archive=R/'archive/external_results_preupdate_20261010T203356Z/tex/tables'
for name in ['language','language_errors']:
 if (archive/(name+'.tex')).exists():put(name+'_archived',(archive/(name+'.tex')).read_text())
lines=[r'\begin{tabular}{llrrrrrrr}',r'\toprule',r'&&&\multicolumn{3}{c}{Direct}&\multicolumn{3}{c}{Set}\\',r'Model & Language & $n$ & U & R & O & U & R & O \\',r'\midrule']
for p,lab in [('ds_flash_low','DS low'),('ds_flash_high','DS high'),('ds_flash_max','DS max'),('astra_max','Astra max')]:
 for l,ln in [('zh','Chinese'),('en','English')]:
  rs=[lb[p,a,l] for a in ('direct','set')]
  vals=[str(v) for r in rs for v in [r['unsafe'],r['false_refusal'],r['n']-r['exact']-r['unsafe']-r['false_refusal']]]
  lines.append(marked(lab,p)+f" & {ln} & {rs[0]['n']} & "+' & '.join(vals)+r' \\')
 if p!='astra_max':lines.append(r'\midrule')
lines += [r'\bottomrule',r'\end{tabular}'];put('language_errors','\n'.join(lines))
# Primary latency and tokens, no assumption of equal visibility.
lines=[r'\begin{tabular}{llrrr}',r'\toprule',r'Model & Method & Input & Output & Seconds \\',r'\midrule']
for p,lab in zip(profiles,['DS low','DS high','Astra max']):
 for i,m in enumerate(['direct','python_fresh','set']):
  r=by[p,m];lines.append(f"{lab if i==0 else ''} & "+{'direct':'Direct','python_fresh':'Set-Py','set':'Set'}[m]+f" & {r['input_tokens']['mean']/1000:.1f}k & {r['output_tokens']['mean']/1000:.1f}k & {r['seconds']['median']:.1f} "+r'\\')
 if p!=profiles[-1]:lines.append(r'\midrule')
lines+=[r'\bottomrule',r'\end{tabular}'];put('costs','\n'.join(lines))
# Cluster intervals.
lines=[r'\begin{tabular}{llrr}',r'\toprule',r'Control & Metric & Difference & 95\% interval \\',r'\midrule']
for r in load('paired_cluster_intervals'):
 if r['profile']!='deepseek_pooled' or r['baseline']!='direct':continue
 lo,hi=r['cluster_bootstrap_95_interval_pp'];lines.append(('Direct' if r['baseline']=='direct' else 'Set-Py')+' & '+('Exact' if r['metric']=='exact' else 'Unsafe')+f" & {r['delta_percentage_points']:+.2f} & [{lo:+.2f}, {hi:+.2f}] "+r'\\')
lines+=[r'\bottomrule',r'\end{tabular}'];put('intervals','\n'.join(lines))

# Consolidated appendix tables supersede repeated presentation fragments.
from make_appendix_tables import build as build_compact_appendix
from execution_reporting import build as build_execution_controls
from prompt_control_reporting import build as build_prompt_controls
build_execution_controls(R)
build_compact_appendix(R, T)
build_prompt_controls(R, T)
