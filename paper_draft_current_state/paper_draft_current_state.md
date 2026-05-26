# Not All Weirdness Is Hallucination: Permission-Aware Auditing of Visual Abnormalities in Text-to-Image Generation

Status: current-state paper draft. This draft is provisional and must be updated after the 79 fully blind adjudication results return.

## Abstract

Text-to-image evaluation often treats visual abnormality as evidence of hallucination or prompt misalignment. However, in creative generation, an abnormal visual feature may be explicitly required by the prompt, merely permitted by the prompt, clearly violating the prompt, genuinely ambiguous, or absent. We introduce a permission-aware formulation for auditing visual abnormalities in generated images and construct a targeted 144-sample benchmark spanning intended deviations, prompt violations, ambiguous boundaries, and no-issue controls. In current permission-aware evaluations, three VLM auditors show strong performance on clear boundaries: intended deviations are rarely misclassified as hallucinations and clear violations are usually detected. However, all three models fail to preserve uncertainty on ambiguous cases, yielding zero ambiguous calibration rate in the current run. A three-rater human pilot further shows that fine-grained permission labels are vulnerable to annotation drift: agreement is high on clear boundaries but collapses for ambiguous and no-issue/control cases. Majority vote would therefore erase the very uncertainty categories the benchmark is designed to measure. We treat the first human round as calibration evidence and construct a revised label guide and fully blind adjudication protocol for final gold construction. These findings suggest that hallucination auditing for generated images should move beyond visual weirdness and incorporate prompt-permission reasoning and uncertainty preservation.

Provisionality note: this abstract summarizes current-state results only. Final metrics will be updated after blind adjudication.

## 1. Introduction

Generated images often contain visually unusual content: distorted hands, unreadable text, strange physical behavior, impossible geometry, abnormal scale, or stylized object deformation. In many evaluation settings, these abnormalities are treated as evidence of hallucination or prompt failure. That shortcut is useful when the prompt demands realistic or literal content, but it becomes misleading for creative image generation. A six-fingered hand is a defect if the prompt requests a natural human hand; it is not a hallucination if the prompt explicitly asks for a six-fingered alien performer. The same visible abnormality can therefore change status depending on the prompt's permission structure.

This paper studies that boundary. Our thesis is that visual weirdness alone is insufficient for hallucination labeling. A generated-image abnormality should be audited relative to the prompt: whether the prompt explicitly requires the abnormality, merely permits it, forbids it, leaves it underdetermined, or contains no target issue at all.

We frame the problem as permission-aware visual hallucination auditing. Given an image, an evaluation prompt, and a target anomaly, the auditor assigns one of five permission labels: `prompt_required`, `prompt_permitted`, `prompt_violating`, `ambiguous`, or `no_issue`. These labels then map to hallucination decisions: violation is hallucination, required/permitted/no-issue cases are not hallucinations, and ambiguous cases should remain uncertain rather than being forced into a binary decision.

Our current study is deliberately small and targeted. It contains 144 prompt-image pairs across eight anomaly axes and four condition families: intended deviations, prompt violations, ambiguous prompts, and no-issue controls. We evaluate three VLM auditors in the permission-aware setting and run a three-rater human pilot. The current results show a split pattern: clear permission boundaries are handled reasonably well, while ambiguity-sensitive categories expose both model uncertainty-calibration failures and human annotation drift.

Contributions:

1. We introduce a permission-aware formulation for auditing visual abnormalities in text-to-image generation.
2. We construct a targeted 144-sample benchmark and report a preliminary permission-aware VLM evaluation showing clear-boundary competence but ambiguity over-resolution.
3. We report a three-rater human pilot showing annotation drift and majority-vote failure for ambiguous and no-issue/control cases, motivating fully blind adjudication before final gold construction.

Important scope note: this draft does not claim final benchmark performance. The current final-gold draft retains 65 metadata-stable clear-boundary samples and marks 79 samples as unresolved pending blind adjudication.

## 2. Related Work

Text-to-image faithfulness evaluation has increasingly moved beyond global image-text similarity. TIFA evaluates text-to-image faithfulness through question answering over generated images, improving interpretability by decomposing prompts into checkable questions. VQAScore and related GenAI-Bench work similarly use image-to-text or VQA-style scoring to evaluate whether visual content matches complex prompts. These works provide important tools for measuring alignment, but they usually ask whether the prompt content is present, not whether an abnormal visual feature is licensed by the prompt.

