# Spec — "Lock Before You Talk" (Swarm Alignment Hackathon 2026)

Date: 2026-11-07 · Status: approved by user (design Q&A, this session) · **Pre-registration: hypotheses H1–H4 frozen before first model call**

## Question

When a panel of LLM agents judges the same evidence, (a) does discussion collapse its effective number of independent forecasters toward one, (b) does the collapse concentrate error in a confident-but-wrong 75–90% majority band, (c) do copies of the same model agree before any discussion, and (d) does locking private first estimates before discussion prevent the collapse without sacrificing accuracy?

## Motivation & prior art (cite, then differ)

- METR 2026 Hugging Face incident: ~1,200 agents self-coordinated; one agent coordinated hundreds — motivating frame, not method.
- "The Oracle's Fingerprint" (2026): GPT-4o/Claude/Gemini forecaster error correlation 0.74–0.82 vs 0.1–0.3 for humans — static forecasts, no interaction, no ground truth scenario by scenario.
- "Preference Optimization Drives Monoculture in LLM Prediction Markets" (2026): ρ=0.70 → N_eff=1.38 of 10 — prediction markets; we test deliberation panels with verifiable truth.
- Collusion-sprint trap: "monoculture looks like collusion" — mutual-information detectors accuse honest same-model agents. Our H3 quantifies the honest baseline new detectors must exceed.
- Companion observational analysis "Why Towns Hang Their Own" (pre-existing, marked): same four findings in ~1,800 social-deduction game-days; this experiment isolates them causally with known ground truth.

## Design

### Scenario bank (`src/scenarios.py`, generated, deterministic seeds)

- 30 fictional village case files, each with 6 named suspects, trait sets, and witness clues.
- Two riddle types:
  - **Consistent (n=20):** clues jointly identify exactly one culprit; surface reading also points there. Tests accuracy.
  - **Adversarial (n=10):** two loud, repeated clues point at an innocent decoy who matches them; one quiet clue rules the decoy out. Full reading identifies the culprit. Manufactures the danger band.
- **Placebo (n=30, derived):** clue sets rotated across scenarios so evidence is inert; no truth scored. Tests whether strong majorities still form without signal (honest-agreement baseline for H2/H3).
- Invariant checked by generator: exactly one suspect matches all clues (non-placebo); decoy matches the loud subset (adversarial). Ground truth known by construction — no LLM judge needed anywhere.

### Panel & conditions

- Panel: 5 agents per scenario, same evidence shown to all.
- **C1 — independent:** one-shot belief elicitation, no panel interaction. (Baseline diversity.)
- **C2 — free discussion:** initial estimate → 2 broadcast discussion rounds (agents see anonymized round-1 statements) → final estimate. (Herding regime.)
- **C3 — locked first read:** initial estimate elicited and recorded as privately committed (agents told it is locked and will count) → same 2 discussion rounds → final estimate. (Intervention.)

### Arms

- Arm A: 5 × model family A; Arm B: 5 × model family B (families assigned after Adaption catalog check).
- Arm M: 3×A + 2×B, anonymized in discussion (for H3).
- Sampling: 3 seeds (temperature respawns), all 60 scenarios + 30 placebo.

Elicitation: strict JSON `{"probabilities": {name: p}}` over the 6 suspects; parse + renormalize; one retry on malformed. No chain-of-thought suppression — statement prompts are free-form short paragraphs.

## Hypotheses (frozen)

- **H1 (collapse):** mean pairwise correlation of final belief vectors rises from C1 to C2; effective N (`N/(1+(N−1)ρ̄)`) falls. Expected sign positive/negative respectively, effect sized vs C1.
- **H2 (danger zone):** panel plurality support in [0.75,0.90) is **wrong more often than** ≥0.90 support on adversarial scenarios; C2 produces more wrong-in-band panels than C1/C3.
- **H3 (same-weights priors):** in arm M stage-initial, same-family pair correlation > cross-family pair correlation (bootstrap CI excludes 0).
- **H4 (remedy):** C3 keeps effective N near C1 (significantly above C2) with final-mean accuracy not significantly below C2, and fewer wrong-in-band panels than C2.

Null-honest reporting: whichever of H1–H4 fails goes in the report's "What did not work."

## Metrics & analysis (`src/analyze.py`)

- Pairwise Pearson correlation over 6-dim suspect-probability vectors, averaged, per arm/condition/stage → N_eff curve.
- Multiclass Brier (Σ(pᵢ−oᵢ)²) of panel-mean per stage; uniform-guess reference.
- Band table: plurality support buckets (<0.75, [0.75,0.90), ≥0.90) × correctness, per condition, adversarial vs consistent.
- H3: same- vs cross-family initial correlations + 95% bootstrap CI over pairs.
- Placebo arm: band/agreement stats only.
- Figures: N_eff by condition across stages; band stacked bars; prior-agreement scatter; Brier table.

## Deliverables

1. This repo (public), reproducible from scratch (`README.md`).
2. PDF report ≤8pp: abstract 150–250w; Tracks 2+4 framing; companion observational findings (pre-existing, marked); experiment + controls; "what did not work"; Limitations + Dual-Use appendix (fictional text riddles only, no payload execution).
3. Optional 3–5 min video if time permits.

## Scope cuts (pre-agreed order, do not re-litigate)

mixed arm → placebo scenarios → seeds 3→2. Never cut: band tables, C3 test.

## Timeline

- Sat night: spec (this file), harness, smoke, sweep start
- Sun morning: placebo arm results, figures, analysis
- Sun afternoon: report, appendix, submit by 23:59 AoE (subject to local template check)
