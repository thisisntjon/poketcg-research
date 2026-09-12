#!/usr/bin/env python3
"""Recount the historical six-implementation sensitivity; no game execution."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def compute(rows: list[dict[str, str]]) -> dict:
    require(len(rows) == 8400, "Expected all 8,400 panel records")
    cells = {f"P{i:02d}" for i in range(1, 8)}
    require({r["opponent_id"] for r in rows} == cells, "Opponent identities changed")
    counts = Counter()
    seen = set()
    scores = {c: {a: [] for a in ("BASELINE", "COMBINED")} for c in cells}
    for row in rows:
        require(row["run"] == "seven_opponent_panel", "Unexpected cohort")
        require(row["arm"] in ("BASELINE", "COMBINED"), "Unexpected arm")
        require(row["seat"] in ("first", "second"), "Unexpected seat")
        require(row["outcome"] in ("win", "draw", "loss"), "Unexpected outcome")
        key = (row["run"], row["arm"], row["opponent_id"], row["game_index"])
        require(key not in seen, "Duplicate game identity")
        seen.add(key)
        counts[(row["opponent_id"], row["arm"], row["seat"])] += 1
        scores[row["opponent_id"]][row["arm"]].append(
            {"win": 1.0, "draw": 0.5, "loss": 0.0}[row["outcome"]]
        )
    require(len(counts) == 28 and set(counts.values()) == {300}, "Seat/cell balance changed")
    per_cell = {}
    for cell in sorted(cells):
        baseline, champion = scores[cell]["BASELINE"], scores[cell]["COMBINED"]
        p0, p1 = sum(baseline) / len(baseline), sum(champion) / len(champion)
        # Deliberately reproduce the historical p*(1-p)/n approximation.
        # Current figure intervals instead use sample variance of fractional scores / n.
        variance = 10000 * (p0 * (1 - p0) / len(baseline) + p1 * (1 - p1) / len(champion))
        per_cell[cell] = {"delta_pp": 100 * (p1 - p0), "variance_pp2": variance}
    selected = [per_cell[c] for c in sorted(cells) if c != "P01"]
    weights = [1 / x["variance_pp2"] for x in selected]
    deltas = [x["delta_pp"] for x in selected]
    fixed = sum(w * d for w, d in zip(weights, deltas)) / sum(weights)
    q = sum(w * (d - fixed) ** 2 for w, d in zip(weights, deltas))
    df = len(selected) - 1
    denominator = sum(weights) - sum(w * w for w in weights) / sum(weights)
    tau2 = max(0, (q - df) / denominator)
    random_weights = [1 / (x["variance_pp2"] + tau2) for x in selected]
    delta = sum(w * d for w, d in zip(random_weights, deltas)) / sum(random_weights)
    se = math.sqrt(1 / sum(random_weights))
    result = {
        "records": len(rows), "selected_records": 7200, "excluded_opponent_id": "P01",
        "selected_opponent_ids": [f"P{i:02d}" for i in range(2, 8)],
        "draw_score": 0.5, "method": "Historical DerSimonian-Laird; p*(1-p)/n arm variance",
        "delta_pp": delta, "se_pp": se, "ci95_pp": [delta - 1.96 * se, delta + 1.96 * se],
        "q": q, "df": df, "i2_percent": max(0, (q - df) / q) * 100,
        "tau2_pp2": tau2, "per_cell": per_cell,
    }
    require(abs(delta - 2.72) < 0.005, "Published effect mismatch")
    require(abs(result["ci95_pp"][0] - (-3.29)) < 0.005, "Published lower limit mismatch")
    require(abs(result["ci95_pp"][1] - 8.74) < 0.005, "Published upper limit mismatch")
    require(result["ci95_pp"][0] < 0 < result["ci95_pp"][1], "Conclusion changed")
    return result


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=Path, default=here.parent / "numerical" / "panel-outcomes.csv")
    parser.add_argument("--opponents", type=Path, default=here.parent / "numerical" / "opponents.json")
    args = parser.parse_args()
    manifest = json.loads((here / "SOURCE-MANIFEST.json").read_text(encoding="utf-8"))
    for name, path in (("panel-outcomes.csv", args.rows), ("opponents.json", args.opponents)):
        require(sha(path) == manifest["inputs"][name]["sha256"], f"Input hash mismatch: {name}")
    for item in manifest["exports"]:
        require(sha(here / item["path"]) == item["sha256"], f"Supplement hash mismatch: {item['path']}")
    opponents = json.loads(args.opponents.read_text(encoding="utf-8"))
    require(opponents["P01"]["shares_development_deck"] is True, "Exclusion no longer matches metadata")
    require(opponents["P01"]["deck_sha256"] == manifest["excluded_deck_sha256"], "Excluded deck changed")
    with args.rows.open(encoding="utf-8", newline="") as handle:
        result = compute(list(csv.DictReader(handle)))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"VERIFICATION FAILED: {error}")