Compositional text-to-image benchmarks such as GenEval and T2I-CompBench focus on object presence, count, color, spatial relations, attribute binding, and other prompt-following dimensions. Our work is complementary. Rather than measuring whether a generation satisfies compositional requirements in general, we isolate one visible anomaly and ask how its hallucination status changes across required, permitted, violating, ambiguous, and no-issue contexts.

Visual hallucination and visual factuality work often treats generated or described visual content as incorrect when it conflicts with observed evidence or prompt requirements. Our setting adds a permission layer: an abnormality may be visually real and still not be an error if the prompt calls for it or licenses it. This is especially relevant for artistic and imaginative prompts.

Finally, annotation-disagreement research warns against flattening subjective labels into majority-vote gold. Davani et al. show that disagreement may encode systematic rater perspectives and uncertainty rather than noise. Our v1 human pilot shows the same problem in a multimodal permission-labeling task: majority vote is relatively stable for clear violations and required abnormalities, but it fails for the uncertainty-sensitive labels that define this benchmark.

## 3. Task Definition

Each sample consists of:

- image `x`;
- evaluation prompt `p`;
- target anomaly `a`;
- anomaly axis `k`;
- auditor instruction `I`.

The auditor returns:

```json
{
  "target_anomaly_detected": true,
  "permission_status": "prompt_required | prompt_permitted | prompt_violating | ambiguous | no_issue",
  "should_label_as_hallucination": "yes | no | uncertain",
  "reason": "...",
  "confidence": "high | medium | low"
}
```

The central task is not aesthetic evaluation and not general image quality scoring. The task is to judge the target anomaly relative to the evaluation prompt. If the anomaly is visible and contradicts the prompt, it is a hallucination. If the prompt explicitly requires or clearly permits the anomaly, it is not a hallucination. If the prompt underdetermines permission, the correct outcome is uncertainty. If there is no target anomaly and no visible issue, the correct permission status is `no_issue`.

## 4. Dataset and Label Schema

The dataset has 144 prompt-image pairs, built from 64 unique images. It covers eight anomaly axes:

| Axis code | Axis |
|---|---|
| A1 | Anatomy / Hands |
| A2 | Text |
| A3 | Physics |
| A4 | Object Fusion |
| A5 | Count / Repetition |
| A6 | Spatial / Impossible Geometry |
| A7 | Scale / Proportion |
| A8 | Artistic Deformation |

For each axis, five target-anomaly images are evaluated under three prompt contexts: violating, intended/required, and ambiguous. Three additional control images per axis are included as no-issue controls. This yields 18 prompt-image pairs per axis and 144 total rows.

Current dataset composition:

| Condition | Count | Current metadata permission label | Hallucination mapping |
|---|---:|---|---|
| intended / required | 40 | `prompt_required` | `no` |
| violating | 40 | `prompt_violating` | `yes` |
| ambiguous | 40 | `ambiguous` | `uncertain` |
| no_issue / control | 24 | `no_issue` | `no` |

Label schema:

| Label | Definition | Hallucination mapping |
|---|---|---|
| `prompt_required` | prompt explicitly requires the target anomaly | `no` |
| `prompt_permitted` | prompt allows but does not require the target anomaly | `no` |
| `prompt_violating` | target anomaly contradicts the prompt | `yes` |
| `ambiguous` | permission boundary is underdetermined | `uncertain` |
| `no_issue` | no target anomaly or no visible issue | `no` |

Important limitation of the current metadata: the intended-deviation rows are currently labeled `prompt_required`, not `prompt_permitted`. Therefore, current results support claims about preserving intended abnormalities, but they do not yet support strong claims about distinguishing required from merely permitted abnormalities.

## 5. VLM Auditor Setup

The repository contains three auditor prompt templates: image-only, prompt-conditioned, and permission-aware. The current result set reported here uses only the permission-aware setting. Therefore, this draft does not claim that permission-aware prompting outperforms image-only or prompt-conditioned prompting.

The permission-aware VLM runner sends each sample's image, evaluation prompt text, target anomaly, axis, and auditor instruction. The model is required to return JSON with the permission status, hallucination label, reason, and confidence. Raw outputs are saved one file per model call, and parsed outputs are stored as CSV files.

Current models:

- GPT-5.4;
- Claude Sonnet 4.6;
- Gemini 3.1 Pro Preview.

Current metrics:

