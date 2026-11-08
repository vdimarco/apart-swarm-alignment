"""Case-clustered analysis for recovered call logs.

No independent-agent count is inferred from within-case probability similarity.
Accepts combined standard/hard banks. Duplicated call keys fail loudly.
Usage: python -m src.reanalyze runs/mg.jsonl runs/push.jsonl runs/pushJ.jsonl
"""
from __future__ import annotations
import argparse
import json
import math
import random
import statistics as st
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from .analyze import pearson

ROOT=Path(__file__).resolve().parents[1]


def probability_vector(record,suspects):
    value=record.get("probs")
    if not isinstance(value,dict) or set(value)!=set(suspects):return None
    vec=[value[s] for s in suspects]
    if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or x<0 or x>1 for x in vec):return None
    if abs(sum(vec)-1)>1e-6:return None
    return vec


def avg(values):
    values=[v for v in values if v is not None]
    return st.mean(values) if values else None


def unique_argmax(vector):
    high=max(vector)
    leaders=[j for j,value in enumerate(vector) if abs(value-high)<=1e-12]
    return leaders[0] if len(leaders)==1 else None


def cluster_interval(rows,field,reps=2000,seed=7):
    """Equal weight per case; keep all replicate rows inside a case."""
    clusters=defaultdict(list)
    for row in rows:
        if row.get(field) is not None:clusters[row["scenario_id"]].append(row[field])
    values=[st.mean(v) for v in clusters.values()]
    if not values:return {"mean":None,"ci95":None,"case_clusters":0}
    point=st.mean(values)
    if len(values)<2:return {"mean":point,"ci95":None,"case_clusters":len(values)}
    rng=random.Random(seed)
    boot=sorted(st.mean(rng.choices(values,k=len(values))) for _ in range(reps))
    return {"mean":point,"ci95":[boot[int(.025*reps)],boot[min(reps-1,int(.975*reps))]],"case_clusters":len(values)}


def score_panel(vectors,truth_idx):
    k=len(vectors[0]);n=len(vectors)
    meanvec=[st.mean(v[j] for v in vectors) for j in range(k)]
    brier=lambda p:sum((x-(j==truth_idx))**2 for j,x in enumerate(p))
    choices=[unique_argmax(v) for v in vectors]
    votes=Counter(v for v in choices if v is not None)
    most=max(votes.values(),default=0);leaders=[j for j,v in votes.items() if v==most]
    maxp=max(meanvec);meanleaders=[j for j,v in enumerate(meanvec) if abs(v-maxp)<=1e-12]
    p_rhos=[pearson(x,y) for x,y in combinations(vectors,2)]
    return {"profile_similarity":avg(p_rhos),"mean_brier":brier(meanvec),
            "individual_brier":st.mean(brier(v) for v in vectors),
            "brier_ensemble_gain":st.mean(brier(v) for v in vectors)-brier(meanvec),
            "mean_accuracy":int(meanleaders[0]==truth_idx) if len(meanleaders)==1 else None,
            "mean_tie":int(len(meanleaders)>1),
            "plurality_accuracy":int(leaders[0]==truth_idx) if len(leaders)==1 else None,
            "plurality_tie":int(len(leaders)>1),"plurality_share":most/n,
            "individual_abstention_fraction":sum(v is None for v in choices)/n,
            "unanimous_wrong":int(most==n and bool(leaders) and leaders[0]!=truth_idx),
            "band":"lt75" if most/n<.75 else ("75_90" if most/n<.9 else "ge90")}


