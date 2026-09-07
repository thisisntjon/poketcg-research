#!/usr/bin/env python
"""Recompute every published Strike 3 figure from the committed rows, in one command.

    python workflow/research/2026-09-03-strike3-recompute.py

Reads ONLY `2026-09-03-strike3-rows.csv` (8,400 rows, committed alongside this file) and
reprints the numbers in `2026-09-03-strike3-generalisation.md`. No network, no harness, no
games, no machine-local paths -- the CSV is resolved relative to this file.

WHY THIS EXISTS. The writeup's rows were banked but the analysis was not, so verifying
`+19.51pp`, the `I2 = 0.0%` vs `92.9%` contrast, or the `7.51pp` detection floor meant
reimplementing DerSimonian-Laird, Cochran Q and the draw convention from prose. The data was
always sufficient; it was not turnkey. This closes that gap and nothing else -- it STRENGTHENS
a true claim rather than fixing a false one (STRATEGIST, 2026-09-03T23:59Z).

CONVENTION. Draws score as HALF a win, over all games, because that is what the harness that
produced these rows does (`eval.py` on origin/main:1271, `score = wins + 0.5 * draws`). Neither
of the two conventions the fleet argued about all evening was the instrument's own. Pass
`--draws loss|excluded` to reproduce the alternatives shown in the writeup's sensitivity table.

Exit 0 if every recomputed figure matches the published value within 0.02pp, else 1.
"""
from __future__ import annotations

import argparse
import csv
import math
import pathlib
import sys

ROWS = pathlib.Path(__file__).with_name("2026-09-03-strike3-rows.csv")

EXPOSED = "tb_567ea9be_llccqq624_ptcg-alakazam-marniebelief-0723-a"  # shares a dev deck
CLEAN = "tb_64e9991a_raunakdey07_pok-mon-tcg-advanced-heuristic-agent"
ALAKAZAM = {EXPOSED, CLEAN}

# Published in 2026-09-03-strike3-generalisation.md under the harness convention.
PUBLISHED = {
    "alakazam_pooled": 19.51,
    "clean_six_re": 2.72,
    "all_seven_re": 5.21,
    "detection_floor": 7.51,
    "seat_gap_alakazam": -0.17,
    "seat_gap_pooled": 3.00,
}


