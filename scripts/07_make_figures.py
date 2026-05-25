"""Create paper figures for the prompt-permission auditing experiment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import patches


AXIS_ORDER = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]
AXIS_LABELS = {
    "A1": "A1 Anatomy / Hands",
    "A2": "A2 Text",
    "A3": "A3 Physics",
    "A4": "A4 Object Fusion",
    "A5": "A5 Count / Repetition",
    "A6": "A6 Impossible Geometry",
    "A7": "A7 Scale / Proportion",
    "A8": "A8 Artistic Deformation",
}


def resolve_path(path: Path, project_root: Path) -> Path:
    return path if path.is_absolute() else project_root / path


def save_figure(fig: plt.Figure, output_dir: Path, stem: str, dpi: int) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for suffix in ("png", "pdf"):
        path = output_dir / f"{stem}.{suffix}"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        paths.append(str(path))
    plt.close(fig)
    return paths


def clean_float(value: Any) -> float | None:
    if value is None or pd.isna(value) or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def metric_column(df: pd.DataFrame, preferred: str, aliases: tuple[str, ...] = ()) -> str:
    for candidate in (preferred, *aliases):
        if candidate in df.columns:
            return candidate
    raise ValueError(f"Missing metric column '{preferred}'. Available columns: {list(df.columns)}")


def display_group(row: pd.Series) -> str:
    model = str(row.get("model", "")).strip()
    audit_prompt_type = str(row.get("audit_prompt_type", row.get("audit_setting", ""))).strip()
    return f"{model}\n{audit_prompt_type}".strip()


def make_concept_diagram(output_dir: Path, dpi: int) -> list[str]:
    fig, ax = plt.subplots(figsize=(10.5, 3.8))
    ax.set_axis_off()

    nodes = [
        {
            "xy": (0.05, 0.44),
            "text": "Visual\nabnormality",
            "fc": "#f2f2f2",
            "ec": "#333333",
        },
        {
            "xy": (0.37, 0.44),
            "text": "Prompt-permission\ncheck",
            "fc": "#e8f2ff",
            "ec": "#2b5f9e",
        },
        {
            "xy": (0.72, 0.66),
            "text": "Hallucination\nprompt-violating",
            "fc": "#ffe8e5",
            "ec": "#b94437",
        },
        {
            "xy": (0.72, 0.42),
            "text": "Intended deviation\nprompt-required/permitted",
            "fc": "#e8f6e8",
            "ec": "#3b7f3f",
        },
        {
            "xy": (0.72, 0.18),
            "text": "Ambiguous\nwithhold hard label",
            "fc": "#fff3d8",
            "ec": "#a66a00",
        },
    ]

    width = 0.23
    height = 0.15
    for node in nodes:
        x, y = node["xy"]
        box = patches.FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.018,rounding_size=0.025",
            linewidth=1.8,
            facecolor=node["fc"],
            edgecolor=node["ec"],
            transform=ax.transAxes,
        )
        ax.add_patch(box)
        ax.text(
            x + width / 2,
            y + height / 2,
            node["text"],
            ha="center",
            va="center",
            fontsize=11,
            transform=ax.transAxes,
        )

    arrow_style = dict(arrowstyle="->", linewidth=2, color="#333333", shrinkA=5, shrinkB=5)
    ax.annotate("", xy=(0.37, 0.515), xytext=(0.28, 0.515), xycoords=ax.transAxes, arrowprops=arrow_style)
    for y in (0.735, 0.495, 0.255):
        ax.annotate("", xy=(0.72, y), xytext=(0.60, 0.515), xycoords=ax.transAxes, arrowprops=arrow_style)

    ax.text(
        0.5,
        0.96,
        "Figure 1. Hallucination-label eligibility is prompt-conditional",
        ha="center",
        va="top",
        fontsize=14,
        fontweight="bold",
        transform=ax.transAxes,
    )
    ax.text(
        0.5,
        0.05,
        "The same apparent abnormality can be an error, a controlled creative choice, or undecidable under the prompt.",
        ha="center",
        va="bottom",
        fontsize=10,
        color="#444444",
        transform=ax.transAxes,
    )
    return save_figure(fig, output_dir, "figure1_concept_diagram", dpi)


def representative_images(metadata: pd.DataFrame, image_dir: Path, project_root: Path) -> list[tuple[str, Path]]:
    reps: list[tuple[str, Path]] = []
    image_dir = resolve_path(image_dir, project_root)

    for axis_code in AXIS_ORDER:
        axis_df = metadata[metadata["axis_code"] == axis_code].copy()
        if axis_df.empty:
            continue
        if "condition" in axis_df.columns:
            target_df = axis_df[axis_df["condition"] == "violating"]
            if not target_df.empty:
                axis_df = target_df
        row = axis_df.iloc[0]
        image_path = Path(str(row["image_path"]))
        candidates = [
            image_dir / image_path.name,
            resolve_path(image_path, project_root),
            project_root / "image" / image_path.name,
        ]
        for candidate in candidates:
            if candidate.exists():
                label = AXIS_LABELS.get(axis_code, f"{axis_code} {row.get('axis_en', '')}".strip())
                reps.append((label, candidate))
                break
    return reps


def make_dataset_grid(metadata_path: Path, image_dir: Path, project_root: Path, output_dir: Path, dpi: int) -> list[str]:
    metadata = pd.read_csv(metadata_path, keep_default_na=False)
    reps = representative_images(metadata, image_dir, project_root)
    if len(reps) != 8:
        raise ValueError(f"Expected 8 representative axis images, found {len(reps)}.")

    fig, axes = plt.subplots(2, 4, figsize=(12, 6.6))
    for ax, (label, image_path) in zip(axes.flat, reps):
        image = mpimg.imread(image_path)
        ax.imshow(image)
        ax.set_title(label, fontsize=10, pad=6)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_linewidth(0.8)
            spine.set_color("#333333")

    fig.suptitle("Figure 2. Dataset example grid: one representative image per anomaly axis", fontsize=14, fontweight="bold")
    fig.subplots_adjust(wspace=0.04, hspace=0.24, top=0.88)
    return save_figure(fig, output_dir, "figure2_dataset_example_grid", dpi)


def load_main_metrics(path: Path) -> pd.DataFrame:
    metrics = pd.read_csv(path, keep_default_na=False)
    required = {"model"}
    if "audit_prompt_type" not in metrics.columns and "audit_setting" in metrics.columns:
        metrics = metrics.rename(columns={"audit_setting": "audit_prompt_type"})
    required.add("audit_prompt_type")
    missing = sorted(required - set(metrics.columns))
    if missing:
        raise ValueError(f"Main metrics CSV is missing columns: {missing}")

    creative_col = metric_column(metrics, "Creative_Preservation", ("CPR",))
    sensitivity_col = metric_column(metrics, "Defect_Sensitivity", ("DS",))
    metrics = metrics.copy()
    metrics["Creative_Preservation"] = metrics[creative_col].map(clean_float)
    metrics["Defect_Sensitivity"] = metrics[sensitivity_col].map(clean_float)
    metrics = metrics.dropna(subset=["Creative_Preservation", "Defect_Sensitivity"])
    return metrics


def make_frontier(metrics_path: Path, output_dir: Path, dpi: int) -> list[str]:
    metrics = load_main_metrics(metrics_path)
    if metrics.empty:
        raise ValueError("No complete Creative_Preservation and Defect_Sensitivity points found.")

    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    models = sorted(metrics["model"].unique())
    marker_cycle = ["o", "s", "^", "D", "P", "X", "v", "*"]
    color_cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    model_style = {
        model: (marker_cycle[i % len(marker_cycle)], color_cycle[i % len(color_cycle)])
        for i, model in enumerate(models)
    }

    for _, row in metrics.iterrows():
        marker, color = model_style[row["model"]]
        x = row["Creative_Preservation"]
        y = row["Defect_Sensitivity"]
        ax.scatter(x, y, s=95, marker=marker, color=color, edgecolor="white", linewidth=0.8, zorder=3)
        ax.annotate(
            str(row["audit_prompt_type"]),
            (x, y),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=8,
            color="#333333",
        )

    handles = [
        ax.scatter([], [], s=80, marker=model_style[model][0], color=model_style[model][1], label=model)
        for model in models
    ]
    ax.legend(handles=handles, title="Model", loc="lower left", frameon=True)
    ax.set_xlim(-0.03, 1.03)
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlabel("Creative Preservation = 1 - FHR_intended")
    ax.set_ylabel("Defect Sensitivity = 1 - MVR_violating")
    ax.set_title("Figure 3. Creative Preservation vs Defect Sensitivity frontier", fontweight="bold")
    ax.grid(True, linewidth=0.6, alpha=0.35)
    ax.axhline(1.0, color="#dddddd", linewidth=0.8)
    ax.axvline(1.0, color="#dddddd", linewidth=0.8)
    return save_figure(fig, output_dir, "figure3_creative_preservation_defect_sensitivity_frontier", dpi)


def load_axis_metrics(path: Path, metric: str) -> pd.DataFrame:
    metrics = pd.read_csv(path, keep_default_na=False)
    if "audit_prompt_type" not in metrics.columns and "audit_setting" in metrics.columns:
        metrics = metrics.rename(columns={"audit_setting": "audit_prompt_type"})
    required = {"model", "audit_prompt_type", "axis_code", metric}
    missing = sorted(required - set(metrics.columns))
    if missing:
        raise ValueError(f"Axis metrics CSV is missing columns: {missing}")
    metrics = metrics.copy()
    metrics[metric] = metrics[metric].map(clean_float)
    return metrics.dropna(subset=[metric])


def make_axis_heatmap(axis_metrics_path: Path, output_dir: Path, dpi: int, heatmap_metric: str) -> list[str]:
    metrics = load_axis_metrics(axis_metrics_path, heatmap_metric)
    if metrics.empty:
        raise ValueError(f"No axis metric values found for {heatmap_metric}.")

    metrics["column_label"] = metrics.apply(display_group, axis=1)
    pivot = metrics.pivot_table(
        index="axis_code",
        columns="column_label",
        values=heatmap_metric,
        aggfunc="mean",
    )
    ordered_rows = [axis for axis in AXIS_ORDER if axis in pivot.index]
    pivot = pivot.loc[ordered_rows]

    fig_width = max(7.5, 1.25 * max(1, len(pivot.columns)) + 2.5)
    fig_height = max(5.2, 0.58 * max(1, len(pivot.index)) + 1.8)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    image = ax.imshow(pivot.values, cmap="viridis", vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=35, ha="right", fontsize=8)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([AXIS_LABELS.get(axis, axis) for axis in pivot.index], fontsize=9)
    ax.set_title(f"Figure 4. Axis-level heatmap: {heatmap_metric}", fontweight="bold")

    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            value = pivot.iat[i, j]
            if pd.isna(value):
                label = ""
            else:
                label = f"{value:.2f}"
            ax.text(j, i, label, ha="center", va="center", color="white" if value < 0.55 else "black", fontsize=8)

    ax.set_xlabel("Model × audit prompt type")
    ax.set_ylabel("Anomaly axis")
    cbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.025)
    cbar.set_label(heatmap_metric)
    return save_figure(fig, output_dir, f"figure4_axis_heatmap_{heatmap_metric}", dpi)


def make_figures(
    metadata_path: Path,
    image_dir: Path,
    main_metrics_path: Path,
    axis_metrics_path: Path,
    output_dir: Path,
    project_root: Path,
    heatmap_metric: str,
    dpi: int,
) -> dict[str, object]:
    project_root = project_root.resolve()
    output_dir = resolve_path(output_dir, project_root)
    created: dict[str, list[str]] = {}

    created["figure1"] = make_concept_diagram(output_dir, dpi)
    created["figure2"] = make_dataset_grid(
        resolve_path(metadata_path, project_root),
        image_dir,
        project_root,
        output_dir,
        dpi,
    )
    created["figure3"] = make_frontier(resolve_path(main_metrics_path, project_root), output_dir, dpi)
    created["figure4"] = make_axis_heatmap(resolve_path(axis_metrics_path, project_root), output_dir, dpi, heatmap_metric)

    return {
        "output_dir": str(output_dir),
        "heatmap_metric": heatmap_metric,
        "created": created,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--metadata",
        type=Path,
        default=Path("data/metadata/metadata_pairs.csv"),
        help="Metadata CSV used for Figure 2.",
    )
    parser.add_argument(
        "--image-dir",
        type=Path,
        default=Path("data/images"),
        help="Image directory. Falls back to metadata paths and image/ when needed.",
    )
    parser.add_argument(
        "--main-metrics",
        type=Path,
        default=Path("outputs/metrics/main_metrics.csv"),
        help="Main metrics CSV from scripts/06_compute_metrics.py.",
    )
    parser.add_argument(
        "--axis-metrics",
        type=Path,
        default=Path("outputs/metrics/axis_metrics.csv"),
        help="Axis metrics CSV from scripts/06_compute_metrics.py.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("paper/figures"))
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--heatmap-metric", choices=["PBA", "FHR_intended"], default="PBA")
    parser.add_argument("--dpi", type=int, default=300)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = make_figures(
        metadata_path=args.metadata,
        image_dir=args.image_dir,
        main_metrics_path=args.main_metrics,
        axis_metrics_path=args.axis_metrics,
        output_dir=args.output_dir,
        project_root=args.project_root,
        heatmap_metric=args.heatmap_metric,
        dpi=args.dpi,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
