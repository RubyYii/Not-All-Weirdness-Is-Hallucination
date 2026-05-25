"""Parse raw VLM audit responses into a flat CSV."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def parse_response_payload(record: dict[str, object]) -> dict[str, object]:
    response_json = record.get("response_json")
    if isinstance(response_json, dict):
        if "permission_status" in response_json or "should_label_as_hallucination" in response_json:
            return response_json
        extracted = extract_response_text_from_api_payload(response_json)
        if extracted:
            try:
                return json.loads(extracted)
            except json.JSONDecodeError:
                pass

    api_response = record.get("api_response")
    if isinstance(api_response, dict):
        extracted = extract_response_text_from_api_payload(api_response)
        if extracted:
            try:
                return json.loads(extracted)
            except json.JSONDecodeError as exc:
                return {"parse_error": f"{exc.__class__.__name__}: {exc}"}

    response_text = record.get("response_text", "")
    if not isinstance(response_text, str) or not response_text.strip():
        return {"parse_error": "missing response_text"}

    try:
        return json.loads(response_text)
    except json.JSONDecodeError as exc:
        return {"parse_error": f"{exc.__class__.__name__}: {exc}"}


def extract_response_text_from_api_payload(payload: dict[str, object]) -> str:
    output = payload.get("output", [])
    if isinstance(output, list):
        texts: list[str] = []
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content", [])
            if not isinstance(content, list):
                continue
            for part in content:
                if isinstance(part, dict) and part.get("type") in {"output_text", "text"}:
                    text = part.get("text")
                    if isinstance(text, str) and text.strip():
                        texts.append(text)
        if texts:
            return "\n".join(texts)

    choices = payload.get("choices", [])
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message", {})
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str):
                    return content

    candidates = payload.get("candidates", [])
    if isinstance(candidates, list) and candidates:
        first = candidates[0]
        if isinstance(first, dict):
            content = first.get("content", {})
            parts = content.get("parts", []) if isinstance(content, dict) else []
            if isinstance(parts, list):
                texts = [part.get("text", "") for part in parts if isinstance(part, dict)]
                texts = [text for text in texts if isinstance(text, str) and text.strip()]
                if texts:
                    return "\n".join(texts)

    return ""


def iter_input_records(input_path: Path) -> list[tuple[int, dict[str, object]]]:
    records: list[tuple[int, dict[str, object]]] = []
    if input_path.is_dir():
        for index, path in enumerate(sorted(input_path.rglob("*.json")), start=1):
            record = json.loads(path.read_text(encoding="utf-8"))
            record.setdefault("output_path", str(path))
            records.append((index, record))
        return records

    if input_path.suffix.lower() == ".json":
        record = json.loads(input_path.read_text(encoding="utf-8"))
        record.setdefault("output_path", str(input_path))
        return [(1, record)]

    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            records.append((line_number, json.loads(line)))
    return records


def parse_outputs(input_path: Path, output_path: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for line_number, record in iter_input_records(input_path):
        parsed = parse_response_payload(record)
        axis = record.get("axis", {})
        if not isinstance(axis, dict):
            axis = {}
        rows.append(
            {
                "line_number": line_number,
                "sample_id": record.get("sample_id", ""),
                "image_id": record.get("image_id", ""),
                "axis_code": record.get("axis_code", axis.get("axis_code", "")),
                "condition": record.get("condition", ""),
                "model": record.get("model", ""),
                "audit_setting": record.get("audit_setting", record.get("audit_prompt_type", "")),
                "target_anomaly_detected": parsed.get("target_anomaly_detected", ""),
                "permission_status_pred": parsed.get("permission_status", ""),
                "hallucination_pred": parsed.get("should_label_as_hallucination", ""),
                "confidence": parsed.get("confidence", ""),
                "reason": parsed.get("reason", ""),
                "parse_error": parsed.get("parse_error", ""),
                "output_path": record.get("output_path", ""),
                "raw_response": record.get("response_text", ""),
            }
        )

    parsed_df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    parsed_df.to_csv(output_path, index=False, encoding="utf-8")
    return parsed_df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Raw model JSONL file, JSON file, or output directory.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/parsed/audit_outputs_parsed.csv"),
        help="Parsed CSV destination.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    parsed_df = parse_outputs(args.input, args.output)
    summary = {
        "input": str(args.input),
        "output": str(args.output),
        "rows": int(len(parsed_df)),
        "parse_errors": int((parsed_df.get("parse_error", "") != "").sum()) if len(parsed_df) else 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
