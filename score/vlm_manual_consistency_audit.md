# VLM Manual Consistency Audit

Project: Not All Weirdness Is Hallucination
Audit date: 2026-05-19
Scope: implementation audit only. No models were rerun, no result files were modified, and no gold labels were changed.

## Conclusion

### Case B: Permission-aware but not fully manual-faithful

Previous VLM results should be described as **permission-aware evaluations**, but not strictly as **manual-following human-guide evaluations**.

The runner, parser, gold labels, and main metric formulas use the intended label set. However, the actual VLM evaluator prompt, especially `prompts/auditor_permission_aware.txt`, contains only simplified label definitions. It does not fully reproduce the human annotation guide's operational definitions, does not explicitly enforce the permission-to-hallucination mapping, and does not strongly preserve ambiguous cases. This matters because all three previous VLM runs collapsed ambiguous samples into required/permitted/no/yes decisions rather than preserving uncertainty.

## Files Inspected

- `prompts/auditor_image_only.txt`
- `prompts/auditor_prompt_conditioned.txt`
- `prompts/auditor_permission_aware.txt`
- `scripts/01_build_metadata.py`
- `scripts/02_validate_dataset.py`
- `scripts/03_run_api_audit.py`
- `scripts/04_parse_outputs.py`
- `scripts/05_merge_human_review.py`
- `scripts/06_compute_metrics.py`
- `README.md`
- `prcv_prompt_permission_experiment_plan.md`
- `data/metadata/generation_prompts.csv`
- `data/metadata/evaluation_context_prompts.csv`
- `data/metadata/metadata_pairs.csv`
- `score/prcv_bilingual_scoring_manual.docx`
- `score/prcv_prompt_permission_scoring_table_reviewer.xlsx`
- `score/rater1.xlsx`
- `outputs/parsed/gpt-5.4_permission_aware_parsed.csv`
- `outputs/parsed/claude-sonnet-4-6_permission_aware_parsed.csv`
- `outputs/parsed/gemini-3.1-pro-preview_permission_aware_parsed.csv`

## 1. Prompt-Guide Consistency

The human guide defines the task as deciding whether the **target anomaly** is allowed by the current `evaluation_prompt`, not judging aesthetic quality. Its label definitions are:

- `prompt_violating`: prompt asks for normal, realistic, clear, or plausible content, but the image contains the target anomaly.
- `prompt_required`: prompt explicitly requires the anomaly.
- `prompt_permitted`: prompt does not explicitly require it, but the style or concept clearly permits it.
- `ambiguous`: prompt is too vague to decide whether the anomaly is allowed.
- `no_issue`: no target anomaly or no visible issue.

The `permission_aware` VLM prompt is aligned with the broad idea, but it is shorter than the manual:

- It says to decide whether the target element is explicitly required, stylistically or semantically permitted, violating/contradicting the prompt, ambiguous, or not an issue.
- It does not include the manual's exact `prompt_violating` criterion about normal/realistic/clear/plausible prompts.
- It does not explicitly define `no_issue` as no target anomaly or no visible issue.
- It does not explicitly state that ambiguous cases should produce `should_label_as_hallucination="uncertain"`.
- It does not warn that broad style terms such as surreal, dreamlike, whimsical, symbolic, or artistic should not automatically become `prompt_required`.

Detailed label-by-label comparison is saved in:

- `score/vlm_prompt_label_definition_comparison.csv`

## 2. Label Parsing Consistency

The implementation uses the intended legal labels:

- Permission labels are enumerated in `scripts/03_run_api_audit.py` and `scripts/06_compute_metrics.py`.
- Hallucination labels are enumerated as `yes`, `no`, and `uncertain`.
- OpenAI and Gemini calls request JSON schema constrained to the legal enum values.
- Anthropic and Qwen calls rely on prompt/schema text rather than provider-enforced JSON schema, but runner validation checks the returned JSON before marking the run log row parseable.

No evidence was found that the parser collapses aliases or merges `prompt_required` and `prompt_permitted`. It also does not coerce `ambiguous` into required/permitted/violating or silently map invalid outputs to a default label.

Important caveats:

- `scripts/04_parse_outputs.py` does not itself validate legal enum values before writing parsed CSV. Invalid labels would appear in the parsed CSV with blank `parse_error`, although `scripts/06_compute_metrics.py` would later exclude them via `parseable_mask`.
- The parser and metrics do not enforce internal consistency between `permission_status_pred` and `hallucination_pred`. For example, Claude has 2 rows where the permission label maps to `no` under the guide but the model returned `hallucination_pred=yes`.

Observed internal mapping mismatches:

| model | mismatches |
|---|---:|
| gpt-5.4 | 0 |
| claude-sonnet-4-6 | 2 |
| gemini-3.1-pro-preview | 0 |

## 3. Gold-Label Consistency

`data/metadata/metadata_pairs.csv` is internally consistent with the designed schema:

| condition | permission_gold | hallucination_gold | count |
|---|---|---|---:|
| violating | prompt_violating | yes | 40 |
| permitted | prompt_required | no | 40 |
| ambiguous | ambiguous | uncertain | 40 |
| no_issue | no_issue | no | 24 |

Required checks:

- `_V` samples are treated as `prompt_violating`: PASS.
- `_P` samples are treated as intended abnormality: PASS, but all are `prompt_required`; none are `prompt_permitted`.
- `_A` samples are treated as `ambiguous`: PASS.
- Control samples with `target_anomaly=none` are treated as `no_issue`: PASS.

The absence of `prompt_permitted` gold rows is not a schema conflict, because the current P prompts usually explicitly describe the target anomaly. But it limits claims about whether models can distinguish `prompt_required` from `prompt_permitted`.

## 4. Metric Consistency

Metric formulas in `scripts/06_compute_metrics.py` mostly match the intended definitions:

| metric | status | note |
|---|---|---|
| PBA | MATCH | Exact permission-label match, not binary hallucination correctness. |
| FHR_intended | MATCH | Uses gold `prompt_required` or `prompt_permitted`; numerator is `hallucination_pred=yes`. |
| Creative Preservation | MATCH | `1 - FHR_intended`. |
| MVR_violating | MATCH | Uses gold `prompt_violating`; counts predictions where hallucination is not `yes`. |
| Defect Sensitivity | MATCH | `1 - MVR_violating`. |
| ACR | MATCH | Uses gold `ambiguous`; counts `hallucination_pred=uncertain`. |
| Control_FPR | MISSING | Not currently computed. README mentions NIFAR, but script does not output it. |
| Non-ambiguous PBA | MISSING | Not currently computed. |

Full metric audit is saved in:

- `score/vlm_metric_mapping_audit.csv`

## 5. Previous VLM Result CSV Audit

All three parsed permission-aware result files have 144 rows and zero parse errors after the Gemini rerun.

Prediction distributions:

| model | prompt_required | prompt_permitted | prompt_violating | ambiguous | no_issue | hallucination uncertain |
|---|---:|---:|---:|---:|---:|---:|
| gpt-5.4 | 55 | 25 | 39 | 0 | 25 | 0 |
| claude-sonnet-4-6 | 68 | 12 | 40 | 0 | 24 | 0 |
| gemini-3.1-pro-preview | 59 | 21 | 43 | 0 | 21 | 0 |

This is the most important behavioral evidence: despite 40 gold ambiguous samples, no previous model output preserved `ambiguous` or `uncertain`. Therefore, the previous results are useful for a permission-aware audit, but they should not be claimed as strict adherence to the human guide's ambiguity rule.

## 6. Rater1 Comparison Caution

`score/rater1.xlsx` should not be used as final gold without adjudication. It shows annotation drift, especially overuse of `prompt_required` for no-issue controls.

Previously computed evidence:

- rater1 vs metadata gold exact permission agreement: 85/144 = 59.0%.
- rater1 vs metadata gold hallucination agreement: 101/144 = 70.1%.
- rater1 label counts: `prompt_required=80`, `prompt_violating=39`, `ambiguous=19`, `no_issue=5`, `prompt_permitted=1`.

The guide defines `prompt_required` as "the prompt explicitly requires the anomaly," not "the image follows the prompt." Therefore, model-vs-rater1 disagreement should not be interpreted as model failure unless those disagreements are adjudicated.

## 7. Practical Interpretation

Safe wording for the current paper/results:

> We evaluate VLMs under a permission-aware audit prompt using the same label schema as the human annotation guide. However, the previous VLM prompt is a simplified operationalization of the guide rather than a full manual-faithful instruction. The results should therefore be interpreted as permission-aware VLM audit results, with a separate caution that ambiguous cases were not preserved by the models.

Avoid this wording:

> The VLMs followed the same annotation manual as human raters.

## 8. Recommended Next Steps Before Any Rerun

1. Strengthen `auditor_permission_aware.txt` by pasting the full manual definitions for all five labels.
2. Add the explicit mapping: `prompt_violating=yes`, `prompt_required=no`, `prompt_permitted=no`, `ambiguous=uncertain`, `no_issue=no`.
3. Add a rule that broad style terms can permit an anomaly or leave it ambiguous, but do not automatically make the anomaly `prompt_required`.
4. Add explicit `no_issue` handling for `target_anomaly=none` and for non-visible target anomaly.
5. Add `Control_FPR` and non-ambiguous PBA to `scripts/06_compute_metrics.py`.
6. Add an internal mapping consistency check for model outputs.
7. Adjudicate `rater1` disagreements before using human labels as final gold.

## Companion Files

- `score/vlm_prompt_label_definition_comparison.csv`
- `score/vlm_metric_mapping_audit.csv`
- `score/vlm_manual_consistency_issues.csv`
