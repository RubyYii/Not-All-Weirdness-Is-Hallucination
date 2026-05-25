"""Validate metadata and local image coverage before running VLM audits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


LEGAL_CONDITIONS = {"violating", "permitted", "ambiguous", "no_issue"}
LEGAL_PERMISSION_LABELS = {
    "prompt_required",
    "prompt_permitted",
    "prompt_violating",
    "ambiguous",
    "no_issue",
}
LEGAL_HALLUCINATION_LABELS = {"yes", "no", "uncertain"}
TARGET_CONDITIONS = {"violating", "permitted", "ambiguous"}


def read_metadata(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing metadata CSV: {path}")
    return pd.read_csv(path, keep_default_na=False)


def add_illegal_value_errors(
    errors: list[str],
    df: pd.DataFrame,
    column: str,
    legal_values: set[str],
) -> None:
    illegal = sorted(set(df[column]) - legal_values)
    if illegal:
        errors.append(f"{column} has illegal values: {illegal}")


def validate_dataset(metadata_path: Path, project_root: Path, expected_axes: int) -> tuple[list[str], dict[str, object]]:
    df = read_metadata(metadata_path)
    errors: list[str] = []

    required_columns = {
        "sample_id",
        "image_id",
        "image_path",
        "axis_code",
        "condition",
        "permission_gold",
        "hallucination_gold",
    }
    missing_columns = sorted(required_columns - set(df.columns))
    if missing_columns:
        errors.append(f"metadata_pairs.csv is missing required columns: {missing_columns}")
        return errors, {"rows": int(len(df))}

    duplicate_sample_ids = sorted(df.loc[df["sample_id"].duplicated(), "sample_id"].unique())
    if duplicate_sample_ids:
        errors.append(f"sample_id values are not unique: {duplicate_sample_ids}")

    if df["image_id"].eq("").any():
        bad_rows = df.index[df["image_id"].eq("")].tolist()
        errors.append(f"image_id is empty in rows: {bad_rows}")

    missing_images = []
    for image_path in sorted(df["image_path"].unique()):
        if not (project_root / image_path).exists():
            missing_images.append(image_path)
    if missing_images:
        errors.append(f"image files referenced by metadata are missing: {missing_images}")

    add_illegal_value_errors(errors, df, "condition", LEGAL_CONDITIONS)
    add_illegal_value_errors(errors, df, "permission_gold", LEGAL_PERMISSION_LABELS)
    add_illegal_value_errors(errors, df, "hallucination_gold", LEGAL_HALLUCINATION_LABELS)

    axis_count = df["axis_code"].nunique()
    if axis_count != expected_axes:
        errors.append(f"expected {expected_axes} axes, found {axis_count}")

    for axis_code, axis_df in df.groupby("axis_code", sort=True):
        target_df = axis_df[axis_df["condition"].isin(TARGET_CONDITIONS)]
        control_df = axis_df[axis_df["condition"] == "no_issue"]

        target_images = sorted(target_df["image_id"].unique())
        control_images = sorted(control_df["image_id"].unique())

        if len(target_images) != 5:
            errors.append(f"{axis_code}: expected 5 target images, found {len(target_images)} ({target_images})")
        if len(control_images) != 3:
            errors.append(f"{axis_code}: expected 3 control images, found {len(control_images)} ({control_images})")

        for image_id, image_df in target_df.groupby("image_id", sort=True):
            conditions = set(image_df["condition"])
            if conditions != TARGET_CONDITIONS:
                errors.append(
                    f"{axis_code}/{image_id}: expected target conditions "
                    f"{sorted(TARGET_CONDITIONS)}, found {sorted(conditions)}"
                )
            if len(image_df) != 3:
                errors.append(f"{axis_code}/{image_id}: expected 3 target rows, found {len(image_df)}")

        for image_id, image_df in control_df.groupby("image_id", sort=True):
            if len(image_df) != 1:
                errors.append(f"{axis_code}/{image_id}: expected 1 control row, found {len(image_df)}")

    summary = {
        "metadata": str(metadata_path),
        "project_root": str(project_root),
        "rows": int(len(df)),
        "axes": int(axis_count),
        "unique_images": int(df["image_id"].nunique()),
        "condition_counts": df["condition"].value_counts().sort_index().to_dict(),
        "permission_gold_counts": df["permission_gold"].value_counts().sort_index().to_dict(),
        "hallucination_gold_counts": df["hallucination_gold"].value_counts().sort_index().to_dict(),
        "valid": not errors,
    }
    return errors, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--metadata",
        type=Path,
        default=Path("data/metadata/metadata_pairs.csv"),
        help="Metadata CSV to validate.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
        help="Repository root used to resolve image_path values.",
    )
    parser.add_argument("--expected-axes", type=int, default=8)
    parser.add_argument("--summary-json", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    errors, summary = validate_dataset(args.metadata, args.project_root, args.expected_axes)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.summary_json:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        args.summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    if errors:
        print("\nValidation errors:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("\nDataset validation passed.")


if __name__ == "__main__":
    main()
