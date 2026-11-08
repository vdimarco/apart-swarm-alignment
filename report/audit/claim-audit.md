# Evidence review of Lock Before You Talk

Prepared for Vaughn DiMarco on 8 November 2026.

## Assessment

The report needs a change in its main claim. The controlled study measures how similar agents' probability lists are within one case. This measure cannot establish how many independent forecasters the panel contains. A direct counterexample gives the reported value of one for six independently sampled estimates. The claim that discussion turns six agents into one is unsupported by this measure.

The strongest result from this review is a set of reproducible checks for panel evaluation. The checks expose a measurement error, test whether the clue split preserves enough information, and check whether the harness performs the stated intervention. They provide a useful contribution to the study of agent networks. The earlier empirical results need the original call logs before they can carry the paper's main argument.

This review examined repository commit `e50bd1386f7ea387bde01d2546d9f6f6a6190bb9`, its history and stored data, the live report, the official event rules, and primary research papers. It ran local controls and code tests. It made no new model API calls.

## Verified results

| Check | Result | Evidence |
|---|---|---|
| Metric applied to independent estimates | Profile similarity 1.000; formula gives 1.000; variance reduction corresponds to 5.953 estimates, with a theoretical value of six | 50,000 simulated panels and an exact derivation |
| Unique culprit in the stored banks | All 30 standard cases and all 12 hard cases pass the grammar check | Exhaustive enumeration |
| Original clue allocation | Two distinct clue sets in every one of 60 case and replicate assignments | Original partition function |
| Combined information in split clues | A symbolic probability average selects the culprit in 60/60 assignments | Solver using structured clues |
| First estimate in later prompts | Absent from the audited harness | Fake-client probe of the pinned commit |
| Resumed discussion | Saved statements disappear from resumed reply prompts | Fake-client probe |
| Strict probability parsing | Original parser accepts negative numbers, Boolean values, and Infinity | Direct parser probes |
| AmongUs-X totals | 147/180 Claude; 220/300 GPT; 87/120 mixed | Recomputed from 600 game summaries |

The solver uses the generator's structured clue meaning. It does not parse prose with a language model. Its result is an information bound under the declared grammar, not a measure of model accuracy on the text.

## Review of every controlled finding

### R1 Discussion collapses six agents to one

**Verdict: replace the interpretation. Retain similarity as a descriptive statistic after checking the logs.**

The analyzer computes Pearson correlation across suspect classes inside one case. Two agents can have similar probability lists because both found the correct culprit. This produces high similarity even when their sampling errors are independent. The variance formula `n / (1 + (n - 1) * rho)` requires a correlation of repeated estimates under specified covariance assumptions. The report inserts a different quantity.

Let `y` mark the true class and let `u` be the uniform probability vector. Give agent `i` the estimate `p_i = a_i*y + (1-a_i)*u`, where each `a_i` is an independent draw between 0.20 and 0.95. Centering across classes gives `a_i*(y-u)`. Every pair has correlation one. Averaging six independent draws still reduces random variance by a factor of six. Our simulation yields a factor of 5.953 from 50,000 panels. The report's formula yields one.

The reported rise from 0.875 to 0.982 or 0.992 can describe greater similarity. It cannot show that independent processes become one. The hard-bank value of 0.995 has the same limit. Perfect answer accuracy can coexist with these values.

Use panel Brier score, individual Brier score, unanimous wrong answers, and correct-to-wrong revisions. Estimate error correlation across cases, mark zero-variance values as undefined, and account for shared task difficulty. Compare discussion with an equal number of private reflection calls. Preserve the same scored agents for paired comparisons. The new analyzer supports these descriptive checks; a causal treatment estimate still needs the matched experiment.

### R2 Same-model pairs have an extra 0.082 agreement

**Verdict: plausible within this setup; revise the confidence interval and causal language.**

Arm D contains five Qwen 3.5 instances and one GLM instance. Cross-model comparisons share that GLM participant within each panel. The original bootstrap samples individual pairs as independent observations, although pairs share agents and cases. It can understate uncertainty.

The code defines a same-model pair by exact model identifier. It does not test a general family effect. The six-model roster contains Qwen twice and Gemma twice, plus GLM and DeepSeek. It covers four named families. Shared training data and architecture were not independently varied.

Compute a gap inside each panel, average replicates inside each case, then resample cases. Analyze each bank separately. The new analyzer does this. Until logs arrive, 0.082 and 0.0004 remain reported values. Similar point estimates in the game study do not establish replication across different outcomes and sampling units.

The hard-bank result is consistent with a ceiling effect in the similarity measure. To establish that the model effect varies with uncertainty, test several difficulty levels and a declared model-by-difficulty comparison.

### R3 Harder logic does not produce the dangerous agreement band

