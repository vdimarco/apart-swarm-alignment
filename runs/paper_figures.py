"""Figures for the audited report. Run after: python -m src.audit_stats ; python -m tests.test_analyze
Usage: python runs/paper_figures.py OUTDIR"""
import json, sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

RUNS = Path(__file__).resolve().parent
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
A = json.loads((RUNS / "audit_stats.json").read_text())
C = {"pool": "#2f6f8f", "delib": "#b3263a", "grey": "#8a93a3", "light": "#9cc3d6"}
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e3e6eb", "axes.axisbelow": True})

# Figure 1: the measure. Simulation (from tests/test_analyze.py) and real panels.
f, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.5), gridspec_kw={"width_ratios": [1, 1.25]})
labs = ["Independent,\ncorrect", "Copies"]
a1.bar([0 - .18, 1 - .18], [1.02, 1.00], .36, color=C["delib"], label="Full vectors (original)")
a1.bar([0 + .18, 1 + .18], [5.86, 1.00], .36, color=C["pool"], label="Errors only (audit)")
a1.set_xticks([0, 1], labs); a1.set_ylabel("N_eff (of 6)"); a1.set_ylim(0, 8.5); a1.set_yticks([0, 2, 4, 6]); a1.set_title("Simulated panels", fontsize=9)
a1.legend(frameon=False, fontsize=7.5, loc="upper right")
X = {d["arm"]: d for d in json.loads((RUNS / "across_case.json").read_text())}
arms = [("mg/M6/C2", "Free\ndiscussion"), ("mg/M6/C3", "Locked\nframing"), ("push_da/M6DA/C2", "Devil's\nadvocate"), ("pushJ/M6J/C2", "Jigsaw")]
xs = range(len(arms))
a2.bar([x - .18 for x in xs], [X[k]["r_initial"] for k, _ in arms], .36, color=C["light"], label="Before talk")
a2.bar([x + .18 for x in xs], [X[k]["r_final"] for k, _ in arms], .36, color=C["pool"], label="After talk")
for x, (k, _) in zip(xs, arms):
    a2.text(x, 0.84, f"{X[k]['pairs']} pairs", ha="center", fontsize=7, color="#555")
a2.set_xticks(list(xs), [l for _, l in arms]); a2.set_ylim(0, 1.15); a2.set_yticks([0, .2, .4, .6, .8, 1.0]); a2.set_ylabel("Error correlation across cases (r)")
a2.set_title("Real panels, same model pairs", fontsize=9); a2.legend(frameon=False, fontsize=7.5, loc="upper left", ncol=2)
f.tight_layout(); f.savefig(out / "fig1_measure.png", dpi=220)

# Figure 2: pooled locked reads vs deliberated vote, and individual accuracy.
f, ax = plt.subplots(figsize=(6.6, 2.5))
arms = [("mg/M6/C2", "Full info,\nfree discussion"), ("mg/M6/C3", "Full info,\nlocked framing"),
        ("push_da/M6DA/C2", "Full info,\ndevil's advocate"), ("pushJ/M6J/C2", "Split evidence\n(jigsaw)")]
w = .2
for x, (k, _) in enumerate(arms):
    d = A[k]; n = d["panels"]
    vals = [d["individual_accuracy_initial"], d["individual_accuracy_final"], d["pooled_locked_reads_correct"] / n, d["deliberated_final_correct"] / n]
    cols = [C["light"], C["grey"], C["pool"], C["delib"]]
    for j, (v, c) in enumerate(zip(vals, cols)):
        ax.bar(x + (j - 1.5) * w, v * 100, w, color=c)
ax.set_xticks(range(len(arms)), [l for _, l in arms]); ax.set_ylim(50, 104); ax.set_ylabel("Correct (%)")
from matplotlib.patches import Patch
ax.legend([Patch(color=c) for c in [C["light"], C["grey"], C["pool"], C["delib"]]],
          ["Individual, first read", "Individual, after talk", "Panel: pooled first reads", "Panel: after talk"],
          frameon=False, fontsize=7.5, ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.0))
f.tight_layout(); f.savefig(out / "fig2_pool_vs_talk.png", dpi=220)
print("figures in", out)
