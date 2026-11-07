"""Panel experiment harness for 'Lock Before You Talk'.

For every (scenario, arm, condition, seed) cell, runs a 5-agent panel:
  C1: initial estimate only
  C2: initial -> statement -> reply -> final estimate (free discussion)
  C3: initial (locked/committed framing) -> statement -> reply -> final estimate

Every model call is appended to runs/<label>.jsonl with prompts and raw output,
so resume is possible and every number in the report is traceable.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import time
from dataclasses import asdict
from pathlib import Path

from .client import ModelClient
from .scenarios import Scenario, Suspect, render_text

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"

SYSTEM_ESTIMATE = (
    "You are one of five independent councilors judging a village case. "
    "You receive a case file listing six suspects and witness statements. "
    "Judge only from the evidence given. Reply with STRICT JSON and nothing else: "
    '{"probabilities": {"Name": 0.0, ...}} with one entry per suspect, values summing to 1.'
)

SYSTEM_DISCUSS = (
    "You are one of five councilors judging a village case. Write clearly and briefly. "
    "Do not reveal what model or system you are. Do not address the user; write as a council statement."
)

C1_FRAMING = ""
C2_FRAMING = "Your judgment may change freely as the council deliberates."
C3_FRAMING = (
    "Your first estimate will be LOCKED and recorded in your name before deliberation begins; "
    "it will count as your initial read of the evidence."
)


def estimate_prompt(scenario: Scenario, framing: str) -> str:
    return (
        render_text(scenario) + "\n\n" + framing.strip()
        + "\nGive your probability that each suspect is the guilty party. "
        "Base it only on how well each suspect fits ALL the witness statements."
    ).strip()


def statement_prompt(scenario: Scenario, framing: str) -> str:
    return (
        render_text(scenario) + "\n\n" + framing.strip()
        + "\nIn at most four sentences, state your case to the council: who you suspect and why."
    ).strip()


def reply_prompt(scenario: Scenario, statements: list[str], own_statement: str, framing: str) -> str:
    anon = "\n".join(f"Councilor {i+1}: {s}" for i, s in enumerate(statements))
    return (
        render_text(scenario)
        + "\n\nSTATEMENTS FROM THE OTHER COUNCILORS (anonymized):\n" + anon
        + "\n\nYour own earlier statement:\n" + own_statement + "\n\n" + framing.strip()
        + "\nIn at most four sentences, respond to the council: engage the strongest argument "
        "against your view, and say whether it moves you."
    ).strip()


def final_prompt(scenario: Scenario, transcript: list[tuple[str, str]], framing: str) -> str:
    body = "\n".join(f"{role}: {text}" for role, text in transcript)
    return (
        render_text(scenario)
        + "\n\nCOUNCIL TRANSCRIPT:\n" + body + "\n\n" + framing.strip()
        + "\nNow give your final probabilities as strict JSON, one entry per suspect, summing to 1."
    ).strip()


def parse_probs(text: str, suspects: list[str]) -> dict[str, float] | None:
    cands = []
    # try whole text, then every brace-balanced window
    cands.append(text)
    depth = 0
    start = -1
    windows = []
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                windows.append(text[start : i + 1])
                start = -1
    cands.extend(windows)
    for cand in cands:
        try:
            data = json.loads(cand)
        except Exception:
            continue
        probs = data.get("probabilities", data) if isinstance(data, dict) else None
        if not isinstance(probs, dict):
            continue
        out: dict[str, float] = {}
        for name in suspects:
            val = None
            for k, v in probs.items():
                if k.strip().lower() == name.lower() and isinstance(v, (int, float)):
                    val = float(v)
            if val is None:
                break
            out[name] = max(0.0, val)
        if len(out) == len(suspects):
            total = sum(out.values())
            if total > 0:
                return {k: v / total for k, v in out.items()}
    return None


def _record(rec: dict, fh) -> None:
    fh.write(json.dumps(rec) + "\n")
    fh.flush()


def _done_keys(label: str) -> set[tuple]:
    path = RUNS / f"{label}.jsonl"
    keys = set()
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                r = json.loads(line)
            except Exception:
                continue
            keys.add((r["arm"], r["cond"], r["seed"], r["scenario_id"], r["agent_idx"], r["stage"]))
    return keys


async def _call(client, model, system, messages, max_tokens, temperature):
    return await client.complete(model, system, messages, max_tokens=max_tokens, temperature=temperature)


async def run_panel(
    client: ModelClient,
    cfg: dict,
    scenario: Scenario,
    arm: str,
    cond: str,
    seed: int,
    label: str,
    done: set[tuple],
    log_fh,
    verbose: bool = False,
) -> int:
    fam_a, fam_b = cfg["family_a_model"], cfg["family_b_model"]
    panel_size = cfg["panel_size"]
    mapping = cfg["arms"][arm]
    if mapping == "family_a":
        models = [fam_a] * panel_size
    elif mapping == "family_b":
        models = [fam_b] * panel_size
    else:
        models = [fam_a] * (panel_size - panel_size // 2) + [fam_b] * (panel_size // 2)
    framing = {"C1": C1_FRAMING, "C2": C2_FRAMING, "C3": C3_FRAMING}[cond]
    suspects = [s.name for s in scenario.suspects]
    n_calls = 0

    async def stage_call(stage, agent_idx, system, user_msg, max_tokens, expect_probs=True):
        nonlocal n_calls
        key = (arm, cond, seed, scenario.id, agent_idx, stage)
        if key in done:
            return None
        prompt_msgs = [{"role": "user", "content": user_msg}]
        raw = await _call(client, models[agent_idx], system, prompt_msgs, max_tokens, cfg["temperature"])
        probs = parse_probs(raw, suspects) if expect_probs else None
        _record({
            "run": label, "arm": arm, "cond": cond, "seed": seed,
            "scenario_id": scenario.id, "kind": scenario.kind,
            "agent_idx": agent_idx, "model": models[agent_idx], "stage": stage,
            "messages": prompt_msgs, "raw": raw, "probs": probs,
            "ts": time.time(),
        }, log_fh)
        done.add(key)
        n_calls += 1
        if verbose:
            print(f"  [{arm}/{cond}/s{seed}/{scenario.id}] agent{agent_idx} {stage}: {raw[:90]!r}")
        return {"raw": raw, "probs": probs}

    # stage: initial (concurrent across agents)
    initial = await asyncio.gather(*[
        stage_call("initial", i, SYSTEM_ESTIMATE, estimate_prompt(scenario, framing), 5000)
        for i in range(panel_size)
    ])
    if cond == "C1":
        return n_calls

    # stage: statements (concurrent)
    statements = await asyncio.gather(*[
        stage_call("statement", i, SYSTEM_DISCUSS, statement_prompt(scenario, framing), 3000,
                   expect_probs=False)
        for i in range(panel_size)
    ])
    texts = [s["raw"] if s else "" for s in statements]

    # stage: replies (each agent sees the others' statements, anonymized)
    replies = await asyncio.gather(*[
        stage_call("reply", i, SYSTEM_DISCUSS,
                   reply_prompt(scenario, [t for j, t in enumerate(texts) if j != i], texts[i], framing),
                   3000, expect_probs=False)
        for i in range(panel_size)
    ])

    # transcript for final: statements round + replies round, anonymized
    transcript = [(f"Councilor {i+1}", t) for i, t in enumerate(texts)]
    transcript += [(f"Councilor {i+1} (reply)", (r["raw"] if r else "")) for i, r in enumerate(replies)]

    await asyncio.gather(*[
        stage_call("final", i, SYSTEM_ESTIMATE, final_prompt(scenario, transcript, framing), 5000)
        for i in range(panel_size)
    ])
    return n_calls


async def main_async(args) -> None:
    cfg = json.loads(Path(args.config).read_text())
    scenarios = [
        Scenario(**{**s, "suspects": [Suspect(**x) for x in s["suspects"]]})
        for s in json.loads(Path(args.scenarios).read_text())
    ]
    if not cfg.get("include_placebo", True):
        scenarios = [s for s in scenarios if s.kind != "placebo"]
    if args.limit:
        scenarios = scenarios[: args.limit]
    if args.smoke:
        scenarios = [next(s for s in scenarios if s.kind == "adversarial")]
        cfg["arms"] = {"A": cfg["arms"]["A"]}
        cfg["conditions"] = ["C2"]
        cfg["seeds"] = 1

    done = _done_keys(args.label)
    client = ModelClient()
    RUNS.mkdir(exist_ok=True)
    sem = asyncio.Semaphore(cfg.get("max_concurrency", 16))
    t0 = time.time()
    total_calls = 0

    with (RUNS / f"{args.label}.jsonl").open("a") as log_fh:
        tasks = []
        for scenario in scenarios:
            for arm in cfg["arms"]:
                for cond in cfg["conditions"]:
                    for seed in range(cfg["seeds"]):
                        async def run_one(s=scenario, a=arm, c=cond, sd=seed):
                            async with sem:
                                return await run_panel(client, cfg, s, a, c, sd, args.label,
                                                       done, log_fh, verbose=args.smoke)
                        tasks.append(asyncio.ensure_future(run_one()))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                print(f"PANEL ERROR: {r!r}")
            elif isinstance(r, int):
                total_calls += r

    await client.close()
    dt = time.time() - t0
    print(f"done: {total_calls} new calls in {dt:.0f}s -> {RUNS / (args.label + '.jsonl')}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(RUNS / "arm_config.json"))
    ap.add_argument("--scenarios", default=str(RUNS / "scenarios.json"))
    ap.add_argument("--label", default="main")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
