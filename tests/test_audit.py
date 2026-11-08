import asyncio
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.audit import bank_checks,load_bank,metric_control,towns_checks
from src import harness
from src.reanalyze import analyze,cluster_interval,probability_vector,score_panel
from src.scenarios import clue_partition_balanced


class OfflineEvidenceTests(unittest.TestCase):
    def test_independent_estimates_are_not_counted_by_class_similarity(self):
        x=metric_control()
        self.assertAlmostEqual(x["class_profile_pearson_mean"],1)
        self.assertAlmostEqual(x["reported_formula_result"],1)
        self.assertLess(abs(x["empirical_variance_equivalent_count"]-6),.15)
        self.assertLess(abs(x["error_correlation_across_independent_repetitions"]),.01)

    def test_case_truth_and_jigsaw_information(self):
        x=bank_checks()
        self.assertEqual(x["validation_errors"],[])
        self.assertEqual(x["standard_real_cases"]+x["hard_cases"],42)
        self.assertEqual(x["jigsaw_unique_packets_per_panel"],{2:60})
        self.assertEqual(x["symbolic_uniform_over_compatible_suspects_panel_mean"]["correct"],60)

    def test_public_game_totals(self):
        x=towns_checks()
        self.assertEqual(x["games"],600)
        self.assertEqual(x["duplicate_file_game_keys"],[])
        self.assertEqual({k:v["wins"] for k,v in x["by_town"].items()},{"claude":147,"gpt":220,"mixed":87})

    def test_balanced_packets_keep_full_union_and_avoid_three_identical_agents(self):
        for clues in (3,4):
            for seed in (0,17,20261108):
                packets=clue_partition_balanced(clues,6,seed)
                self.assertEqual(len({tuple(x) for x in packets}),6)
                self.assertEqual([sum(c in p for p in packets) for c in range(clues)],[3]*clues)
                self.assertTrue(all(0<len(p)<clues for p in packets))

    def test_bootstrap_gives_equal_weight_to_cases(self):
        rows=[{"scenario_id":"A","x":0}]*20 + [{"scenario_id":"B","x":1}]
        self.assertEqual(cluster_interval(rows,"x",100)["mean"],.5)
        self.assertEqual(cluster_interval(rows,"x",100)["case_clusters"],2)

    def test_mean_vote_and_plurality_are_separate(self):
        # Two weak votes for class 0, one strong vote for true class 1.
        x=score_panel([[.51,.49],[.51,.49],[0,1]],1)
        self.assertEqual(x["plurality_accuracy"],0)
        self.assertEqual(x["mean_accuracy"],1)
        self.assertGreater(x["brier_ensemble_gain"],0)
        tied=score_panel([[.5,.5]]*6,1)
        self.assertIsNone(tied["plurality_accuracy"])
        self.assertEqual(tied["unanimous_wrong"],0)
        self.assertEqual(tied["individual_abstention_fraction"],1)

    def test_invalid_probabilities_are_rejected(self):
        for text in ('{"A":Infinity,"B":1}','{"A":NaN,"B":1}',
                     '{"A":-0.1,"B":1.1}','{"A":true,"B":false}',
                     '{"A":.2,"B":.2}','{"A":0.5,"B":0.5,"C":0.0}',
                     '{"A":0.4,"a":0.1,"B":0.5}'):
            self.assertIsNone(harness.parse_probs(text,["A","B"]),text)
        self.assertEqual(harness.parse_probs('{"A":0.25,"B":0.75}',["A","B"]),{"A":.25,"B":.75})
        self.assertIsNone(probability_vector({"probs":{"A":float('nan'),"B":0}},["A","B"]))


class FakeClient:
    def __init__(self,names):self.names=names;self.calls=0
    async def complete(self,model,system,messages,**kwargs):
        self.calls+=1
        if "STRICT JSON" in system:
            return json.dumps({"probabilities":{n:(.75 if i==0 else .05) for i,n in enumerate(self.names)}})
        digest=hashlib.sha256((model+messages[0]["content"]).encode()).hexdigest()[:16]
        return "SAVED_STATEMENT_"+digest


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.scenario=next(s for s in load_bank("scenarios.json") if s.kind=="adversarial")
        self.names=[x.name for x in self.scenario.suspects]
        self.cfg={"arms":{"M6":["fake"+str(i) for i in range(6)]},"temperature":1}
    def run_panel(self,cond="C3",done=None):
        out=io.StringIO();client=FakeClient(self.names)
        asyncio.run(harness.run_panel(client,self.cfg,self.scenario,"M6",cond,0,"test",done or {},out))
        return [json.loads(x) for x in out.getvalue().splitlines()],client.calls
    def test_resume_preserves_full_conversation(self):
        full,calls=self.run_panel()
        done={tuple(r[k] for k in ("arm","cond","seed","scenario_id","agent_idx","stage")):r for r in full if r["stage"] in ("initial","statement")}
        resumed,calls=self.run_panel(done=done)
        self.assertEqual(calls,12)
        expected=[r for r in full if r["stage"] in ("reply","final")]
        self.assertEqual([(r["messages"],r["raw"]) for r in resumed],[(r["messages"],r["raw"]) for r in expected])
    def test_first_estimate_is_available_to_later_calls(self):
        records,_=self.run_panel()
        initial={r["agent_idx"]:r["raw"] for r in records if r["stage"]=="initial"}
        for r in records:
            if r["stage"]!="initial":self.assertIn(initial[r["agent_idx"]],r["messages"][0]["content"])
    def test_private_reflection_never_sees_peer_statements(self):
        records,calls=self.run_panel("C4")
        self.assertEqual(calls,24)
        statements={r["agent_idx"]:r["raw"] for r in records if r["stage"]=="statement"}
        for r in records:
            if r["stage"] in ("reply","final"):
                text=r["messages"][0]["content"]
                self.assertIn(statements[r["agent_idx"]],text)
                for i,statement in statements.items():
                    if i!=r["agent_idx"]:self.assertNotIn(statement,text)
    def test_old_logs_require_new_run_label(self):
        with tempfile.TemporaryDirectory() as td, patch.object(harness,"RUNS",Path(td)):
            (Path(td)/"old.jsonl").write_text(json.dumps({"arm":"M6"})+"\n")
            with self.assertRaisesRegex(ValueError,"different protocol"):
                harness._completed_records("old","new-hash")
    def test_reanalysis_reports_ceiling_as_undefined_and_rejects_duplicate_keys(self):
        records,_=self.run_panel()
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"fake.jsonl";path.write_text("\n".join(json.dumps(r) for r in records)+"\n")
            result=analyze([path])
            for cell in result["error_correlation_across_cases"].values():self.assertIsNone(cell["mean_pairwise"])
            with self.assertRaisesRegex(ValueError,"duplicate call key"):analyze([path,path])


if __name__=="__main__":unittest.main()
