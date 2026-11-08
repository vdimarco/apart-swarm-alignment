# Lock Before You Talk

## Testing what agreement measures in AI panels

Vaughn DiMarco

Affiliation to be supplied before submission

Research conducted at the Swarm Alignment Hackathon, November 2026

Primary track: The Science of Agent Networks

## Abstract

AI panels often use discussion to check answers. Evaluating this process requires a measure that separates similar answers from shared errors. We audit a six-agent study of fictional deduction tasks and test its main agreement measure. The study correlates probability lists across candidate answers within each case, then converts that value into an effective number of forecasters. We construct six independently sampled estimates for which this calculation returns one. Across 50,000 simulated panels, averaging reduces variance by a factor of 5.95, close to the theoretical factor of six. We also enumerate the study's clue allocation. Its six agents receive only two distinct evidence packets. A symbolic solver that uses each assigned packet and averages the resulting probabilities answers all 60 tested case and replicate assignments correctly. Thus the shared evidence retains a complete solution under the task grammar. Code probes find that recorded first estimates were absent from later prompts and that resumed runs could omit prior statements. We repair these paths and add a private reflection control. The audit provides reproducible checks for evaluating agent panels. The earlier model outcomes remain provisional until their call logs are available; these checks do not establish that discussion causes harmful dependence.

## 1 Introduction

An operator who uses several AI agents needs to know whether they catch one another's mistakes. Several agents can reach the same correct result from the evidence. They can also repeat a shared mistake. The evaluation must distinguish these cases before it can guide an oversight policy.

This project began as a study of first-answer commitment in six-agent panels. It used fictional village cases with a known solution. The first report interpreted greater similarity after discussion as a loss of independent forecasters. We review that interpretation, test the clue allocation, and inspect the implementation. These checks help a panel study decide when agreement can support a claim about safety or collusion.

The contribution is a small, executable evaluation kit. It includes a counterexample for the original measure and a solver that checks how much information remains after clues are split. The revised harness makes private reflection available as a comparison and preserves prior estimates through resumed runs. These changes support a later test of how communication changes errors.

## 2 Related work

Du et al. [1] show that debate can improve model answers on several tasks. This makes task performance a necessary part of an evaluation of growing agreement. Kim et al. [2] study shared errors across many models and show why provider diversity alone is insufficient evidence of independent behavior.

Batra et al. [3] compare discussion with private reflection using matched rounds and examine unanimous errors. Huang et al. [4] study public and private answers under adversarial discussion. Their work already addresses broad claims about belief change and shared failure. Our contribution is a reproducible audit of one panel metric, one evidence-allocation rule, and the code used to test them.

## 3 Methods

### 3.1 Evidence and scope

We inspect repository commit `e50bd13`, its stored configurations, and its scenario banks [5]. They contain 30 standard cases, 12 hard cases, and 30 rotated-clue placebo cases. The generator defines a culprit by a conjunction of suspect traits. We check every scored case against that grammar. The placebo cases have no scored truth and were disabled in the active configurations.

The original roster has six model identifiers drawn from four named families: Qwen, GLM, DeepSeek, and Gemma. The duplicate-model arm contains five Qwen 3.5 instances and one GLM instance. The recorded replicate number is not an API random seed.

The repository contains a jigsaw summary but omits the model call logs. The empirical values in Appendix A are reported results. The computations here use stored cases, local simulations, and fake-client probes. They make no new model calls.

### 3.2 Test of the agreement measure

For one case with K suspects, the original measure correlates two agents' K-dimensional probability lists. It averages these correlations across pairs, then applies n / (1 + (n - 1) rho).

For equal-variance random estimates of the same quantity, the variance identity is Var(mean) = sigma squared / n times (1 + (n - 1) rho). Its rho describes dependence across repeated estimates. Correlation across candidate classes within one case is a different statistic.

Our control fixes a correct class y and a uniform distribution u. Each of six agents draws its own coefficient a from Uniform(0.20, 0.95), independently, and returns p = a y + (1-a)u. We use 50,000 panels with random seed 20261108. We calculate the original similarity and the ratio of average individual variance to variance of the panel mean.

### 3.3 Information after the clue split

We reproduce the original allocation for all 30 standard cases and two replicate labels. Each clue goes to three agents. We count unique packets and check each against the stored trait grammar.

The symbolic estimator assigns equal probability to suspects compatible with that agent's clues. The panel averages the six distributions. The estimator uses structured clue traits and suspect attributes. It never reads ground truth to choose an answer. Ground truth is used only for scoring. This gives an information bound for the grammar without testing language comprehension.

