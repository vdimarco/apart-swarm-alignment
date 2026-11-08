"""Reproduce harness defects at the audited commit with a fake client.

This does not contact a model service. The source is read from local git.
"""
import asyncio
import io
import json
import math
import subprocess
import types
from pathlib import Path

from src.audit import BASE_COMMIT, load_bank

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = subprocess.check_output(["git","show",f"{BASE_COMMIT}:src/harness.py"],cwd=ROOT,text=True)
    old = types.ModuleType("src._historical_harness")
    old.__file__ = str(ROOT / "src/harness.py")
    exec(compile(source, old.__file__, "exec"),old.__dict__)
    scenario = next(s for s in load_bank("scenarios.json") if s.kind == "adversarial")
    names = [s.name for s in scenario.suspects]

    class Fake:
        def __init__(self):self.calls=0
        async def complete(self,model,system,messages,**kwargs):
            self.calls+=1
            if "STRICT JSON" in system:
                return json.dumps({"probabilities":{n:(.75 if i==0 else .05) for i,n in enumerate(names)}})
            return f"SAVED_STATEMENT_{self.calls}"

    cfg={"arms":{"M6":["fake"]*6},"temperature":1}
    first=io.StringIO()
    asyncio.run(old.run_panel(Fake(),cfg,scenario,"M6","C3",0,"probe",set(),first))
    full=[json.loads(l) for l in first.getvalue().splitlines()]
    complete={tuple(r[k] for k in ("arm","cond","seed","scenario_id","agent_idx","stage"))
              for r in full if r["stage"] in ("initial","statement")}
    resumed=io.StringIO()
    asyncio.run(old.run_panel(Fake(),cfg,scenario,"M6","C3",0,"probe",complete,resumed))
    resumed_records=[json.loads(l) for l in resumed.getvalue().splitlines()]
    first_estimate=next(r["raw"] for r in full if r["stage"]=="initial")
    malformed={
        "infinity":'{"probabilities":{"A":Infinity,"B":1}}',
        "negative":'{"probabilities":{"A":-0.5,"B":1.5}}',
        "boolean":'{"probabilities":{"A":true,"B":false}}',
    }
    parsed={}
    for label,value in malformed.items():
        out=old.parse_probs(value,["A","B"])
        parsed[label]={"accepted":out is not None,
                       "all_finite":all(math.isfinite(v) for v in out.values()) if out else None}
    result={"source":"fake-client probes of git commit "+BASE_COMMIT,"model_api_calls":0,
            "normal_reply_sees_saved_statements":all("SAVED_STATEMENT_" in r["messages"][0]["content"] for r in full if r["stage"]=="reply"),
            "resumed_reply_sees_saved_statements":any("SAVED_STATEMENT_" in r["messages"][0]["content"] for r in resumed_records if r["stage"]=="reply"),
            "recorded_initial_estimate_present_in_any_later_prompt":any(first_estimate in r["messages"][0]["content"] for r in full if r["stage"]!="initial"),
            "malformed_probability_inputs":parsed,
            "scope":"These probes establish code behavior. The number of historical model panels affected requires the original logs."}
    path=ROOT/"review/historical-probes.json";path.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
