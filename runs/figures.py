"""Report figures as dependency-free SVG (Hermes venv has no matplotlib).

Reads runs/mg.jsonl, runs/push.jsonl and writes report/fig*.svg.
Re-run after new data lands; deterministic output.
"""
from __future__ import annotations

import json
import statistics as st
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.analyze import vec, pair_corrs, pearson

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"
REPORT = ROOT / "report"
REPORT.mkdir(exist_ok=True)

W, H = 760, 340
MARGIN = dict(l=70, r=20, t=36, b=64)
INK = "#222"; GRID = "#ccc"; ACC = "#b03030"; BLU = "#2b5f9e"; GRN = "#2e7d32"; GRY = "#777"


def load_scen():
    scen = {s["id"]: s for s in json.loads((RUNS / "scenarios.json").read_text())}
    scen.update({s["id"]: s for s in json.loads((RUNS / "scenarios_hard.json").read_text())})
    return scen


def panels_from(recs, scen):
    panels = defaultdict(lambda: defaultdict(dict))
    for r in recs:
        panels[(r["arm"], r["cond"], r["seed"], r["scenario_id"])][r["stage"]][r["agent_idx"]] = r
    return panels


def rho_by(panels, scen, arm, cond, stage):
    rhos = []
    for (a, c, s, sid), stages in panels.items():
        if (a, c) != (arm, cond):
            continue
        sus = [x["name"] for x in scen[sid]["suspects"]]
        ag = {i: v for i, r in stages.get(stage, {}).items() if (v := vec(r, sus)) is not None}
        if len(ag) < 2:
            continue
        cs = pair_corrs(ag)
        if cs:
            rhos.append(sum(cs) / len(cs))
    return st.mean(rhos) if rhos else None, len(rhos)


def svg_bars(path, title, groups, ymax, ylabel, series_names, series_colors):
    """groups: list of (group_label, [values per series])"""
    inner_w, inner_h = W - MARGIN["l"] - MARGIN["r"], H - MARGIN["t"] - MARGIN["b"]
    nb = sum(len(vals) for _, vals in groups)
    bw = inner_w / (nb + len(groups))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif">']
    parts.append(f'<text x="{W/2}" y="20" text-anchor="middle" font-size="15" font-weight="bold">{title}</text>')
    for i in range(5):
        y = MARGIN["t"] + inner_h * i / 4
        v = ymax * (1 - i / 4)
        parts.append(f'<line x1="{MARGIN["l"]}" y1="{y:.1f}" x2="{W-MARGIN["r"]}" y2="{y:.1f}" stroke="{GRID}" stroke-width="0.5"/>')
        parts.append(f'<text x="{MARGIN["l"]-6}" y="{y+4:.1f}" text-anchor="end" font-size="10" fill="{GRY}">{v:.2f}</text>')
    x = MARGIN["l"] + bw / 2
    for gi, (label, vals) in enumerate(groups):
        for vi, v in enumerate(vals):
            if v is None:
                x += bw
                continue
            bh = inner_h * v / ymax
            color = series_colors[vi % len(series_colors)]
            parts.append(f'<rect x="{x:.1f}" y="{MARGIN["t"]+inner_h-bh:.1f}" width="{bw*0.8:.1f}" height="{bh:.1f}" fill="{color}"/>')
            parts.append(f'<text x="{x+bw*0.4:.1f}" y="{MARGIN["t"]+inner_h-bh-4:.1f}" text-anchor="middle" font-size="9.5">{v:.2f}</text>')
            x += bw
        parts.append(f'<text x="{x - bw*len(vals)/2 - bw*0.1:.1f}" y="{H-MARGIN["b"]+18}" text-anchor="middle" font-size="11">{label}</text>')
        x += bw * 0.6
    lx = MARGIN["l"] + 10
    for name, color in zip(series_names, series_colors):
        parts.append(f'<rect x="{lx}" y="{H-16}" width="10" height="10" fill="{color}"/>')
        parts.append(f'<text x="{lx+14}" y="{H-7}" font-size="10">{name}</text>')
        lx += 14 + len(name) * 6 + 24
    parts.append(f'<text x="14" y="{H/2}" transform="rotate(-90 14 {H/2})" font-size="10" fill="{GRY}" text-anchor="middle">{ylabel}</text>')
    parts.append("</svg>")
    (REPORT / path).write_text("".join(parts))


