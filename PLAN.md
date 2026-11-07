# PLAN.md — Lock Before You Talk (Swarm Alignment Hackathon 2026)

> Project plan of record · Owner: Von (@vaughn) · Agent: Hermes
> Created: 2026-11-07 · Status: in progress (Phase 2)
> Repo: `~/Work/swarm-alignment-2026` · Deadline: **Sun 2026-11-08, 23:59 AoE**

## Goal

Submit a competitive Track 2+4 project to the Apart Research / AIAF Swarm Alignment Hackathon:
the observational report **"Why Towns Hang Their Own"** (pre-existing ~1,800 game-day LLM
social-deduction dataset, marked pre-existing per rules) plus one fresh weekend experiment,
**"Lock Before You Talk"** — a controlled test of belief-collapse in LLM panels and of a
mechanism (locked independent first reads) to prevent it.

## Exit Criteria

- [ ] Harness runs end-to-end on Adaption against ≥2 model families, all runs logged to JSONL
- [ ] At least one pre-registered hypothesis (H1–H4) supported with an effect + CI/reportable number
- [ ] Negative results from "what didn't work" / failed arms kept honest in the report
- [ ] PDF report ≤ 8 pages (official template) + 150–250 word abstract + Limitations/Dual-Use appendix submitted via Apart form before deadline
- [ ] Code repo pushed (public) and linked from the submission; provenance section marks pre-existing vs weekend work

## Plan of Record

| Sub-question | Hypothesis (frozen 2026-11-07, pre-registration) | Method | Status |
|---|---|---|---|
| H1 collapse | N_eff falls & pairwise correlation rises from C1 to C2 | 30 scenarios × 3 arms × 3 conditions × seeds | pending |
| H2 danger zone | 75–90% plurality wrong more often than ≥90%; worse in C2 | band tables on verdicts vs ground truth | pending |
| H3 same-weights priors | same-family C1 correlation > cross-family | pair correlations in C1, mixed arm | pending |
| H4 remedy | C3 keeps C1 diversity at ≥ C2 accuracy | N_eff + accuracy per condition | pending |

**Structure subtask ordering:** explore/scope (done) → spec+pre-reg → harness/plumbing → smoke → sweep → analysis → report → submit.

## Phase Status

- [x] Ideate — 2026-11-07
- [~] Discover — model-catalog check blocked on API key; see open items
- [ ] Build harness (Tasks 2–3)
- [ ] Smoke (Task 4)
- [ ] Sweep (Task 5)
- [ ] Analysis + figures (Task 6)
- [ ] Report + submission (Task 7)

## Next Clarify Decision

Model-family assignment for arms A/B — decision lands once `python -m src.client --models` returns the granted catalog (needs `ADAPTION_API_KEY` in `.env`; user action). Fallback: run two weakly-related open families; downgrade H3's "replicates Claude/GPT" claim to "replicates across open-weight families," still novel.

## Risks / Decisions

- **Pre-existing data marking.** Towns analysis predates the weekend → disclosed in report + submission form; only the experiment + report-writing count as weekend work.
- **Adaption catalog depth.** Only observed `qwen3.5-397b`. If only one capable family is granted, experiment collapses to "copies of one model herd" (still covers H1/H2/H4; H3 weakened). Decision recorded here, not re-litigated later.
- **Time.** ~36h. Scope cuts pre-agreed in order: (1) drop mixed arm → keep 2 all-family arms; (2) drop placebo scenarios; (3) drop seeds 3→2. Never cut: danger-band numbers or the C3 test.
- **Fabrication risk.** Every number in the PDF traces to `runs/*.jsonl` + `src/analyze.py` output; nothing hand-typed.

## Decomposition

