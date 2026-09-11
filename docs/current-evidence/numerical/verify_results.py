#!/usr/bin/env python3
"""Recount the report's numerical evidence using only Python's standard library.

    python verify_results.py
    python verify_results.py --output verified-results.json
    python verify_results.py --json

No network, game engine, training framework, or private path is used. Read METHODS.md
for scoring conventions, approximation assumptions, cohort choices, and limitations.
"""
import argparse
import csv
import hashlib
import json
import math
import pathlib
import sys
from collections import Counter, defaultdict


HERE = pathlib.Path(__file__).resolve().parent
FIELDS = ["run", "arm", "opponent_id", "game_index", "seat", "outcome", "source_id", "source_record"]
DEV_ARMS = {
    "xerosic_screen1": ("control", "variant"),
    "xerosic_replicate": ("control", "variant"),
    "sniper_screen1": ("OFF", "ON"),
    "factorial": ("A_baseline", "B_sniper", "C_xerosic", "D_both"),
    "combined_replicate": ("A_baseline", "D_both"),
    "combined_reproduction_4070": ("A_baseline", "D_both"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_bundle(directory):
    manifest = json.loads((directory / "SOURCE-MANIFEST.json").read_text(encoding="utf-8"))
    source_ids = {s["id"] for s in manifest["sources"]}
    expected_files = {"development-outcomes.csv": 28000, "panel-outcomes.csv": 8400,
                      "anchor-outcomes.csv": 16000, "student-outcomes.csv": 1203}
    required = set(expected_files) | {"opponents.json", "learning-summary.json", "activation-checks.json", "retained-opponent-identity.json"}
    exported = {item["file"]: item for item in manifest["exports"]}
    require(set(exported) == required, "Manifest export file set differs from the supported bundle")
    for name, entry in exported.items():
        path = directory / name
        require(path.is_file(), "Missing required file: " + name)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], "SHA256 mismatch: " + name)
    opponents = json.loads((directory / "opponents.json").read_text(encoding="utf-8"))
    retained = json.loads((directory / "retained-opponent-identity.json").read_text(encoding="utf-8"))
    require(retained["opponent_id"] == "P07" and retained["source_alias"] == opponents["P07"]["source_alias"], "Retained identity alias mismatch")
    retained_files = {item["file"]: item for item in retained["files"]}
    for filename, field in [("main.py", "policy_sha256"), ("deck.csv", "deck_sha256")]:
        require(retained_files[filename]["sha256"] == opponents["P07"][field], "Retained identity hash mismatch: " + filename)
    data = {}
    for name, expected in expected_files.items():
        with (directory / name).open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            require(reader.fieldnames == FIELDS, "Unexpected columns: " + name)
            rows = list(reader)
        require(len(rows) == expected, "%s: expected %s rows, found %s" % (name, expected, len(rows)))
        keys = set()
        for index, row in enumerate(rows, 2):
            require(None not in row and None not in row.values(), "Malformed row %s:%s" % (name, index))
            require(row["outcome"] in {"win", "loss", "draw"}, "Unknown outcome")
            require(row["seat"] in {"first", "second"}, "Unknown seat")
            require(row["source_id"] in source_ids, "Unknown source locator")
            require(row["opponent_id"] in opponents, "Unknown opponent ID")
            row["game_index"] = int(row["game_index"])
            row["source_record"] = int(row["source_record"])
            require(row["game_index"] >= 0 and row["source_record"] >= 0, "Negative source/game index")
            key = tuple(row[k] for k in ("run", "arm", "opponent_id", "game_index"))
            require(key not in keys, "Duplicate game key: " + str(key))
            keys.add(key)
        data[name] = rows
    dev = data["development-outcomes.csv"]
    counts = Counter((r["run"], r["arm"]) for r in dev)
    expected = {(run, arm): 2000 for run, arms in DEV_ARMS.items() for arm in arms}
    require(dict(counts) == expected, "Development cohort/arm counts differ from the stated design")
    dev_ids = {oid for oid in opponents if oid.startswith("D")}
    require(len(dev_ids) == 5 and sum(opponents[x]["group"] == "Alakazam" for x in dev_ids) == 2, "Expected five development opponents, two Alakazam")
    for (run, arm) in expected:
        subset = [r for r in dev if r["run"] == run and r["arm"] == arm]
        require(Counter((r["opponent_id"], r["seat"]) for r in subset) == Counter({(oid, seat): 200 for oid in dev_ids for seat in ("first", "second")}), "Development opponent/seat imbalance: " + run)
    panel = data["panel-outcomes.csv"]
    require({r["run"] for r in panel} == {"seven_opponent_panel"}, "Unexpected panel cohort")
    require(Counter((r["arm"], r["opponent_id"], r["seat"]) for r in panel) == Counter({(arm, "P%02d" % i, seat): 300 for arm in ("BASELINE", "COMBINED") for i in range(1, 8) for seat in ("first", "second")}), "Panel does not contain exactly 300 games per arm/opponent/seat")
    anchor = data["anchor-outcomes.csv"]
    require({(r["run"], r["opponent_id"]) for r in anchor} == {("c61_anchor_followup", "C61")}, "Unexpected anchor cohort/opponent")
    require(Counter((r["arm"], r["seat"]) for r in anchor) == Counter({(arm, seat): 4000 for arm in ("BASELINE", "COMBINED") for seat in ("first", "second")}), "Anchor arm/seat counts differ")
    for arm in ("BASELINE", "COMBINED"):
        require({r["game_index"] for r in anchor if r["arm"] == arm} == set(range(8000)), "Missing anchor game indices")
    student = data["student-outcomes.csv"]
    require({(r["run"], r["arm"], r["opponent_id"]) for r in student} == {("historical_student_e8", "STUDENT", "C61")}, "Unexpected student cohort")
    require({r["game_index"] for r in student} == set(range(1203)), "Missing historical student attempts")
    return data, opponents, json.loads((directory / "learning-summary.json").read_text(encoding="utf-8")), manifest


