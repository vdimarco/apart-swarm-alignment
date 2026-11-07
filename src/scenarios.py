"""Scenario bank generator for 'Lock Before You Talk'.

Deterministically generates village case files with provably unique culprits:
- consistent: clues jointly identify exactly one suspect (surface reading agrees)
- adversarial: loud repeated clues point at an innocent decoy; one quiet clue
  rules the decoy out; full reading identifies the culprit
- placebo: clue sets rotated across scenarios so the evidence is inert
"""
from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path

TRAITS: dict[str, str] = {
    "red_scarf": "a red wool scarf",
    "heavy_limp": "a heavy limp",
    "oil_lantern": "an oil lantern",
    "large_dog": "a large grey dog",
    "white_gloves": "white gloves",
    "tall_hat": "a tall felt hat",
    "wooden_flute": "a wooden flute",
    "brass_key": "a brass gate key",
    "flour_apron": "an apron dusted with flour",
    "green_coat": "a green raincoat",
}

NAMES = [
    "Amara", "Bram", "Cora", "Dain", "Elsa", "Fen", "Greta", "Hugo",
    "Ida", "Joss", "Kael", "Lev", "Mira", "Nils", "Oda", "Pavel",
]

ROLES = [
    "baker", "miller", "blacksmith", "schoolteacher", "shepherd",
    "clerk", "midwife", "cotter", "brewer", "watchman",
]

WITNESSES = [
    "Old Tomas", "Widow Ferne", "the gatekeeper", "Young Piotr",
    "the candlemaker", "a travelling tinker", "Sister Mellis", "the mill hand",
]

PLACES = [
    "mill bridge", "well", "chapel yard", "market square", "orchard gate",
    "tannery lane", "old fence", "granary steps",
]

TITLES = [
    ("The Disturbed Shrine", "Someone broke the votive lamps at the shrine and took the offering box. It happened in the hour before the watch bell."),
    ("The Poisoned Well", "Dead fish floated in the lower well by morning; someone had dumped tannery slops there overnight."),
    ("The Granary Theft", "Two sacks of winter grain vanished from the granary; the lock was not forced."),
    ("The Burned Hayrick", "The east hayrick went up in flames just after midnight, and the night's rain never came."),
    ("The Cut Bell Rope", "The chapel bell rope was cut through and the bell could not ring the dawn watch."),
]

LOUD_TEMPLATES = [
    "Several villagers insist they saw someone with {trait} heading toward the {place} that night.",
    "Both {w1} and {w2} swear the figure they saw was someone with {trait}.",
    "{w1} is certain: whoever it was, it was someone with {trait}. It was said twice before breakfast.",
    "At the inn, three people separately described someone with {trait} crossing the {place}.",
]

MID_TEMPLATES = [
    "{w1} saw someone with {trait} near the {place} that night.",
    "{w1} told the council the figure was someone with {trait}.",
]

QUIET_TEMPLATES = [
    "One villager mentioned, almost as an afterthought, someone with {trait} by the {place}.",
    "In passing, {w1} recalled noticing someone with {trait} near the {place}.",
    "Only {w1} remarked on it at all: someone with {trait}, seen by the {place}.",
]


@dataclass
class Suspect:
    name: str
    role: str
    traits: list[str]


@dataclass
class Scenario:
    id: str
    kind: str  # "consistent" | "adversarial" | "placebo"
    title: str
    story: str
    suspects: list[Suspect]
    clues: list[str]                # rendered text
    clue_traits: list[str]          # trait id each clue references (for checking)
    loud_traits: list[str] = field(default_factory=list)  # salient subset (adversarial)
    ground_truth: str | None = None
    decoy: str | None = None


def _matches(traits_needed: list[str], suspects: list[Suspect]) -> list[str]:
    """Names of suspects possessing every trait in traits_needed."""
    return [s.name for s in suspects if all(t in s.traits for t in traits_needed)]


def _draw_suspects(rng: random.Random) -> list[Suspect]:
    names = rng.sample(NAMES, 6)
    roles = rng.sample(ROLES, 6)
    suspects: list[Suspect] = []
    seen: set[frozenset[str]] = set()
    for n, r in zip(names, roles):
        # keep trait sets distinct per suspect
        for _ in range(50):
            traits = rng.sample(list(TRAITS), 3)
            if frozenset(traits) not in seen:
                break
        else:
            traits = rng.sample(list(TRAITS), 3)
        seen.add(frozenset(traits))
        suspects.append(Suspect(name=n, role=r, traits=traits))
    return suspects


def _render_suspect_line(s: Suspect) -> str:
    parts = [TRAITS[t] for t in s.traits]
    desc = ", ".join(parts[:-1]) + f", and {parts[-1]}"
    return f"- {s.name}, the {s.role}. Known about the village for {desc}."


def _clue_text(trait: str, kind: str, rng: random.Random) -> str:
    tmpl = rng.choice({"loud": LOUD_TEMPLATES, "mid": MID_TEMPLATES, "quiet": QUIET_TEMPLATES}[kind])
    w1, w2 = rng.sample(WITNESSES, 2)
    return tmpl.format(trait=TRAITS[trait], place=rng.choice(PLACES), w1=w1, w2=w2)


