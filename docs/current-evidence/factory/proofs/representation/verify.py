"""Check two retained aggregate experiments. No training or raw game inputs."""

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
    "second/repr_probe_kernel_summary.json": "ded35c19470ab8a2331e9e8aab0146b7a91739bf5ccb8848058dacdd1c90fd14",
    "second/cache_meta.json": "69d988de075dc89e3649c4111aeb8ec317126cfd3d8b7922f9b208ce0d883768",
    "second/CORPUS-PROVENANCE-EXCERPT.json": "9197aa80a2666f36d48d5820c0f008e11bafce71cb382338a7a83bd7d13afb21",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def recount(receipt: dict, meta: dict, expected_examples: int) -> dict:
    require(receipt["schema"] == "ptcg.repr_probe.receipt/v1", "Unexpected receipt schema")
    require(meta["schema"] == "ptcg.repr_probe_cache/v1", "Unexpected cache schema")
    require(receipt["seeds"] == [0, 1, 2], "Unexpected seed list")
    require(meta["n_examples"] == expected_examples, "Unexpected example count")
    require((meta["state_dim"], meta["n_options"], meta["n_opt_feats"]) == (148, 16, 4),
            "Unexpected cache dimensions")
    require(type(meta["n_skipped"]) is int and meta["n_skipped"] >= 0, "Invalid skipped count")
    rows = receipt["runs"]
    require(len(rows) == 6, "Expected exactly six arm/seed rows")
    by_key = {}
    for row in rows:
        require(type(row["use_ids"]) is bool and type(row["seed"]) is int,
                "Invalid arm/seed types")
        key = (row["use_ids"], row["seed"])
        require(key not in by_key, f"Duplicate arm/seed: {key}")
        require(type(row["n_val"]) is int and 0 < row["n_val"] <= expected_examples,
                "Invalid validation count")
        require(type(row["n_val_tied"]) is int and 0 <= row["n_val_tied"] <= row["n_val"],
                "Invalid tied-row count")
        for metric in ("raw", "tie_excluded", "on_tied_rows"):
            require(type(row[metric]) in (int, float) and math.isfinite(row[metric])
                    and 0 <= row[metric] <= 1, f"Invalid agreement: {metric}")
        by_key[key] = row
    require(set(by_key) == {(arm, seed) for arm in (False, True) for seed in range(3)},
            "Missing or unexpected arm/seed")

    pairs = []
    for seed in range(3):
        baseline, identity = by_key[False, seed], by_key[True, seed]
        require(all(baseline[k] == identity[k] for k in ("n_val", "n_val_tied")),
                f"Paired counts differ at seed {seed}")
        pairs.append({
            "seed": seed,
            "n_val_per_arm": baseline["n_val"],
            "n_val_tied_per_arm": baseline["n_val_tied"],
            "baseline_raw_agreement_pct": 100 * baseline["raw"],
            "identity_raw_agreement_pct": 100 * identity["raw"],
            "delta_percentage_points": 100 * (identity["raw"] - baseline["raw"]),
        })

    summaries = {}
    for arm, label in ((False, "baseline"), (True, "identity")):
        summaries[label] = {}
        for metric in ("raw", "tie_excluded", "on_tied_rows"):
            values = [by_key[arm, seed][metric] for seed in range(3)]
            mean, sd = statistics.mean(values), statistics.stdev(values)
            retained = receipt[label][metric]
            require(math.isclose(round(mean, 4), retained["mean"], abs_tol=1e-12),
                    f"Stored mean mismatch: {label}/{metric}")
            require(math.isclose(round(sd, 4), retained["sd"], abs_tol=1e-12),
                    f"Stored sample SD mismatch: {label}/{metric}")
            summaries[label][metric] = {"mean": mean, "sample_sd": sd}

    baseline = summaries["baseline"]["raw"]["mean"]
    identity = summaries["identity"]["raw"]["mean"]
    delta = 100 * (identity - baseline)
    require(math.isclose(round(delta, 2), receipt["delta_raw_pp"], abs_tol=1e-12),
            "Stored raw difference mismatch")
    return {
        "cache_examples": expected_examples,
        "cached_skipped_rows": meta["n_skipped"],
        "seed_comparisons": 3,
        "arm_seed_rows_checked": 6,
        "paired_seed_validation_counts_match": True,
        "actual_validation_assignments_reconstructed": False,
        "baseline_mean_raw_accuracy_pct": 100 * baseline,
        "identity_mean_raw_accuracy_pct": 100 * identity,
        "delta_percentage_points": delta,
        "all_recorded_seed_deltas_positive": all(p["delta_percentage_points"] > 0 for p in pairs),
        "aggregation": "Equal weight per recorded seed, not pooled validation rows",
        "seed_rows": pairs,
        "all_retained_metric_summaries_checked": summaries,
    }


def main() -> None:
    base = Path(__file__).resolve().parent
    manifest = json.loads((base / "MANIFEST.json").read_text(encoding="utf-8"))
    inputs = {}
    expected_files = set(EXPECTED)
    artifacts = manifest["artifacts"]
    require(len(artifacts) == 5 and {a["file"] for a in artifacts} == expected_files,
            "Unexpected manifest input set")
    for item in artifacts:
        name = item["file"]
        data = (base / name).read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        require(actual == item["sha256"], f"Manifest hash mismatch: {name}")
        if name in EXPECTED:
            require(actual == EXPECTED[name], f"Pinned source hash mismatch: {name}")
        require(len(data) == item["bytes"], f"Input size mismatch: {name}")
        inputs[name] = json.loads(data)

    first = recount(inputs["repr_probe_01_summary.json"], inputs["cache_meta.json"], 44343)
    second = recount(inputs["second/repr_probe_kernel_summary.json"], inputs["second/cache_meta.json"], 66030)
    provenance = inputs["second/CORPUS-PROVENANCE-EXCERPT.json"]
    require(provenance["source_sha256"] == "bf8b35d34e7fea7613ca48dc756310c3c8bb0e0bbc38e66bc72fbe0ceda1ee08",
            "Unexpected original producer receipt identity")
    require(set(provenance["teacher"]) == {"key", "loaded_via", "main_sha256", "deck_sha256"},
            "Teacher provenance must contain only the selected identity fields")
    require(provenance["n_rows"] == 66074 and provenance["n_games"] == 500
            and provenance["gen_errors"] == 0, "Unexpected producer counts")
    require(second["cache_examples"] + second["cached_skipped_rows"] == provenance["n_rows"],
            "Generated/cached/skipped row accounting does not reconcile")
    second["generated_row_accounting"] = {
        "generated_rows_as_recorded": provenance["n_rows"],
        "cached_examples": second["cache_examples"],
        "skipped_rows": second["cached_skipped_rows"],
        "reconciles": True,
    }
    output = {
        "verification": "PASS",
        "python_version": platform.python_version(),
        "scope": "Saved aggregate arithmetic and recorded provenance counts only; no training reproduction",
        "source_sha256": {item["file"]: item["sha256"] for item in artifacts},
        "first": first,
        "second": second,
        "additional_parameters_from_inspected_design": 4096 * 16 + 16 * 256,
        "capacity_matched_control": False,
        "raw_overlap_or_deduplication_audit_performed": False,
        "independent_or_disjoint_replication_established": False,
        "original_runtime_and_checkpoint_identity_reproduced": False,
        "teacher_correctness_or_playing_strength_measured": False,
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