def score(rows, convention):
    counts = Counter(r["outcome"] for r in rows)
    w, l, d = (counts[k] for k in ("win", "loss", "draw"))
    n = w + l if convention == "decided" else w + l + d
    total = w if convention == "decided" else w + 0.5 * d
    require(n > 0, "Empty score denominator")
    p = total / n
    if convention == "half":
        require(n > 1, "At least two scores required for sample variance")
        # Score values are 0, 0.5, 1: sum(x^2) = wins + draws/4.
        # Unbiased sample variance / n, matching current article figures.
        variance = 10000 * (w + 0.25 * d - n * p * p) / (n * (n-1))
    else:
        variance = 10000 * p * (1-p) / n
    return {"wins": w, "losses": l, "draws": d, "attempts": w + l + d,
            "denominator": n, "score_total": total, "score_pct": 100 * p,
            "mean_variance_pct2": variance}


def interval(value, variance):
    se = math.sqrt(variance)
    return {"delta_pp": value, "variance_pp2": variance, "se_pp": se,
            "ci95_pp": [value - 1.96 * se, value + 1.96 * se]}


def contrast(rows, baseline="BASELINE", combined="COMBINED", convention="half"):
    b = score([r for r in rows if r["arm"] == baseline], convention)
    c = score([r for r in rows if r["arm"] == combined], convention)
    return {"baseline": b, "combined": c, "draw_convention": convention,
            **interval(c["score_pct"] - b["score_pct"], b["mean_variance_pct2"] + c["mean_variance_pct2"])}


def pooled(items, weights="inverse_variance"):
    ws = [1 / item["variance_pp2"] if weights == "inverse_variance" else 1.0 for item in items]
    total = sum(ws)
    normalized = [w / total for w in ws]
    value = sum(w * item["delta_pp"] for w, item in zip(normalized, items))
    variance = sum(w * w * item["variance_pp2"] for w, item in zip(normalized, items))
    return {"weighting": weights, "count": len(items), "weights": normalized, **interval(value, variance)}


