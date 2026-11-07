# The Evidence Jigsaw (M6J arm)

**One-line:** split the clues across panel members so priors decorrelate by construction — the only intervention measured to move any number in the remedy arc, and a *partial, lossy* one.

## Mechanism

- 6-agent mixed panel (`qwen3.5-397b`, `glm-5.2`, `qwen3.8-27b`, `deepseek-v4-flash`, `gemma-4-31b-it`, `gemma-4-26b-a4b-it`).
- Each case file has 4 witness clues. Each clue is shown to **3 of 6 agents**, assigned round-robin on a per-scenario-seeded shuffle (`clue_partition(..., copies=3)`). Every agent sees every suspect; no agent sees every clue.
- Baseline arms see the full case file. Everything else identical: same 30 validated scenarios, same elicitation format, same 2-round anonymized discussion for C2.

## Measured result (2,947+1,780 logged calls, 60 panels/cell)

| | initial ρ | final ρ | N_eff final (n=6) | panel accuracy |
|---|---|---|---|---|
| Full-info C2 (M6) | 0.880 | 0.982 | 1.02 | 100% |
| **Jigsaw C2 (M6J)** | **0.685** | **0.847** | **1.15** | **87%** |
| Jigsaw C1 (no discussion) | 0.683 | — | — | — |

## Honest verdict

- Priors decorrelate by ~20 points (0.875 → 0.685). Real.
- Deliberation still converges the final vote: **65% of the prior-decorrelation gain is surrendered** during two discussion rounds (N_eff 1.36 → 1.15).
- The cost is information-loss itself: 13 points of accuracy.
- Classification: **partial input de-correlator, not a deliberation fix**. Nothing measured (commitment C3, forced dissent M6DA, jigsaw C2) protects independence *through* consensus; final N_eff stays ≈ 1.0–1.15 of 6 in every condition.

## Reproduce

```bash
python -m src.harness --config runs/arm_config_pushJ.json --label pushJ   # ~1,800 calls
python -m src.analyze --label mg && python runs/figures.py                # metrics + svg figs
```

Numbers regenerate from `runs/pushJ.jsonl` / `runs/mg.jsonl` only. Any figure not traceable there belongs nowhere near the report.
