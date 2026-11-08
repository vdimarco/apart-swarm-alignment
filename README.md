# Lock Before You Talk

## Evidence review for the Swarm Alignment Hackathon 2026

The study's original agreement measure does not establish a count of independent agents. The review adds an exact counterexample and offline checks of the clue allocation and harness. Earlier model outcomes remain provisional because the public repository does not contain their call logs.

Read the [reviewed report](report/draft.md) and the [claim audit](report/audit/claim-audit.md). The earlier report is preserved in [the archive](report/archive/draft-before-audit.md). Existing website and slide files record the earlier interpretation; this review branch has not deployed them.

## Verified evidence

The metric reports one effective forecaster for six independently sampled estimates. A 50,000-panel simulation measures variance reduction of 5.953, close to the theoretical factor of six. The original clue split creates two distinct packets. A symbolic probability average finds the culprit in all 60 stored case and replicate assignments. This solver uses the generator's structured clues and measures information sufficiency under its grammar.

Fake-client probes reproduce a lost-transcript bug on resume and confirm that initial estimates were absent from later prompts. The repaired harness retains both. Twelve tests pass. No new model API calls were made for the review.

## Reproduce the offline checks

Use a full git clone, since the historical probe reads commit `e50bd13` from git history.

```bash
python -m pip install -r requirements.txt
python -m src.audit
python -m review.probe_original
python -m unittest discover -s tests -v
```

Results are in [verified-results.json](review/verified-results.json) and [historical-probes.json](review/historical-probes.json). The result manifest records input hashes. The game totals are recomputed from the committed AmongUs-X summaries.

To build the figures and PDFs:

```bash
python -m pip install -r requirements-audit.txt
python -m review.build_figures
python -m review.build_pdfs --out /absolute/output/directory
```

The PDF builder expects Liberation fonts under `/usr/share/fonts/truetype/liberation`. It follows the official template's section order, with a visible author-affiliation field to complete. The main text has five pages, followed by references and appendices. It is a review copy.

## Reanalyze the original model runs

The required call logs are absent from this public repository. Recover `runs/mg.jsonl`, `runs/push.jsonl`, and `runs/pushJ.jsonl`. Preserve checksums and original records. The older detector figure also depends on `runs/collusion_fp_metrics.json` and an unpublished computation. Check data releases for credentials and provider restrictions.

```bash
python -m src.reanalyze runs/mg.jsonl runs/push.jsonl runs/pushJ.jsonl --out review/reanalysis.json
```

The reviewed analyzer reports probability-average and plurality decisions separately, Brier loss, ensemble gain relative to mean individual Brier loss, unanimous wrong answers, and paired before-and-after changes. It uses case clusters and reports available-agent sensitivity results. It rejects duplicate stage keys. Complete scheduled-panel counts still require a run manifest. The historical analyzer and figures are retained for provenance; their independent-agent interpretation and pair-level bootstrap are superseded.

## New model runs use a separate protocol

The repaired harness uses protocol `2-audit-20261108` and refuses to append to historical logs. C3 remains commitment wording. C4 is private reflection. The optional `balanced3` allocation produces six distinct packets while retaining three copies of each clue. These new arms have no model results in this review.

Read [the experiment amendment](review/experiment-amendment.md) before collecting new outcomes. The client still needs provider usage and finish-status logging for cost and truncation claims.

With authorized Adaption credentials in `.env`, the following smoke command makes one six-agent, four-stage panel, or 24 scheduled calls:

```bash
cp .env.example .env
python -m src.harness --config runs/arm_config_audit_smoke.json --label audit_smoke_v2 --smoke
```

Fill in the key before running. The audit did not run this paid smoke test. The concurrency setting counts panels; each panel can issue several agent calls at once. A `seed` value labels a replicate and is not a provider sampling seed.

## Provenance and prior work

The original [H1 to H4 specification](docs/superpowers/specs/2026-11-07-lock-before-you-talk-design.md) is preserved. Later arms and this review are exploratory. Call logs are needed to verify the claimed ordering of the first model call. Older plan entries include inconsistent dates that need source review.

The Clocktower analysis named in the earlier report predates the sprint. Its observation table and analysis code were unavailable for this review. AmongUs-X is a separate preexisting dataset. Its 600 committed summaries yield 147/180 Claude crew wins, 220/300 GPT wins, and 87/120 mixed wins. Groups contain several model versions; these are descriptive totals.

The offline audit, revised analysis, harness fixes, and figures were produced during the sprint. This branch has not submitted a report or changed the production site.

## Data attribution and ethics

AmongUs-X: [dataset and CC BY 4.0 licence](https://huggingface.co/datasets/Among-us-X/AmongUs-X). The project source code is MIT-licensed. Data retain their source licence. The village cases are fictional. The audit does not operate on deployed agent systems. See the report's Limitations and Dual-Use / Ethical Considerations appendix.
