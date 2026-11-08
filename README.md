# Lock Before You Talk

Swarm Alignment Hackathon 2026 (Apart Research and AI Alignment Foundation) · Tracks 2 and 4 · Vaughn DiMarco

**Report:** [`report/Lock_Before_You_Talk.pdf`](report/Lock_Before_You_Talk.pdf) · live page: https://lock-before-you-talk.vercel.app

Panels of six open-weight models from six families solve 30 fictional whodunit cases with known answers. We compare
three ways to decide: the average of each agent's locked first read, the average after two rounds of discussion,
and agents told their first read is locked. We also split the evidence so each agent sees half the clues.

## Results (after the audit)

- **Our first agreement measure was wrong.** Correlating probability lists within a case scores six agents that each
  solve it alone as 1.02 effective forecasters. On the right quantity, error correlation across cases, discussion does
  make errors line up in all four arms (free discussion r 0.42 → 0.77; N_eff about 2–3 → 1.2–1.8), on 5 to 14 model pairs.
- **With split evidence, pooling first reads beats discussion.** The average of locked first reads is right in 60 of
  60 panels; the discussed vote in 53 (exact McNemar p = 0.016; 5 of 30 cases fail, p = 0.06 by case). Discussion raises
  individual accuracy from 64% to 80% but lowers the panel's.
- **Retracted or revised:** the +0.082 same-model premium (a certainty artifact), the failure of locked reads, the
  collusion-detector result, and the size and evidence for deliberation collapse. See [`AUDIT.md`](AUDIT.md) and Appendix B of the report.

Companion submission: [Why AI Towns Hang Their Own](https://github.com/vdimarco/why-ai-towns-hang-their-own), herding
in 538 games of AI social deduction (third-party Clocktower Bench data, analysis done this weekend).

## Reproduce the numbers (no API key)

```bash
pip install -r requirements.txt matplotlib
python -m tests.test_analyze          # simulation check of the agreement measure
python -m src.audit_stats             # every number in report Sections 4.1 to 4.3 -> runs/audit_stats.json
python runs/paper_figures.py report   # Figures 1 and 2
python -m src.analyze --label mg      # per-arm tables (also: pushJ, push_da; push_hard with --scenarios scenarios_hard.json)
```

All 11,402 logged calls (prompts and outputs) are in `runs/*.jsonl`.

## Rerun the experiment (needs an Adaption API key)

```bash
cp .env.example .env   # put ADAPTION_API_KEY in .env
python -m src.scenarios --check
python -m src.harness --config runs/arm_config_mg.json --label mg
```

## Second, independent review

A second AI-assisted review (branch `review/evidence-audit`, merged) worked without the logs and added offline checks:
an exact counterexample for the within-case agreement measure, a check that the original jigsaw split gives only two
distinct clue packets, and probes that reproduce two harness bugs (lost discussion text on resume; first reads never
passed to later prompts). The repaired harness keeps both. Its claim audit is in
[`report/audit/claim-audit.md`](report/audit/claim-audit.md); its draft, written before the logs were available, is in
`report/archive/review-draft-without-logs.md`.

```bash
python -m src.audit                       # offline checks (counterexample, clue allocation, solver)
python -m unittest discover -s tests -v   # 12 tests
python -m src.across_case                 # across-case error correlation before and after talk
```

New model runs use protocol `2-audit-20261108` (`runs/arm_config_audit_smoke.json`), which refuses to append to the
historical logs, adds private reflection (C4) and a balanced split with six distinct clue packets. See
[`review/experiment-amendment.md`](review/experiment-amendment.md). No new paid runs were made.

## Data attribution

AmongUs-X summaries in `runs/towns/` come from the [AmongUs-X dataset](https://huggingface.co/datasets/Among-us-X/AmongUs-X)
(CC BY 4.0) and are unrelated to the Clocktower study. Project code is MIT-licensed.

## Pre-registration

Hypotheses H1–H4 were committed before the first model call (commit `b01f872`) in
[`docs/superpowers/specs/`](docs/superpowers/specs/2026-11-07-lock-before-you-talk-design.md) and are unchanged.
Deviations and exploratory arms are listed in the report's Methods section.

## Provenance

All code, runs, analysis and the report were made during the hackathon (November 7 to 8, 2026). LLM coding agents wrote
most of the code; the audit and report are described in the report's LLM Usage Statement. `report/first-draft.html`
keeps the first draft, with its retracted claims marked.

## Ethics

All cases are fictional text puzzles. No real systems were touched.