**Verdict: retain a limited result about the tested cases. Remove the causal claim about game errors.**

The report says the full-information panels made no errors. This leaves little information about how discussion spreads mistakes. Zero observed errors cannot establish zero risk. For illustration, zero failures in 30 independent cases permits a one-sided 95% upper error bound of about 9.5%. The actual design requires a clustered interval.

The study did not randomly vary deception or unverifiable claims. A difference between a social game and a trait puzzle does not identify which feature caused the outcome. An empty 75 to 90% band can also arise from the few vote shares possible with six agents. Missing agents change those shares.

Use this wording: "The tested full-information cases did not produce enough errors to evaluate the proposed danger band." Show band counts by condition and bank, with ties and missing panels. Use a separate pilot to select a task range with errors, then evaluate held-out cases. Report harmful and helpful revisions separately.

### R4 Commitment and a designated dissenter fail

**Verdict: narrow the conclusion to the interventions actually delivered.**

The initial probabilities are recorded in a file. Later calls never receive that record. C3 says the answer will be locked, but the statement and final calls cannot inspect the stored answer. Peers do not see a public commitment board. The final answer remains free to change. This tests commitment wording in separate calls, not a decision rule bound to initial votes.

The dissenter receives its role in the statement and reply stages. Its final estimate uses the ordinary estimation prompt. Returning to the correct answer after arguing against it can be sensible. The claimed 30/30 agreement does not establish failure of a safety measure. That denominator also differs from the 57 or 60 panels mentioned elsewhere and needs reconciliation.

The revised harness supplies each first estimate to later calls, restores messages on resume, and adds private reflection. C3 is labelled commitment framing. A frozen initial aggregate can be scored as a separate policy. Do not describe that arithmetic decision rule as a psychological effect of a prompt.

### R5 Splitting clues reduces agreement at an accuracy cost

**Verdict: preserve the reported observation with its source status; replace the proposed mechanism.**

The stored summary contains initial similarity 0.68544, final similarity 0.84672, and 52 correct panels out of 60. The exact rate is 86.7%. An illustrative independent-panel Wilson interval is 75.8 to 93.1%, but there are only 30 case clusters. Use a case bootstrap once the logs arrive. The full-information comparator must use matched cases and scored membership.

The round-robin function gives agents 0, 1, and 2 the same packet. Agents 3, 4, and 5 share the other packet. This occurs in all 60 assignments. There are two information groups, and every clue remains present in the panel.

Our symbolic estimator assigns equal probability to suspects compatible with each agent's clues. Averaging the six distributions finds the culprit in all 60 assignments, without discussion. The minimum winning margin is 0.125. The solver uses structured clue traits. This proves that a solution remains available under the grammar; it does not measure a model's ability to extract or share it.

The reported 52/60 score could involve interpretation, missing outputs, poor pooling, or lost evidence in conversation. The supplied data do not isolate these causes. An accuracy loss is not a necessary consequence of the information split at panel level.

Remove the "65% of the gain is lost" statement. Its reference values change across versions, and it uses the invalid independent-agent interpretation. The new balanced allocation gives six distinct packets with three copies of each clue. It preserves the clue union. No model result is claimed for this new arm.

### R6 Agreement-based collusion detection cannot work

**Verdict: limit the result to false alarms for the tested thresholds.**

The reported threshold sweep uses honest runs. Without labelled positive collusion cases, it cannot measure collusion sensitivity, an ROC curve, or precision at a stated prevalence. Separating same-model from different-model pairs would answer another question.

The claimed calibrated threshold of 1.27 exceeds Pearson correlation's maximum of one. It is a rule that never flags a pair. It cannot validate a detector. A mean-plus-two-standard-deviations rule is also poorly suited to a bounded distribution with a large mass near one.

Use this wording: "The tested raw-similarity thresholds generate frequent false alarms on reported honest runs. These results do not assess detection of collusion." Fit a threshold on held-out honest cases and test on separate cases. A collusion study also needs a defined positive condition, such as coordination on a false answer within the fictional tasks, plus a sham messaging control.

The figure generator reads a metrics file but draws fixed false-alarm values typed into the source. Another figure also contains a fixed same-model gap. The required metrics file and call logs are absent from the repository. Generate each figure directly from the recovered data.

## Review of the observational findings

