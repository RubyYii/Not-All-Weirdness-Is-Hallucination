"""Compute VLM prompt-permission auditing metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


INTENDED_PERMISSION_LABELS = {"prompt_required", "prompt_permitted"}
LEGAL_PERMISSION_LABELS = {
    "prompt_required",
    "prompt_permitted",
    "prompt_violating",
    "ambiguous",
    "no_issue",
}
LEGAL_HALLUCINATION_LABELS = {"yes", "no", "uncertain"}


def safe_rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def first_existing(columns: set[str], candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def normalize_gold(gold: pd.DataFrame) -> pd.DataFrame:
    columns = set(gold.columns)
    rename_map: dict[str, str] = {}

    sample_id = first_existing(columns, ("sample_id",))
    axis = first_existing(columns, ("axis_code", "axis_id", "axis"))
    permission = first_existing(columns, ("permission_gold", "permission_status_gold", "final_label", "gold_permission_status"))
    hallucination = first_existing(columns, ("hallucination_gold", "gold_hallucination_label", "hallucination_label_gold"))

    required = {
        "sample_id": sample_id,
        "axis_code": axis,
        "permission_gold": permission,
        "hallucination_gold": hallucination,
    }
    missing = sorted(name for name, source in required.items() if source is None)
    if missing:
        raise ValueError(f"Gold labels CSV is missing required logical columns: {missing}")

    for target, source in required.items():
        if source != target:
            rename_map[source] = target  # type: ignore[index]

    normalized = gold.rename(columns=rename_map).copy()
    normalized["permission_gold"] = normalized["permission_gold"].astype(str).str.strip()
    normalized["hallucination_gold"] = normalized["hallucination_gold"].astype(str).str.strip()
    return normalized


def normalize_predictions(predictions: pd.DataFrame) -> pd.DataFrame:
    columns = set(predictions.columns)
    rename_map: dict[str, str] = {}

    sample_id = first_existing(columns, ("sample_id",))
    model = first_existing(columns, ("model", "model_name"))
    audit_prompt_type = first_existing(columns, ("audit_prompt_type", "audit_setting", "setting"))
    permission = first_existing(columns, ("permission_status_pred", "permission_status", "pred_permission_status"))
    hallucination = first_existing(
        columns,
        ("hallucination_pred", "should_label_as_hallucination", "pred_hallucination_label"),
    )
    parse_error = first_existing(columns, ("parse_error", "error_message"))

    required = {
        "sample_id": sample_id,
        "model": model,
        "audit_prompt_type": audit_prompt_type,
        "permission_status_pred": permission,
        "hallucination_pred": hallucination,
    }
    missing = sorted(name for name, source in required.items() if source is None)
    if missing:
        raise ValueError(f"Parsed model outputs CSV is missing required logical columns: {missing}")

    for target, source in required.items():
        if source != target:
            rename_map[source] = target  # type: ignore[index]
    if parse_error and parse_error != "parse_error":
        rename_map[parse_error] = "parse_error"

    normalized = predictions.rename(columns=rename_map).copy()
    if "parse_error" not in normalized.columns:
        normalized["parse_error"] = ""

    normalized["permission_status_pred"] = normalized["permission_status_pred"].astype(str).str.strip()
    normalized["hallucination_pred"] = normalized["hallucination_pred"].astype(str).str.strip()
    normalized["parse_error"] = normalized["parse_error"].fillna("").astype(str).str.strip()
    return normalized


def parseable_mask(group: pd.DataFrame) -> pd.Series:
    no_parse_error = group["parse_error"].eq("")
    legal_permission = group["permission_status_pred"].isin(LEGAL_PERMISSION_LABELS)
    legal_hallucination = group["hallucination_pred"].isin(LEGAL_HALLUCINATION_LABELS)
    return no_parse_error & legal_permission & legal_hallucination


def metric_record(group: pd.DataFrame, keys: dict[str, Any]) -> dict[str, Any]:
    parseable = parseable_mask(group)
    scored = group[parseable].copy()

    total_n = int(len(group))
    parseable_n = int(parseable.sum())
    parse_error_n = total_n - parseable_n

    intended = scored["permission_gold"].isin(INTENDED_PERMISSION_LABELS)
    violating = scored["permission_gold"] == "prompt_violating"
    ambiguous = scored["permission_gold"] == "ambiguous"

    fhr_intended = safe_rate(
        int(scored.loc[intended, "hallucination_pred"].eq("yes").sum()),
        int(intended.sum()),
    )
    mvr_violating = safe_rate(
        int(scored.loc[violating, "hallucination_pred"].ne("yes").sum()),
        int(violating.sum()),
    )

    return {
        **keys,
        "n_total": total_n,
        "n_parseable": parseable_n,
        "n_parse_error": parse_error_n,
        "parse_error_rate": safe_rate(parse_error_n, total_n),
        "PBA": safe_rate(
            int(scored["permission_status_pred"].eq(scored["permission_gold"]).sum()),
            parseable_n,
        ),
        "FHR_intended": fhr_intended,
        "MVR_violating": mvr_violating,
        "ACR": safe_rate(
            int(scored.loc[ambiguous, "hallucination_pred"].eq("uncertain").sum()),
            int(ambiguous.sum()),
        ),
        "Creative_Preservation": None if fhr_intended is None else 1 - fhr_intended,
        "Defect_Sensitivity": None if mvr_violating is None else 1 - mvr_violating,
    }


def validate_labels(gold: pd.DataFrame) -> None:
    illegal_permission = sorted(set(gold["permission_gold"]) - LEGAL_PERMISSION_LABELS)
    illegal_hallucination = sorted(set(gold["hallucination_gold"]) - LEGAL_HALLUCINATION_LABELS)
    if illegal_permission:
        raise ValueError(f"Gold labels contain illegal permission labels: {illegal_permission}")
    if illegal_hallucination:
        raise ValueError(f"Gold labels contain illegal hallucination labels: {illegal_hallucination}")


def build_metric_table(merged: pd.DataFrame, group_columns: list[str]) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for keys, group in merged.groupby(group_columns, dropna=False, sort=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        records.append(metric_record(group, dict(zip(group_columns, keys))))
    return pd.DataFrame(records)


def write_latex_table(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    display_df = df.copy()
    metric_columns = [
        "parse_error_rate",
        "PBA",
        "FHR_intended",
        "MVR_violating",
        "ACR",
        "Creative_Preservation",
        "Defect_Sensitivity",
    ]
    for column in metric_columns:
        if column in display_df.columns:
            display_df[column] = display_df[column].map(lambda value: "" if pd.isna(value) else f"{value:.3f}")
    latex = dataframe_to_latex(display_df)
    path.write_text(latex, encoding="utf-8")


def escape_latex(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def dataframe_to_latex(df: pd.DataFrame) -> str:
    alignment = "l" * len(df.columns)
    lines = [
        rf"\begin{{tabular}}{{{alignment}}}",
        r"\toprule",
        " & ".join(escape_latex(column) for column in df.columns) + r" \\",
        r"\midrule",
    ]
    for _, row in df.iterrows():
        lines.append(" & ".join(escape_latex(row[column]) for column in df.columns) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    return "\n".join(lines)


def compute_metrics(
    gold_path: Path,
    predictions_path: Path,
    main_metrics_path: Path,
    axis_metrics_path: Path,
    main_latex_path: Path,
    axis_latex_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    gold = normalize_gold(pd.read_csv(gold_path, keep_default_na=False))
    predictions = normalize_predictions(pd.read_csv(predictions_path, keep_default_na=False))
    validate_labels(gold)

    if gold["sample_id"].duplicated().any():
        duplicates = sorted(gold.loc[gold["sample_id"].duplicated(), "sample_id"].unique())
        raise ValueError(f"Gold labels contain duplicate sample_id values: {duplicates}")

    merged = predictions.merge(
        gold[["sample_id", "axis_code", "permission_gold", "hallucination_gold"]],
        on="sample_id",
        how="inner",
        suffixes=("", "_gold"),
    )
    if merged.empty:
        raise ValueError("No overlapping sample_id values between gold labels and parsed model outputs.")

    missing_predictions = sorted(set(gold["sample_id"]) - set(predictions["sample_id"]))
    if missing_predictions:
        print(f"Warning: {len(missing_predictions)} gold sample_id values have no prediction.")

    main_metrics = build_metric_table(merged, ["model", "audit_prompt_type"])
    axis_metrics = build_metric_table(merged, ["model", "audit_prompt_type", "axis_code"])

    main_metrics_path.parent.mkdir(parents=True, exist_ok=True)
    axis_metrics_path.parent.mkdir(parents=True, exist_ok=True)
    main_metrics.to_csv(main_metrics_path, index=False, encoding="utf-8")
    axis_metrics.to_csv(axis_metrics_path, index=False, encoding="utf-8")
    write_latex_table(main_metrics, main_latex_path)
    write_latex_table(axis_metrics, axis_latex_path)
    return main_metrics, axis_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--gold",
        "--final-gold-labels",
        dest="gold",
        type=Path,
        default=Path("data/metadata/final_gold_labels.csv"),
        help="Final gold labels CSV. Must include sample_id, axis, permission gold, and hallucination gold.",
    )
    parser.add_argument(
        "--predictions",
        "--parsed-outputs",
        dest="predictions",
        type=Path,
        required=True,
        help="Parsed model outputs CSV.",
    )
    parser.add_argument("--main-output", type=Path, default=Path("outputs/metrics/main_metrics.csv"))
    parser.add_argument("--axis-output", type=Path, default=Path("outputs/metrics/axis_metrics.csv"))
    parser.add_argument("--main-tex", type=Path, default=Path("paper/tables/main_metrics.tex"))
    parser.add_argument("--axis-tex", type=Path, default=Path("paper/tables/axis_metrics.tex"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    main_metrics, axis_metrics = compute_metrics(
        gold_path=args.gold,
        predictions_path=args.predictions,
        main_metrics_path=args.main_output,
        axis_metrics_path=args.axis_output,
        main_latex_path=args.main_tex,
        axis_latex_path=args.axis_tex,
    )
    summary = {
        "gold": str(args.gold),
        "predictions": str(args.predictions),
        "main_metrics": str(args.main_output),
        "axis_metrics": str(args.axis_output),
        "main_rows": int(len(main_metrics)),
        "axis_rows": int(len(axis_metrics)),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