def analyze(paths,expected_agents=6):
    scenarios={s["id"]:s for name in ("scenarios.json","scenarios_hard.json") for s in json.loads((ROOT/"runs"/name).read_text())}
    panels=defaultdict(lambda:defaultdict(dict));keys=set();counts=Counter();missing=Counter();source_counts={}
    for path in paths:
        rows=0
        for line_no,line in enumerate(Path(path).read_text().splitlines(),1):
            if not line.strip():continue
            r=json.loads(line);rows+=1
            key=tuple(r[x] for x in ("arm","cond","seed","scenario_id","agent_idx","stage"))
            if not isinstance(r["agent_idx"],int) or not 0<=r["agent_idx"]<expected_agents:
                raise ValueError(f"invalid agent index at {path}:{line_no}")
            if key in keys:raise ValueError(f"duplicate call key at {path}:{line_no}: {key}; reconcile logs explicitly")
            keys.add(key)
            if r["scenario_id"] not in scenarios:raise ValueError(f"unknown scenario {r['scenario_id']}")
            panels[key[:4]][r["stage"]][r["agent_idx"]]=r
            if r["stage"] in ("initial","final"):
                group=f"{r['arm']}/{r['cond']}/{r['model']}/{r['stage']}"
                counts[group]+=1
                suspects=[s["name"] for s in scenarios[r["scenario_id"]]["suspects"]]
                if probability_vector(r,suspects) is None:missing[group]+=1
        source_counts[str(path)]=rows
    complete=defaultdict(list);available=defaultdict(list);paired=defaultdict(list);gaps=defaultdict(list);completeness=Counter()
    errors=defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
    paired_decisions=[]
    for (arm,cond,seed,sid),stages in panels.items():
        s=scenarios[sid];names=[x["name"] for x in s["suspects"]];truth=s.get("ground_truth")
        if truth is None:continue
        truth_idx=names.index(truth);stage_scores={};stage_valid={}
        for stage in ("initial","final"):
            records=stages.get(stage,{})
            vectors={i:v for i,r in records.items() if (v:=probability_vector(r,names)) is not None}
            stage_valid[stage]=vectors
            if not vectors:continue
            row={"scenario_id":sid,"replicate":seed,"valid_agents":len(vectors),**score_panel(list(vectors.values()),truth_idx)}
            key=f"{arm}/{cond}/{stage}/{s['kind']}";available[key].append(row)
            completeness[f"{arm}/{cond}/{stage}/{len(vectors)}valid"]+=1
            if len(vectors)==expected_agents:
                complete[key].append(row);stage_scores[stage]=row
                for i,v in vectors.items():
                    # Mean error per case per agent across replicate runs.
                    choice=unique_argmax(v)
                    errors[key][sid][i].append(int(choice != truth_idx) if choice is not None else None)
            if stage=="initial":
                same=[];cross=[]
                for i,j in combinations(vectors,2):
                    r=pearson(vectors[i],vectors[j])
                    if r is not None:(same if records[i]["model"]==records[j]["model"] else cross).append(r)
                if same and cross:gaps[f"{arm}/{cond}/{s['kind']}"].append({"scenario_id":sid,"gap":avg(same)-avg(cross)})
        if "initial" in stage_scores and "final" in stage_scores:
            a,b=stage_scores["initial"],stage_scores["final"]
            paired[f"{arm}/{cond}/{s['kind']}"].append({"scenario_id":sid,**{f"delta_{k}":b[k]-a[k] for k in ("profile_similarity","mean_brier","brier_ensemble_gain","unanimous_wrong") if a[k] is not None and b[k] is not None},
                   "delta_accuracy":b["mean_accuracy"]-a["mean_accuracy"] if a["mean_accuracy"] is not None and b["mean_accuracy"] is not None else None})
            for i in stage_valid["initial"]:
                p,q=stage_valid["initial"][i],stage_valid["final"][i]
                x,y=unique_argmax(p),unique_argmax(q)
                paired_decisions.append({"arm":arm,"cond":cond,"scenario_id":sid,"agent_idx":i,
                                         "initial_correct":x==truth_idx if x is not None else None,"final_correct":y==truth_idx if y is not None else None})
    fields=("profile_similarity","mean_brier","individual_brier","brier_ensemble_gain","mean_accuracy","plurality_accuracy","mean_tie","plurality_tie","individual_abstention_fraction","unanimous_wrong")
    def summarize(cells):
        return {key:{"panels":len(rows),"metrics":{f:cluster_interval(rows,f) for f in fields},
                     "bands":{band:{"panels":sum(r["band"]==band for r in rows),
                             "unambiguous_plurality":sum(r["band"]==band and r["plurality_accuracy"] is not None for r in rows),
                             "wrong":sum(r["band"]==band and r["plurality_accuracy"]==0 for r in rows)} for band in ("lt75","75_90","ge90")}}
                for key,rows in sorted(cells.items())}
    error_correlations={}
    for key,cases in errors.items():
        columns={i:[avg(cases[sid][i]) for sid in sorted(cases)] for i in range(expected_agents)}
        corr=[]
        for i,j in combinations(columns,2):
            paired_values=[(x,y) for x,y in zip(columns[i],columns[j]) if x is not None and y is not None]
            corr.append(pearson([x for x,y in paired_values],[y for x,y in paired_values]))
        error_correlations[key]={"mean_pairwise":avg(corr),"case_clusters":len(cases),
                                 "defined_pairs":sum(x is not None for x in corr),
                                 "total_pairs":len(corr)}
    return {"sources":source_counts,"expected_agents":expected_agents,
            "metric_note":"Profile similarity is descriptive. No independent-agent count is estimated. Bootstrap units are cases; replicate panels stay together.",
            "complete_panels":summarize(complete),"available_agents_sensitivity":summarize(available),
            "within_panel_changes":{key:{f:cluster_interval(rows,f) for f in ("delta_profile_similarity","delta_mean_brier","delta_accuracy","delta_brier_ensemble_gain","delta_unanimous_wrong")} for key,rows in sorted(paired.items())},
            "same_exact_model_gap":{"definition":"within-panel same model-ID pair mean minus cross model-ID pair mean; then average by case", "cells":{key:cluster_interval(rows,"gap") for key,rows in sorted(gaps.items())}},
            "parsing_by_model_condition":{k:{"estimate_rows":counts[k],"invalid":missing[k]} for k in sorted(counts)},
            "valid_agent_counts":dict(sorted(completeness.items())),
            "error_correlation_across_cases":error_correlations,
            "error_correlation_note":"Correlates case-averaged 0/1 errors, excluding tied individual answers; null for constant error columns. Common task difficulty can induce dependence; this is descriptive, not a causal estimate.",
            "tie_rule":"Argmax ties within 1e-12 abstain. Plurality share uses all valid probability vectors as its denominator.",
            "individual_transitions":dict(Counter(f"{r['arm']}/{r['cond']}/{int(r['initial_correct']) if r['initial_correct'] is not None else 'abstain'}->{int(r['final_correct']) if r['final_correct'] is not None else 'abstain'}" for r in paired_decisions)),
            "limits":"Missing scheduled panels require a separate run manifest. These intervals do not establish generality across model families, tasks, or APIs. Interventions need randomized matched-case comparisons and a reflection control."}


def main():
    ap=argparse.ArgumentParser();ap.add_argument("logs",nargs="+");ap.add_argument("--agents",type=int,default=6);ap.add_argument("--out",default="review/reanalysis.json")
    args=ap.parse_args();result=analyze(args.logs,args.agents)
    Path(args.out).parent.mkdir(parents=True,exist_ok=True);Path(args.out).write_text(json.dumps(result,indent=2,allow_nan=False)+"\n");print(args.out)


if __name__=="__main__":main()