def main():
    scen = load_scen()
    mg = [json.loads(l) for l in (RUNS / "mg.jsonl").read_text().splitlines()]
    push = [json.loads(l) for l in (RUNS / "push.jsonl").read_text().splitlines()]
    pushj_path = RUNS / "pushJ.jsonl"
    pushj = [json.loads(l) for l in pushj_path.read_text().splitlines()] if pushj_path.exists() else []
    pm = panels_from(mg, scen)
    pp = panels_from(push, scen)
    pj = panels_from(pushj, scen)

    n5 = lambda rho: 5 / (1 + 4 * rho) if rho is not None else None

    # fig1: N_eff initial vs final across arms/conditions (mixed arms on v1 bank)
    cells = [("M6/C1 (no discourse)", ("M6", "C1", pm)), ("M6/C2 (free)", ("M6", "C2", pm)),
             ("M6/C3 (locked read)", ("M6", "C3", pm)), ("M6DA/C2 (devil's adv.)", ("M6DA", "C2", pp))]
    if pj:
        cells.append(("M6J/C2 (evidence jigsaw)", ("M6J", "C2", pj)))
    groups = []
    for label, (arm, cond, pan) in cells:
        ri, _ = rho_by(pan, scen, arm, cond, "initial")
        rf, _ = (rho_by(pan, scen, arm, cond, "final") if cond != "C1" else (None, 0))
        groups.append((label, [n5(ri), n5(rf) if rf is not None else None]))
    svg_bars("fig1_n_eff.svg", "Effective number of independent forecasters (of 5-6): initial vs final",
             groups, 3.0, "N_eff", ["initial", "final"], [BLU, ACC])

    # fig2: same-weights premium across datasets
    towns_gap, towns_lo, towns_hi = 0.078, None, None
    v1_gap, v1_lo, v1_hi = 0.0816, 0.0744, 0.0889
    # recompute hard-bank DH gap fresh (verified source)
    same, cross = [], []
    for (a, c, s, sid), stages in pp.items():
        if a != "DH" or c != "C1":
            continue
        sus = [x["name"] for x in scen[sid]["suspects"]]
        ag = {i: (r["model"], v) for i, r in stages.get("initial", {}).items() if (v := vec(r, sus)) is not None}
        for i, j in combinations(sorted(ag), 2):
            cc = pearson(ag[i][1], ag[j][1])
            if cc is None: continue
            (same if ag[i][0] == ag[j][0] else cross).append(cc)
    hard_gap = st.mean(same) - st.mean(cross) if same and cross else None
    svg_bars("fig2_gap.svg", "Same-weights agreement premium (same-model rho − cross-family rho)",
             [("Towns (observational)", [towns_gap]),
              ("Panels v1 (uncertainty)", [v1_gap]),
              ("Panels hard (ceiling)", [hard_gap])],
             0.12, "+gap", ["gap"], [BLU])

    # fig3: naive collusion detector flag rates
    fp_metrics = json.loads((RUNS / "collusion_fp_metrics.json").read_text())
    thresholds = [0.5, 0.8, 0.9, 0.95, 0.99]
    # recompute flag rates from fp script values (stored means) — use recorded curve:
    rates_same = [1.0, 1.0, 1.0, 1.0, 1.0]
    rates_cross = [0.9672, 0.8360, 0.7921, 0.7629, 0.6668]
    svg_bars("fig3_collusion_fp.svg", "Naive agreement-as-collusion flag rate on honest panels",
             [(f"ρ>{t}", [1.0, c]) for t, c in zip(thresholds, rates_cross)],
             1.15, "flag rate", ["same-model copies", "different families"], [ACC, GRY])

    # fig4: remedy arc on v1 bank (initial -> final rho)
    groups = []
    for label, (arm, cond, pan) in [("M6/C2 free", ("M6", "C2", pm)),
                                    ("M6/C3 lock", ("M6", "C3", pm)),
                                    ("M6DA dissent", ("M6DA", "C2", pp))] + (
                                    [("M6J jigsaw", ("M6J", "C2", pj))] if pj else []):
        ri, _ = rho_by(pan, scen, arm, cond, "initial")
        rf, _ = rho_by(pan, scen, arm, cond, "final")
        groups.append((label, [ri, rf]))
    svg_bars("fig4_remedy.svg", "Pairwise belief agreement before vs after discussion (remedy candidates)",
             groups, 1.15, "rho", ["initial", "final"], [BLU, ACC])

    print("figs written:", [p.name for p in REPORT.glob("fig*.svg")])
    if pj:
        ri, n = rho_by(pj, scen, "M6J", "C1", "initial")
        print(f"M6J C1 initial rho so far: {ri} (n={n})")


if __name__ == "__main__":
    main()
