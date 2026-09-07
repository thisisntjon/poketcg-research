#!/usr/bin/env python3
"""Auto-forensics: cluster losses from raw games.jsonl to surface failure modes.

PILLAR 1 of the scaling charter. The charter names a 5D failure vector
(delta_prizes, relative_deck_pressure, active_energy, target_wall_hp, game_turn).

SCHEMA REALITY, checked before this file was written rather than after:

    delta_prizes            AVAILABLE  prize_margin / *_prize_remaining
    relative_deck_pressure  AVAILABLE  u6.deck_counts (both seats, at game end)
    game_turn               AVAILABLE  turns
    active_energy           ABSENT     no such field on any row
    target_wall_hp          ABSENT     no such field on any row

The last two are PER-DECISION BOARD STATE. games.jsonl records how a game ENDED, not the
board at any point during it, so no value of n recovers them -- they need traces. This
module therefore clusters on the 3 dimensions that exist and says so, rather than
silently inventing proxies for the 2 that do not. Extend it when traces are available.

Usage:
  python scripts/loss_clustering.py <games.jsonl> [more.jsonl ...] [--opponent KEY] [--k N]
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

FEATURES = ("delta_prizes", "deck_pressure", "game_turn")


def load_losses(paths: list[Path], opponent: str | None) -> list[dict]:
    rows = []
    for p in paths:
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("error") or r.get("outcome") != "loss":
                continue
            if opponent and r.get("opponent") != opponent:
                continue
            f = featurise(r)
            if f is not None:
                rows.append({"row": r, "f": f})
    return rows


def featurise(r: dict) -> dict | None:
    """3D vector. Returns None if a required field is missing -- never a guessed default.

    u6.deck_counts is SEAT-INDEXED, not candidate-first, and our seat alternates roughly
    50/50. Reading decks[1] as "the opponent" is wrong in half of all games and produced a
    phantom bimodal result on 2026-09-03 that had to be retracted. On a LOSS we are the
    loser, so u6.loser_seat identifies us; the opponent is the other index. Proven on 527
    deckout losses: decks[loser_seat] == 0 in 527/527, decks[0] == 0 in only 274/527.
    """
    u6 = r.get("u6") or {}
    decks = u6.get("deck_counts")
    ls = u6.get("loser_seat")
    turns = r.get("turns")
    margin = r.get("prize_margin")
    if not (isinstance(decks, list) and len(decks) >= 2):
        return None
    if ls not in (0, 1) or turns is None or margin is None:
        return None
    ours, theirs = decks[ls], decks[1 - ls]
    # (theirs - ours)/total, so the sign reads as DECK PRESSURE ON US:
    #   +1 = WE were empty while they still held cards  (a deckout loss MUST sit here)
    #   -1 = they were empty while we still held cards
    # Self-check for the next reader: cluster the deckout losses and confirm they land at
    # +1. If they land at -1 the seat indexing has been broken again.
    total = (ours + theirs) or 1
    return {"delta_prizes": float(margin),
            "deck_pressure": (theirs - ours) / total,
            "game_turn": float(turns)}


def zscore(rows: list[dict]) -> tuple[list[list[float]], dict]:
    stats = {}
    for k in FEATURES:
        vals = [x["f"][k] for x in rows]
        mu = statistics.mean(vals)
        sd = statistics.pstdev(vals) or 1.0
        stats[k] = (mu, sd)
    return [[(x["f"][k] - stats[k][0]) / stats[k][1] for k in FEATURES] for x in rows], stats


def kmeans(X: list[list[float]], k: int, iters: int = 60, seed: int = 0) -> list[int]:
    """Deterministic k-means++ init. No sklearn dependency in the harness."""
    import random
    rng = random.Random(seed)
    cents = [X[rng.randrange(len(X))]]
    while len(cents) < k:
        d2 = [min(sum((a - b) ** 2 for a, b in zip(x, c)) for c in cents) for x in X]
        tot = sum(d2) or 1.0
        pick, acc = rng.random() * tot, 0.0
        for i, d in enumerate(d2):
            acc += d
            if acc >= pick:
                cents.append(X[i])
                break
        else:
            cents.append(X[-1])
    lab = [0] * len(X)
    for _ in range(iters):
        moved = False
        for i, x in enumerate(X):
            best = min(range(k), key=lambda c: sum((a - b) ** 2
                                                   for a, b in zip(x, cents[c])))
            if best != lab[i]:
                lab[i], moved = best, True
        for c in range(k):
            pts = [X[i] for i in range(len(X)) if lab[i] == c]
            if pts:
                cents[c] = [sum(col) / len(pts) for col in zip(*pts)]
        if not moved:
            break
    return lab


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--opponent", default=None)
    ap.add_argument("--k", type=int, default=3)
    a = ap.parse_args()

    rows = load_losses(a.paths, a.opponent)
    if not rows:
        print("no losses with a complete 3D vector among the inputs; nothing to cluster")
        return 0
    print(f"losses with a complete vector: {len(rows)}")
    print(f"clustering on {FEATURES} -- active_energy and target_wall_hp are ABSENT "
          f"from games.jsonl and are NOT substituted")

    X, _ = zscore(rows)
    lab = kmeans(X, a.k)

    for c in range(a.k):
        idx = [i for i in range(len(rows)) if lab[i] == c]
        if not idx:
            continue
        f = [rows[i]["f"] for i in idx]
        reasons = Counter(rows[i]["row"].get("end_reason_detail") or "?" for i in idx)
        opps = Counter(rows[i]["row"].get("opponent") or "?" for i in idx)
        print(f"\nCLUSTER {c}  n={len(idx)} ({100*len(idx)/len(rows):.1f}%)")
        print(f"  delta_prizes   median {statistics.median(x['delta_prizes'] for x in f):+.1f}")
        print(f"  deck_pressure  median {statistics.median(x['deck_pressure'] for x in f):+.2f}"
              f"   (+1 = WE were empty, -1 = they were)")
        print(f"  game_turn      median {statistics.median(x['game_turn'] for x in f):.0f}")
        print(f"  end_reason     {dict(reasons.most_common(3))}")
        print(f"  opponents      {dict(opps.most_common(3))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
