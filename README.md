# Lock Before You Talk — Swarm Alignment Hackathon 2026

**One-line:** Do LLM swarm beliefs collapse to one voice under discussion, does a committed-independent-first-read rule stop it, and do same-weights copies agree before they talk?

Repo: https://github.com/vdimarco/apart-swarm-alignment · live report: https://lock-before-you-talk.vercel.app · slides: https://lock-before-you-talk.vercel.app/slides.html

Pre-registration and full design: [`docs/superpowers/specs/2026-11-07-lock-before-you-talk-design.md`](docs/superpowers/specs/2026-11-07-lock-before-you-talk-design.md)

Tracks: 2 (Science of Agent Networks) + 4 (Multi-Agent Oversight). Companion piece: "Why Towns Hang Their Own" (observational analysis of ~1,800 game-days of LLM social-deduction games from Dwarkesh Patel's **Blood on the Clocktower** LLM benchmark, pre-existing data collected before the sprint, marked as such everywhere it appears).

## Setup

```bash
cp .env.example .env   # then put your Adaption API key in .env
pip install -r requirements.txt
```

Adaption key: https://adaptionlabs.ai/app/settings?tab=api_keys → `ADAPTION_API_KEY` in `.env`.

## Run

```bash
python -m src.scenarios --check            # generate + validate scenario bank (no API)
python -m src.client --models              # list models your key grants
python -m src.run_smoke                    # 1 scenario, 1 panel, C1 only (key required)
python -m src.harness --config runs/arm_config.json --label main   # full sweep
python -m src.analyze --label main         # metrics + tables
```

## Pre-registration

Hypotheses H1–H4 frozen in the spec on 2026-11-07 before the first model call; spec git hash recorded in the commit log.

## Ethics / dual-use

All scenarios are fictional text riddles. No deceptive payloads are deployed anywhere, no real agent infrastructure touched. The manipulative "adversarial" scenarios mislead only the panel under study.