def load():
    """Read the rows and refuse to compute on an incomplete file.

    Without this a truncated CSV dies inside the arithmetic with a ZeroDivisionError,
    which tells the reader nothing about what is wrong. Say it plainly instead.
    """
    if not ROWS.exists():
        sys.exit(f"rows file not found next to this script: {ROWS.name}")
    with open(ROWS, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    counts = {}
    for g in rows:
        counts[(g["arm"], g["opponent"])] = counts.get((g["arm"], g["opponent"]), 0) + 1
    cells = sorted({g["opponent"] for g in rows})
    problems = []
    if len(rows) != 8400:
        problems.append(f"expected 8,400 rows, found {len(rows)}")
    if len(cells) != 7:
        problems.append(f"expected 7 opponents, found {len(cells)}")
    for c in cells:
        for arm in ("BASELINE", "CHAMPION"):
            n = counts.get((arm, c), 0)
            if n != 600:
                problems.append(f"{arm} x {c}: expected 600 games, found {n}")
    if problems:
        sys.exit("INCOMPLETE DATA -- refusing to compute:\n  "
                 + "\n  ".join(problems))
    return rows


def rate(games, conv):
    """Score and DENOMINATOR under the chosen draw convention.

    Returns both, not just the ratio, because the variance must use the same n the rate
    was computed on. Under `excluded` the denominator is decisive games only, which is
    smaller than len(games) -- see the note in delta().
    """
    w = sum(1 for g in games if g["outcome"].lower() == "win")
    l = sum(1 for g in games if g["outcome"].lower() == "loss")
    d = sum(1 for g in games if g["outcome"].lower() == "draw")
    if conv == "half":          # harness: eval.py origin/main:1271
        return w + 0.5 * d, w + l + d
    if conv == "loss":          # draws counted as non-wins
        return w, w + l + d
    if conv == "excluded":      # decisive games only
        return w, w + l
    raise ValueError(conv)


def delta(rows, pred, conv):
    """Champion minus baseline, as a percentage-point difference, with its variance.

    The variance uses the denominator `rate()` actually divided by. An earlier version
    hardcoded len(games) here, which was right for `half` and `loss` -- where the
    denominator IS every game -- and WRONG for `excluded`, where draws leave the
    denominator. That inflated Q from 83.87 to 84.08 on the seven-cell pool and made the
    published draws-excluded sensitivity disagree with an independent recompute. The
    default (`half`) path and every published figure were unaffected.
    """
    b = [g for g in rows if g["arm"] == "BASELINE" and pred(g)]
    c = [g for g in rows if g["arm"] == "CHAMPION" and pred(g)]
    k0, n0 = rate(b, conv)
    k1, n1 = rate(c, conv)
    p0, p1 = k0 / n0, k1 / n1
    d = 100 * (p1 - p0)
    v = 1e4 * (p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
    return d, v


def pool(items):
    """Fixed- and random-effects (DerSimonian-Laird) pooling of per-cell deltas."""
    ws = [1 / v for _, v in items]
    ds = [d for d, _ in items]
    fe = sum(w * d for w, d in zip(ws, ds)) / sum(ws)
    se_fe = math.sqrt(1 / sum(ws))
    q = sum(w * (d - fe) ** 2 for w, d in zip(ws, ds))
    k = len(items)
    if k > 1:
        c = sum(ws) - sum(w * w for w in ws) / sum(ws)
        tau2 = max(0.0, (q - (k - 1)) / c)
    else:
        tau2 = 0.0
    w2 = [1 / (v + tau2) for _, v in items]
    re = sum(w * d for w, d in zip(w2, ds)) / sum(w2)
    se_re = math.sqrt(1 / sum(w2))
    i2 = max(0.0, (q - (k - 1)) / q) * 100 if q > 0 else 0.0
    return fe, se_fe, re, se_re, q, k - 1, i2


def ci(d, se):
    return f"[{d - 1.96 * se:+.2f}, {d + 1.96 * se:+.2f}]"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--draws", choices=("half", "loss", "excluded"), default="half",
                    help="draw convention; 'half' is the harness's own (default)")
    args = ap.parse_args()
    conv = args.draws

    rows = load()
    print(f"rows: {len(rows)}   draw convention: {conv}"
          f"{'  (harness, eval.py origin/main:1271)' if conv == 'half' else ''}\n")

    cells = sorted({g["opponent"] for g in rows})
    per_cell = {}
    print(f"{'cell':52s} {'delta':>8s} {'SE':>6s}  {'archetype':>9s}")
    for c in cells:
        d, v = delta(rows, lambda g, c=c: g["opponent"] == c, conv)
        per_cell[c] = (d, v)
        tag = "ALAKAZAM" if c in ALAKAZAM else "-"
        print(f"{c[:52]:52s} {d:+8.2f} {math.sqrt(v):6.2f}  {tag:>9s}")

    got = {}
    print()
    for label, sel, key in (
        ("ALL SEVEN", cells, "all_seven_re"),
        ("CLEAN SIX (headline)", [c for c in cells if c != EXPOSED], "clean_six_re"),
        ("ALAKAZAM pair", [c for c in cells if c in ALAKAZAM], "alakazam_pooled"),
    ):
        items = [per_cell[c] for c in sel]
        fe, sfe, re_, sre, q, df, i2 = pool(items)
        got[key] = re_ if key != "alakazam_pooled" else fe
        print(f"{label}  (k={len(items)})")
        print(f"   fixed  {fe:+6.2f}pp {ci(fe, sfe)}")
        print(f"   random {re_:+6.2f}pp {ci(re_, sre)}")
        print(f"   Q={q:.2f} on {df} df   I2={i2:.1f}%")

    a, b = per_cell[EXPOSED], per_cell[CLEAN]
    floor = 1.96 * math.sqrt(a[1] + b[1])
    got["detection_floor"] = floor
    print(f"\nsmallest cell-to-cell difference detectable at 95%: {floor:.2f}pp"
          f"   (observed difference {abs(a[0] - b[0]):.2f}pp)")

    print("\nseat gaps (first - second)")
    for label, pred, key in (
        ("Alakazam", lambda g: g["opponent"] in ALAKAZAM, "seat_gap_alakazam"),
        ("non-Alakazam", lambda g: g["opponent"] not in ALAKAZAM, None),
        ("pooled", lambda g: True, "seat_gap_pooled"),
    ):
        df_, vf = delta(rows, lambda g, p=pred: p(g) and g["seat"] == "first", conv)
        ds_, vs = delta(rows, lambda g, p=pred: p(g) and g["seat"] == "second", conv)
        gap, gse = df_ - ds_, math.sqrt(vf + vs)
        if key:
            got[key] = gap
        print(f"   {label:14s} first {df_:+6.2f}  second {ds_:+6.2f}  "
              f"gap {gap:+6.2f} {ci(gap, gse)}")

    if conv != "half":
        print("\n(published values are stated under the harness convention; "
              "skipping the match check)")
        return 0

    print("\ncheck against the published values")
    worst = 0.0
    for key, want in PUBLISHED.items():
        have = got[key]
        worst = max(worst, abs(have - want))
        flag = "ok " if abs(have - want) <= 0.02 else "MISMATCH"
        print(f"   {flag} {key:20s} recomputed {have:+7.2f}  published {want:+7.2f}")
    print(f"\nworst deviation: {worst:.4f}pp")
    return 0 if worst <= 0.02 else 1


if __name__ == "__main__":
    sys.exit(main())