### 3.4 Implementation probes

We load the original harness from its pinned git commit and replace the provider with a deterministic fake client. We compare normal and resumed prompts, check whether the first estimate reaches later calls, and supply invalid probability values to the parser. Tests of the revised code verify that resumed transcripts match an uninterrupted run and that private reflection excludes peer statements.

## 4 Results

### 4.1 Independent estimates can have perfect profile similarity

Centering each control estimate across classes gives a(y-u). All centered vectors point in the same direction, so pairwise Pearson similarity is exactly one. The original conversion therefore returns one effective forecaster.

The six coefficients were sampled independently. Their mean has one sixth of the individual variance in expectation. The simulation gives a variance ratio of 5.953. Mean error correlation across independent repetitions is 0.0016. Every individual selects the correct class. Figure 1 shows why the profile measure cannot identify dependence of forecast errors.

![Figure 1. Independent coefficients give profile similarity one. The measured variance reduction stays close to the sixfold theoretical value. These are simulated controls, not model results.](assets/metric-control.png)

This counterexample does not establish that the original models are independent. Their error dependence requires data across cases and a suitable control for shared evidence and task difficulty.

### 4.2 The original jigsaw has two distinct packets

All 60 original clue assignments produce two unique packets. Agents 0 to 2 receive one; agents 3 to 5 receive the other. Of 360 individual assignments, 171 uniquely identify the culprit and 189 allow more than one suspect. Every panel retains the complete clue union.

The symbolic probability average selects the culprit in 60 of 60 assignments. Its smallest winning margin is 0.125. Any other suspect fails at least one packet because the full clue set has a unique solution. The true suspect receives probability from every packet. An excluded suspect loses at least one positive contribution. With uniform probabilities over each compatible set, the true suspect's panel probability is strictly greater.

![Figure 2. The original round-robin rule forms two groups with identical packets. The new exploratory allocation gives each agent a distinct pair in a four-clue case. Both retain three copies of each clue.](assets/clue-allocation.png)

The reported model score of 52/60 therefore does not establish an unavoidable loss of information at panel level. Parsing, sharing facts, incomplete outputs, and pooling remain possible sources of error. The balanced allocation in Figure 2 is implemented but has not been evaluated with models.

### 4.3 The original harness did not preserve first estimates

The original statement and final prompts contain no record of an agent's initial probabilities. C3 adds commitment wording, but the estimate is not supplied to later calls or enforced in the final decision. A resumed run also replaces completed statements with empty text because it reloads only completed keys.

The probes reproduce these behaviors at the audited commit. The absent logs prevent a count of affected model panels. We also confirm that the original parser accepts Infinity, negative values, and Boolean probabilities.

The revised protocol restores cached outputs, supplies each first estimate to later calls, and rejects invalid numbers. It records system prompts, token ceilings, configuration hashes, and scenario hashes. It rejects a changed protocol or configuration under an existing run label. Twelve offline tests pass. A provider smoke test remains necessary before new data collection.

## 5 Discussion and limitations

The current evidence supports a measurement audit. A higher similarity score can accompany correct reasoning. An oversight system that uses agreement needs outcome measures and a clear account of how evidence is shared. A useful next experiment would compare discussion with private reflection, score harmful and helpful revisions, and retain the initial aggregate as a separate decision policy.

The original model values cannot yet be reproduced from the public repository. The accuracy ceiling limits what those runs can establish about shared failure. The private reflection condition matches the number of stages and output-token ceilings; actual token use can differ. New effects require case-clustered comparisons on held-out tasks.

The symbolic solver assumes exact truth conditions from the generator. It does not handle ambiguous language, unreliable witnesses, or open-ended work. The simulation is a mathematical control rather than an observation of model behavior. The corrected code and balanced allocation still need model evaluation.

## 6 Implications for oversight

A panel study should publish outcome scores alongside answer similarity. The first aggregate, final aggregate, and private reflection control can then be compared on the same cases. A claim about collusion also needs labelled coordinated behavior and a threshold tested on held-out honest cases. The earlier honest-only threshold sweep cannot supply those results.

## Code and data

Repository: https://github.com/vdimarco/apart-swarm-alignment

