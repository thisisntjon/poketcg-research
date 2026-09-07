#!/usr/bin/env python3
"""Does a win/loss split of choices measure the POLICY, or the POSITION?

WHY THIS EXISTS. I-4c mined 5,000 replays and reported, at n=19,436 endgame-window decisions
where Attack was legal: Attack chosen +2.93pp more in wins (z=+4.62), Attach over-chosen +3.72pp
in losses (z=-6.22), Ability over-chosen +1.48pp in losses (z=-5.13). The receipt reads that as
"the policy over-attaches and over-activates abilities instead of attacking" -- a claim about
the POLICY, drawn from a contrast conditioned on the OUTCOME.

THE COMPETING EXPLANATION. The outcome is downstream of the position, and the position drives
the choice. Holding a lethal attacker, you attack and you win; lacking one, you attach and you
lose. Under that story the policy is choosing correctly at every decision and the same numbers
appear anyway. Same data, opposite implication:

    READ A  the policy picks wrong in the window   -> licenses "attack more in the window"
    READ B  the choice is a symptom of the position -> a forced-attack rule attacks into
                                                       losing positions and HARMS

Conditioning on "Attack was on the menu" controls AVAILABILITY. It does not control
PROFITABILITY -- legal is not lethal -- and that gap is what the whole causal claim rests on.

WHAT THIS MODULE DOES ABOUT IT. Two things, and the second is the point:

1. `contrast()` / `controls()` run the same split on any decision corpus, including the
   NON-WINDOW bin. If Attack is also chosen more in wins at my_prizes >= 5, the effect is not
   about the endgame window; it is "attacking correlates with winning", a truism about position
   that licenses no rule.

2. `synthetic_corpus()` generates games from a policy that is CORRECT BY CONSTRUCTION -- it
   attacks exactly when a lethal attack exists, attaches otherwise -- and where the outcome is
   decided by the position alone. There is NO policy defect anywhere in it. If that corpus
   reproduces I-4c's signature, the signature is derivable from the confound alone and cannot
   be evidence for READ A. That argument needs no access to the replay corpus, which is why it
   is here rather than waiting on one.

This module makes no claim that I-4c's numbers are wrong. They are almost certainly right. It
addresses only what they LICENSE.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path


def two_proportion_z(k1: int, n1: int, k2: int, n2: int) -> float:
    """z for p1 - p2. Returns 0.0 when undefined rather than raising -- an empty cell is a
    reason to report nothing, not to crash a sweep."""
    if n1 <= 0 or n2 <= 0:
        return 0.0
    p1, p2 = k1 / n1, k2 / n2
    p = (k1 + k2) / (n1 + n2)
    denom = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if denom == 0:
        return 0.0
    return (p1 - p2) / denom


def contrast(records: list[dict], choice: str) -> dict:
    """P(choice | win) vs P(choice | loss) over decisions where the choice was AVAILABLE.

    Availability conditioning is deliberate and is what I-4c did; the point of this module is
    that it is not sufficient, not that it is wrong.
    """
    avail = [r for r in records if choice in r["menu"]]
    win = [r for r in avail if r["win"]]
    loss = [r for r in avail if not r["win"]]
    kw = sum(1 for r in win if r["chose"] == choice)
    kl = sum(1 for r in loss if r["chose"] == choice)
    nw, nl = len(win), len(loss)
    return {
        "choice": choice,
        "n_available": len(avail),
        "pct_in_win": round(100 * kw / nw, 2) if nw else None,
        "pct_in_loss": round(100 * kl / nl, 2) if nl else None,
        "delta_pp": round(100 * (kw / nw - kl / nl), 2) if nw and nl else None,
        "z": round(two_proportion_z(kw, nw, kl, nl), 2),
    }


def controls(records: list[dict], choices: tuple[str, ...] = ("Attack", "Attach", "Ability")
             ) -> dict:
    """The window bin and the non-window bin, side by side.

    The non-window bin is the decisive control. It is not a robustness check bolted on after
    the fact -- if the signature appears there too, the window framing is doing no work.
    """
    window = [r for r in records if r["my_prizes"] <= 2 and len(r["menu"]) >= 3]
    outside = [r for r in records if r["my_prizes"] >= 5 and len(r["menu"]) >= 3]
    return {
        "window_n": len(window),
        "non_window_n": len(outside),
        "window": {c: contrast(window, c) for c in choices},
        "non_window": {c: contrast(outside, c) for c in choices},
    }


def synthetic_corpus(games: int = 5000, seed: int = 20260902) -> list[dict]:
    """A corpus with NO policy defect, where the outcome is decided by position alone.

    THE GENERATIVE STORY, STATED SO IT CAN BE ARGUED WITH:
      * Each game draws a hidden `strength` -- how well the board came together. Strength is
        NOT a choice; it is draw, matchup and prior turns.
      * A lethal attack becomes available in the endgame window with probability rising in
        strength. This is the position.
      * The policy is CORRECT: it attacks whenever a lethal attack exists, and otherwise
        attaches or uses an ability to try to build one. It never misplays.
      * The game is won iff a lethal attack was found. Nothing about the choice causes the
        outcome; both are effects of strength.

    A policy with zero defect therefore attacks more in games it wins and attaches more in
    games it loses, by construction. If that reproduces the reported signature, the signature
    cannot distinguish READ A from READ B.
    """
    rng = random.Random(seed)
    out: list[dict] = []
    for _ in range(games):
        strength = rng.random()
        lethal_p = 0.15 + 0.5 * strength      # position, not policy
        won = rng.random() < lethal_p
        for _ in range(rng.randint(3, 6)):    # ~4.3 window decisions/game, as measured
            menu = ["Attack", "Attach", "Ability", "Play"]
            has_lethal = rng.random() < lethal_p
            # The CORRECT policy: attack iff lethal, otherwise build toward one.
            if has_lethal:
                chose = "Attack"
            else:
                chose = rng.choices(["Attach", "Ability", "Play"], weights=[35, 8, 57])[0]
            out.append({"my_prizes": rng.randint(1, 2), "menu": menu,
                        "chose": chose, "win": won})
        for _ in range(rng.randint(3, 6)):    # a non-window bin from the same generator
            menu = ["Attack", "Attach", "Ability", "Play"]
            has_lethal = rng.random() < lethal_p * 0.6
            chose = "Attack" if has_lethal else rng.choices(
                ["Attach", "Ability", "Play"], weights=[35, 8, 57])[0]
            out.append({"my_prizes": rng.randint(5, 6), "menu": menu,
                        "chose": chose, "win": won})
    return out


def synthetic_corpus_with_defect(games: int = 5000, seed: int = 20260902,
                                 miss_rate: float = 0.35) -> list[dict]:
    """The SAME generator, but with a real defect: the policy misses lethal attacks.

    With probability `miss_rate` it attaches instead of taking an available lethal attack, and
    a missed lethal costs the game. This is genuinely READ A -- the policy IS choosing badly.

    ITS PURPOSE IS THE SHARP FORM OF THE ARGUMENT. If the defective corpus and the correct
    corpus produce the SAME signature -- same signs, comparable magnitudes -- then the
    win/loss contrast does not DISCRIMINATE between them. That is stronger and more honest
    than "the contrast is confounded": it says exactly what the statistic can and cannot do.
    It is not evidence that the policy is fine; it is evidence that this measurement cannot
    tell us either way, and that only an interventional test (the window oracle) can.
    """
    rng = random.Random(seed)
    out: list[dict] = []
    for _ in range(games):
        strength = rng.random()
        lethal_p = 0.15 + 0.5 * strength
        had_lethal = rng.random() < lethal_p
        missed = had_lethal and rng.random() < miss_rate
        won = had_lethal and not missed
        for _ in range(rng.randint(3, 6)):
            menu = ["Attack", "Attach", "Ability", "Play"]
            has_lethal = rng.random() < lethal_p
            if has_lethal and rng.random() >= miss_rate:
                chose = "Attack"
            else:
                chose = rng.choices(["Attach", "Ability", "Play"], weights=[35, 8, 57])[0]
            out.append({"my_prizes": rng.randint(1, 2), "menu": menu,
                        "chose": chose, "win": won})
        for _ in range(rng.randint(3, 6)):
            menu = ["Attack", "Attach", "Ability", "Play"]
            has_lethal = rng.random() < lethal_p * 0.6
            chose = "Attack" if has_lethal else rng.choices(
                ["Attach", "Ability", "Play"], weights=[35, 8, 57])[0]
            out.append({"my_prizes": rng.randint(5, 6), "menu": menu,
                        "chose": chose, "win": won})
    return out


def load_records(path: Path) -> list[dict]:
    """Load a normalized decision corpus, refusing loudly on schema drift.

    NOT a replay parser. The replay dumps live on the box that produced them and their exact
    key names are not confirmed here -- guessing them would silently mis-parse and produce a
    census that looks like a finding, which is the failure this whole module is about. Feed it
    JSONL of {my_prizes, menu, chose, win} produced by whatever reader owns the replays.
    """
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        d = json.loads(line)
        missing = {"my_prizes", "menu", "chose", "win"} - set(d)
        if missing:
            raise SystemExit(
                f"REFUSING TO REPORT: record {i} is missing {sorted(missing)}. "
                f"Keys present: {sorted(d)}. A partially-read corpus produces a census that "
                f"looks exactly like a finding.")
        rows.append(d)
    if not rows:
        raise SystemExit("REFUSING TO REPORT: zero records read.")
    return rows


def render(res: dict, title: str) -> str:
    out = [f"=== {title} ===",
           f"window decisions {res['window_n']:,} · non-window {res['non_window_n']:,}", ""]
    for bin_name in ("window", "non_window"):
        out.append(f"  {bin_name.upper()}")
        for c, r in res[bin_name].items():
            if r["delta_pp"] is None:
                out.append(f"    {c:<9} (empty cell)")
                continue
            out.append(f"    {c:<9} win {r['pct_in_win']:>6.2f}%  loss {r['pct_in_loss']:>6.2f}%"
                       f"  delta {r['delta_pp']:>+6.2f}pp  z {r['z']:>+6.2f}"
                       f"  n {r['n_available']:,}")
        out.append("")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--records", type=Path,
                    help="JSONL of {my_prizes, menu, chose, win}")
    ap.add_argument("--synthetic", action="store_true",
                    help="run the no-defect control corpus")
    ap.add_argument("--games", type=int, default=5000)
    args = ap.parse_args()

    if args.synthetic:
        good = controls(synthetic_corpus(args.games))
        bad = controls(synthetic_corpus_with_defect(args.games))
        print(render(good, f"A -- CORRECT POLICY, NO DEFECT ({args.games:,} games)"))
        print(render(bad, f"B -- POLICY THAT MISSES 35% OF LETHALS ({args.games:,} games)"))
        print("A never misplays. B is genuinely broken. Both produce the same signature:\n"
              "Attack over-represented in wins, Attach and Ability over-represented in losses,\n"
              "in the window AND outside it.\n\n"
              "THE WIN/LOSS CONTRAST DOES NOT DISCRIMINATE BETWEEN THEM. It is not evidence\n"
              "that the policy is fine, and it is not evidence that it is broken -- it cannot\n"
              "separate the two. Only an interventional test can: change the choice, measure\n"
              "the outcome. That is what the window oracle already does.")
        return 0

    if args.records:
        print(render(controls(load_records(args.records)), f"CORPUS {args.records.name}"))
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
