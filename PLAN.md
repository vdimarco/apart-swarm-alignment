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

- **2026-11-07 (evening)** — Adaption key provisioned from user clipboard (primary selection) into `.env` (chmod 600). Catalog verified: 7 hosted models across GLM/Qwen/Gemma/DeepSeek — **decision: family_a=qwen3.5-397b (frontier-analog), family_b=glm-5.2** (distinct family, 4x lighter reasoning); recorded per Next Clarify Decision. Discovered platform models are reasoning-heavy (estimates burn 2-4k reasoning tokens) → budgets raised to 5k/3k; ping + stage probes validated on real A00 prompt (qwen 45s, glm 16s per estimate). Smoke pipeline: 20/20 calls, log written. **Sweep `main` launched 21:5x EST: 60 scenarios × 3 arms × {C1,C2,C3} × 3 seeds ≈ 24.3k calls, ~4-6h ETA at 16-panel concurrency, budget est. $150-250 of $500.**
- **2026-11-07** — Initialized repo;... (see above) ran ideation Q&A (direction = report core + fresh experiment; assets = Adaption-only + downloadable logs; design approved). Verified Adaption API shape (`/api/v1/responses`, `/api/v1/models`) and hackathon constraints (8-page PDF, dual-use appendix, weekend-work-only judging). Wrote README/.env.example/.gitignore scaffold. Discovered ranked-ideas artifact confirming towns-analysis = top solo pick and "monoculture looks like collusion" trap is known → our H3 must cite and differ (interactive game + ground truth vs static forecasts). Next: verify catalog, write spec, build harness.
