"""Verify retained aggregate bytes and recalculate their arithmetic; no training."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import platform
import statistics
import sys


EXPECTED = {
    "repr_probe_01_summary.json": "df1f04deef1fa7ce98ff421a920cfd1977a68cfde243c0df33656deabb46d888",
    "cache_meta.json": "f7506ddc1e1d9d3fe015030057404bcd5c07db5a8ab4cade63152a090503a1a1",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    base = Path(__file__).resolve().parent
    loaded = {}
    for name, expected in EXPECTED.items():
        data = (base / name).read_bytes()
        require(hashlib.sha256(data).hexdigest() == expected, f"Source hash mismatch: {name}")
        loaded[name] = json.loads(data)

    receipt = loaded["repr_probe_01_summary.json"]
    meta = loaded["cache_meta.json"]
    require(receipt["schema"] == "ptcg.repr_probe.receipt/v1", "Unexpected receipt schema")
    require(meta["schema"] == "ptcg.repr_probe_cache/v1", "Unexpected cache schema")
    require(receipt["seeds"] == [0, 1, 2], "Unexpected seed list")
    require(meta["n_examples"] == 44343, "Unexpected example count")
    require((meta["state_dim"], meta["n_options"], meta["n_opt_feats"]) == (148, 16, 4),
            "Unexpected cache dimensions")
    runs = receipt["runs"]
    require(len(runs) == 6, "Expected six arm/seed rows")
    by_key = {}
    for row in runs:
        require(type(row["use_ids"]) is bool and type(row["seed"]) is int,
                "Invalid arm/seed types")
        key = (row["use_ids"], row["seed"])
        require(key not in by_key, f"Duplicate arm/seed: {key}")
        require(0 < row["n_val"] <= meta["n_examples"], "Invalid validation count")
        require(0 <= row["n_val_tied"] <= row["n_val"], "Invalid tied-row count")
        for metric in ("raw", "tie_excluded", "on_tied_rows"):
            require(math.isfinite(row[metric]) and 0 <= row[metric] <= 1,
                    f"Invalid accuracy: {metric}")
        by_key[key] = row
    require(set(by_key) == {(arm, seed) for arm in (False, True) for seed in (0, 1, 2)},
            "Missing or unexpected arm/seed")

    for seed in receipt["seeds"]:
        a, b = by_key[(False, seed)], by_key[(True, seed)]
        require(a["n_val"] == b["n_val"] and a["n_val_tied"] == b["n_val_tied"],
                f"Paired counts differ for seed {seed}")

    means = {}
    for arm, label in ((False, "baseline"), (True, "identity")):
        for metric in ("raw", "tie_excluded", "on_tied_rows"):
            values = [by_key[(arm, seed)][metric] for seed in receipt["seeds"]]
            mean, sd = statistics.mean(values), statistics.stdev(values)
            retained = receipt[label][metric]
            require(math.isclose(round(mean, 4), retained["mean"], abs_tol=1e-12),
                    f"Retained mean mismatch: {label}/{metric}")
            require(math.isclose(round(sd, 4), retained["sd"], abs_tol=1e-12),
                    f"Retained standard deviation mismatch: {label}/{metric}")
            if metric == "raw":
                means[label] = mean

    delta = 100 * (means["identity"] - means["baseline"])
    require(math.isclose(round(delta, 2), receipt["delta_raw_pp"], abs_tol=1e-12),
            "Retained delta mismatch")
    output = {
        "verification": "PASS",
        "python_version": platform.python_version(),
        "scope": "Retained aggregate arithmetic only; not a historical training reproduction",
        "source_sha256": EXPECTED,
        "cache_examples": meta["n_examples"],
        "seed_comparisons": 3,
        "paired_seed_validation_counts_match": True,
        "actual_validation_assignments_reconstructed": False,
        "baseline_mean_raw_accuracy_pct": round(100 * means["baseline"], 2),
        "identity_mean_raw_accuracy_pct": round(100 * means["identity"], 2),
        "delta_percentage_points": round(delta, 2),
        "aggregation": "Equal weight per seed, not pooled validation rows",
        "paired_deltas_percentage_points": [
            {"seed": seed,
             "n_val_per_arm": by_key[(False, seed)]["n_val"],
             "delta": round(100 * (by_key[(True, seed)]["raw"] - by_key[(False, seed)]["raw"]), 6)}
            for seed in receipt["seeds"]
        ],
        "additional_parameters_from_inspected_design": 4096 * 16 + 16 * 256,
        "capacity_matched_control": False,
        "original_runtime_and_checkpoint_identity_reproduced": False,
        "models_trained": 0,
        "games_run": 0,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, statistics.StatisticsError) as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
