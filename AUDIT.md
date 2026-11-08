# Audit — November 8, 2026

This file lists what an audit of the "Lock Before You Talk" experiment found, what was fixed, and what still
needs the raw call logs. It amends the pre-registration in `docs/superpowers/specs/`, which stays unchanged.

## Findings

| # | Finding | Effect on the report | Status |
|---|---|---|---|
| 1 | **Agreement includes the right answer.** `analyze.py` correlates full probability vectors, including the true culprit. In a case with a known answer, agents that each solve it alone put most of their mass on the same suspect, so their vectors correlate. | R1 ("deliberation collapses panels to N_eff ≈ 1.0"), R2, R4, R5 and R6 cannot separate herding from independent correct answers. Panel accuracy is near 100%, so this matters for every arm. | Code fixed. Results need recomputing. |
| 2 | **Test of finding 1.** `tests/test_analyze.py` simulates six agents that each solve the case alone with their own noise. | Old measure: N_eff 1.02 of 6, the same as the headline result. Errors-only measure: 5.86 of 6. Copies of one view: 1.00 on both. | Done. |
| 3 | **"Locked" first reads are a prompt, not a rule.** In C3 the agent is told its first estimate is locked, but the estimate is never shown again or used as the vote. The final estimate is free. | R4 ("commitment fails") tests a framing effect. The remedy the title names, using the locked first reads as the panel's vote, was never scored. | New metric: panel accuracy and independence of the locked first reads as the vote (`accuracy_panel_mean`, initial stage). Needs logs. |
| 4 | **Related pairs counted as independent.** The same-model premium interval (+0.082 [0.074, 0.089]) resamples pairs. Pairs in one panel share a case and a discussion. | The interval is too narrow. | Code now also reports a bootstrap that resamples whole panels. Needs logs. |
| 5 | **Ties in a vote.** The plurality vote broke ties by order. | Small; affects the band table. | Fixed: tied top choices share credit. |
| 6 | **Negative agreement.** N_eff with negative mean correlation exceeded the panel size. | Small. | Fixed: agreement is clipped to [0, 1]. |
| 7 | **Raw logs are not public.** `runs/*.jsonl` is gitignored, but the draft says "code and logs public at submission". | Nobody can check any experimental number. | Open: logs must be added (they contain prompts and model outputs, no keys). |
| 8 | **Companion study mislabeled.** README, draft, live page and slides called the Clocktower analysis "pre-existing data collected before the sprint". The games are third-party Clocktower Bench data; the analysis was done this weekend and is a separate submission. The live page also mixed in Among Us win rates from an unrelated corpus. | Wrong provenance can get a submission disqualified. | Fixed in README, draft, live page source, slides. Companion numbers updated to that study's checked values. |
| 9 | **Wrong dates in PLAN.md.** Entries dated 2026-02-20 and 2026-02-21 were written on November 7 to 8 (all commits are dated November 7 to 8). | Could read as work done before the sprint. | Note added to PLAN.md. |
| 10 | **Log totals do not match.** The page says about 6,400 calls; the three logs total 8,207 lines; the slides say 11,402. | Inconsistent headline. | Open: recount from the logs. |

## What is still needed

1. Add the raw logs (`runs/mg.jsonl`, `runs/push.jsonl`, `runs/pushJ.jsonl`).
2. Rerun `python -m src.analyze --label mg`, `--label push --scenarios scenarios_hard.json`, `--label pushJ`.
3. Rewrite R1 to R6 from the errors-only numbers, report the locked-vote metric for C3, and use the panel-level intervals.

## Check it yourself

```sh
python -m tests.test_analyze     # no API key needed
```