def calculate(data, opponents, learning):
    dev = data["development-outcomes.csv"]
    definitions = {
        "card": [("xerosic_screen1", "control", "variant"), ("xerosic_replicate", "control", "variant"), ("factorial", "A_baseline", "C_xerosic")],
        "rule": [("sniper_screen1", "OFF", "ON"), ("factorial", "A_baseline", "B_sniper")],
        "combined": [("factorial", "A_baseline", "D_both"), ("combined_replicate", "A_baseline", "D_both"), ("combined_reproduction_4070", "A_baseline", "D_both")],
    }
    development = {"records": len(dev), "panel_alakazam_fraction": 0.4, "effects": {}}
    for effect, contrasts in definitions.items():
        parts = [{"run": run, "baseline_arm": b, "treatment_arm": c,
                  **contrast([r for r in dev if r["run"] == run], b, c, "decided")} for run, b, c in contrasts]
        development["effects"][effect] = {"comparisons": parts, "pooled": pooled(parts)}
    factorial = {arm: score([r for r in dev if r["run"] == "factorial" and r["arm"] == arm], "decided") for arm in DEV_ARMS["factorial"]}
    interaction = factorial["D_both"]["score_pct"] - factorial["C_xerosic"]["score_pct"] - factorial["B_sniper"]["score_pct"] + factorial["A_baseline"]["score_pct"]
    development["factorial"] = {"arms": factorial, "interaction": interval(interaction, sum(item["mean_variance_pct2"] for item in factorial.values()))}
    panel_rows = data["panel-outcomes.csv"]
    cells = [{"opponent_id": oid, "opponent_label": opponents[oid]["label"], "group": opponents[oid]["group"],
              **contrast([r for r in panel_rows if r["opponent_id"] == oid])} for oid in sorted({r["opponent_id"] for r in panel_rows})]
    groups = {group: pooled([c for c in cells if c["group"] == group], "equal") for group in ("Alakazam", "Other")}
    q = 0.25
    mixture = {"q": q, "group_weights": {"Alakazam": q, "Other": 1-q},
               **interval(q * groups["Alakazam"]["delta_pp"] + (1-q) * groups["Other"]["delta_pp"],
                          q*q * groups["Alakazam"]["variance_pp2"] + (1-q)**2 * groups["Other"]["variance_pp2"])}
    seat_groups = {}
    for group in ("Alakazam", "Other", "All"):
        selected = [r for r in panel_rows if group == "All" or opponents[r["opponent_id"]]["group"] == group]
        seats = {seat: contrast([r for r in selected if r["seat"] == seat]) for seat in ("first", "second")}
        seat_groups[group] = {**seats, "first_minus_second": interval(seats["first"]["delta_pp"] - seats["second"]["delta_pp"], seats["first"]["variance_pp2"] + seats["second"]["variance_pp2"])}
    anchor_rows = data["anchor-outcomes.csv"]
    anchor = {"records": len(anchor_rows), "all": contrast(anchor_rows, convention="decided"),
              "seats": {seat: contrast([r for r in anchor_rows if r["seat"] == seat], convention="decided") for seat in ("first", "second")}}
    student_rows = data["student-outcomes.csv"]
    student = {"all": score(student_rows, "decided"), "seats": {seat: score([r for r in student_rows if r["seat"] == seat], "decided") for seat in ("first", "second")}, "learning_receipt": learning}
    student["validation_nll_change"] = learning["selected_validation_nll"] - learning["parent_validation_nll"]
    return {"schema": "ptcg.verified_writeup_results/v1", "verification_scope": "Recount of saved terminal outcomes and arithmetic from exported receipts; no new execution of players or training",
            "interval_method": "Normal 1.96 SE; independent games/arms/cells. Decided games use p(1-p)/n; half-draw scores use unbiased sample variance/n, matching current article figures (see METHODS.md)",
            "development": development, "panel": {"records": len(panel_rows), "cells": cells, "equal_groups": groups, "mixture": mixture, "seat_groups": seat_groups},
            "anchor": anchor, "student": student}


def check_published(results):
    checks = []
    def check(name, got, want, tolerance=0.005):
        require(abs(got-want) <= tolerance, "%s: expected %s +/- %s, got %s" % (name, want, tolerance, got))
        checks.append({"claim": name, "recomputed": got, "published_rounded": want, "tolerance": tolerance})
    for name, value in (("card", 5.02), ("rule", 3.62), ("combined", 7.82)):
        check("development_" + name, results["development"]["effects"][name]["pooled"]["delta_pp"], value)
    check("factorial_interaction", results["development"]["factorial"]["interaction"]["delta_pp"], 1.71)
    for cell, value in zip(results["panel"]["cells"], [20.42, 18.75, 0.67, 0.33, 0.50, -0.75, -3.08]):
        check(cell["opponent_id"] + "_delta", cell["delta_pp"], value)
    # Independent reference values retained by the current package's prior figure builder.
    reference_variances = [7.945824058616213, 6.702919217213875, 7.362919680949731,
                           7.162864032647004, 3.8645427564459287, 4.278832776850307,
                           8.13683685772584]
    for cell, variance in zip(results["panel"]["cells"], reference_variances):
        check(cell["opponent_id"] + "_current_figure_variance", cell["variance_pp2"], variance, 1e-10)
    check("other_five_equal_mean", results["panel"]["equal_groups"]["Other"]["delta_pp"], -0.47)
    check("assumed_q_0.25", results["panel"]["mixture"]["delta_pp"], 4.55)
    check("alakazam_first", results["panel"]["seat_groups"]["Alakazam"]["first"]["delta_pp"], 19.50)
    check("alakazam_second", results["panel"]["seat_groups"]["Alakazam"]["second"]["delta_pp"], 19.67)
    check("c61_followup", results["anchor"]["all"]["delta_pp"], -0.14)
    check("student_wins", results["student"]["all"]["wins"], 23, 0)
    check("student_decided", results["student"]["all"]["denominator"], 1200, 0)
    check("student_draws", results["student"]["all"]["draws"], 3, 0)
    require(results["student"]["all"]["attempts"] == 1203, "Student attempt count differs")
    require(all(s["denominator"] == 600 for s in results["student"]["seats"].values()), "Student decided-seat counts differ")
    require(results["student"]["learning_receipt"]["learner_state_teacher_decisions"] == 1358, "Training receipt label-count differs")
    results["published_value_checks"] = checks


