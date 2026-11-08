"""Across-case error correlation (the quantity behind N_eff = n / (1 + (n-1) r)).
For each pair of models in a panel, correlate their errors (1 - p(culprit)) across cases, before and after
discussion, on the same pairs. Interval: bootstrap over cases. Run: python -m src.across_case"""
import json, itertools, random
from collections import defaultdict
from pathlib import Path
import numpy as np
RUNS = Path(__file__).resolve().parent.parent / "runs"

def errors(label, bank, arm, cond):
    sc = {s["id"]: s for s in json.loads((RUNS / bank).read_text())}
    e = {"initial": defaultdict(dict), "final": defaultdict(dict)}
    for l in (RUNS / f"{label}.jsonl").read_text().splitlines():
        x = json.loads(l)
        if x["arm"] == arm and x["cond"] == cond and x["stage"] in e and x.get("probs"):
            s = sc[x["scenario_id"]]
            e[x["stage"]][x["agent_idx"]][(x["seed"], x["scenario_id"])] = 1 - x["probs"].get(s["ground_truth"], 0.0)
    return e

def corr(a, b, keys):
    x = np.array([a[k] for k in keys]); y = np.array([b[k] for k in keys])
    return np.corrcoef(x, y)[0, 1] if x.std() > 0 and y.std() > 0 else None

def run(label, bank, arm, cond, reps=2000):
    e = errors(label, bank, arm, cond)
    ag = sorted(set(e["initial"]) & set(e["final"]))
    keys = sorted(set().union(*[set(e[s][a]) for s in e for a in ag]))
    def stat(ks):
        pi, pf = [], []
        for a, b in itertools.combinations(ag, 2):
            kk = [k for k in ks if all(k in e[s][z] for s in e for z in (a, b))]  # cases this pair answered in both stages
            ri, rf = corr(e["initial"][a], e["initial"][b], kk), corr(e["final"][a], e["final"][b], kk)
            if ri is not None and rf is not None:
                pi.append(ri); pf.append(rf)
        return (np.mean(pi), np.mean(pf), len(pi)) if pi else (None, None, 0)
    ri, rf, npairs = stat(keys)
    rng = random.Random(0); cases = sorted({k[1] for k in keys}); diffs = []
    for _ in range(reps):
        pick = rng.choices(cases, k=len(cases)); ks = [k for c in pick for k in keys if k[1] == c]
        a, b, n = stat(ks)
        if n: diffs.append(b - a)
    if not npairs:
        return dict(arm=f"{label}/{arm}/{cond}", pairs=0, note="no pair has error variance in both stages")
    diffs.sort()
    neff = lambda r: 6 / (1 + 5 * max(r, 0))
    return dict(arm=f"{label}/{arm}/{cond}", cases=len(keys), pairs=npairs, r_initial=round(ri, 3), r_final=round(rf, 3),
                neff_initial=round(neff(ri), 2), neff_final=round(neff(rf), 2),
                diff=round(rf - ri, 3), ci95=[round(diffs[int(.025 * len(diffs))], 3), round(diffs[int(.975 * len(diffs))], 3)])

if __name__ == "__main__":
    out = [run("mg", "scenarios.json", "M6", "C2"), run("mg", "scenarios.json", "M6", "C3"),
           run("push_da", "scenarios.json", "M6DA", "C2"), run("pushJ", "scenarios.json", "M6J", "C2")]
    (RUNS / "across_case.json").write_text(json.dumps(out, indent=2))
    for o in out: print(o)
