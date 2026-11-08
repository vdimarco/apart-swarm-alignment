"""Build the audit figures from saved checks. Uses no model APIs."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from src.scenarios import clue_partition,clue_partition_balanced

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"report/assets";OUT.mkdir(exist_ok=True)
r=json.loads((ROOT/"review/verified-results.json").read_text())
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.titlesize":12,
                     "axes.labelsize":10,"axes.spines.top":False,"axes.spines.right":False,
                     "axes.edgecolor":"#b7bec5","text.color":"#17212b","axes.labelcolor":"#17212b",
                     "xtick.color":"#46525e","ytick.color":"#46525e","savefig.facecolor":"white"})

fig,(ax,bx)=plt.subplots(1,2,figsize=(10.5,3.7),gridspec_kw={"width_ratios":[1,1.25]})
coefs=[.22,.35,.49,.63,.78,.92]
for i,a in enumerate(coefs):
    probs=np.full(6,(1-a)/6);probs[0]+=a
    ax.plot(range(6),probs,marker="o",markersize=3,lw=1.4,color=plt.cm.Blues(.32+i*.12))
ax.set(xticks=range(6),xticklabels=["True","B","C","D","E","F"],ylim=(0,1),ylabel="Assigned probability",xlabel="Candidate answer")
ax.set_title("A  All six profiles point to the truth",loc="left",pad=15,fontweight="bold")
ax.text(.98,.86,"Profile correlation = 1.000",transform=ax.transAxes,ha="right",fontsize=10)
ax.grid(axis="y",color="#e9edf0",lw=.7);ax.set_axisbelow(True)
values=[1,r["metric_control"]["empirical_variance_equivalent_count"]]
bx.barh([1,0],values,height=.40,color=["#b34a3c","#1d6688"])
for y,value in zip([1,0],values):bx.text(value+.12,y,f"{value:.2f}",va="center",weight="bold",fontsize=12)
bx.set(yticks=[1,0],yticklabels=["Original formula","Variance measured"],xlim=(0,7),ylim=(-.7,1.8),xlabel="Number of estimates",xticks=[0,1,2,3,4,5,6])
bx.axvline(6,color="#17212b",ls=(0,(3,3)),lw=1)
bx.text(6,1.65,"Theory: 6",ha="center",fontsize=9)
bx.set_title("B  Averaging still reduces variance",loc="left",pad=15,fontweight="bold")
bx.grid(axis="x",color="#e9edf0",lw=.7);bx.set_axisbelow(True);bx.spines['left'].set_visible(False);bx.tick_params(axis='y',length=0)
fig.subplots_adjust(left=.07,right=.97,bottom=.20,top=.83,wspace=.60)
fig.text(.07,.025,"Control: independent coefficients; 50,000 simulated panels. Left: six example profiles from the same construction.",fontsize=8,color="#596675")
for suffix in ("png","svg"):fig.savefig(OUT/f"metric-control.{suffix}",dpi=190)
plt.close(fig)

fig,axes=plt.subplots(1,2,figsize=(10.5,3.8))
for ax,parts,title,subtitle in zip(axes,[clue_partition(4,6,0),clue_partition_balanced(4,6,0)],
        ["A  Original allocation","B  New exploratory allocation"],
        ["2 distinct packets","6 distinct packets; no model results yet"]):
    a=np.array([[int(c in packet) for c in range(4)] for packet in parts])
    from matplotlib.colors import ListedColormap
    ax.imshow(a,cmap=ListedColormap(["#eef1f3","#276c8e"]),vmin=0,vmax=1,aspect="auto")
    ax.set(xticks=range(4),xticklabels=["Clue A","Clue B","Clue C","Clue D"],yticks=range(6),yticklabels=[f"Agent {i+1}" for i in range(6)])
    ax.set_xticks(np.arange(-.5,4,1),minor=True);ax.set_yticks(np.arange(-.5,6,1),minor=True)
    ax.grid(which="minor",color="white",linewidth=4);ax.tick_params(which="both",length=0)
    for row in range(6):
        for col in range(4):
            if a[row,col]:ax.text(col,row,"Seen",color="white",ha="center",va="center",fontsize=9)
    for spine in ax.spines.values():spine.set_visible(False)
    ax.set_title(title,loc="left",pad=31,fontweight="bold")
    ax.text(0,1.035,subtitle,transform=ax.transAxes,fontsize=10)
fig.subplots_adjust(left=.09,right=.98,bottom=.17,top=.78,wspace=.30)
fig.text(.09,.025,"Four-clue example. Each allocation retains all four clues and gives each clue to three agents.",fontsize=8,color="#596675")
for suffix in ("png","svg"):fig.savefig(OUT/f"clue-allocation.{suffix}",dpi=190)
plt.close(fig)
print("Figures:",*[str(p.relative_to(ROOT)) for p in sorted(OUT.glob('*'))],sep="\n")