- Permission Boundary Accuracy (PBA): exact match between predicted permission label and gold permission label.
- False Hallucination Rate on Intended Deviations (FHR_intended): among gold `prompt_required` or `prompt_permitted` samples, fraction labeled hallucination `yes`.
- Creative Preservation: `1 - FHR_intended`.
- Missed Violation Rate (MVR_violating): among gold `prompt_violating` samples, fraction not labeled hallucination `yes`.
- Defect Sensitivity: `1 - MVR_violating`.
- Ambiguity Calibration Rate (ACR): among gold `ambiguous` samples, fraction labeled hallucination `uncertain`.
- Parse error rate: fraction of non-parseable outputs or outputs with illegal labels.

Metric caution: the current `06_compute_metrics.py` script does not yet output Control_FPR or non-ambiguous PBA, although those metrics are planned for the final paper.

## 6. Human Rating Protocol

Three human raters completed the v1 rating sheet for all 144 samples. The task asked raters to judge target-anomaly visibility and assign one permission label. The v1 human ratings are treated as a calibration pilot, not as final gold.

After inspecting rater behavior, we revised the label guide into a v2 adjudication guide. The guide clarifies that `prompt_required` means the prompt explicitly requires the target anomaly, not that the image generally follows the prompt. It also clarifies that `no_issue` must be used for target-anomaly-free controls, and that broad style words such as surreal, dreamlike, whimsical, symbolic, artistic, fantasy, imaginative, and stylized do not automatically imply `prompt_required`.

Because ambiguous and no-issue/control cases show severe annotation drift, majority vote is not used for final labels. Instead, 79 unresolved rows have been placed into a fully blind adjudicator package.

## 7. Current Results

Table 1 reports current permission-aware VLM results against the current metadata-defined labels. These are current-state results, not final adjudicated benchmark results.

| Model | FHR_intended | Creative Preservation | MVR_violating | Defect Sensitivity | ACR | PBA |
|---|---:|---:|---:|---:|---:|---:|
| GPT-5.4 | 0.000 | 1.000 | 0.025 | 0.975 | 0.000 | 0.715 |
| Claude Sonnet 4.6 | 0.025 | 0.975 | 0.000 | 1.000 | 0.000 | 0.722 |
| Gemini 3.1 Pro Preview | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 | 0.701 |

The current permission-aware auditors mostly preserve intended deviations: FHR_intended is 0.000 for GPT-5.4 and Gemini and 0.025 for Claude. They also detect clear prompt violations with high sensitivity: MVR_violating is 0.025 for GPT-5.4 and 0.000 for Claude and Gemini.

The dominant failure mode is ambiguity calibration. All three models have ACR = 0.000. In other words, none of the three current permission-aware runs preserves the `uncertain` hallucination label for metadata-ambiguous samples. This suggests that current VLM auditors over-resolve ambiguous permission boundaries. The wording should remain cautious: these are results from the current permission-aware prompt, which was later audited as permission-aware but not fully manual-faithful.

The apparent PBA ceiling is mostly driven by ambiguous cases, not by failure on clear boundaries. Because non-ambiguous PBA is not yet computed in the metric script, this statement should be treated as a current interpretation rather than a final table result.

## 8. Human Annotation Drift and Majority-Vote Failure

The v1 human pilot produced the following aggregate agreement:

| Metric | Result |
|---|---:|
| Three-rater exact permission agreement | 69/144 = 47.9% |
| Three-rater anomaly_visible agreement | 95/144 = 66.0% |
| Three-rater binary hallucination agreement | 107/144 = 74.3% |

Pairwise permission agreement:

| Pair | Permission agreement | Cohen kappa |
|---|---:|---:|
| A vs B | 50.0% | 0.339 |
| A vs C | 77.1% | 0.684 |
| B vs C | 60.4% | 0.409 |

Condition-level exact permission agreement:

| Condition | Three-rater exact agreement |
|---|---:|
| violating | 34/40 = 85.0% |
| permitted / required clear-boundary | 35/40 = 87.5% |
| ambiguous | 0/40 = 0.0% |
| no_issue/control | 0/24 = 0.0% |

The pattern is clear: humans agree on clear boundaries and drift on uncertainty-sensitive categories. Rater A almost never uses `ambiguous` and tends to map metadata-ambiguous cases to `prompt_permitted`. Rater B overuses `prompt_required`, apparently interpreting it as general prompt compliance. Rater C uses no `no_issue`, often mapping controls to `prompt_required`.

Majority vote is therefore unsafe for final gold. It works relatively well for clear cases, but it fails exactly where the benchmark needs to preserve uncertainty. In the v1 ratings, majority vote matches metadata gold for 0/40 ambiguous cases and only 3/24 no-issue/control cases.

## 9. Adjudication Protocol

