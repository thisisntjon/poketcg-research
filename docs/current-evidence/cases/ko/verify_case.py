#!/usr/bin/env python3
"""Recount the complete historical KO panel using this directory only.

Python standard library; read-only; no original games, engine, imports of player
code, Git, network, environment configuration, or external paths are required.
This verifies the released records and arithmetic, not historical execution.
"""
import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def same_number(actual, expected, label):
    require(isinstance(expected, (int, float)) and not isinstance(expected, bool),
            label + ": expected a number")
    require(math.isfinite(expected) and abs(actual - expected) <= 1e-10,
            label + ": arithmetic mismatch")


def summarize(records):
    counts = Counter(r["outcome"] for r in records)
    n = len(records)
    mean = (counts["win"] + 0.5 * counts["draw"]) / n
    variance = (counts["win"] + 0.25 * counts["draw"] - n * mean * mean) / (n - 1)
    return {"n": n, "wins": counts["win"], "losses": counts["loss"],
            "draws": counts["draw"], "score_mean": mean,
            "sample_score_variance": variance, "variance_of_mean": variance / n,
            "seats": dict(Counter(r["seat"] for r in records))}


def main():
    contract = read_json("CLAIM-CONTRACT.json")
    identity = read_json("identities.json")
    aggregate = read_json("aggregates.json")
    figure = read_json("figure-input.json")
    manifest = read_json("SOURCE-MANIFEST.json")
    require(contract["dataset_id"] == "ko_priority_seven_implementations_20260904_8400", "dataset identity")
    for item in (identity, aggregate, figure, manifest):
        require(item["dataset_id"] == contract["dataset_id"], "mixed dataset identities")
    cells = contract["included_cells"]
    require(len(cells) == 7 and len(set(cells)) == 7, "exactly seven distinct cells required")
    require(contract["arms"] == ["OFF", "ON"], "arm order")
    require(contract["rows"] == 8400 and contract["games_per_arm_cell"] == 600, "population contract")
    require(contract["games_per_seat_arm_cell"] == 300, "seat contract")
    require(contract["outcome_scores"] == {"win": 1, "draw": 0.5, "loss": 0}, "score convention")
    require(contract["ci_multiplier"] == 1.96, "interval multiplier")
    require(hashlib.sha256((HERE / "identities.json").read_bytes()).hexdigest() ==
            contract["identities_sha256"], "frozen candidate/opponent identity receipt")
    require(contract["candidate_identity"] == identity["candidate"], "candidate identity contract")
    require(contract["runtime_identity"] == identity["runtime"]["files"], "runtime source identity contract")
    require(set(identity["opponents"]) == set(cells), "opponent identity membership")
    require(set(aggregate["cells"]) == set(cells), "aggregate membership")
    require([c["opponent"] for c in figure["cells"]] == cells, "figure must retain all seven ordered cells")

    required_files = {"outcomes.csv", "aggregates.json", "identities.json", "figure-input.json",
                      "CLAIM-CONTRACT.json", "README.md", "BODY-PARAGRAPH.md", "verify_case.py", "verify.py"}
    require(set(manifest["exported_files"]) == required_files, "manifest membership")
    for name, details in manifest["exported_files"].items():
        require(Path(name).name == name, "manifest paths must be local basenames")
        content = (HERE / name).read_bytes()
        require(len(content) == details["bytes"], name + ": byte count")
        require(hashlib.sha256(content).hexdigest() == details["sha256"], name + ": SHA-256")
    require(hashlib.sha256((HERE / "outcomes.csv").read_bytes()).hexdigest() ==
            contract["outcomes_sha256"], "frozen outcome identity")

    with (HERE / "outcomes.csv").open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames == ["opponent", "arm", "game_index", "seat", "outcome"], "CSV schema")
        rows = list(reader)
    require(len(rows) == 8400, "8,400 outcome rows required")
    groups = defaultdict(list)
    for row in rows:
        require(set(row) == set(reader.fieldnames) and None not in row.values(), "malformed CSV row")
        require(row["opponent"] in cells and row["arm"] in ("OFF", "ON"), "unexpected row population")
        require(row["outcome"] in contract["outcome_scores"], "unknown outcome")
        require(row["seat"] in ("first", "second"), "unknown seat")
        require(row["game_index"].isdigit(), "game index must be a nonnegative integer")
        groups[(row["opponent"], row["arm"])].append(row)

    totals = {arm: Counter() for arm in contract["arms"]}
    print("Dataset: " + contract["dataset_id"])
    for cell, plot in zip(cells, figure["cells"]):
        parts = {}
        for arm in contract["arms"]:
            records = groups[(cell, arm)]
            require(len(records) == 600, cell + " " + arm + ": 600 games required")
            require(sorted(int(r["game_index"]) for r in records) == list(range(600)), cell + " " + arm + ": indices")
            require(all(r["seat"] == ("first" if int(r["game_index"]) % 2 == 0 else "second") for r in records),
                    cell + " " + arm + ": alternating seats")
            value = summarize(records)
            require(value["seats"] == {"first": 300, "second": 300}, cell + " " + arm + ": seat balance")
            stored = aggregate["cells"][cell][arm]
            require(set(value) == set(stored), cell + " " + arm + ": statistic fields")
            for key in value:
                if key == "seats":
                    require(value[key] == stored[key], "stored seats")
                else:
                    same_number(value[key], stored[key], cell + " " + arm + " " + key)
            parts[arm] = value
            totals[arm].update({k: value[k] for k in ("n", "wins", "losses", "draws")})
            run = identity["runs"][cell][arm]
            expected_flag = "1" if arm == "ON" else None
            require(run["recorded_environment"].get("PTCG_MIRROR_PATCH_01_KO") == expected_flag, "recorded arm flag")
            require(run["recorded_environment"].get("PTCG_MIRROR_PATCH_01") is None, "broader flag must be absent")
            require(run["recorded_effective_policy"] == "rules_lucario", "recorded policy")
            require(run["per_game_isolation"] and run["distinct_worker_tokens"] == 600, "recorded isolation")
            require(run["recorded_errors"] == 0 and not run["recorded_runtime_dirty_paths"], "recorded run quality")
            require(run["deck_sha256"] == identity["candidate"]["deck_sha256"], "candidate deck identity")
            require(run["config_sha256"] == identity["candidate"]["config_sha256"], "candidate config identity")
        run_a, run_b = (identity["runs"][cell][a] for a in contract["arms"])
        require(run_a["pool_alias_selfcheck_hash"] == run_b["pool_alias_selfcheck_hash"], "paired alias/selfcheck identity")
        require({k: v for k, v in run_a["recorded_environment"].items() if k != "PTCG_MIRROR_PATCH_01_KO"} ==
                {k: v for k, v in run_b["recorded_environment"].items() if k != "PTCG_MIRROR_PATCH_01_KO"}, "other recorded environment differs")
        delta = 100 * (parts["ON"]["score_mean"] - parts["OFF"]["score_mean"])
        se = 100 * math.sqrt(parts["OFF"]["variance_of_mean"] + parts["ON"]["variance_of_mean"])
        interval = [delta - 1.96 * se, delta + 1.96 * se]
        same_number(delta, aggregate["cells"][cell]["delta_pp"], cell + " difference")
        same_number(delta, plot["delta_pp"], cell + " plot difference")
        require(plot["label"] == identity["opponents"][cell]["label"], "figure label identity")
        for i in range(2):
            same_number(interval[i], aggregate["cells"][cell]["ci95_pp"][i], cell + " interval")
            same_number(interval[i], plot["ci95_pp"][i], cell + " plot interval")
        require(plot["display_delta_pp"] == f"{delta:+.2f}", "rounded figure difference")
        require(plot["display_ci95_pp"] == [f"{v:+.2f}" for v in interval], "rounded figure interval")
        print(f"{plot['label']}: ON-OFF {delta:+.2f} pp; approximate 95% CI [{interval[0]:+.2f}, {interval[1]:+.2f}]")
    for arm in contract["arms"]:
        require(dict(totals[arm]) == aggregate["panel_totals"][arm], "panel totals")
    require(sum(v["n"] for v in totals.values()) == 8400, "panel denominator")
    print("PASS: 8,400 rows; 7 cells; 600 games/arm/cell; 300/seat; all W/L/D counts, score means, sample variances, intervals, figure values and local hashes agree.")
    print("Scope: retained outcome recount and exported identity-receipt consistency; historical runtime, random-seed independence, decision causality and opponent-source custody are not replayed or certified.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, csv.Error) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        raise SystemExit(1)
