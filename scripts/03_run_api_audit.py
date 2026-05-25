"""Run VLM prompt-permission audits and save one raw output per sample."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd


PROMPT_FILES = {
    "image_only": Path("prompts/auditor_image_only.txt"),
    "prompt_conditioned": Path("prompts/auditor_prompt_conditioned.txt"),
    "permission_aware": Path("prompts/auditor_permission_aware.txt"),
}

LEGAL_PERMISSION_LABELS = {
    "prompt_required",
    "prompt_permitted",
    "prompt_violating",
    "ambiguous",
    "no_issue",
}
LEGAL_HALLUCINATION_LABELS = {"yes", "no", "uncertain"}
LEGAL_CONFIDENCE_LABELS = {"high", "medium", "low"}

AUDIT_RESPONSE_FORMAT = {
    "type": "json_schema",
    "name": "vlm_prompt_permission_audit",
    "schema": {
        "type": "object",
        "properties": {
            "target_anomaly_detected": {"type": "boolean"},
            "permission_status": {
                "type": "string",
                "enum": sorted(LEGAL_PERMISSION_LABELS),
            },
            "should_label_as_hallucination": {
                "type": "string",
                "enum": sorted(LEGAL_HALLUCINATION_LABELS),
            },
            "reason": {"type": "string"},
            "confidence": {
                "type": "string",
                "enum": sorted(LEGAL_CONFIDENCE_LABELS),
            },
        },
        "required": [
            "target_anomaly_detected",
            "permission_status",
            "should_label_as_hallucination",
            "reason",
            "confidence",
        ],
        "additionalProperties": False,
    },
    "strict": True,
}


def load_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing prompt template: {path}")
    return path.read_text(encoding="utf-8")


def render_template(template: str, row: pd.Series) -> str:
    values = {key: "" if pd.isna(value) else value for key, value in row.to_dict().items()}
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{" + key + "}", str(value))
    return rendered


def resolve_path(path: Path, project_root: Path) -> Path:
    return path if path.is_absolute() else project_root / path


def resolve_image_path(row: pd.Series, image_dir: Path, project_root: Path) -> Path:
    metadata_image_path = Path(str(row["image_path"]))
    image_dir = resolve_path(image_dir, project_root)
    metadata_path = resolve_path(metadata_image_path, project_root)
    suffix = metadata_image_path.suffix or ".png"
    filename = metadata_image_path.name or f"{row['image_id']}{suffix}"

    candidates = [
        image_dir / filename,
        image_dir / f"{row['image_id']}{suffix}",
        metadata_path,
        project_root / "image" / filename,
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    checked = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"Could not find image for sample_id={row['sample_id']}. Checked: {checked}")


def image_to_data_url(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if mime_type is None:
        mime_type = "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def image_to_base64_payload(image_path: Path) -> tuple[str, str]:
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if mime_type is None:
        mime_type = "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return mime_type, encoded


def safe_path_component(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._") or "model"


def build_auditor_instruction(template: str, row: pd.Series) -> str:
    rendered_template = render_template(template, row).strip()
    return f"""{rendered_template}

Sample metadata:
- sample_id: {row["sample_id"]}
- axis: {row["axis_code"]} / {row.get("axis_en", "")}
- evaluation_prompt_text: {row.get("evaluation_prompt_en", "")}
- target_anomaly: {row.get("target_anomaly_en", "")}