| Finding | Assessment and required change |
|---|---|
| About 1,800 Clocktower game-days | Matching observations and analysis code are absent. Specify games, days, surviving agents, exclusions, and repeated observations. Treat as preexisting background until verified. |
| Eight players become fewer than two effective forecasters by day two | Supply the metric definition. The within-case similarity shortcut would have the problem demonstrated above. This review cannot establish which calculation was used. |
| Wrong executions at 65%, 62%, and 1% across agreement bands | Supply counts and intervals. Define the denominator: nominations, votes, executions, or games. Cluster repeated days by game. These rates do not establish a universal threshold. |
| Evil players nominate wrong targets four times as often | Define the comparison group and opportunities to nominate. The denominator is unclear across report versions. |
| Good players account for about 70% of wrong-execution nominations | This count cannot assign causal responsibility. Account for the larger number of good players, participation, and selection of nominations that reach a vote. |
| Same-model gap 0.078, p below 0.001, 8,275 pairs | Pairs share players and games. Refit with game clusters and inspect the controls. Agreement does not identify a training-data effect. |
| Mean Brier 0.866; blind 0.908; extremized 0.980 | These are different comparators. Define the target, eligible classes, forecast time, and scoring convention. Use paired game-level uncertainty and held-out tuning. |
| No pooling method beats the mean; best agent cannot be selected in advance | Requires a common test set, a declared selection rule, and enough precision to assess useful differences. An inconclusive difference does not establish equivalence. |
| AmongUs-X crew wins of 81.7%, 73.3%, and 72.5% | Reproduced: 147/180, 220/300, and 87/120. Keep as a separate descriptive appendix. These are not the Clocktower data. |
| Two-impostor crew rates span 34.7 to 77.8% | The stored configuration table supports this range. Player count and model setup also vary. Avoid a causal claim about model diversity. |

The AmongUs-X groups contain several model versions. The Claude group includes Haiku 4.5, its thinking variant, and Sonnet 4.6. The GPT group contains five GPT-5.4 variants. These totals do not compare two fixed models. Wilson intervals added by this review are descriptive; inferential comparisons need run-level resampling. The original summary JSON did not contain the confidence intervals promised by the page.

## Design and provenance failures to fix

### Recover the evidence for the model results

The repository excludes `runs/*.jsonl` and `runs/*_metrics.json`. Missing inputs include `mg.jsonl`, `push.jsonl`, `pushJ.jsonl`, and `collusion_fp_metrics.json`. The default analyzer seeks an absent `main.jsonl`. The README also names a smoke module that does not exist.

Publish a versioned data archive with checksums, model identifiers, per-run configurations, and a command for every figure. Check it for credentials and provider restrictions. Separate API attempts, stored stage records, valid estimates, scored panels, and unique cases. Retain failed outputs in the flow table.

The page lists 3,568, 2,859, and 1,780 rows, which add to 8,207. The committed configurations imply 8,280 scheduled stage calls. Neither is 6,400 or 11,402. These are accounting checks on stated numbers, not a recount of absent logs. An earlier partial run or provider retries could explain a different total, but it must be documented.

### Audit resumed runs

The historical resume path retains completed keys without their outputs. It substitutes empty text for saved statements and replies. The plan records interrupted sweeps and resume passes. The probe reproduces the bug; the original prompts are needed to identify affected panels.

The repaired harness restores cached records. A test compares its resumed transcript with an uninterrupted run. It rejects older protocols or changed configurations under the same label. Historical outcomes must never be silently attributed to the fixed code.

### Correct the controls and sampling units

The active configurations disable placebo cases. The reported runs should not be described as having used them. Four of the 30 stored rotated-clue cases still identify a unique suspect under the grammar; 26 identify none. Rotating clues within a shared trait vocabulary does not ensure a neutral stimulus. Use a verified no-evidence condition if needed.

The `seed` field labels a replicate. It is not sent to the provider as a sampling seed. Fixed agent positions put both Qwen models in one clue group and both Gemma models in the other. Randomize packet ownership and save the mapping.

The original parser clips negative values and normalizes arbitrary positive totals. It can admit non-finite probabilities. The new parser rejects invalid numbers and permits only small rounding differences from a sum of one. Missingness attributed to reasoning truncation remains unverified: the original client saves output text without provider finish reasons or token usage.

The old analysis drops invalid agents, changing the panel being scored. It pools some band results across arms. Use complete panels for a declared primary analysis and show available-agent sensitivity results. Missing entire panels require a separate scheduled-run manifest. Score probability-average and plurality decisions separately; they can disagree.

### Preserve the chronology

Commit `b01f872` contains H1 to H4. Later changes include a new panel size and roster, fewer replicates, removal of placebo cases, a hard bank, a dissenter, and split clues. Label those additions exploratory. Keep the original specification intact. The git history records an internal sequence; absent call logs limit verification of first-call timing. Some plan entries also use February dates rather than November. Resolve those dates from source records without backdating an amendment.

## Improve the submission against the judging criteria

The global event scores impact and innovation, execution quality, and presentation and clarity. It requires the official PDF template, a 150 to 250 word abstract, author details, and a Limitations and Dual-Use / Ethical Considerations appendix. The body limit is eight pages. Disclose preexisting work. The deadline is 8 November 2026 at 23:59 AoE, or 9 November at 11:59 UTC. [1, 2]

