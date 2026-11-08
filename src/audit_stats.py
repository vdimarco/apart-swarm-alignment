"""Audit statistics for 'Lock Before You Talk' (November 8, 2026). Reads the raw logs in runs/.

1. Pooled locked first reads vs deliberated final reads: panel accuracy, paired by panel (exact McNemar).
2. Individual accuracy before and after discussion (does pooling add information?).
3. Errors-only agreement before vs after discussion, on panels where both are defined.
4. Certainty: share of agents giving >= 0.99 to one suspect, before and after discussion.
5. What the 'same-model premium' compares: certainty of copies vs other models.
Run: python -m src.audit_stats
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from src.analyze import drop_truth, mean, n_eff, pearson

RUNS = Path(__file__).resolve().parent.parent / "runs"


def load(label: str, bank: str):
    recs = [json.loads(l) for l in (RUNS / f"{label}.jsonl").read_text().splitlines()]
    sc = {s["id"]: s for s in json.loads((RUNS / bank).read_text())}
    pan = defaultdict(lambda: defaultdict(dict))
    for r in recs:
        if r.get("probs"):
            pan[(r["arm"], r["cond"], r["seed"], r["scenario_id"])][r["stage"]][r["agent_idx"]] = r
    return pan, sc


def vecs(stage_map, names):
    return {i: [r["probs"].get(n, 0.0) for n in names] for i, r in stage_map.items()}


def top(v):
    return max(range(len(v)), key=lambda k: v[k])


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value from discordant counts b and c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def run(label: str, bank: str) -> dict:
    pan, sc = load(label, bank)
    out = {}
    by = defaultdict(list)
    for key, st in pan.items():
        arm, cond, seed, sid = key
        names = [s["name"] for s in sc[sid]["suspects"]]
        truth = names.index(sc[sid]["ground_truth"])
        if "initial" not in st or "final" not in st:
            continue
        vi, vf = vecs(st["initial"], names), vecs(st["final"], names)
        if len(vi) < 2 or len(vf) < 2:
            continue
        mi = [sum(v[k] for v in vi.values()) / len(vi) for k in range(len(names))]
        mf = [sum(v[k] for v in vf.values()) / len(vf) for k in range(len(names))]
        ind_i = mean([1.0 if top(v) == truth else 0.0 for v in vi.values()])
        ind_f = mean([1.0 if top(v) == truth else 0.0 for v in vf.values()])
        ei = mean([pearson(drop_truth(vi[a], truth), drop_truth(vi[b], truth)) for a, b in combinations(vi, 2)])
        ef = mean([pearson(drop_truth(vf[a], truth), drop_truth(vf[b], truth)) for a, b in combinations(vf, 2)])
        ci = mean([1.0 if max(v) >= 0.99 else 0.0 for v in vi.values()])
        cf = mean([1.0 if max(v) >= 0.99 else 0.0 for v in vf.values()])
        by[(arm, cond)].append(dict(pool=top(mi) == truth, final=top(mf) == truth, ind_i=ind_i, ind_f=ind_f,
                                    ei=ei, ef=ef, ci=ci, cf=cf, n=len(vi)))
    for (arm, cond), rows in sorted(by.items()):
        b = sum(r["pool"] and not r["final"] for r in rows)
        c = sum(r["final"] and not r["pool"] for r in rows)
        both = [r for r in rows if r["ei"] is not None and r["ef"] is not None]
        o = {
            "panels": len(rows),
            "pooled_locked_reads_correct": sum(r["pool"] for r in rows),
            "deliberated_final_correct": sum(r["final"] for r in rows),
            "pool_right_final_wrong": b, "final_right_pool_wrong": c, "mcnemar_p": mcnemar_exact(b, c),
            "individual_accuracy_initial": mean([r["ind_i"] for r in rows]),
            "individual_accuracy_final": mean([r["ind_f"] for r in rows]),
            "certain_agents_initial": mean([r["ci"] for r in rows]),
            "certain_agents_final": mean([r["cf"] for r in rows]),
            "errors_only_matched_panels": len(both),
            "errors_only_rho_initial": mean([r["ei"] for r in both]),
            "errors_only_rho_final": mean([r["ef"] for r in both]),
        }
        n = mean([r["n"] for r in rows]) or 6
        o["errors_only_neff_initial"] = n_eff(round(n), o["errors_only_rho_initial"])
        o["errors_only_neff_final"] = n_eff(round(n), o["errors_only_rho_final"])
        out[f"{label}/{arm}/{cond}"] = o
    return out


def premium_check() -> dict:
    """What the duplicate arm's same-vs-cross comparison measures."""
    pan, sc = load("mg", "scenarios.json")
    stats = defaultdict(lambda: [0, 0])
    for (arm, cond, seed, sid), st in pan.items():
        if arm not in ("D", "M6") or "initial" not in st:
            continue
        for r in st["initial"].values():
            stats[(arm, r["model"])][0] += max(r["probs"].values()) >= 0.99
            stats[(arm, r["model"])][1] += 1
    return {f"{a}/{m}": round(k / n, 3) for (a, m), (k, n) in sorted(stats.items())}


def main():
    res = {}
    for label, bank in [("mg", "scenarios.json"), ("pushJ", "scenarios.json"),
                        ("push_da", "scenarios.json"), ("push_hard", "scenarios_hard.json")]:
        res.update(run(label, bank))
    res["share_of_initial_reads_with_p>=0.99"] = premium_check()
    (RUNS / "audit_stats.json").write_text(json.dumps(res, indent=2))
    for k, v in res.items():
        print(k, json.dumps(v, default=lambda x: round(x, 3) if isinstance(x, float) else x))


if __name__ == "__main__":
    main()
