"""Export a compact model score workbook without optional Excel writer dependencies."""

from __future__ import annotations

import argparse
import html
import json
import re
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd


MAX_CELL_CHARS = 32000


def sanitize_sheet_name(name: str) -> str:
    cleaned = re.sub(r"[\[\]:*?/\\]", "_", name)[:31]
    return cleaned or "Sheet"


def cell_ref(row_index: int, col_index: int) -> str:
    letters = ""
    col = col_index
    while col:
        col, remainder = divmod(col - 1, 26)
        letters = chr(65 + remainder) + letters
    return f"{letters}{row_index}"


def xml_value(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    text = str(value)
    if len(text) > MAX_CELL_CHARS:
        text = text[: MAX_CELL_CHARS - 16] + " [truncated]"
    return escape(text)


def sheet_xml(df: pd.DataFrame) -> str:
    rows: list[str] = []
    headers = list(df.columns)
    for row_idx, values in enumerate([headers, *df.astype(object).values.tolist()], start=1):
        cells = []
        for col_idx, value in enumerate(values, start=1):
            ref = cell_ref(row_idx, col_idx)
            cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{xml_value(value)}</t></is></c>')
        rows.append(f'<row r="{row_idx}">{"".join(cells)}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(rows)}</sheetData>'
        "</worksheet>"
    )


def workbook_xml(sheet_names: list[str]) -> str:
    sheets = "".join(
        f'<sheet name="{escape(name)}" sheetId="{idx}" r:id="rId{idx}"/>'
        for idx, name in enumerate(sheet_names, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheets>{sheets}</sheets>"
        "</workbook>"
    )


def workbook_rels_xml(sheet_count: int) -> str:
    rels = [
        '<Relationship Id="rIdStyles" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
    ]
    rels.extend(
        f'<Relationship Id="rId{idx}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        f'Target="worksheets/sheet{idx}.xml"/>'
        for idx in range(1, sheet_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'{"".join(rels)}'
        "</Relationships>"
    )


def content_types_xml(sheet_count: int) -> str:
    sheet_overrides = "".join(
        f'<Override PartName="/xl/worksheets/sheet{idx}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for idx in range(1, sheet_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        f"{sheet_overrides}"
        "</Types>"
    )


def root_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    )


def styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>'
        '<borders count="1"><border/></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
        "</styleSheet>"
    )


def write_xlsx(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet_names = [sanitize_sheet_name(name) for name in sheets]
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml(len(sheets)))
        zf.writestr("_rels/.rels", root_rels_xml())
        zf.writestr("xl/workbook.xml", workbook_xml(sheet_names))
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml(len(sheets)))
        zf.writestr("xl/styles.xml", styles_xml())
        for idx, (_, df) in enumerate(sheets.items(), start=1):
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", sheet_xml(df))


def build_score_sheets(gold_path: Path, parsed_path: Path, main_metrics_path: Path, axis_metrics_path: Path, run_log_path: Path) -> dict[str, pd.DataFrame]:
    gold = pd.read_csv(gold_path, keep_default_na=False)
    parsed = pd.read_csv(parsed_path, keep_default_na=False)
    main_metrics = pd.read_csv(main_metrics_path, keep_default_na=False)
    axis_metrics = pd.read_csv(axis_metrics_path, keep_default_na=False)
    run_log = pd.read_csv(run_log_path, keep_default_na=False)

    comparison = gold.merge(parsed, on="sample_id", how="left", suffixes=("_goldsrc", "_predsrc"))
    comparison["permission_match"] = comparison["permission_gold"] == comparison["permission_status_pred"]
    comparison["hallucination_match"] = comparison["hallucination_gold"] == comparison["hallucination_pred"]
    comparison["overall_match"] = comparison["permission_match"] & comparison["hallucination_match"]

    columns = [
        "sample_id",
        "image_id_goldsrc",
        "image_path",
        "axis_code_goldsrc",
        "axis_en",
        "condition_goldsrc",
        "target_anomaly_en",
        "permission_gold",
        "permission_status_pred",
        "hallucination_gold",
        "hallucination_pred",
        "target_anomaly_detected",
        "confidence",
        "permission_match",
        "hallucination_match",
        "overall_match",
        "reason",
        "parse_error",
    ]
    available_columns = [column for column in columns if column in comparison.columns]
    compact = comparison[available_columns].copy()
    mismatches = compact[compact["overall_match"] == False].copy()  # noqa: E712 - pandas comparison.

    model = parsed["model"].iloc[0] if len(parsed) else ""
    audit_prompt_type = parsed["audit_setting"].iloc[0] if "audit_setting" in parsed.columns and len(parsed) else ""

    summary = pd.DataFrame(
        [
            {"field": "model", "value": model},
            {"field": "audit_prompt_type", "value": audit_prompt_type},
            {"field": "rows", "value": len(parsed)},
            {"field": "parse_errors", "value": int(parsed.get("parse_error", pd.Series(dtype=str)).astype(str).ne("").sum()) if len(parsed) else 0},
            {"field": "raw_outputs", "value": f"outputs/raw/{model}/{audit_prompt_type}" if model and audit_prompt_type else ""},
        ]
    )

    return {
        "summary": summary,
        "main_metrics": main_metrics,
        "axis_metrics": axis_metrics,
        "comparison": compact,
        "mismatches": mismatches,
        "run_log": run_log,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, default=Path("data/metadata/metadata_pairs.csv"))
    parser.add_argument("--parsed", type=Path, default=Path("outputs/parsed/gpt-5.4_permission_aware_parsed.csv"))
    parser.add_argument("--main-metrics", type=Path, default=Path("outputs/metrics/main_metrics.csv"))
    parser.add_argument("--axis-metrics", type=Path, default=Path("outputs/metrics/axis_metrics.csv"))
    parser.add_argument("--run-log", type=Path, default=Path("outputs/run_logs/gpt-5.4_permission_aware_run_log.csv"))
    parser.add_argument("--output", type=Path, default=Path("score/gpt5.4score.xlsx"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sheets = build_score_sheets(args.gold, args.parsed, args.main_metrics, args.axis_metrics, args.run_log)
    write_xlsx(args.output, sheets)
    print(json.dumps({"output": str(args.output), "sheets": list(sheets)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
