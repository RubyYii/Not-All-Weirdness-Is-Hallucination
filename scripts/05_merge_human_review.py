"""Merge human review labels with metadata pairs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def merge_human_review(metadata_path: Path, review_path: Path, output_path: Path) -> pd.DataFrame:
    metadata = pd.read_csv(metadata_path, keep_default_na=False)
    review = pd.read_csv(review_path, keep_default_na=False)

    if "sample_id" not in review.columns:
        raise ValueError("Human review CSV must contain a sample_id column.")
    if review["sample_id"].duplicated().any():
        duplicates = sorted(review.loc[review["sample_id"].duplicated(), "sample_id"].unique())
        raise ValueError(f"Human review CSV has duplicate sample_id values: {duplicates}")

    merged = metadata.merge(review, on="sample_id", how="left", suffixes=("", "_human"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False, encoding="utf-8")
    return merged


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--metadata",
        type=Path,
        default=Path("data/metadata/metadata_pairs.csv"),
        help="Metadata CSV produced by scripts/01_build_metadata.py.",
    )
    parser.add_argument("--review", type=Path, required=True, help="Human review CSV.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/human_review/metadata_with_human_review.csv"),
        help="Merged output CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    review = pd.read_csv(args.review, keep_default_na=False)
    merged = merge_human_review(args.metadata, args.review, args.output)
    review_columns = [column for column in review.columns if column != "sample_id"]
    summary = {
        "metadata": str(args.metadata),
        "review": str(args.review),
        "output": str(args.output),
        "rows": int(len(merged)),
        "review_columns_detected": review_columns,
        "reviewed_rows": int(merged[review_columns].notna().any(axis=1).sum()) if review_columns else 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