Checked outputs are in `review/verified-results.json` and `review/historical-probes.json`. Run `python -m src.audit`, `python -m review.probe_original`, and `python -m unittest discover -s tests -v`. The revised analyzer accepts recovered call logs and clusters uncertainty by case. Earlier model call logs remain absent from the public repository at the time of review.

The Clocktower analysis described in the previous report predates the sprint. Its records were unavailable here. AmongUs-X data also predate the sprint; we recomputed stored summary counts. The offline audit, revised analysis, code fixes, and figures were produced during the sprint. The original H1 to H4 specification is preserved. Later arms and this audit are exploratory.

## References

1. Du, Y., Li, S., Torralba, A., Tenenbaum, J. B., and Mordatch, I. (2023). Improving Factuality and Reasoning in Language Models through Multiagent Debate. https://arxiv.org/abs/2305.14325
2. Kim, E. M., Garg, A., Peng, K., and Garg, N. (2025). Correlated Errors in Large Language Models. ICML, PMLR 267. https://proceedings.mlr.press/v267/kim25e.html
3. Batra, A. et al. (2026). Who Convinced Whom? Tracing How LLMs Change Their Minds in Multi-Agent Systems. Preprint. https://arxiv.org/abs/2610.35930
4. Huang, L. et al. (2026). Believed but Not Said: Measuring Hidden Belief Collapse in Multi-Agent LLM Discussions. Preprint. https://arxiv.org/abs/2610.22138
5. DiMarco, V. (2026). apart-swarm-alignment. Audited commit e50bd1386f7ea387bde01d2546d9f6f6a6190bb9. https://github.com/vdimarco/apart-swarm-alignment/tree/e50bd1386f7ea387bde01d2546d9f6f6a6190bb9
6. Among-us-X (2026). AmongUs-X dataset. CC BY 4.0. https://huggingface.co/datasets/Among-us-X/AmongUs-X

## Appendix A Earlier model results awaiting log review

These values show what the earlier report claimed. They have not been recomputed from call logs in this review. Similarity means Pearson correlation across candidate probabilities within one case.

| Result | Reported value | Test still needed |
|---|---|---|
| Full evidence | Initial 0.875; final 0.982 with discussion and 0.992 with commitment wording | Whether communication changes shared errors relative to reflection |
| Same-model gap | 0.082 on standard bank; 0.0004 on hard bank | Uncertainty from case resampling and scope beyond tested model identifiers |
| Full-information accuracy | 100% on reported scored panels | Exact denominator, missingness, and tasks with errors |
| Designated dissenter | Final similarity 0.990; agreement in 30/30 panels | Argument behavior, private estimates, and effect on accuracy |
| Split clues | 0.68544 initial, 0.84672 final; 52/60 correct | Matched accuracy and causes of eight reported errors |
| Honest-pair detector | False alarms of 66 to 97%; 100% on same-model pairs | Reproduce honest baseline; no positive collusion condition exists |

The earlier effective-forecaster values and the 65% loss statement are withdrawn from the interpretation. A threshold of 1.27 cannot validate a detector whose statistic is bounded above by one.

## Appendix B Public game counts

AmongUs-X is separate from the preexisting Clocktower analysis. We recomputed these totals from 600 stored summaries. Groups contain several model versions. The descriptive Wilson intervals treat games as independent; comparisons need run-level resampling and configuration controls.

| Group | Crew wins | Games | Win rate | Descriptive 95% interval |
|---|---|---|---|---|
| Claude | 147 | 180 | 81.7% | 75.4 to 86.6% |
| GPT | 220 | 300 | 73.3% | 68.1 to 78.0% |
| Mixed | 87 | 120 | 72.5% | 63.9 to 79.7% |

## Appendix C Limitations and Dual-Use / Ethical Considerations

The experiment uses fictional village cases. This audit does not access or interfere with deployed agents. It cannot establish the safety of an open-ended network, infer malicious intent from shared answers, or validate a collusion detector. A known solution exists under the generator's trait grammar. Language interpretation remains a separate source of error.

Coordination measures can help build more capable multi-agent systems, including systems with harmful goals. The release contains no covert communication mechanism or deployed attack. Future positive collusion controls should stay within fictional tasks and retain complete records. Public data releases must respect source licences and remove credentials. AmongUs-X summaries are attributed under CC BY 4.0 [6].

## Appendix D LLM usage

AI assistance was used to inspect code, construct offline checks, prepare figures, and draft this report. Checked outputs are saved with executable scripts and input hashes. Earlier model outcomes are labelled as awaiting log review. The author must review the claims and author details before submission.
