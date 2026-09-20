> Historical documentation of a separate 64-image / 144-pair prompt-permission study. The text below is preserved from the previous repository homepage; status statements and model names are historical. Run its commands from the repository root. It is not the CAC 2026 200-image analysis.

[Return to the CAC 2026 study](README.md)

---

# Not All Weirdness Is Hallucination

Small PRCV 2026 special-session experiment repository for auditing prompt-permission boundaries in generated images.

The central claim is that a visual anomaly is not automatically a hallucination. It should be labelled as hallucination only when the anomaly violates the prompt's explicit or implicit permission boundary.

## Dataset Design

- 8 anomaly axes.
- 5 target-anomaly images per axis.
- 3 evaluation contexts per target image: `violating`, `permitted`, `ambiguous`.
- 3 no-issue control images per axis.
- 64 unique images.
- 144 prompt-image pairs.

The current image naming convention is flat:

```text
image/A1.png ... image/H8.png
```

Axis mapping:

| Image prefix | Axis code | Axis |
|---|---|---|
| A | A1 | Anatomy / Hands |
| B | A2 | Text |
| C | A3 | Physics |
| D | A4 | Object Fusion |
| E | A5 | Count / Repetition |
| F | A6 | Spatial / Impossible Geometry |
| G | A7 | Scale / Proportion |
| H | A8 | Artistic Deformation |

For each axis, images `1-5` are target-anomaly images and images `6-8` are no-issue controls.

## Repository Structure

```text
data/metadata/
  generation_prompts.csv
  evaluation_context_prompts.csv
  metadata_pairs.csv
image/
  A1.png ... H8.png
prompts/
  auditor_image_only.txt
  auditor_prompt_conditioned.txt
  auditor_permission_aware.txt
scripts/
  01_build_metadata.py
  02_validate_dataset.py
  03_run_api_audit.py
  04_parse_outputs.py
  05_merge_human_review.py
  06_compute_metrics.py
  07_make_figures.py
score/
  human scoring workbooks and manual
```

## Quick Start

Install dependencies in your preferred Python environment:

```bash
pip install pandas openai matplotlib
```

Build metadata:

```bash
python scripts/01_build_metadata.py
```

Validate metadata and local image coverage:

```bash
python scripts/02_validate_dataset.py
```

Run a dry-run for one sample without calling any API:

```bash
python scripts/03_run_api_audit.py --model gpt-4.1-mini --audit_prompt_type permission_aware --limit 1 --dry-run
```

Run a real API audit after setting `OPENAI_API_KEY`:

```bash
python scripts/03_run_api_audit.py --model gpt-4.1-mini --audit_prompt_type permission_aware
```

Run a real Claude audit after setting `ANTHROPIC_API_KEY`:

```bash
python scripts/03_run_api_audit.py \
  --provider anthropic \
  --model claude-sonnet-4-5 \
  --audit_prompt_type permission_aware
```

Raw outputs are written one file per sample:

Run Gemini and Qwen audits after setting `GEMINI_API_KEY` or `DASHSCOPE_API_KEY`:

```bash
python scripts/03_run_api_audit.py --model gemini-3.1-pro --audit_prompt_type permission_aware
python scripts/03_run_api_audit.py --model qwen3-vl-32b-instruct --audit_prompt_type permission_aware
```

The runner auto-selects providers from model prefixes: `gpt` -> OpenAI, `claude` -> Anthropic, `gemini` -> Gemini, `qwen` -> DashScope/Qwen.

```text
outputs/raw/{model}/{audit_prompt_type}/{sample_id}.json
```

A run log CSV is written under `outputs/run_logs/`.

## Gold Labels

Permission labels:

- `prompt_required`
- `prompt_permitted`
- `prompt_violating`
- `ambiguous`
- `no_issue`

Hallucination labels:

- `yes`
- `no`
- `uncertain`

Mapping:

| Permission label | Hallucination label |
|---|---|
| `prompt_required` | `no` |
| `prompt_permitted` | `no` |
| `prompt_violating` | `yes` |
| `ambiguous` | `uncertain` |
| `no_issue` | `no` |

## Metrics

The metric script computes:

- Permission Boundary Accuracy (`PBA`)
- False Hallucination Rate on Intended Deviations (`FHR_intended`)
- Creative Preservation Rate (`CPR`)
- Missed Violation Rate (`MVR`)
- Defect Sensitivity (`DS`)
- Ambiguity Calibration Rate (`ACR`)
- No-issue False Alarm Rate (`NIFAR`)

## Current Status

The repository is scaffolded for offline dataset validation and request preparation. The next step is to choose VLM auditors and implement the API-specific runner once the dataset and human review labels are frozen.