The current final-gold draft is conservative:

| Source | Count |
|---|---:|
| metadata_stable | 65 |
| excluded_uncertain | 79 |
| adjudicated_ambiguous | 0 |
| adjudicated_control | 0 |
| adjudicated_disagreement | 0 |

The unresolved rows are:

| Category | Count |
|---|---:|
| ambiguous | 40 |
| no_issue/control | 24 |
| violating disagreement | 11 |
| permitted disagreement | 4 |

These 79 rows have been prepared in a fully blind adjudicator package. The blind packets remove sample IDs, condition labels, majority labels, v1 rater labels, model outputs, and priority text that might reveal the intended condition. A coordinator-only mapping file is retained separately and should not be sent to adjudicators.

Final gold construction will follow these rules:

1. Retain stable metadata gold for clear-boundary rows with human support.
2. Use adjudicator labels where `adjudicator_final_permission` is filled.
3. Do not infer missing adjudicator labels.
4. Do not use simple majority vote for ambiguous or no-issue/control cases.
5. Mark every final label with `gold_source`.
6. Report unresolved cases separately or exclude them from the main exact-label metric.

## 10. Discussion

The current study supports a methodological claim: hallucination auditing should separate visual abnormality from prompt violation. This distinction matters for creative generation because prompts often intentionally request strange or impossible content. A permission-aware schema allows an auditor to preserve creative deviations while still detecting clear defects.

The VLM results and human pilot point to the same pressure point. Clear permission boundaries are relatively easy: models and humans both handle required/intended abnormalities and violations reasonably well. Ambiguous and no-issue/control cases are harder. Models over-resolve ambiguity by avoiding `uncertain`; humans drift because some raters treat prompt compliance as `prompt_required` and some do not preserve `no_issue`.

This has practical consequences. Benchmarks that only report binary hallucination rates may hide whether a model is preserving creative intent, detecting violations, or forcing ambiguity into an overconfident label. Similarly, majority-vote human labels may look like a convenient gold construction method, but in this task they erase the uncertainty categories that the benchmark is designed to measure.

## 11. Limitations

This is a small pilot benchmark with 144 prompt-image pairs. The current images and prompts are targeted rather than naturally sampled from deployed text-to-image systems. The metadata contains intended rows labeled as `prompt_required`; it does not yet include a balanced set of `prompt_permitted` gold rows. This limits conclusions about the required/permitted distinction.

The current VLM results are permission-aware evaluations, but an implementation audit found that the VLM prompt is not fully manual-faithful. It uses the same broad schema but omits some operational guidance from the human label guide. Therefore, the current results should not be described as models following the full human annotation manual.

The current metrics are pre-adjudication. Final benchmark metrics, model ranking, Control_FPR, non-ambiguous PBA, final ACR, and adjudicator agreement must be updated after the 79 blind adjudication rows return.

## 12. Conclusion

This work argues that not all visual weirdness is hallucination. The hallucination status of a generated-image abnormality depends on whether the prompt requires, permits, forbids, underdetermines, or lacks the target anomaly. Current permission-aware VLM auditors perform well on clear intended deviations and clear violations, but they fail to preserve ambiguity in the current run. A three-rater human pilot shows a parallel problem: clear-boundary agreement is high, while ambiguous and no-issue/control labels suffer from severe annotation drift. These current-state findings motivate a permission-aware benchmark and a blind adjudication protocol for final gold construction. Final results will be reported after adjudication.

## References

- TIFA: Accurate and Interpretable Text-to-Image Faithfulness Evaluation with Question Answering. ICCV 2023.
- GenEval: An Object-Focused Framework for Evaluating Text-to-Image Alignment. NeurIPS 2023.
- T2I-CompBench: A Comprehensive Benchmark for Open-world Compositional Text-to-image Generation. NeurIPS 2023.
- VQAScore / GenAI-Bench: Evaluating Text-to-Visual Generation with Image-to-Text Generation. 2024.
- Aida Mostafazadeh Davani, Mark Diaz, and Vinodkumar Prabhakaran. Dealing with Disagreements: Looking Beyond the Majority Vote in Subjective Annotations. TACL 2022.

Figure placeholders:

1. Pipeline figure: prompt + image + target anomaly -> permission-aware auditor -> label + hallucination mapping.
2. Boundary examples: same anomaly under required/permitted/violating/ambiguous/no_issue contexts.
3. Result figure: clear-boundary competence vs ambiguity failure.
4. Human pilot figure: agreement high for clear cases, zero for ambiguous/control.
