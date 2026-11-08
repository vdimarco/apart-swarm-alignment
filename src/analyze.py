"""Historical analysis for 'Lock Before You Talk' sweeps.

AUDIT NOTE (2026-11-08): its within-case probability correlation is a
descriptive similarity, not error dependence. The n_eff output must not be
interpreted as a count of independent agents. The pair bootstrap also ignores
case clusters. Retained for historical reproduction; use src.reanalyze for
the reviewed analysis. See report/audit/claim-audit.md.

Reads runs/<label>.jsonl + runs/scenarios.json, computes:
  - belief-vector pairwise correlation & effective N per arm/condition/stage
  - plurality-support band table (<0.75, [0.75,0.90), >=0.90) x correctness per condition
  - multiclass Brier of panel mean vs uniform baseline
  - same-family vs cross-family initial correlations in arm M (H3) + bootstrap CI
  - missingness (parse failures) per model/stage
Writes runs/<label>_metrics.json and prints report-ready tables.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"


def pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0 or vy == 0:
        return None
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return cov / math.sqrt(vx * vy)


def load(label: str, scenarios_file: str = "scenarios.json"):
    recs = [json.loads(l) for l in (RUNS / f"{label}.jsonl").read_text().splitlines()]
    scenarios = {s["id"]: s for s in json.loads((RUNS / scenarios_file).read_text())}
    return recs, scenarios


def panels(recs):
    """(arm, cond, seed, scenario_id) -> stage -> agent_idx -> record"""
    out = defaultdict(lambda: defaultdict(dict))
    for r in recs:
        out[(r["arm"], r["cond"], r["seed"], r["scenario_id"])][r["stage"]][r["agent_idx"]] = r
    return out


def vec(rec, suspects):
    return [rec["probs"][s] for s in suspects] if rec.get("probs") else None


def pair_corrs(vecs: dict[int, list[float]]) -> list[float]:
    out = []
    for i, j in combinations(sorted(vecs), 2):
        c = pearson(vecs[i], vecs[j])
        if c is not None:
            out.append(c)
    return out


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def n_eff(n: int, rho: float | None) -> float | None:
    """Effective independent count for a panel of size n with mean pairwise rho."""
    if rho is None:
        return None
    rho = min(max(rho, 0.0), 1.0)  # negative mean correlation is treated as independent
    return n / (1 + (n - 1) * rho)


def brier(probs: list[float], truth_idx: int) -> float:
    return sum((p - (1.0 if i == truth_idx else 0.0)) ** 2 for i, p in enumerate(probs))


def drop_truth(v: list[float], truth_idx: int | None) -> list[float]:
    """Belief vector over innocent suspects only. Agreeing on the right answer is not dependence:
    two agents that each solve the case alone both put mass on the culprit. What matters for
    aggregation is whether their errors (mass on innocents) line up."""
    return v if truth_idx is None else [p for k, p in enumerate(v) if k != truth_idx]


def plurality(agents: dict[int, list[float]], suspects: list[str]) -> dict[str, float]:
    """Tie-aware vote shares: an agent whose top probability is shared by k suspects gives 1/k to each."""
    votes: dict[str, float] = defaultdict(float)
    for v in agents.values():
        top = max(v)
        tied = [k for k, p in enumerate(v) if abs(p - top) < 1e-9]
        for k in tied:
            votes[suspects[k]] += 1 / len(tied)
    n = len(agents)
    return {k: c / n for k, c in votes.items()}


def cluster_boot_diff(groups: dict, reps: int, seed: int = 7):
    """95% CI for mean(same) - mean(cross), resampling whole panels (pairs in one panel are not independent)."""
    keys = [k for k, (a, b) in groups.items() if a or b]
    rng = random.Random(seed)
    out = []
    for _ in range(reps):
        pick = rng.choices(keys, k=len(keys))
        sa = [x for k in pick for x in groups[k][0]]
        cr = [x for k in pick for x in groups[k][1]]
        if sa and cr:
            out.append(sum(sa) / len(sa) - sum(cr) / len(cr))
    out.sort()
    return (out[int(0.025 * len(out))], out[int(0.975 * len(out))]) if out else None


def analyze(label: str, bootstrap_reps: int = 2000, scenarios_file: str = "scenarios.json"):
    recs, scenarios = load(label, scenarios_file)
    pan = panels(recs)
    # true panel size per (arm, cond) — arms differ (6 for M6/D/DH/M6DA/M6J/M6H, legacy 5)
    panel_sizes: dict = {}
    for (arm, cond, seed, sid), stages in pan.items():
        for stage_map in stages.values():
            panel_sizes[(arm, cond)] = max(panel_sizes.get((arm, cond), 0), len(stage_map))

    metrics: dict = {"label": label, "panels": len(pan)}

    # ---- missingness
    miss = defaultdict(int)
    tot = defaultdict(int)
    for r in recs:
        tot[(r["model"], r["stage"])] += 1
        if r["probs"] is None and r["stage"] in ("initial", "final"):
            miss[(r["model"], r["stage"])] += 1
    metrics["missingness"] = {
        f"{m}/{s}": {"n": tot[(m, s)], "parse_fail": miss.get((m, s), 0)}
        for (m, s) in sorted(tot)
    }

    # ---- per arm/cond/stage: correlations, n_eff, brier, band
    corr_by = defaultdict(list)
    corr_err_by = defaultdict(list)
    acc_by = defaultdict(list)  # panel-mean top pick correct, per arm/cond/stage
    brier_by = defaultdict(list)
    uniform_by = defaultdict(list)
    band = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # cond -> bucket -> [n, wrong]
    for (arm, cond, seed, sid), stages in pan.items():
        sc = scenarios[sid]
        suspects = [s["name"] for s in sc["suspects"]]
        truth = sc["ground_truth"]
        truth_idx = suspects.index(truth) if truth else None
        for stage in ("initial", "final"):
            agents = {
                i: v for i, r in stages.get(stage, {}).items()
                if (v := vec(r, suspects)) is not None
            }
            if len(agents) < 2:
                continue
            rho = mean(pair_corrs(agents))
            if rho is not None:
                corr_by[(arm, cond, stage)].append(rho)
            rho_err = mean(pair_corrs({i: drop_truth(v, truth_idx) for i, v in agents.items()}))
            if rho_err is not None:
                corr_err_by[(arm, cond, stage)].append(rho_err)
            if truth_idx is not None:
                n_ag = len(agents)
                mv = [sum(agents[i][k] for i in agents) / n_ag for k in range(len(suspects))]
                brier_by[(arm, cond, stage, sc["kind"])].append(brier(mv, truth_idx))
                uniform_by[(arm, cond, stage, sc["kind"])].append(brier([1 / len(suspects)] * len(suspects), truth_idx))
                acc_by[(arm, cond, stage)].append(1.0 if max(range(len(mv)), key=lambda k: mv[k]) == truth_idx else 0.0)
                shares = plurality(agents, suspects)
                top_sus, share = max(shares.items(), key=lambda kv: kv[1])
                bucket = "lt75" if share < 0.75 else ("75_90" if share < 0.90 else "ge90")
                cell = band[(cond, stage, sc["kind"])][bucket]
                cell[0] += 1
                cell[1] += 0 if top_sus == truth else 1

    metrics["correlation"] = {
        f"{a}/{c}/{s}": {"mean_rho": mean(v), "n_eff_panelsize": n_eff(panel_sizes.get((a, c), 5), mean(v)), "panels": len(v)}
        for (a, c, s), v in sorted(corr_by.items())
    }
    metrics["correlation_errors_only"] = {
        f"{a}/{c}/{s}": {"mean_rho": mean(v), "n_eff_panelsize": n_eff(panel_sizes.get((a, c), 5), mean(v)), "panels": len(v)}
        for (a, c, s), v in sorted(corr_err_by.items())
    }
    # "Lock before you talk" as a decision rule: the locked first reads ARE the vote.
    metrics["accuracy_panel_mean"] = {
        f"{a}/{c}/{s}": {"accuracy": mean(v), "panels": len(v)} for (a, c, s), v in sorted(acc_by.items())
    }
    metrics["brier"] = {
        f"{a}/{c}/{s}/{k}": {"panel_mean": mean(v), "uniform": mean(uniform_by[(a, c, s, k)]), "panels": len(v)}
        for (a, c, s, k), v in sorted(brier_by.items())
    }
    metrics["bands"] = {
        f"{c}/{s}/{k}": {b: {"n": n, "wrong": w, "wrong_rate": (w / n if n else None)}
                         for b, (n, w) in sorted(v.items())}
        for (c, s, k), v in sorted(band.items())
    }

    # ---- H3/H5: same- vs cross-family initial correlations in mixed arms
    # (any arm whose panel includes more than one distinct model)
    same_rhos, cross_rhos = [], []
    by_panel: dict = defaultdict(lambda: ([], []))
    same_err, cross_err = [], []
    by_panel_err: dict = defaultdict(lambda: ([], []))
    for (arm, cond, seed, sid), stages in pan.items():
        m_suspects = [s["name"] for s in scenarios[sid]["suspects"]]
        agents = {
            i: (r["model"], v)
            for i, r in stages.get("initial", {}).items()
            if (v := vec(r, m_suspects)) is not None
        }
        if len({m for m, _ in agents.values()}) < 2:
            continue
        for i, j in combinations(sorted(agents), 2):
            c = pearson(agents[i][1], agents[j][1])
            if c is None:
                continue
            same = agents[i][0] == agents[j][0]
            (same_rhos if same else cross_rhos).append(c)
            by_panel[(arm, cond, seed, sid)][0 if same else 1].append(c)
            t = scenarios[sid]["ground_truth"]
            ti = m_suspects.index(t) if t else None
            ce = pearson(drop_truth(agents[i][1], ti), drop_truth(agents[j][1], ti))
            if ce is not None:
                (same_err if same else cross_err).append(ce)
                by_panel_err[(arm, cond, seed, sid)][0 if same else 1].append(ce)
    obs = (mean(same_rhos) or 0) - (mean(cross_rhos) or 0) if (same_rhos and cross_rhos) else None
    ci = None
    if same_rhos and cross_rhos:
        rng = random.Random(7)
        boots = []
        for _ in range(bootstrap_reps):
            x1 = rng.choices(same_rhos, k=len(same_rhos))
            x2 = rng.choices(cross_rhos, k=len(cross_rhos))
            boots.append(sum(x1) / len(x1) - sum(x2) / len(x2))
        boots.sort()
        ci = (boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots))])
    metrics["h3_same_vs_cross_family"] = {
        "same_family": {"n": len(same_rhos), "mean": mean(same_rhos)},
        "cross_family": {"n": len(cross_rhos), "mean": mean(cross_rhos)},
        "diff": obs, "ci95_pairs_iid": ci,
        "ci95_cluster_by_panel": cluster_boot_diff(by_panel, bootstrap_reps),
        "errors_only": {
            "same_family": {"n": len(same_err), "mean": mean(same_err)},
            "cross_family": {"n": len(cross_err), "mean": mean(cross_err)},
            "diff": (mean(same_err) - mean(cross_err)) if (same_err and cross_err) else None,
            "ci95_cluster_by_panel": cluster_boot_diff(by_panel_err, bootstrap_reps),
        },
    }

    out = RUNS / f"{label}_metrics.json"
    out.write_text(json.dumps(metrics, indent=2))

    # ---------- console tables ----------
    print(f"metrics -> {out}")
    print("\n== effective N (5-agent panels) ==")
    print(f"{'arm/cond':12} {'stage':8} {'rho':>7} {'N_eff':>6} {'panels':>7}")
    for (a, c, s), v in sorted(corr_by.items()):
        m = mean(v)
        print(f"{a+'/'+c:12} {s:8} {m:7.3f} {n_eff(panel_sizes.get((a,c),5), m):6.2f} {len(v):7}")
    print("\n== effective N, errors only (truth suspect left out) ==")
    for (a, c, st), v in sorted(corr_err_by.items()):
        m = mean(v)
        print(f"{a+'/'+c:12} {st:8} {m:7.3f} {n_eff(panel_sizes.get((a,c),5), m):6.2f} {len(v):7}")
    print("\n== panel-mean accuracy (initial = locked first reads as the vote) ==")
    for (a, c, st), v in sorted(acc_by.items()):
        print(f"{a+'/'+c:12} {st:8} {mean(v):6.3f} {len(v):7}")
    print("\n== danger bands (non-placebo) ==")
    for (c, s, k), v in sorted(band.items()):
        for b, (n, w) in sorted(v.items()):
            print(f"{c}/{s}/{k:11} {b:6} n={n:4} wrong={w:4} rate={w/n if n else 0:.2f}")
    print("\n== H3 ==")
    h = metrics["h3_same_vs_cross_family"]
    print(f"same-family rho={h['same_family']['mean']}, cross-family rho={h['cross_family']['mean']}, "
          f"diff={h['diff']} ci95(pairs iid)={h['ci95_pairs_iid']} ci95(cluster)={h['ci95_cluster_by_panel']}")
    e = h["errors_only"]
    print(f"errors only: diff={e['diff']} ci95(cluster)={e['ci95_cluster_by_panel']}")
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="main")
    ap.add_argument("--scenarios", default="scenarios.json",
                    help="scenario bank file under runs/ (e.g. scenarios_hard.json)")
    args = ap.parse_args()
    analyze(args.label, scenarios_file=args.scenarios)


if __name__ == "__main__":
    main()