Use Track 2, the science of agent networks, as the primary fit. The useful question concerns how evidence allocation and communication change shared errors. Track 4 can be a secondary link through honest false-alarm controls. The project has not validated a collusion detector.

| Judging area | Strongest improvement |
|---|---|
| Impact and innovation | Offer a reusable evaluation kit for panel studies. Connect it to an operator's choice about allowing discussion or keeping an initial aggregate. |
| Execution quality | Lead with the exact metric counterexample and exhaustive clue checks. Recover empirical data, repair the harness, and add matched private reflection on held-out cases with errors. |
| Presentation and clarity | Use one question. Label each evidence source and show accuracy beside similarity. Move older game statistics to an appendix. Replace the independent-agent visual with the metric control and clue allocation. |

The novelty section needs revision. Du and colleagues studied debate gains. Kim and colleagues measured shared errors across models. Batra and colleagues compare debate with matched reflection and examine unanimous errors. Huang and colleagues test public and private answers under adversarial discussion. [3-6] A broad claim to be the first controlled study of belief collapse will fail against this literature. The compact measurement audit and clue checks offer a narrower contribution that can be shown now.

### Next experiment with a bounded scope

Use a two-by-two study: full or balanced split evidence, each with discussion or private reflection. Score the initial probability average from those panels as another decision policy. Select cases with room for mistakes and recovery in a separate pilot. Freeze the held-out cases and analysis before collecting final outcomes.

Thirty held-out cases, four cells, six agents, and four stages require 2,880 scheduled calls for one replicate. A ten-case pilot adds 960. These are call counts, not cost or duration estimates. Token use, credits, and latency determine the budget. This session had no access to the original provider credentials or logs, so no new paid run was started.

Use final Brier loss as the primary outcome. Also report unanimous wrong answers and correct-to-wrong revisions. Compare change from the first estimate under discussion with the corresponding change under private reflection, using case clusters. Hold the roster, number of stages, and output-token ceilings fixed. Matching call counts does not ensure equal inference cost.

If the pilot stays at perfect accuracy, stop making a claim about protection from errors. Test a controlled false peer statement within the fictional cases, or submit the verified measurement audit. A detector extension needs labelled positives and held-out calibration. Keep it outside the main experiment until that experiment is reproducible.

## Completed changes and remaining work

The review branch contains a revised report, this audit, a new analyzer, exact figures, and offline result files. The harness restores messages on resume and carries first estimates forward. It adds private reflection and an optional balanced clue split. Probability parsing rejects invalid values. A new protocol label prevents mixing old and new runs.

Twelve tests passed. They cover the metric counterexample, clue sufficiency, game totals, clue coverage, case weighting, voting differences, invalid probabilities, resumed transcripts, initial estimates, the private control, protocol guards, and undefined correlation at the accuracy ceiling. Provider integration still needs a live smoke test.

Recover the original logs and the Clocktower analysis before presenting those outcomes as verified. Add the author's affiliation and review the final paper. If a report was already submitted, preserve its form title when replacing it. These files are review materials. This task did not submit the project or change the production website.

## References

1. Apart Research. Swarm Alignment Hackathon 2026. https://apartresearch.com/sprints/swarm-alignment-2026
2. Apart Research. Official submission template. https://docs.google.com/document/d/1_1_27EyZriMlc8n8EBE2YScaeyMjm-8xjR097nmHXAE/edit
3. Du, Y., Li, S., Torralba, A., Tenenbaum, J. B., and Mordatch, I. (2023). Improving Factuality and Reasoning in Language Models through Multiagent Debate. https://arxiv.org/abs/2305.14325
4. Kim, E. M., Garg, A., Peng, K., and Garg, N. (2025). Correlated Errors in Large Language Models. ICML, PMLR 267. https://proceedings.mlr.press/v267/kim25e.html
5. Batra, A. et al. (2026). Who Convinced Whom? Tracing How LLMs Change Their Minds in Multi-Agent Systems. Preprint. https://arxiv.org/abs/2610.35930
6. Huang, L. et al. (2026). Believed but Not Said: Measuring Hidden Belief Collapse in Multi-Agent LLM Discussions. Preprint. https://arxiv.org/abs/2610.22138
7. DiMarco, V. (2026). apart-swarm-alignment, audited commit e50bd1386f7ea387bde01d2546d9f6f6a6190bb9. https://github.com/vdimarco/apart-swarm-alignment/tree/e50bd1386f7ea387bde01d2546d9f6f6a6190bb9
8. Among-us-X (2026). AmongUs-X dataset. CC BY 4.0. https://huggingface.co/datasets/Among-us-X/AmongUs-X
9. Executable evidence: src/audit.py, review/verified-results.json, review/probe_original.py, and review/historical-probes.json in the review branch.