- [x] Task 1 — Ideate → Confirm focus (combined direction approved, assets verified) — **done 2026-11-07**
- [x] Task 2 — Discover → verify Adaption models, towns-log dump location, repo hygiene — **done 2026-11-07** (catalog = 7 platform models; arms = qwen3.5-397b/glm-5.2; towns-log location still open for Task 7)
- [x] Task 3 — Spec + pre-registration doc; harness `src/{scenarios,client,harness}.py` — **done 2026-11-07**
- [x] Task 4 — Smoke: scenario validation + 1-panel C2 live call — **done 2026-11-07**
- [~] Task 5 — Full sweep overnight (label=main, ~24.3k calls); resume-safe JSONL — **running**
- [ ] Task 6 — `analyze.py` metrics: N_eff, bands, prior agreement, figs
- [ ] Task 7 — Report (template), appendix, submission, repo push

## Unknowns Inventory

| Unknown | Status | Resolved at |
|---|---|---|
| Adaption granted models | open → blocked on key | Task 2 |
| Towns logs location/format | pre-verbal (user: "downloadable") | Task 7 |
| Report official template URL | open — fetch from Apart page | Task 7 |
| Same-weights gap size (H3) | pending sweep | Task 6 |

## Alignment Notes

This is the design the user already green-lit via structured Q&A (2026-11-07): A-as-core + small addition; full design in session, summarized in the spec. Design doc (when written) lives at `docs/superpowers/specs/2026-11-07-lock-before-you-talk-design.md` and is the traceable artifact for the Plan of Record.

User tip logged: **Adaption connects directly to Hugging Face** (datasets API). Confirmed full `/models` on this key still shows only the 7 platform models — arm assignment stands (no model expansion). HF access is for W2 (provenance/data mirror of towns logs + scenario bank via Adaption datasets) and possibly ingesting the gated AI Village transcripts if approval lands in time — parked, not on critical path.

## Confirmed Decisions

- [x] Direction: package towns analysis as core + one fresh controlled experiment
- [x] Compute backend: Adaption API only (user credits); OpenAI-Responses-compatible client
- [x] Scope-cut ordering agreed (mixed arm → placebo → seeds)
- [x] Harness-first sequencing: build tonight, sweep overnight, write Sunday afternoon

## Ideas Paused (do not pursue this weekend)

