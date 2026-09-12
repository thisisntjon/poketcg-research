"""Verify the portable Recycler case; stdlib only, no network or game execution."""

import hashlib
import json
import math
from pathlib import Path


BASE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_manifest():
    manifest = read_json("SOURCE-MANIFEST.json")
    checked = []
    for item in manifest["exports"]:
        path = BASE / item["file"]
        require(path.resolve().parent == BASE, "Export path leaves this case")
        require(path.is_file(), "Missing export: " + item["file"])
        require(sha256(path) == item["sha256"], "SHA mismatch: " + item["file"])
        require(path.stat().st_size == item["bytes"], "Size mismatch: " + item["file"])
        checked.append(item["file"])
    required = {"README.md", "SOURCES.md", "BODY-PARAGRAPH.md", "aggregates.json",
                "identities.json", "expected-results.json", "verify_case.py", "verify.py"}
    require(set(checked) == required, "Unexpected manifest export membership")
    require(len(checked) == len(set(checked)), "Duplicate manifest member")
    for source in manifest["sources"]:
        require(source["exported_receipt"] == "SOURCES.md", "External receipt dependency")
        require(len(source["original_file_sha256"]) == 64, "Invalid source identity")
    return checked


def main():
    checked = verify_manifest()
    data = read_json("aggregates.json")
    identities = read_json("identities.json")
    expected = read_json("expected-results.json")
    require(data["schema"] == "recycler_aggregate_case/v1", "Unknown schema")
    require(data["method"]["id"] == "independent_arm_binomial_normal", "Method changed")
    require(data["method"]["z"] == 1.96, "Interval multiplier changed")
    require(data["outcome_convention"].startswith("wins_divided_by_decided;"),
            "Outcome convention changed")
    control = identities["control"]
    treatment = identities["treatment"]
    require(control["deck_size"] == treatment["deck_size"] == 60, "Deck-size summary mismatch")
    require(control["basic_fighting_energy_count"] == treatment["basic_fighting_energy_count"] == 14,
            "Energy summary mismatch")
    require(control["changed_card_counts"] == {"1152": 2, "1139": 0}, "Control swap mismatch")
    require(treatment["changed_card_counts"] == {"1152": 1, "1139": 1}, "Treatment swap mismatch")
    require(control["recorded_policy_flags"] == treatment["recorded_policy_flags"] ==
            {"PTCG_ALAKAZAM_SNIPER": "1"}, "Policy setting mismatch")
    require(control["deck_file_sha256"] != treatment["deck_file_sha256"], "Deck hashes must differ")
    require(identities["configuration_summary"]["other_card_counts_equal_on_original_inspection"],
            "Unverified comparison summary")
    results = {}
    unique_attempts = 0
    unique_decided = 0
    for contrast in data["contrasts"]:
        arms = {}
        for role in ("control", "treatment"):
            counts = contrast[role]
            require(all(type(counts[k]) is int for k in ("wins", "decided", "attempts", "undecided")),
                    "Counts must be integers")
            require(0 <= counts["wins"] <= counts["decided"] <= counts["attempts"],
                    "Invalid count bounds")
            require(counts["attempts"] - counts["decided"] == counts["undecided"],
                    "Decided/undecided denominator mismatch")
            require(counts["reported_errors"] == 0, "Historical error count changed")
            p = counts["wins"] / counts["decided"]
            arms[role] = {"pct": 100 * p, "variance": p * (1 - p) / counts["decided"]}
            unique_attempts += counts["attempts"]
            unique_decided += counts["decided"]
        difference = arms["treatment"]["pct"] - arms["control"]["pct"]
        se = 100 * math.sqrt(sum(a["variance"] for a in arms.values()))
        result = {"control_pct": arms["control"]["pct"],
                  "treatment_pct": arms["treatment"]["pct"],
                  "delta_pp": difference, "se_pp": se,
                  "ci95_pp": [difference - 1.96 * se, difference + 1.96 * se]}
        require(contrast["id"] not in results, "Duplicate population ID")
        results[contrast["id"]] = result
        for key, reference in expected["contrasts"][contrast["id"]].items():
            actual_values = result[key] if isinstance(reference, list) else [result[key]]
            reference_values = reference if isinstance(reference, list) else [reference]
            for actual, rounded in zip(actual_values, reference_values):
                require(abs(actual - rounded) <= expected["rounding_tolerance"],
                        "Rounded result mismatch: " + contrast["id"] + "/" + key)
    require(set(results) == set(expected["contrasts"]), "Population set mismatch")
    first, wider = data["contrasts"]
    require(first["stage"] == 1 and wider["stage"] == 2, "Stage order mismatch")
    require(first["opponents"] == ["prvsiyan_844_router"], "First target identity mismatch")
    require(len(set(wider["opponents"])) == 5 and first["opponents"][0] in wider["opponents"],
            "Wider panel must include the second target batch")
    membership = data["stage_membership"]
    require(membership["stage2_target_attempts"] ==
            membership["target_pool_and_stage2_panel_overlap_attempts"] == 2000,
            "Target/panel overlap mismatch")
    require(unique_attempts == membership["unique_total_attempts"] ==
            expected["unique_total_attempts"], "Total attempts mismatch")
    require(unique_decided == membership["unique_total_decided"] ==
            expected["unique_total_decided"], "Total decided mismatch")
    endings = data["stage1_endings"]
    changes = {key: endings["treatment"][key] - endings["control"][key]
               for key in endings["control"]}
    changes["wins"] = first["treatment"]["wins"] - first["control"]["wins"]
    changes["losses"] = ((first["treatment"]["decided"] - first["treatment"]["wins"]) -
                         (first["control"]["decided"] - first["control"]["wins"]))
    require(changes == expected["stage1_count_changes"], "Ending count changes mismatch")
    for role in ("control", "treatment"):
        counts = endings[role]
        require(counts["deckout_losses"] <= counts["all_deckouts"] <= first[role]["decided"],
                "Invalid deckout counts")
        require(counts["prize_wins"] <= first[role]["wins"], "Prize wins exceed all wins")
    historical = data["historical_only"]
    require(historical["excluded_from_headlines_and_plots"] is True,
            "Historical-only fence removed")
    require(historical["target_pool"]["exact_wins"] is None and
            historical["target_pool"]["method_reconciled"] is False and
            historical["stage2_target"]["exact_wins"] is None,
            "Unrecovered target inputs promoted")
    require(results["stage1_first_target_batch"]["ci95_pp"][0] > 0,
            "First-batch direction does not match wording")
    lo, hi = results["stage2_wider_panel"]["ci95_pp"]
    require(lo < 0 < hi, "Panel interval does not match wording")
    output = {"status": "PASS", "schema": "recycler_case_verification/v1",
              "scope": "Recounted exported historical aggregate arithmetic; no game re-execution or runtime certification",
              "independent_review": False,
              "checked_export_count": len(checked),
              "source_manifest_sha256": sha256(BASE / "SOURCE-MANIFEST.json"),
              "recounted_contrasts": results, "stage1_count_changes": changes,
              "unique_attempts": unique_attempts, "unique_decided": unique_decided,
              "historical_only_not_recomputed": ["stage2_target", "two_stage_target_pool", "stage2_per_cell_table"],
              "headline_boundary": "Stage1 must be labeled first target batch and carry later-batch/panel limits."}
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