def fmt(item):
    lo, hi = item["ci95_pp"]
    return "%+.2f pp [%+.2f, %+.2f]" % (item["delta_pp"], lo, hi)


def human(results):
    lines = ["PASS: hashes, complete cohorts, unique game keys, seat counts and published numerical checks.",
             "Saved outcomes only; no games or training executed.", "", "Development: decided games; inverse-variance within-batch contrasts; 40% Alakazam."]
    for name, effect in results["development"]["effects"].items():
        lines.append("  %s (%s contrasts): %s" % (name, len(effect["comparisons"]), fmt(effect["pooled"])))
    lines.append("  Four-arm interaction: " + fmt(results["development"]["factorial"]["interaction"]))
    lines.extend(["", "Seven-opponent panel: 8,400 records; win=1, draw=0.5, loss=0."])
    for cell in results["panel"]["cells"]:
        lines.append("  %s: %.2f%% -> %.2f%%; %s" % (cell["opponent_label"], cell["baseline"]["score_pct"], cell["combined"]["score_pct"], fmt(cell)))
    for group, result in results["panel"]["equal_groups"].items():
        lines.append("  Equal-weight %s group: %s" % (group, fmt(result)))
    lines.append("  Assumed Alakazam share q=0.25: " + fmt(results["panel"]["mixture"]))
    for seat in ("first", "second"):
        lines.append("  Alakazam %s seat: %s" % (seat, fmt(results["panel"]["seat_groups"]["Alakazam"][seat])))
    lines.append("  Alakazam first-minus-second: " + fmt(results["panel"]["seat_groups"]["Alakazam"]["first_minus_second"]))
    lines.extend(["", "Exact-c61 opponent follow-up: 16,000 records; draws excluded.", "  All: " + fmt(results["anchor"]["all"])])
    for seat in ("first", "second"):
        lines.append("  %s: %s" % (seat, fmt(results["anchor"]["seats"][seat])))
    student = results["student"]["all"]
    learning = results["student"]["learning_receipt"]
    lines.extend(["", "Historical student: %s wins / %s decided (%.4f%%); %s excluded draws; %s attempts." % (student["wins"], student["denominator"], student["score_pct"], student["draws"], student["attempts"]),
                  "Training receipt reports %s learner-state teacher labels; original labels are not recounted here." % learning["learner_state_teacher_decisions"],
                  "Selection-set validation NLL %.9f -> %.9f (change %+.9f)." % (learning["parent_validation_nll"], learning["selected_validation_nll"], results["student"]["validation_nll_change"])])
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", type=pathlib.Path, default=HERE, help="Directory containing exported bundle files")
    ap.add_argument("--json", action="store_true", help="Print machine-readable results instead of the human summary")
    ap.add_argument("--output", type=pathlib.Path, help="Also write machine-readable JSON to this path")
    args = ap.parse_args()
    try:
        data, opponents, learning, manifest = load_bundle(args.data_dir)
        results = calculate(data, opponents, learning)
        check_published(results)
        results["bundle_manifest_sha256"] = hashlib.sha256((args.data_dir / "SOURCE-MANIFEST.json").read_bytes()).hexdigest()
        content = json.dumps(results, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        if args.output:
            protected = {args.data_dir.resolve() / item["file"] for item in manifest["exports"]} | {args.data_dir.resolve() / "SOURCE-MANIFEST.json", pathlib.Path(__file__).resolve()}
            require(args.output.resolve() not in protected, "Output path would overwrite bundle input")
            args.output.write_text(content, encoding="utf-8", newline="\n")
        print(content if args.json else human(results), end="" if args.json else "\n")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("INCOMPLETE OR ALTERED DATA -- refusing to report results: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