- Gateway-side lineage identity audit trail (ranked-doc #2) — strong, but second project max; rules allow ≤2 projects/person only if bandwidth exists
- Validator-reputation testbed (ranked-doc #3)
- Full game-engine replication of the towns protocol

## Parallel Workstreams

| Stream | Status | Notes |
|---|---|---|
| W1: experiment code + sweep | active | this repo |
| W2: towns report core (charts/numbers from downloadable logs) | queued | starts Sunday; depends on user locating log dump |

## Deferred Clarification / External Dependencies

- User: create Adaption API key → `.env` (from hackathon signup; adaptionlabs.ai/app) — **blocks Task 2+
- User: locate/confirm towns log exports for provenance appendix — needed before Task 7 only
- Organizer docs: official report template (link check during Task 7)

- **2026-02-20 (afternoon, push COMPLETE — all results in)** — Final sweep results, all arms done, nothing left running:
  - **Hard bank (push_hard, ~1,440 recs target):** H2 null TOTAL — 0 wrong in every danger band. H1 collapse replicates: M6H initial ρ=0.862/N_eff 1.12 (n=48) → C2 final 0.995/1.00 (n=23). **H3 does NOT replicate on the hard bank: DH same=1.000 vs cross=0.9996, diff +0.0004 (CI 0.0002–0.0007)** — ceiling confidence erases the same-weights premium. Note: an external PLAN edit (commit 0352dee) claimed "+0.097 replicates on 2nd bank" — NOT reproducible from runs/push.jsonl; corrected here from the data (verified computation in this session).
  - **DA arm (M6DA, 1,344 recs, 57/60 panels with finals):** H4' devil's advocate FAILS — initial ρ=0.891 → C2 final 0.990/1.01; dissenter absorbed (30/30 agree with majority, ρ=0.995). Danger bands unpopulated on v1 bank as well.
  - **Full experimental picture for the report:** H1 replicated on both experimental banks + towns; H3 same-weights premium replicates under non-degenerate uncertainty (v1 +0.082 ≈ towns +0.078) but saturates at ceiling (+0.0004 on hard bank) — gap is a *tail-belief* phenomenon; H2 honest null; H4 remedies (C3 lock, DA dissenter) both fail — collapse robust to two interventions.
- **2026-02-20 (night, mg FINAL-final)** — mg.jsonl complete at 3,568 records (second mg process finished its tail after the first snapshot; all 60/60 panels present). Corrected headline: **M6 initial ρ=0.875/N_eff 1.11 → C2 final 0.982, C3 final 0.992 (full collapse both); D same-model ρ=1.000; H3 gap +0.082 (CI 0.074–0.089), replicating towns' +0.078.** Missingness settled: M6 17%, D 10% estimate parse-fails. Supersedes the 2,947-record snapshot numbers.
- **2026-02-21 (~04:45 EST, R5 CALIBRATED)** — External FYI (HAJ≠2) flagged jigsaw as "lossy-vote filter, not a consensus fix". Its specific paths/numbers (fullrev=0.446) are **not reproducible on this machine** (multi-agent-verst/, whodunit dirs don't exist — third such phantom reference), but our own data supports the *framing*: final ρ 0.847 with N_eff 1.14 means deliberation returns 65% of the prior-decorrelation gain. **R5 rewritten: jigsaw = partial de-correlator with an accuracy price, not a remedy that holds.** Discussion Q1/Q4 hardened: no measured intervention protects independence through consensus. Optional bounded follow-up: harder jigsaw (2-of-6 copies) or jigsaw+lock combo to map capacity bound — user decision.
- **2026-02-21 (~04:30 EST, R5 LOCKED)** — pushJ complete: 1,780 records, 60/60 panels, 9% missingness. **Jigsaw C1 ρ=0.683/N_eff 1.34; C2 0.685→0.847/N_eff 1.14 vs baseline 0.982/1.01; accuracy 52/60 (87%). The only working remedy, priced in accuracy.** Figures regenerated with M6J bars; report R5 + abstract finalized. Next: template port + submission assembly. Dataset closed across all arms.
- **2026-02-21 (~03:00 EST)** — Jigsaw run launched (M6J arm: per-agent clue partition rr3, each clue seen by 3/6 agents) × C1/C2 × v1 bank × 2 seeds, label pushJ (~1,800 calls). **Early signal: C1 initial ρ=0.55 vs 0.875 full-info — the first intervention that decorrelates priors.** Figures switched to dependency-free SVG (Hermes venv has no pip/matplotlib): runs/figures.py → report/fig1-4.svg. Report drafting next.
- **2026-02-21 (~02:00 EST, experiment CLOSED)** — Resume pass recovered 107 504-shed calls. Final completeness: **383/384 panels complete** (only M6H/C2 23/24; one panel recorded missing after retry exhaustion). Data frozen for analysis: `runs/mg.jsonl` (3,568 recs) + `runs/push.jsonl` (~2,840 recs). Experiment phase done; remaining Tasks 6-7 (figures + report) and open user items (towns-logs location, official report template URL).
- **2026-02-21 (~01:30 EST, DA verdict)** — Devil's-advocate arm (57 panels): **remedy H4' FAILED.** M6DA final ρ=0.990 ≈ baseline 0.982; accuracy holds 57/57. Mechanism detail: the designated dissenter's *final* beliefs agree with the majority in **30/30** panels (ρ=0.995 vs others) — the dissenter is absorbed, not merely outvoted. Remedy arc now: commitment fails, forced dissent fails, collapse is structural on these tasks. Framing guardrail for report: our banks never produce wrong majorities, so remedies' failure = *diversity not preserved*; error-cost claim stays anchored to observational towns data. Resume pass queued for ~350 504-shed calls.
- **2026-02-20 (night, pushH verdict)** — Hard bank (12 × 8-suspect negative-clue scenarios) × M6H+DH × C1/C2 × 2 seeds: **100% accuracy across all 94 scored panels, decoy never won, danger band unpopulated.** H2 confirmed null at two difficulty tiers → boundary condition: observational danger band arises from unverifiable social evidence (bluffing, role claims), not from deduction difficulty. pushH missing ~250 calls to 504s; resume pass deferred (saturated null). pushDA in flight.
- **2026-02-20 (night, push)** — Three pushes: (1) **collusion-detector calibration on existing data** — naive agreement detectors flag 100% of honest same-model copies *and* 66–97% of honest strangers (thresholds 0.5–0.99); calibrated threshold flags nothing; pair-level AUC ≈ 0.36 → group-mean monoculture premium is real (CI excludes 0) but pair-level detection is unworkable: quantified Track-4 result. (2) **H2 hard-scenario rerun** launched: new bank `scenarios_hard.json` (12 items, 8 suspects, decoy ruled out ONLY by a negative sighting), M6H + DH arms × C1+C2 × 2 seeds. (3) **H4' devil's-advocate remedy** chained after: M6DA arm (agent 0 forced to argue against the emerging favorite) × C2 × v1 scenarios × 2 seeds. All landing in `runs/push.jsonl`, notify on completion.
- **2026-02-20 (night, final)** — `mg` complete: 2,947 records (M6 2,590 + D 357). **H3 replicated: same-family ρ=1.00 vs cross-family 0.92, diff +0.078 (CI 0.071-0.085) ≈ towns' +0.078. H1 replicated: N_eff 1.11→1.01 in both C2 and C3 → H4 remedy FAILED honestly. H2 null (ceiling accuracy). Missingness: M6 16%, D 9.5% estimate-stage parse-fails, all recorded.** Report skeleton + figures next (Task 6/7); towns-log provenance link still open with user.
- **2026-02-20 (night, cont.)** — First `mg` launch shed panels on **504 Gateway Time-out** (not in client retry list): 390/~3.2k calls landed. Fixed: 5-attempt backoff covering 429/500/502/503/504, concurrency 16→8 panels, relaunched with JSONL resume. +3.3 min: 2,251 records, C1 60/60 ✓, full C2/C3 71/120. ETA ~30 min more.
- **2026-02-20 (night)** — User ordered kill of `main` sweep (441 records preserved → `runs/main_partial_20260220.jsonl`) and a **shortened relaunch with the December sprint's 6-way mixed roster**: label `mg`, one arm × 6 distinct families (qwen3.5-397b, glm-5.2, qwen3.8-27b, deepseek-v4-flash, gemma-4-31b-it, gemma-4-26b-a4b-it), C1+C2+C3 × 30 real scenarios × 2 seeds, placebo off ≈ 3.2k calls (~1.5-3h ETA). Harness extended: explicit per-arm `models` list support. Health check 2.5 min in: 340 records, all 6 models producing, 9.5% estimate parse-fails (recorded, not hidden). Same-night goal: H3/H5 priors + H1 collapse + H4 remedy signal before Sunday report.
- **2026-11-07 (evening)** — Adaption key provisioned from user clipboard (primary selection) into `.env` (chmod 600). Catalog verified: 7 hosted models across GLM/Qwen/Gemma/DeepSeek — **decision: family_a=qwen3.5-397b (frontier-analog), family_b=glm-5.2** (distinct family, 4x lighter reasoning); recorded per Next Clarify Decision. Discovered platform models are reasoning-heavy (estimates burn 2-4k reasoning tokens) → budgets raised to 5k/3k; ping + stage probes validated on real A00 prompt (qwen 45s, glm 16s per estimate). Smoke pipeline: 20/20 calls, log written. **Sweep `main` launched 21:5x EST: 60 scenarios × 3 arms × {C1,C2,C3} × 3 seeds ≈ 24.3k calls, ~4-6h ETA at 16-panel concurrency, budget est. $150-250 of $500.**
- **2026-11-07** — Initialized repo;... (see above) ran ideation Q&A (direction = report core + fresh experiment; assets = Adaption-only + downloadable logs; design approved). Verified Adaption API shape (`/api/v1/responses`, `/api/v1/models`) and hackathon constraints (8-page PDF, dual-use appendix, weekend-work-only judging). Wrote README/.env.example/.gitignore scaffold. Discovered ranked-ideas artifact confirming towns-analysis = top solo pick and "monoculture looks like collusion" trap is known → our H3 must cite and differ (interactive game + ground truth vs static forecasts). Next: verify catalog, write spec, build harness.
