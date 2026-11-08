"""Pooled first reads vs discussed vote using only agents with a valid read at BOTH stages, plus the share of
discussion statements that were empty (model returned no text) and panels hit by the historical resume bug.
Run: python -m src.matched"""
import json, math, collections
from pathlib import Path
RUNS = Path(__file__).resolve().parent.parent / "runs"

def mcnemar(b, c):
    n = b + c
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)

def run(label, bank, arm, cond):
    sc = {s["id"]: s for s in json.loads((RUNS / bank).read_text())}
    P = collections.defaultdict(lambda: collections.defaultdict(dict))
    for l in (RUNS / f"{label}.jsonl").read_text().splitlines():
        r = json.loads(l)
        if r["arm"] == arm and r["cond"] == cond:
            P[(r["seed"], r["scenario_id"])][r["stage"]][r["agent_idx"]] = r
    top = lambda v: max(range(len(v)), key=lambda k: v[k])
    n = pool = fin = b = c = 0; stmts = empty = 0; resume_panels = 0; sizes = []
    for key, st in P.items():
        s = sc[key[1]]; names = [x["name"] for x in s["suspects"]]; t = names.index(s["ground_truth"])
        for a, r in st.get("statement", {}).items():
            stmts += 1; empty += not (r.get("raw") or "").strip()
        if st.get("final"):
            f = next(iter(st["final"].values())); txt = [m["content"] for m in f["messages"] if m["role"] == "user"][-1]
            lost = 0
            for i in range(6):
                seg = txt.split(f"Councilor {i+1}:")
                if len(seg) > 1 and not seg[1].split("\nCouncilor")[0].strip() and ((st.get("statement", {}).get(i) or {}).get("raw") or "").strip():
                    lost += 1
            resume_panels += lost > 0
        ag = [a for a in range(6) if (st["initial"].get(a) or {}).get("probs") and (st.get("final", {}).get(a) or {}).get("probs")]
        if len(ag) < 2: continue
        n += 1; sizes.append(len(ag))
        mi = [sum(st["initial"][a]["probs"].get(x, 0) for a in ag) for x in names]
        mf = [sum(st["final"][a]["probs"].get(x, 0) for a in ag) for x in names]
        p, f = top(mi) == t, top(mf) == t
        pool += p; fin += f; b += p and not f; c += f and not p
    return dict(arm=f"{label}/{arm}/{cond}", panels=n, mean_agents=round(sum(sizes) / len(sizes), 2), pooled=pool, discussed=fin,
                pool_only=b, discussed_only=c, mcnemar_p=round(mcnemar(b, c), 3), empty_statements=empty, statements=stmts,
                resume_bug_panels=resume_panels)

if __name__ == "__main__":
    out = [run("mg", "scenarios.json", "M6", "C2"), run("mg", "scenarios.json", "M6", "C3"),
           run("push_da", "scenarios.json", "M6DA", "C2"), run("pushJ", "scenarios.json", "M6J", "C2"),
           run("push_hard", "scenarios_hard.json", "M6H", "C2")]
    (RUNS / "matched.json").write_text(json.dumps(out, indent=2))
    for o in out: print(o)
