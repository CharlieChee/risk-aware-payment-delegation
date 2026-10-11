"""Risk-aware intent and decisions, above any particular executable representation.

Original vector artwork. The lower row distinguishes executable realization
from offline semantic evaluation. No empirical result or statistical calibration
guarantee is implied by this conceptual illustration.
"""
from pathlib import Path
import json
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon
INK='#203647';MUTED='#637583';LINE='#D8E2E8'
BLUE='#36659A';PURPLE='#745D98';TEAL='#087D78';AMBER='#A87424'


def draw_architecture():
    fig=plt.figure(figsize=(7.15,3.03),facecolor='white')
    ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,7.15),ylim=(0,3.03),aspect='equal');ax.axis('off')
    def text(x,y,s,size=8.2,color=INK,weight='normal',**kw):
        return ax.text(x,y,s,fontsize=size,color=color,fontweight=weight,va='center',**kw)
    def box(x,y,w,h,fc='white',ec=LINE,radius=.065,lw=.7,**kw):
        p=FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={radius}',facecolor=fc,edgecolor=ec,linewidth=lw,**kw)
        ax.add_patch(p);return p
    def line(points,color=LINE,lw=.8,**kw):
        xx,yy=zip(*points);ax.plot(xx,yy,color=color,lw=lw,solid_capstyle='round',**kw)
    def arrow(a,b,color=MUTED,lw=1,**kw):
        ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=8,linewidth=lw,color=color,shrinkA=0,shrinkB=0,**kw))
    def stage(x,n,label,color):
        ax.add_patch(Circle((x+.085,2.87),.085,facecolor=color,edgecolor='none'))
        text(x+.085,2.87,n,7.4,'white','bold',ha='center');text(x+.23,2.87,label,9.3,INK,'bold')
    def check(x,y,color=TEAL):
        line([(x-.027,y),(x-.004,y-.025),(x+.043,y+.033)],color,1.0)
    stage(.03,'1','Request & context',BLUE)
    stage(1.86,'2','Structure risk-aware intent',PURPLE)
    stage(5.58,'3','Act or abstain',TEAL)
    line([(.03,2.69),(7.11,2.69)],LINE,.75)
    box(.03,1.20,1.43,1.34,'#F2F6FB','#C8D6E6')
    text(.16,2.35,'COMPLEX PAYMENT',7.2,BLUE,'bold')
    text(.16,1.90,'Interacting conditions\nUnequal costs\nPossible ambiguity',8.0,linespacing=1.65)
    ax.add_patch(Polygon([(.22,1.20),(.35,1.20),(.22,1.10)],closed=True,facecolor='#F2F6FB',edgecolor='#C8D6E6',linewidth=.7))
    line([(.223,1.20),(.346,1.20)],'#F2F6FB',1.15)
    box(.03,.84,1.43,.27,'#FCFAF5','#E4DCC8',.06)
    text(.745,.975,'No follow-up available',7.5,AMBER,'bold',ha='center')
    line([(1.47,1.78),(1.56,1.78),(1.56,1.52)],BLUE,.9)
    line([(1.47,.975),(1.56,.975),(1.56,1.52)],AMBER,.9)
    arrow((1.56,1.52),(1.83,1.52),PURPLE,1.05)
    text(1.68,1.72,'LLM',7.3,PURPLE,'bold',ha='center')
    # Semantic model: uncertainty, authorized consequences, and utility.
    box(1.86,.98,3.48,1.56,'#FCFDFE','#BDCDE0',.09,.85)
    box(1.86,2.20,3.48,.34,'#EDF1F8','#BDCDE0',.09,.85)
    text(3.60,2.37,'RAC-inspired decision model',9.8,PURPLE,'bold',ha='center')
    line([(3.03,1.10),(3.03,2.08)],LINE,.7);line([(4.18,1.10),(4.18,2.08)],LINE,.7)
    centers=[2.44,3.60,4.76]
    cx=centers[0]
    ax.add_patch(Circle((cx-.085,1.995),.027,facecolor=BLUE,edgecolor='none'))
    for yy in [1.92,2.07]:
        line([(cx-.06,1.995),(cx+.055,yy)],BLUE,.9)
        ax.add_patch(Circle((cx+.08,yy),.027,facecolor='white',edgecolor=BLUE,lw=.8))
    cx=centers[1]
    shield=[(cx-.095,2.065),(cx,2.095),(cx+.095,2.065),(cx+.075,1.97),(cx,1.915),(cx-.075,1.97)]
    ax.add_patch(Polygon(shield,closed=True,facecolor='#FAF1DA',edgecolor=AMBER,lw=.85));check(cx,2.008,AMBER)
    cx=centers[2]
    for offset,height in [(-.085,.075),(0,.12),(.085,.18)]:box(cx+offset-.025,1.92,.05,height,'#B4DDD4',TEAL,.015,.65)
    columns=[('Uncertainty',r'$\Theta(x),\ \ell_\theta$','Relevant states\nand consequences',BLUE),('Risk boundaries',r'$H_\theta,\ \mathcal{A}_\theta$','Hard requirements\nand allowed exposure',AMBER),('User value',r'$u_\theta$','Preferences and\nstate-wise utility',TEAL)]
    for cx,(title,formula,caption,color) in zip(centers,columns):
        text(cx,1.77,title,8.8,color,'bold',ha='center');text(cx,1.49,formula,10.8,color,ha='center')
        text(cx,1.18,caption,7.5,MUTED,ha='center',linespacing=1.35)
    text(3.60,.82,'Authorization is fixed before optimization.',7.7,AMBER,ha='center')
    arrow((5.35,1.77),(5.57,1.77),TEAL,1.05)
    box(5.60,.98,1.51,1.56,'#F2F9F7','#ADCDC5',.09,.85)
    text(6.355,2.35,'GUARANTEED VALUE',7.15,TEAL,'bold',ha='center')
    text(6.355,2.055,r'$\max_z\;\inf_\theta\,u_\theta(z)$',11.8,TEAL,ha='center')
    text(6.355,1.745,'within authorized limits',7.5,INK,ha='center')
    box(5.73,1.35,1.25,.255,'#DDEFE8','#B9D9CF',.045,.5)
    text(6.355,1.477,'Choose if value > 0',7.8,TEAL,'bold',ha='center')
    box(5.73,1.07,1.25,.22,'white','#CDD7DD',.04,.5)
    text(6.355,1.18,'Otherwise abstain',7.7,MUTED,ha='center')
    text(6.355,.82,'Outside option: value = 0',7.3,MUTED,ha='center')
    # Implementation and evaluation have distinct roles in the framework.
    line([(.03,.68),(7.11,.68)],LINE,.75)
    text(.03,.555,'REALIZATION AND EVALUATION',7.3,MUTED,'bold')
    text(7.11,.555,'Current decision + admitted domain',7.3,MUTED,ha='right')
    routes=[(.03,1.66,'Compile intent','state-wise executable rules','#F7F3FA',PURPLE),(1.82,1.66,'Check exposure','hard + risk predicates','#F1F5FA',BLUE),(3.61,1.66,'Select or refuse','guaranteed user value','#E8F4F0',TEAL),(5.40,1.71,'Audit rule domain','offline reference checks','#FCFAF5',AMBER)]
    for x,w,title,desc,fc,color in routes:
        box(x,.20,w,.235,fc,LINE,.045,.6)
        text(x+w/2,.317,title,8.1,color,'bold',ha='center')
        text(x+w/2,.085,desc,7.1,MUTED,ha='center')
    return fig

DESIGN_REFERENCES=[dict(url='https://aclanthology.org/2026.acl-long.48/',figure=1,role='Grouped process flow and visible intermediate representations.'),dict(url='https://aclanthology.org/2025.acl-long.242/',figure=1,role='Natural language, formal representation, and decision separated visually.'),dict(url='https://aclanthology.org/2026.acl-long.1273/',figure=1,role='Financial decision context and an explicit abstention outcome.')]

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1];(root/'figures').mkdir(exist_ok=True)
    with plt.rc_context({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','mathtext.fontset':'dejavusans'}):
        fig=draw_architecture()
        for ext in ['pdf','svg','png']:fig.savefig(root/'figures'/f'01_contract_architecture.{ext}',dpi=400,bbox_inches='tight',pad_inches=.065)
        plt.close(fig)
    (root/'figures/figure1_design_notes.json').write_text(json.dumps(dict(purpose='Risk-aware payment delegation: semantic model, executable decision, and offline rule-domain evaluation.',original_artwork=True,illustrative_not_empirical=True,mathematical_change=False,experimental_change=False,implementation='Matplotlib vector geometry; editable SVG text.',references=DESIGN_REFERENCES),indent=2)+'\n')
