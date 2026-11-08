# Experiment amendment for the panel study

Prepared on 8 November 2026 after the original results. This is an exploratory follow-up. The original H1 to H4 specification remains unchanged.

## Question

Does a balanced split of evidence change the effect of discussion on panel error, compared with private reflection?

## Design to freeze before collecting new outcomes

Use 30 held-out cases with unique solutions and a fixed six-model roster. Cross full or balanced split evidence with discussion or private reflection. One replicate gives 120 panels and 2,880 scheduled stage calls. A separate ten-case pilot gives 960 calls. The final case file must have a different seed and checksum from the pilot. The pilot should contain both mistakes and recovery; a ceiling result blocks claims about protection from errors.

Use the same stage count and output-token ceilings in all cells. Randomize packet ownership and condition order. Record exact model IDs, request times, complete prompts, response status, usage, and run hashes. A replicate label is not a provider random seed. The current client does not retain full provider usage and finish metadata; add that before collecting results intended for a cost comparison.

The revised harness provides a private reflection condition (C4), carries each agent's initial estimate into later calls, and supports six distinct clue packets under `balanced3`. C3 remains a prompt commitment condition. The initial aggregate is a separate decision policy computed from recorded first estimates. Its output is fixed arithmetically.

## Outcomes and comparisons

The primary loss is the Brier score of the panel probability average. For each evidence allocation, compare change in Brier loss from the initial estimate under discussion with that under private reflection. The planned interaction is the balanced-allocation contrast minus the full-information contrast. A negative interaction means the balanced allocation reduces the added loss associated with discussion in this setup.

Use cases as the unit for paired bootstrap intervals. Keep all conditions and replicates for a sampled case together. Declare ties, invalid outputs, and missing-panel rules before the run. Analyze complete panels, then show results using all available valid agents and bounds for missing panels. Display exact denominators. Secondary outcomes are unanimous wrong answers, harmful and helpful answer revisions, and accuracy of the initial and final aggregates. Treat error correlation as descriptive and report undefined values at a zero-variance ceiling.

Do not choose the primary outcome, direction, or cases after seeing the held-out results. Report all cells. Preserve failed calls and distinguish request attempts from successful stage records. A claim that an intervention has no useful effect needs a prespecified equivalence margin and enough precision; an inconclusive interval is insufficient.

## Optional extension

A controlled false peer statement within the fictional cases can test response to misinformation if the pilot is otherwise at ceiling. This changes the treatment and requires a new protocol record before the held-out run. Collusion detection is a separate study with labelled positive coordination, honest and sham-message controls, and held-out threshold calibration.

## Status

No model data were collected for this amendment during the audit. The repaired harness passes offline tests with a fake client. Run a live smoke test before a pilot. Original outcomes must continue to point to their historical code version.