def _gen_one(seed: int, idx: int, kind: str) -> Scenario:
    rng = random.Random(seed * 1009 + idx * 9176 + (0 if kind == "consistent" else 4021))
    title, story = TITLES[idx % len(TITLES)]
    for _attempt in range(400):
        suspects = _draw_suspects(rng)
        culprit = rng.choice(suspects)
        if kind == "consistent":
            # pick 3 of the culprit's traits s.t. only the culprit matches all
            for clue_size in (3, 2):
                for subset in rng.sample(
                    [c for c in _combos(culprit.traits, clue_size)],
                    k=min(6, len(_combos(culprit.traits, clue_size))),
                ):
                    if _matches(list(subset), suspects) == [culprit.name]:
                        clue_traits = list(subset)
                        loud = clue_traits[:2]
                        clues = (
                            [_clue_text(t, "loud", rng) for t in loud]
                            + [_clue_text(t, "mid", rng) for t in clue_traits[2:]]
                        )
                        return Scenario(
                            id=f"C{idx:02d}", kind=kind, title=title, story=story,
                            suspects=suspects, clues=clues, clue_traits=clue_traits,
                            loud_traits=loud, ground_truth=culprit.name,
                        )
            continue
        # adversarial: need a decoy sharing >=2 traits with the culprit
        decoys = [s for s in suspects if s is not culprit and len(set(s.traits) & set(culprit.traits)) >= 2]
        rng.shuffle(decoys)
        for decoy in decoys:
            shared = sorted(set(decoy.traits) & set(culprit.traits))
            quiet_opts = [t for t in culprit.traits if t not in decoy.traits]
            if len(shared) < 2 or not quiet_opts:
                continue
            loud = shared[:2]
            quiet = quiet_opts[0]
            clue_traits = [loud[0], loud[0], loud[1], quiet]  # loud trait 1 said twice
            if _matches(clue_traits, suspects) != [culprit.name]:
                continue
            if decoy.name not in _matches(loud, suspects):
                continue
            clues = (
                [_clue_text(loud[0], "loud", rng), _clue_text(loud[0], "loud", rng)]
                + [_clue_text(loud[1], "mid", rng)]
                + [_clue_text(quiet, "quiet", rng)]
            )
            return Scenario(
                id=f"A{idx:02d}", kind=kind, title=title, story=story,
                suspects=suspects, clues=clues, clue_traits=clue_traits,
                loud_traits=loud, ground_truth=culprit.name, decoy=decoy.name,
            )
    raise RuntimeError(f"could not generate a valid {kind} scenario idx={idx}")


def _combos(items: list[str], k: int) -> list[tuple[str, ...]]:
    from itertools import combinations
    return list(combinations(items, min(k, len(items))))


def make_placebo(scenarios: list[Scenario], seed: int) -> list[Scenario]:
    """Rotate clue sets across scenarios so evidence becomes inert."""
    rng = random.Random(seed * 31 + 7)
    real = [s for s in scenarios if s.kind != "placebo"]
    offset = rng.randrange(1, len(real))
    out = []
    for i, s in enumerate(real):
        donor = real[(i + offset) % len(real)]
        clues = [_clue_text(t, "mid", rng) for t in donor.clue_traits]
        out.append(Scenario(
            id=f"P{i:02d}", kind="placebo", title=s.title, story=s.story,
            suspects=s.suspects, clues=clues, clue_traits=donor.clue_traits,
            ground_truth=None,
        ))
    return out


def render_text(s: Scenario) -> str:
    lines = [
        f"# {s.title}",
        "",
        s.story,
        "",
        "The council has named six suspects.",
        "",
        "SUSPECTS",
        *[_render_suspect_line(x) for x in s.suspects],
        "",
        "WITNESS STATEMENTS",
        *[f"- {c}" for c in s.clues],
    ]
    return "\n".join(lines)


def validate(scenarios: list[Scenario]) -> list[str]:
    errs = []
    for s in scenarios:
        if s.kind == "placebo":
            continue
        m = _matches(s.clue_traits, s.suspects)
        if m != [s.ground_truth]:
            errs.append(f"{s.id}: matches={m} truth={s.ground_truth}")
        if s.kind == "adversarial":
            loud_matches = _matches(s.loud_traits, s.suspects)
            if s.decoy not in loud_matches or len(loud_matches) < 2:
                errs.append(f"{s.id}: loud matches={loud_matches} decoy={s.decoy}")
    return errs


def generate(seed: int = 20261107, n_consistent: int = 20, n_adversarial: int = 10) -> list[Scenario]:
    scenarios = [_gen_one(seed, i, "consistent") for i in range(n_consistent)]
    scenarios += [_gen_one(seed, i, "adversarial") for i in range(n_adversarial)]
    scenarios += make_placebo(scenarios, seed)
    errs = validate(scenarios)
    if errs:
        raise RuntimeError("scenario validation failed:\n" + "\n".join(errs))
    return scenarios


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="generate, validate, print summary + one sample")
    ap.add_argument("--out", default="runs/scenarios.json")
    ap.add_argument("--seed", type=int, default=20261107)
    args = ap.parse_args()

    scenarios = generate(seed=args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps([asdict(s) for s in scenarios], indent=2))

    from collections import Counter
    kinds = Counter(s.kind for s in scenarios)
    print(f"generated {len(scenarios)} scenarios -> {out} ({dict(kinds)})")
    if args.check:
        ad = [s for s in scenarios if s.kind == "adversarial"]
        loud_sizes = [len(_matches(s.loud_traits, s.suspects)) for s in ad]
        print(f"adversarial: truth unique in all {len(ad)}; loud-subset match counts {sorted(loud_sizes)}")
        sample = next(s for s in scenarios if s.kind == "adversarial")
        print("\n----- sample adversarial scenario -----\n")
        print(render_text(sample))
        print(f"\n(ground truth: {sample.ground_truth}, decoy: {sample.decoy})")


if __name__ == "__main__":
    main()