Return exactly one JSON object with this schema:
{{
  "target_anomaly_detected": true,
  "permission_status": "prompt_required | prompt_permitted | prompt_violating | ambiguous | no_issue",
  "should_label_as_hallucination": "yes | no | uncertain",
  "reason": "...",
  "confidence": "high | medium | low"
}}
"""


def extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        parsed = json.loads(text[start : end + 1])

    if not isinstance(parsed, dict):
        raise ValueError("Model output parsed as JSON but was not an object.")
    return parsed


def validate_audit_json(parsed: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "target_anomaly_detected",
        "permission_status",
        "should_label_as_hallucination",
        "reason",
        "confidence",
    }
    missing = sorted(required - set(parsed))
    if missing:
        errors.append(f"missing required keys: {missing}")

    if "target_anomaly_detected" in parsed and not isinstance(parsed["target_anomaly_detected"], bool):
        errors.append("target_anomaly_detected must be boolean")
    if parsed.get("permission_status") not in LEGAL_PERMISSION_LABELS:
        errors.append(f"illegal permission_status: {parsed.get('permission_status')!r}")
    if parsed.get("should_label_as_hallucination") not in LEGAL_HALLUCINATION_LABELS:
        errors.append(
            "illegal should_label_as_hallucination: "
            f"{parsed.get('should_label_as_hallucination')!r}"
        )
    if parsed.get("confidence") not in LEGAL_CONFIDENCE_LABELS:
        errors.append(f"illegal confidence: {parsed.get('confidence')!r}")
    if "reason" in parsed and not isinstance(parsed["reason"], str):
        errors.append("reason must be a string")

    return errors


def get_openai_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Set it in your shell before running OpenAI audits.")
    return api_key


def get_anthropic_api_key() -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Set it in your shell before running Claude audits."
        )
    return api_key


def get_gemini_api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set. Set it in your shell before running Gemini audits.")
    return api_key


def get_qwen_api_key() -> str:
    api_key = os.environ.get("DASHSCOPE_API_KEY", "").strip() or os.environ.get("QWEN_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "DASHSCOPE_API_KEY or QWEN_API_KEY is not set. Set one before running Qwen audits."
        )
    return api_key


def choose_provider(provider: str, model: str) -> str:
    if provider != "auto":
        return provider
    model_lower = model.lower()
    if model_lower.startswith("claude"):
        return "anthropic"
    if model_lower.startswith("gemini"):
        return "gemini"
    if model_lower.startswith("qwen"):
        return "qwen"
    return "openai"


def response_to_text(response: Any) -> str:
    if isinstance(response, dict):
        output = response.get("output", [])
        if output and isinstance(output, list):
            output_texts = []
            for item in output:
                if not isinstance(item, dict):
                    continue
                for content in item.get("content", []):
                    if isinstance(content, dict) and content.get("type") in {"output_text", "text"}:
                        text = content.get("text")
                        if text:
                            output_texts.append(str(text))
            if output_texts:
                return "\n".join(output_texts)

        choices = response.get("choices", [])
        if choices and isinstance(choices, list):
            message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
            content = message.get("content") if isinstance(message, dict) else None
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts = [str(part.get("text", "")) for part in content if isinstance(part, dict)]
                if parts:
                    return "\n".join(parts)

        candidates = response.get("candidates", [])
        if candidates and isinstance(candidates, list):
            content = candidates[0].get("content", {}) if isinstance(candidates[0], dict) else {}
            parts = content.get("parts", []) if isinstance(content, dict) else []
            texts = [str(part.get("text", "")) for part in parts if isinstance(part, dict) and part.get("text")]
            if texts:
                return "\n".join(texts)

        texts = [
            str(item.get("text", ""))
            for item in response.get("content", [])
            if isinstance(item, dict) and item.get("type") == "text"
        ]
        if texts:
            return "\n".join(texts)
        return json.dumps(response, ensure_ascii=False)

    output_text = getattr(response, "output_text", None)
    if output_text:
        return str(output_text)

    if hasattr(response, "model_dump"):
        dumped = response.model_dump(mode="json")
    elif hasattr(response, "to_dict"):
        dumped = response.to_dict()
    else:
        dumped = {}

    for item in dumped.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                return str(content["text"])
    return json.dumps(dumped, ensure_ascii=False)


def response_to_dict(response: Any) -> dict[str, Any] | None:
    if isinstance(response, dict):
        return response
    if hasattr(response, "model_dump"):
        return response.model_dump(mode="json")
    if hasattr(response, "to_dict"):
        return response.to_dict()
    return None


def call_openai_responses_api(
    api_key: str,
    model: str,
    instruction: str,
    image_path: Path,
    image_detail: str,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": instruction},
                    {
                        "type": "input_image",
                        "image_url": image_to_data_url(image_path),
                        "detail": image_detail,
                    },
                ],
            }
        ],
        "text": {"format": AUDIT_RESPONSE_FORMAT},
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {exc.code}: {body}") from exc


def call_anthropic_messages_api(
    api_key: str,
    model: str,
    instruction: str,
    image_path: Path,
    max_tokens: int,
    anthropic_version: str,
) -> dict[str, Any]:
    mime_type, image_data = image_to_base64_payload(image_path)
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": instruction},
                ],
            }
        ],
    }
    request = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": anthropic_version,
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Anthropic API HTTP {exc.code}: {body}") from exc


def call_gemini_generate_content_api(
    api_key: str,
    model: str,
    instruction: str,
    image_path: Path,
    max_tokens: int,
) -> dict[str, Any]:
    mime_type, image_data = image_to_base64_payload(image_path)
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"inline_data": {"mime_type": mime_type, "data": image_data}},
                    {"text": instruction},
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": max_tokens,
            "responseMimeType": "application/json",
            "responseJsonSchema": AUDIT_RESPONSE_FORMAT["schema"],
        },
    }
    encoded_model = urllib.parse.quote(model, safe="")
    request = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{encoded_model}:generateContent",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-goog-api-key": api_key,
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini API HTTP {exc.code}: {body}") from exc


def assert_gemini_model_supports_generate_content(api_key: str, model: str) -> None:
    request = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/models",
        headers={"x-goog-api-key": api_key},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini model list HTTP {exc.code}: {body}") from exc

    normalized_target = model.removeprefix("models/")
    generate_models = []
    for item in data.get("models", []):
        name = str(item.get("name", "")).removeprefix("models/")
        methods = item.get("supportedGenerationMethods", [])
        if "generateContent" in methods:
            generate_models.append(name)

    if normalized_target not in generate_models:
        preview = ", ".join(generate_models[:30])
        raise RuntimeError(
            f"Gemini model '{model}' is not available for generateContent. "
            f"Available generateContent models include: {preview}"
        )


def call_qwen_openai_compatible_api(
    api_key: str,
    model: str,
    instruction: str,
    image_path: Path,
    max_tokens: int,
    base_url: str,
) -> dict[str, Any]:
    base_url = base_url.rstrip("/")
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": instruction},
                    {"type": "image_url", "image_url": {"url": image_to_data_url(image_path)}},
                ],
            }
        ],
        "temperature": 0,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
        "stream": False,
    }
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Qwen API HTTP {exc.code}: {body}") from exc


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_log(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8")


def select_rows(metadata: pd.DataFrame, sample_ids: list[str] | None, limit: int | None) -> pd.DataFrame:
    selected = metadata
    if sample_ids:
        requested = set(sample_ids)
        selected = selected[selected["sample_id"].isin(requested)]
        missing = sorted(requested - set(selected["sample_id"]))
        if missing:
            raise ValueError(f"Requested sample_id values not found in metadata: {missing}")
    if limit is not None:
        selected = selected.head(limit)
    return selected.reset_index(drop=True)


def run_audit(args: argparse.Namespace) -> pd.DataFrame:
    project_root = args.project_root.resolve()
    metadata = pd.read_csv(resolve_path(args.metadata, project_root), keep_default_na=False)
    metadata = select_rows(metadata, args.sample_id, args.limit)

    template_path = PROMPT_FILES[args.audit_prompt_type]
    template = load_template(resolve_path(template_path, project_root))

    safe_model = safe_path_component(args.model)
    output_root = resolve_path(args.output_folder, project_root)
    raw_dir = output_root / safe_model / args.audit_prompt_type
    run_log = args.run_log or Path("outputs/run_logs") / f"{safe_model}_{args.audit_prompt_type}_run_log.csv"
    run_log = resolve_path(run_log, project_root)

    provider = choose_provider(args.provider, args.model)
    openai_api_key = None
    anthropic_api_key = None
    gemini_api_key = None
    qwen_api_key = None
    if not args.dry_run:
        if provider == "openai":
            openai_api_key = get_openai_api_key()
        elif provider == "anthropic":
            anthropic_api_key = get_anthropic_api_key()
        elif provider == "gemini":
            gemini_api_key = get_gemini_api_key()
            if args.preflight:
                assert_gemini_model_supports_generate_content(gemini_api_key, args.model)
        elif provider == "qwen":
            qwen_api_key = get_qwen_api_key()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    logs: list[dict[str, Any]] = []

    for _, row in metadata.iterrows():
        sample_id = row["sample_id"]
        output_path = raw_dir / f"{sample_id}.json"
        log_row = {
            "sample_id": sample_id,
            "model": args.model,
            "audit_prompt_type": args.audit_prompt_type,
            "status": "pending",
            "parseable": False,
            "output_path": str(output_path),
            "error_message": "",
        }

        if args.resume and output_path.exists():
            log_row.update({"status": "skipped_existing", "parseable": ""})
            logs.append(log_row)
            write_log(run_log, logs)
            continue

        try:
            image_path = resolve_image_path(row, args.image_dir, project_root)
            instruction = build_auditor_instruction(template, row)

            if args.dry_run:
                raw_payload = {
                    "sample_id": sample_id,
                    "model": args.model,
                    "provider": provider,
                    "audit_prompt_type": args.audit_prompt_type,
                    "dry_run": True,
                    "image_path": str(image_path),
                    "evaluation_prompt_text": row.get("evaluation_prompt_en", ""),
                    "target_anomaly": row.get("target_anomaly_en", ""),
                    "axis": {"axis_code": row.get("axis_code", ""), "axis_en": row.get("axis_en", "")},
                    "auditor_instruction": instruction,
                }
                write_json(output_path, raw_payload)
                log_row.update({"status": "dry_run", "parseable": ""})
                logs.append(log_row)
                write_log(run_log, logs)
                continue

            if provider == "openai":
                response = call_openai_responses_api(
                    api_key=openai_api_key,
                    model=args.model,
                    instruction=instruction,
                    image_path=image_path,
                    image_detail=args.image_detail,
                )
            else:
                if provider == "anthropic":
                    response = call_anthropic_messages_api(
                        api_key=anthropic_api_key,
                        model=args.model,
                        instruction=instruction,
                        image_path=image_path,
                        max_tokens=args.max_tokens,
                        anthropic_version=args.anthropic_version,
                    )
                elif provider == "gemini":
                    response = call_gemini_generate_content_api(
                        api_key=gemini_api_key,
                        model=args.model,
                        instruction=instruction,
                        image_path=image_path,
                        max_tokens=args.max_tokens,
                    )
                elif provider == "qwen":
                    response = call_qwen_openai_compatible_api(
                        api_key=qwen_api_key,
                        model=args.model,
                        instruction=instruction,
                        image_path=image_path,
                        max_tokens=args.max_tokens,
                        base_url=args.qwen_base_url,
                    )
                else:
                    raise ValueError(f"Unsupported provider: {provider}")
            response_text = response_to_text(response)
            parsed_response: dict[str, Any] | None = None
            parseable = False
            parse_error = ""

            try:
                parsed_response = extract_json_object(response_text)
                validation_errors = validate_audit_json(parsed_response)
                if validation_errors:
                    parse_error = "; ".join(validation_errors)
                else:
                    parseable = True
            except Exception as exc:  # noqa: BLE001 - parse failure should be logged, not fatal.
                parse_error = str(exc)

            raw_payload = {
                "sample_id": sample_id,
                "model": args.model,
                "provider": provider,
                "audit_prompt_type": args.audit_prompt_type,
                "image_path": str(image_path),
                "evaluation_prompt_text": row.get("evaluation_prompt_en", ""),
                "target_anomaly": row.get("target_anomaly_en", ""),
                "axis": {"axis_code": row.get("axis_code", ""), "axis_en": row.get("axis_en", "")},
                "response_text": response_text,
                "response_json": parsed_response,
                "api_response": response_to_dict(response),
            }
            write_json(output_path, raw_payload)

            log_row.update(
                {
                    "status": "success",
                    "parseable": parseable,
                    "error_message": parse_error,
                }
            )
        except Exception as exc:  # noqa: BLE001 - keep batch running and log each failure.
            error_payload = {
                "sample_id": sample_id,
                "model": args.model,
                "provider": provider,
                "audit_prompt_type": args.audit_prompt_type,
                "status": "error",
                "error_message": str(exc),
            }
            write_json(output_path, error_payload)
            log_row.update({"status": "error", "parseable": False, "error_message": str(exc)})

        logs.append(log_row)
        write_log(run_log, logs)

    return pd.DataFrame(logs)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--metadata",
        type=Path,
        default=Path("data/metadata/metadata_pairs.csv"),
        help="Metadata CSV produced by scripts/01_build_metadata.py.",
    )
    parser.add_argument(
        "--image-dir",
        type=Path,
        default=Path("data/images"),
        help="Folder containing image files. Defaults to data/images; falls back to metadata image_path.",
    )
    parser.add_argument(
        "--audit_prompt_type",
        "--setting",
        dest="audit_prompt_type",
        choices=sorted(PROMPT_FILES),
        default="permission_aware",
        help="Auditor prompt template to use.",
    )
    parser.add_argument("--model", required=True, help="Vision-capable model name.")
    parser.add_argument(
        "--provider",
        choices=["auto", "openai", "anthropic", "gemini", "qwen"],
        default="auto",
        help="API provider. auto selects from the model name prefix.",
    )
    parser.add_argument(
        "--output-folder",
        type=Path,
        default=Path("outputs/raw"),
        help="Root folder for per-sample raw output files.",
    )
    parser.add_argument(
        "--run-log",
        type=Path,
        default=None,
        help="Run log CSV path. Defaults to outputs/run_logs/{model}_{audit_prompt_type}_run_log.csv.",
    )
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--image-detail", choices=["low", "high", "auto"], default="auto")
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4096,
        help="Maximum output tokens for model responses.",
    )
    parser.add_argument(
        "--anthropic-version",
        default="2023-06-01",
        help="Anthropic API version header.",
    )
    parser.add_argument(
        "--qwen-base-url",
        default="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        help="Qwen OpenAI-compatible base URL.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Optional maximum number of rows to run.")
    parser.add_argument("--sample-id", action="append", default=None, help="Run only this sample_id; repeatable.")
    parser.add_argument("--resume", action="store_true", help="Skip samples whose output file already exists.")
    parser.add_argument(
        "--no-preflight",
        dest="preflight",
        action="store_false",
        help="Disable provider-specific preflight checks.",
    )
    parser.set_defaults(preflight=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write request payload files and run log without calling the API.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    log = run_audit(args)
    summary = {
        "model": args.model,
        "provider": choose_provider(args.provider, args.model),
        "audit_prompt_type": args.audit_prompt_type,
        "rows": int(len(log)),
        "status_counts": log["status"].value_counts(dropna=False).to_dict() if len(log) else {},
        "parseable_counts": log["parseable"].value_counts(dropna=False).to_dict() if len(log) else {},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
