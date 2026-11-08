"""Checks that the agreement measure does not count independent, correct agents as one voice.

Run: python -m tests.test_analyze   (no API calls; writes runs/selftest_*.jsonl, gitignored)
"""
import json
import random
from pathlib import Path

from src import analyze

RUNS = Path(analyze.__file__).resolve().parent.parent / "runs"


def make(label: str, kind: str, n_panels: int = 40, size: int = 6, seed: int = 0) -> None:
    rng = random.Random(seed)
    scen = [s for s in json.loads((RUNS / "scenarios.json").read_text()) if s["ground_truth"]][:n_panels]
    recs = []
    for sc in scen:
        names = [s["name"] for s in sc["suspects"]]
        truth = names.index(sc["ground_truth"])
        shared = [rng.random() for _ in names]
        for a in range(size):
            if kind == "independent_correct":   # each agent solves alone; errors are its own noise
                w = [rng.random() for _ in names]
            elif kind == "copies":              # every agent holds the same view
                w = list(shared)
            w[truth] = 0.0
            tot = sum(w)
            p = [0.3 * x / tot for x in w]
            p[truth] = 0.7
            recs.append({"arm": "T", "cond": "C1", "seed": 0, "scenario_id": sc["id"], "stage": "initial",
                         "agent_idx": a, "model": f"m{a % 2}", "probs": dict(zip(names, p))})
    (RUNS / f"{label}.jsonl").write_text("\n".join(json.dumps(r) for r in recs))


def main() -> None:
    make("selftest_indep", "independent_correct")
    make("selftest_copy", "copies")
    m1 = analyze.analyze("selftest_indep", bootstrap_reps=200)
    m2 = analyze.analyze("selftest_copy", bootstrap_reps=200)
    full = m1["correlation"]["T/C1/initial"]["n_eff_panelsize"]
    err = m1["correlation_errors_only"]["T/C1/initial"]["n_eff_panelsize"]
    cop = m2["correlation_errors_only"]["T/C1/initial"]["n_eff_panelsize"]
    print(f"\nindependent correct agents: N_eff full vectors {full:.2f}, errors only {err:.2f} (of 6)")
    print(f"copies of one view:         N_eff errors only {cop:.2f} (of 6)")
    assert full < 2.0, "full-vector measure should (wrongly) call independent correct agents one voice"
    assert err > 4.0, "errors-only measure should see independent agents as independent"
    assert cop < 1.1, "errors-only measure should see copies as one voice"
    print("PASS")


if __name__ == "__main__":
    main()
