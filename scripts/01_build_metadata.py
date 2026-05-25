"""Build the 144-row prompt-image metadata table for the PRCV pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


TARGET_IMAGE_COUNT = 5
CONTROL_IMAGE_COUNT = 3
TARGET_CONDITIONS = ("violating", "permitted", "ambiguous")
CONTROL_CONDITION = "no_issue"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing input CSV: {path}")
    return pd.read_csv(path, keep_default_na=False)


def require_columns(df: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = sorted(columns.difference(df.columns))
    if missing:
        raise ValueError(f"{label} is missing required columns: {missing}")


def build_metadata(
    generation_prompts_path: Path,
    evaluation_contexts_path: Path,
    output_path: Path,
) -> pd.DataFrame:
    generation = read_csv(generation_prompts_path)
    contexts = read_csv(evaluation_contexts_path)

    require_columns(
        generation,
        {
            "axis_code",
            "image_prefix",
            "axis_en",
            "axis_zh",
            "target_anomaly_en",
            "target_anomaly_zh",
            "core_generation_prompt_en",
            "no_issue_generation_prompt_en",
        },
        "generation_prompts.csv",
    )
    require_columns(
        contexts,
        {
            "axis_code",
            "condition",
            "sample_suffix",
            "evaluation_prompt_en",
            "evaluation_prompt_zh",
            "permission_gold",
            "hallucination_gold",
        },
        "evaluation_context_prompts.csv",
    )

    rows: list[dict[str, object]] = []
    for axis in generation.to_dict("records"):
        axis_code = axis["axis_code"]
        prefix = axis["image_prefix"]
        axis_contexts = contexts[contexts["axis_code"] == axis_code]

        for condition in (*TARGET_CONDITIONS, CONTROL_CONDITION):
            matches = axis_contexts[axis_contexts["condition"] == condition]
            if len(matches) != 1:
                raise ValueError(
                    f"Expected exactly one context for axis={axis_code}, "
                    f"condition={condition}; found {len(matches)}"
                )

        for image_index in range(1, TARGET_IMAGE_COUNT + 1):
            image_id = f"{prefix}{image_index}"
            for condition in TARGET_CONDITIONS:
                context = axis_contexts[axis_contexts["condition"] == condition].iloc[0]
                sample_suffix = context["sample_suffix"]
                rows.append(
                    {
                        "sample_id": f"{image_id}_{sample_suffix}",
                        "image_id": image_id,
                        "image_path": f"image/{image_id}.png",
                        "axis_code": axis_code,
                        "axis_en": axis["axis_en"],
                        "axis_zh": axis["axis_zh"],
                        "condition": condition,
                        "target_anomaly_en": axis["target_anomaly_en"],
                        "target_anomaly_zh": axis["target_anomaly_zh"],
                        "source_generation_prompt_en": axis["core_generation_prompt_en"],
                        "evaluation_prompt_en": context["evaluation_prompt_en"],
                        "evaluation_prompt_zh": context["evaluation_prompt_zh"],
                        "permission_gold": context["permission_gold"],
                        "hallucination_gold": context["hallucination_gold"],
                        "is_control": False,
                        "include_in_main": True,
                    }
                )

        no_issue_context = axis_contexts[axis_contexts["condition"] == CONTROL_CONDITION].iloc[0]
        for image_index in range(TARGET_IMAGE_COUNT + 1, TARGET_IMAGE_COUNT + CONTROL_IMAGE_COUNT + 1):
            image_id = f"{prefix}{image_index}"
            rows.append(
                {
                    "sample_id": image_id,
                    "image_id": image_id,
                    "image_path": f"image/{image_id}.png",
                    "axis_code": axis_code,
                    "axis_en": axis["axis_en"],
                    "axis_zh": axis["axis_zh"],
                    "condition": CONTROL_CONDITION,
                    "target_anomaly_en": "none",
                    "target_anomaly_zh": "无",
                    "source_generation_prompt_en": axis["no_issue_generation_prompt_en"],
                    "evaluation_prompt_en": no_issue_context["evaluation_prompt_en"],
                    "evaluation_prompt_zh": no_issue_context["evaluation_prompt_zh"],
                    "permission_gold": no_issue_context["permission_gold"],
                    "hallucination_gold": no_issue_context["hallucination_gold"],
                    "is_control": True,
                    "include_in_main": True,
                }
            )

    metadata = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metadata.to_csv(output_path, index=False, encoding="utf-8")
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--generation-prompts",
        type=Path,
        default=Path("data/metadata/generation_prompts.csv"),
        help="Axis-level generation prompt CSV.",
    )
    parser.add_argument(
        "--evaluation-contexts",
        type=Path,
        default=Path("data/metadata/evaluation_context_prompts.csv"),
        help="Axis-by-condition evaluation prompt CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/metadata/metadata_pairs.csv"),
        help="Destination metadata CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = build_metadata(args.generation_prompts, args.evaluation_contexts, args.output)
    summary = {
        "output": str(args.output),
        "rows": int(len(metadata)),
        "axes": int(metadata["axis_code"].nunique()),
        "unique_images": int(metadata["image_id"].nunique()),
        "condition_counts": metadata["condition"].value_counts().sort_index().to_dict(),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
