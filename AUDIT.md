# Audit — November 8, 2026

This file lists what an audit of the "Lock Before You Talk" experiment found, what was fixed, and what still
needs the raw call logs. It amends the pre-registration in `docs/superpowers/specs/`, which stays unchanged.

## Findings

| # | Finding | Effect on the report | Status |
|---|---|---|---|
| 1 | **Agreement includes the right answer.** `analyze.py` correlates full probability vectors, including the true culprit. In a case with a known answer, agents that each solve it alone put most of their mass on the same suspect, so their vectors correlate. | R1 ("deliberation collapses panels to N_eff ≈ 1.0"), R2, R4, R5 and R6 cannot separate herding from independent correct answers. Panel accuracy is near 100%, so this matters for every arm. | Fixed and recomputed. Collapse claim retracted. |
| 2 | **Test of finding 1.** `tests/test_analyze.py` simulates six agents that each solve the case alone with their own noise. | Old measure: N_eff 1.02 of 6, the same as the headline result. Errors-only measure: 5.86 of 6. Copies of one view: 1.00 on both. | Done. |
| 3 | **"Locked" first reads are a prompt, not a rule.** In C3 the agent is told its first estimate is locked, but the estimate is never shown again or used as the vote. The final estimate is free. | R4 ("commitment fails") tests a framing effect. The remedy the title names, using the locked first reads as the panel's vote, was never scored. | Scored: pooled locked reads beat the discussed vote with split evidence. |
| 4 | **Related pairs counted as independent.** The same-model premium interval (+0.082 [0.074, 0.089]) resamples pairs. Pairs in one panel share a case and a discussion. | The interval is too narrow. | Fixed: panel-level interval reported. Premium retracted as a certainty artifact. |
| 5 | **Ties in a vote.** The plurality vote broke ties by order. | Small; affects the band table. | Fixed: tied top choices share credit. |
| 6 | **Negative agreement.** N_eff with negative mean correlation exceeded the panel size. | Small. | Fixed: agreement is clipped to [0, 1]. |
| 7 | **Raw logs are not public.** `runs/*.jsonl` is gitignored, but the draft says "code and logs public at submission". | Nobody can check any experimental number. | Fixed: logs published (scanned for keys). |
| 8 | **Companion study mislabeled.** README, draft, live page and slides called the Clocktower analysis "pre-existing data collected before the sprint". The games are third-party Clocktower Bench data; the analysis was done this weekend and is a separate submission. The live page also mixed in Among Us win rates from an unrelated corpus. | Wrong provenance can get a submission disqualified. | Fixed in README, draft, live page source, slides. Companion numbers updated to that study's checked values. |
| 9 | **Wrong dates in PLAN.md.** Entries dated 2026-02-20 and 2026-02-21 were written on November 7 to 8 (all commits are dated November 7 to 8). | Could read as work done before the sprint. | Note added to PLAN.md. |
| 10 | **Log totals do not match.** The page says about 6,400 calls; the three logs total 8,207 lines; the slides say 11,402. | Inconsistent headline. | Fixed: 11,402 records; 8,082 calls analyzed. |

## Status after re-analysis (November 8, 2026)

The raw logs are now in `runs/`. `src/audit_stats.py` recomputes everything on the real data:

- Errors-only agreement before and after free discussion: 0.857 → 0.863 (16 matched panels). The collapse claim is retracted.
- The duplicate arm's "same-model premium" compares Qwen 3.5 copies that are one-hot in 100% of first reads. It measures
  certainty, not shared beliefs, and is retracted. Even on the old measure, the panel-level interval is [0.068, 0.095].
- Scoring the locked first reads as the vote: never worse than the discussed vote; with split evidence (jigsaw) 60/60
  against 53/60 (exact McNemar p = 0.016; 5 of 30 cases, p = 0.06 by case).
- Call counts: 11,402 logged records in all; the analysis uses 8,082 calls from four runs.

The corrected report is `report/Lock_Before_You_Talk.pdf`.

## Check it yourself

```sh
python -m tests.test_analyze     # no API key needed
python -m src.audit_stats
```
