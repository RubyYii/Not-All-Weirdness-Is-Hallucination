"""Reproduce the paper's numerical results using only files in this supplement.

Python 3.9+; standard library only. Statistical functions retain the accepted
analysis definitions. Input validation and the public-file entry point were
added for the camera-ready package. No image loading or network access occurs.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

STATE_CATEGORIES = ("target_present", "target_absent", "uncertain")
RATER_COLUMNS = ("R1", "R2", "R3")
PUBLIC_RATER_COLUMNS = RATER_COLUMNS

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def majority(values: list[str]) -> str:
    counts = Counter(values)
    for value in STATE_CATEGORIES:
        if counts[value] >= 2:
            return value
    return "no_majority"


def local_outcome(majority_state: str, expected_state: str) -> str:
    if majority_state == "no_majority":
        return "no_majority"
    if majority_state == "uncertain":
        return "not_judgeable"
    return "match" if majority_state == expected_state else "mismatch"


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> dict[str, float]:
    proportion = successes / total
    denominator = 1.0 + z * z / total
    centre = (proportion + z * z / (2.0 * total)) / denominator
    half = (
        z
        * math.sqrt(
            proportion * (1.0 - proportion) / total
            + z * z / (4.0 * total * total)
        )
        / denominator
    )
    return {"estimate": proportion, "lower": centre - half, "upper": centre + half}


def reliability(rows: list[dict[str, str]]) -> dict[str, object]:
    category_totals = Counter()
    pair_agreement_sum = 0.0
    exact = 0
    pairwise_counts = {"R1_R2": 0, "R1_R3": 0, "R2_R3": 0}
    uncertain_by_rater = dict.fromkeys(PUBLIC_RATER_COLUMNS, 0)

    for row in rows:
        values = [row[column] for column in RATER_COLUMNS]
        counts = Counter(values)
        category_totals.update(values)
        exact += int(len(set(values)) == 1)
        pair_agreement_sum += sum(count * (count - 1) for count in counts.values()) / 6.0
        pairwise_counts["R1_R2"] += int(values[0] == values[1])
        pairwise_counts["R1_R3"] += int(values[0] == values[2])
        pairwise_counts["R2_R3"] += int(values[1] == values[2])
        for label, value in zip(PUBLIC_RATER_COLUMNS, values):
            uncertain_by_rater[label] += int(value == "uncertain")

    n_items = len(rows)
    n_ratings = n_items * 3
    observed = pair_agreement_sum / n_items
    proportions = {
        category: category_totals[category] / n_ratings
        for category in STATE_CATEGORIES
    }
    fleiss_expected = sum(value * value for value in proportions.values())
    gwet_expected = sum(value * (1.0 - value) for value in proportions.values()) / 2.0
    return {
        "exact_agreement_n": exact,
        "exact_agreement_rate": exact / n_items,
        "mean_pairwise_agreement": observed,
        "pairwise_agreement_n": pairwise_counts,
        "uncertain_by_rater": uncertain_by_rater,
        "category_totals": dict(category_totals),
        "fleiss_kappa": (observed - fleiss_expected) / (1.0 - fleiss_expected),
        "gwet_ac1": (observed - gwet_expected) / (1.0 - gwet_expected),
    }


def count_group(rows: list[dict[str, str]]) -> dict[str, object]:
    outcomes = Counter(row["outcome_recomputed"] for row in rows)
    match = outcomes["match"]
    mismatch = outcomes["mismatch"]
    unresolved = outcomes["not_judgeable"] + outcomes["no_majority"]
    judgeable = match + mismatch
    total = len(rows)
    return {
        "n": total,
        "match": match,
        "mismatch": mismatch,
        "uncertain_majority": outcomes["not_judgeable"],
        "no_majority": outcomes["no_majority"],
        "unresolved": unresolved,
        "judgeable": judgeable,
        "all_sample_rate": match / total,
        "all_sample_wilson_95": wilson(match, total),
        "judgeable_rate": match / judgeable if judgeable else None,
        "judgeable_wilson_95": wilson(match, judgeable) if judgeable else None,
    }


def grouped_counts(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, object]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row[key]].append(row)
    return {group: count_group(group_rows) for group, group_rows in sorted(groups.items())}


def fisher_exact_two_sided(table: list[list[int]]) -> tuple[float, float]:
    """Return the sample odds ratio and Fisher's exact two-sided p value.

    The p value follows the common probability-ordering definition used by
    SciPy/R: sum the fixed-margin tables no more probable than the observed
    table.  A standard-library implementation keeps the release dependency-free.
    """
    (a, b), (c, d) = table
    row_one = a + b
    column_one = a + c
    total = a + b + c + d
    lower = max(0, row_one - (total - column_one))
    upper = min(row_one, column_one)
    denominator = math.comb(total, row_one)

    def probability(x: int) -> float:
        return (
            math.comb(column_one, x)
            * math.comb(total - column_one, row_one - x)
            / denominator
        )

    observed_probability = probability(a)
    p_value = sum(
        probability(x)
        for x in range(lower, upper + 1)
        if probability(x) <= observed_probability * (1.0 + 1e-12)
    )
    if b * c == 0:
        odds_ratio = math.inf if a * d else math.nan
    else:
        odds_ratio = (a * d) / (b * c)
    return odds_ratio, min(1.0, p_value)


def cross_counts(rows: list[dict[str, str]], first: str, second: str) -> list[dict[str, object]]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[(row[first], row[second])].append(row)
    result = []
    for (left, right), group_rows in sorted(groups.items()):
        result.append({first: left, second: right, **count_group(group_rows)})
    return result


def condition_tests(condition: dict[str, dict[str, object]]) -> dict[str, object]:
    present = condition["target_present"]
    absent = condition["target_absent"]
    judgeable_table = [
        [present["match"], present["mismatch"]],
        [absent["match"], absent["mismatch"]],
    ]
    all_sample_table = [
        [present["match"], present["n"] - present["match"]],
        [absent["match"], absent["n"] - absent["match"]],
    ]
    j_or, j_p = fisher_exact_two_sided(judgeable_table)
    a_or, a_p = fisher_exact_two_sided(all_sample_table)
    return {
        "judgeable": {"table": judgeable_table, "odds_ratio": j_or, "p_two_sided": j_p},
        "all_sample": {"table": all_sample_table, "odds_ratio": a_or, "p_two_sided": a_p},
    }


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    condition = grouped_counts(rows, "condition")
    return {
        "overall": count_group(rows),
        "reliability": reliability(rows),
        "by_condition": condition,
        "condition_fisher_tests": condition_tests(condition),
        "by_family": grouped_counts(rows, "axis_code"),
        "by_lineage": grouped_counts(rows, "lineage"),
        "family_by_condition": cross_counts(rows, "axis_code", "condition"),
        "family_by_lineage": cross_counts(rows, "axis_code", "lineage"),
    }


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compare(actual, expected, path="root"):
    """Compare all numerical leaves, allowing only floating-point roundoff."""
    if isinstance(expected, dict):
        require(isinstance(actual, dict) and set(actual) == set(expected), path + ": keys differ")
        return sum(compare(actual[k], expected[k], path + "." + k) for k in expected)
    if isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), path + ": length differs")
        return sum(compare(a, e, f"{path}[{i}]") for i, (a, e) in enumerate(zip(actual, expected)))
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        require(isinstance(actual, (int, float)) and math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-12),
                f"{path}: {actual!r} != {expected!r}")
    else:
        require(actual == expected, f"{path}: {actual!r} != {expected!r}")
    return 1


def keyed(rows, name, count=200):
    require(len(rows) == count, f"{name}: expected {count} rows, got {len(rows)}")
    result = {row["task_id"]: row for row in rows}
    require(len(result) == count, name + ": duplicate task IDs")
    return result


def validate_matrix(rows, source_map, name):
    by_id = keyed(rows, name)
    require(set(by_id) == set(source_map), name + ": task set differs from coordinator map")
    require({int(r["task_order"]) for r in rows} == set(range(1, 201)), name + ": task orders invalid")
    require(len({r["image_sha256"].upper() for r in rows}) == 200, name + ": duplicate image hashes")
    result = []
    for row in rows:
        src = source_map[row["task_id"]]
        for field in ("task_order", "image_sha256", "axis_code", "expected_observed_target_state"):
            require(row[field] == src[field], f"{name}/{row['task_id']}: {field} differs")
        require(re.fullmatch(r"[0-9A-Fa-f]{64}", row["image_sha256"]) is not None, name + ": invalid SHA-256")
        require(src["intended_role"] in ("anomaly_present", "target_absent_control"), name + ": unknown intended role")
        expected = "target_present" if src["intended_role"] == "anomaly_present" else "target_absent"
        require(row["expected_observed_target_state"] == row["condition"] == expected, name + ": requested state differs")
        lineage = "pilot" if src["source_batch"] == "legacy_prcv_64" else "expansion"
        require(row["lineage"] == src["source_lineage"] == lineage, name + ": lineage differs")
        ratings = [row[r] for r in RATER_COLUMNS]
        require(all(r in STATE_CATEGORIES for r in ratings), name + ": invalid response")
        state = majority(ratings)
        outcome = local_outcome(state, expected)
        exact = str(len(set(ratings)) == 1).lower()
        require(row["majority_state"] == state, name + ": supplied majority differs")
        require(row["outcome"] == outcome, name + ": supplied outcome differs")
        require(row["exact_agreement"] == exact, name + ": exact agreement differs")
        result.append({**row, "majority_state_recomputed": state, "outcome_recomputed": outcome,
                       "exact_agreement_recomputed": exact})
    require(Counter(r["axis_code"] for r in rows) == Counter({f"A{i}": 25 for i in range(1, 9)}), name + ": family quotas differ")
    require(Counter((r["axis_code"], r["condition"]) for r in rows) == Counter({(f"A{i}", c): n for i in range(1, 9) for c, n in (("target_present", 15), ("target_absent", 10))}), name + ": state quotas differ")
    return result


def audit_changes(raw, corrected, audit_rows):
    before = keyed(raw, "primary")
    after = keyed(corrected, "sensitivity")
    audit = keyed(audit_rows, "correction audit", count=12)
    changed = []
    metadata = ("task_order", "task_id", "image_sha256", "axis_code", "target_anomaly_en",
                "condition", "expected_observed_target_state", "lineage")
    for task_id in sorted(before, key=lambda k: int(before[k]["task_order"])):
        a, b = before[task_id], after[task_id]
        for k in metadata:
            require(a[k] == b[k], f"{task_id}: metadata changed in sensitivity file")
        changed_raters = [r for r in RATER_COLUMNS if a[r] != b[r]]
        if not changed_raters:
            continue
        require(changed_raters == ["R2"], f"{task_id}: changes outside R2")
        entry = {"task_order": a["task_order"], "task_id": task_id, "axis_code": a["axis_code"],
                 "condition": a["condition"], "lineage": a["lineage"], "old_R2_state": a["R2"],
                 "confirmed_R2_state": b["R2"], "majority_before": a["majority_state_recomputed"],
                 "majority_after": b["majority_state_recomputed"], "outcome_before": a["outcome_recomputed"],
                 "outcome_after": b["outcome_recomputed"],
                 "majority_changed": str(a["majority_state_recomputed"] != b["majority_state_recomputed"]).lower(),
                 "exact_before": a["exact_agreement_recomputed"], "exact_after": b["exact_agreement_recomputed"],
                 "blindness_status": "not_established_after_prompt_reveal"}
        require(task_id in audit, f"{task_id}: undocumented correction")
        compare(entry, audit[task_id], "correction." + task_id)
        changed.append(entry)
    require(len(changed) == 12 and {r["task_id"] for r in changed} == set(audit), "correction sets differ")
    return {"changed_rows": len(changed),
            "exact_disagreement_to_agreement": sum(r["exact_before"] == "false" and r["exact_after"] == "true" for r in changed),
            "majority_changed": sum(r["majority_changed"] == "true" for r in changed),
            "nonmatch_to_match": sum(r["outcome_before"] != "match" and r["outcome_after"] == "match" for r in changed)}


def verify_strata(raw, corrected, supplied):
    generated = {}
    for analysis, rows in (("locked_primary", raw), ("sensitivity", corrected)):
        for grouping, key in (("condition", "condition"), ("family", "axis_code"), ("lineage", "lineage")):
            for group, values in grouped_counts(rows, key).items():
                generated[(analysis, grouping, group)] = values
        for grouping, first, second in (("family_x_condition", "axis_code", "condition"), ("family_x_lineage", "axis_code", "lineage")):
            for values in cross_counts(rows, first, second):
                generated[(analysis, grouping, f"{values[first]}|{values[second]}")] = values
    supplied_keys = [(r["analysis"], r["grouping"], r["group"]) for r in supplied]
    require(len(supplied_keys) == len(set(supplied_keys)) and set(supplied_keys) == set(generated), "stratified group sets differ")
    count = 0
    for row, key in zip(supplied, supplied_keys):
        for field, value in row.items():
            if field in ("analysis", "grouping", "group"):
                continue
            expected = generated[key][field]
            actual = None if value == "" else float(value)
            count += compare(actual, expected, "stratum." + "/".join(key) + "." + field)
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output", type=Path, default=None, help="Optional report path; must not replace an input")
    args = parser.parse_args()
    folder = args.input_dir.resolve()
    names = ("locked_primary_ratings.csv", "rater_confirmed_sensitivity_ratings.csv", "coordinator_state_map.csv",
             "correction_audit.csv", "stratified_counts.csv", "analysis_results.json")
    paths = {name: folder / name for name in names}
    source_map = keyed(read_csv(paths["coordinator_state_map.csv"]), "coordinator map")
    raw = validate_matrix(read_csv(paths["locked_primary_ratings.csv"]), source_map, "primary")
    corrected = validate_matrix(read_csv(paths["rater_confirmed_sensitivity_ratings.csv"]), source_map, "sensitivity")
    archived = json.loads(paths["analysis_results.json"].read_text(encoding="utf-8-sig"))
    results = {"locked_primary": summarize(raw), "rater_confirmed_sensitivity": summarize(corrected),
               "correction_audit_summary": audit_changes(raw, corrected, read_csv(paths["correction_audit.csv"]))}
    leaves = sum(compare(value, archived[key], key) for key, value in results.items())
    strata = read_csv(paths["stratified_counts.csv"])
    stratum_leaves = verify_strata(raw, corrected, strata)
    report = {"status": "passed", "public_input_sha256": {name: file_sha256(path) for name, path in paths.items()},
              "checks": {"images_per_matrix": 200, "ratings_per_matrix": 600, "unique_image_hashes": 200,
                         "confirmed_changed_cells": 12, "matched_summary_leaves": leaves,
                         "matched_stratified_rows": len(strata), "matched_stratified_values": stratum_leaves},
              "scope": "Numerical reproduction from supplied matrices; not independent validation of images, rater behaviour, or historical private-file hashes.",
              **results}
    if args.output:
        destination = args.output.resolve()
        require(destination not in [p.resolve() for p in paths.values()], "Output must not overwrite an input")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "checks": report["checks"],
                      "primary": results["locked_primary"]["overall"], "primary_reliability": results["locked_primary"]["reliability"],
                      "sensitivity": results["rater_confirmed_sensitivity"]["overall"],
                      "corrections": results["correction_audit_summary"]}, indent=2))


if __name__ == "__main__":
    main()
