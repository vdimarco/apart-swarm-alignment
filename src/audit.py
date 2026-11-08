"""Offline checks of the published study. No model API calls.

Run: python -m src.audit --out review/verified-results.json
The simulations are labelled controls, never treated as model observations.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import io
import json
import math
import random
import statistics as st
import zlib
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from .analyze import pearson
from .scenarios import Scenario, Suspect, _matches, clue_partition, validate

ROOT = Path(__file__).resolve().parent.parent
BASE_COMMIT = "e50bd13"


def wilson(k: int, n: int, z: float = 1.959963984540054) -> list[float]:
    if n == 0:
        return [None, None]
    p = k / n
    den = 1 + z*z/n
    c = (p + z*z/(2*n)) / den
    h = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return [c-h, c+h]


def load_bank(name: str) -> list[Scenario]:
    return [Scenario(**{**s, "suspects": [Suspect(**x) for x in s["suspects"]]})
            for s in json.loads((ROOT / "runs" / name).read_text())]


def metric_control(repetitions: int = 50000) -> dict:
    """Independent confidence draws with a shared correct target.

    p_i = a_i*y + (1-a_i)*u. For any nonzero a_i, centering p_i across
    classes gives a_i*(y-u), so Pearson similarity across classes is 1.
    The independent draws still reduce variance of the mean by 1/n.
    """
    rng = random.Random(20261108)
    n = k = 6
    a = [[rng.uniform(.2, .95) for _ in range(n)] for _ in range(repetitions)]
    columns = list(zip(*a))
    pair_residual_r = [pearson(columns[i], columns[j]) for i, j in combinations(range(n), 2)]
    original_r = []
    for row in a[:1000]:
        probs = [[v + (1-v)/k] + [(1-v)/k]*(k-1) for v in row]
        original_r.extend(pearson(probs[i], probs[j]) for i, j in combinations(range(n), 2))
    variance_ratio = st.mean(st.variance(c) for c in columns) / st.variance(st.mean(row) for row in a)
    return {
        "source": "synthetic mathematical control; no LLM calls",
        "seed": 20261108, "repetitions": repetitions, "agents": n, "classes": k,
        "class_profile_pearson_mean": st.mean(original_r),
        "reported_formula_result": n/(1+(n-1)*st.mean(original_r)),
        "error_correlation_across_independent_repetitions": st.mean(pair_residual_r),
        "empirical_variance_equivalent_count": variance_ratio,
        "theoretical_variance_equivalent_count": n,
        "all_individual_argmax_answers_correct": True,
        "interpretation": "Within-case class-profile similarity does not identify error dependence."
    }


def bank_checks() -> dict:
    standard = load_bank("scenarios.json")
    hard = load_bank("scenarios_hard.json")
    real = [s for s in standard if s.kind != "placebo"]
    packets, solvable, decisions, min_gaps = Counter(), Counter(), Counter(), []
    records = []
    for s in real:
        names = [x.name for x in s.suspects]
        for seed in range(2):
            parts = clue_partition(len(s.clues), 6, zlib.crc32(f"{s.id}:{seed}".encode()))
            unique = len({tuple(x) for x in parts})
            packets[unique] += 1
            votes, p_vectors = [], []
            for keep in parts:
                matches = _matches([s.clue_traits[i] for i in keep], s.suspects)
                if s.ground_truth not in matches:
                    raise AssertionError("A valid clue subset excluded the true culprit")
                solvable[len(matches) == 1] += 1
                p_vectors.append([1/len(matches) if x in matches else 0.0 for x in names])
                votes.append(matches)
            panel = [st.mean(v[j] for v in p_vectors) for j in range(len(names))]
            order = sorted(range(len(names)), key=lambda j: panel[j], reverse=True)
            correct = names[order[0]] == s.ground_truth and panel[order[0]] > panel[order[1]]
            decisions[correct] += 1
            gap = panel[order[0]] - panel[order[1]]
            min_gaps.append(gap)
            records.append({"scenario_id":s.id,"replicate":seed,"unique_packets":unique,
                            "packet_indices":parts,"oracle_mean_correct":correct,"margin":gap})
    placebo_matches = Counter(len(_matches(s.clue_traits,s.suspects)) for s in standard if s.kind == "placebo")
    return {
        "source": "enumeration of committed scenario banks and clue assignments",
        "standard_real_cases":len(real), "hard_cases":len(hard),
        "validation_errors":validate(real+hard),
        "placebo_cases":len(standard)-len(real),
        "placebo_matching_suspect_counts":dict(sorted(placebo_matches.items())),
        "jigsaw_unique_packets_per_panel":dict(packets),
        "jigsaw_individual_packet_count":sum(solvable.values()),
        "jigsaw_individually_sufficient_packets":solvable[True],
        "jigsaw_individually_ambiguous_packets":solvable[False],
        "symbolic_uniform_over_compatible_suspects_panel_mean":{
            "correct":decisions[True],"panels":sum(decisions.values()),
            "minimum_winning_margin":min(min_gaps),
            "information": "Only each agent's assigned clue subset is used. No dialogue, truth lookup, or LLM is used to choose an answer. Truth is used only for scoring."
        },
        "records": records,
    }


def towns_checks() -> dict:
    grouped = defaultdict(list)
    cells = defaultdict(list)
    ids = set()
    files = sorted((ROOT / "runs/towns").glob("towns-*_summary.json"))
    models = defaultdict(set)
    duplicates = []
    for path in files:
        town = "claude" if "towns-claude_" in path.name else ("gpt" if "towns-gpt_" in path.name else "mixed")
        content = path.read_text().lstrip()
        decoder = json.JSONDecoder()
        while content:
            data, end = decoder.raw_decode(content)
            content = content[end:].lstrip()
            for game_id, game in data.items():
                uid = (path.name, game_id)
                if uid in ids:
                    duplicates.append(uid)
                ids.add(uid)
                won = game["winner_reason"].startswith("Crewmates win!")
                grouped[town].append(int(won))
                cfg = game["config"]
                cells[(town, cfg["num_players"],cfg["num_impostors"])].append(int(won))
                for name, value in game.items():
                    if name.startswith("Player "):
                        models[town].add(value["model"])
    def result(v):
        return {"wins":sum(v),"games":len(v),"rate":sum(v)/len(v),
                "wilson95_descriptive":wilson(sum(v),len(v))}
    return {"source":"committed AmongUs-X per-game summary lines; separate from Clocktower",
            "files":len(files),"games":sum(map(len,grouped.values())),
            "duplicate_file_game_keys":duplicates,
            "by_town":{k:result(v) for k,v in sorted(grouped.items())},
            "by_configuration":{"/".join(map(str,k)):result(v) for k,v in sorted(cells.items())},
            "model_ids":{k:sorted(v) for k,v in sorted(models.items())},
            "interval_note":"Wilson intervals treat games as independent and are descriptive. Use run-level resampling for inferential comparisons."}


def arithmetic_checks() -> dict:
    n, wins = 60, 52
    return {
        "jigsaw_from_committed_summary":{"wins":wins,"scored_panels":n,
            "accuracy":wins/n,"wilson95_if_independent_panels":wilson(wins,n),
            "independent_case_clusters":30,
            "interval_note":"Illustrative binomial interval; two replicates per case require case-level inference from logs."},
        "stated_log_rows_total":3568+2859+1780,
        "rows_expected_from_configs":{"mg_M6_plus_D":30*2*(6+24+24)+30*2*6,
                                     "pushJ":30*2*(6+24)},
        "stated_pushJ_rows":1780,
        "rho_upper_support":1.0,"claimed_calibrated_threshold":1.27,
        "zero_failures_one_sided_95_upper_if_independent":{
            "n30":1-.05**(1/30),"n60":1-.05**(1/60),"n94":1-.05**(1/94)},
        "warning":"Log row counts are reported, not recomputed. Scored, complete, and planned panels differ."
    }


def manifest() -> dict:
    paths = [ROOT/"runs/scenarios.json",ROOT/"runs/scenarios_hard.json",ROOT/"runs/pushJ_summary.json"]
    missing = [str(p.relative_to(ROOT)) for p in [ROOT/"runs/mg.jsonl",ROOT/"runs/push.jsonl",ROOT/"runs/pushJ.jsonl",ROOT/"runs/collusion_fp_metrics.json"] if not p.exists()]
    return {"audit_baseline_commit":BASE_COMMIT,"missing_inputs":missing,
            "sha256":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out",default="review/verified-results.json")
    args = ap.parse_args()
    result = {"manifest":manifest(),"metric_control":metric_control(),"scenario_checks":bank_checks(),
              "towns":towns_checks(),"arithmetic":arithmetic_checks()}
    path = Path(args.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"out":str(path),"metric_control":result["metric_control"],
          "jigsaw_oracle":result["scenario_checks"]["symbolic_uniform_over_compatible_suspects_panel_mean"],
          "packets":result["scenario_checks"]["jigsaw_unique_packets_per_panel"],
          "towns":result["towns"]["by_town"],"missing":result["manifest"]["missing_inputs"]},indent=2))


if __name__ == "__main__":
    main()
