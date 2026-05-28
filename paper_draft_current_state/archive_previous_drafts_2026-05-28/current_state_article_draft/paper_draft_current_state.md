# Not All Weirdness Is Hallucination: Permission-Aware Safety Auditing for Vision-Language Models

Status: current-state paper draft reframed for the PRCV special session "From Robust Training to Safe Inference: New Security Paradigms in the Era of Large Vision Models." This draft is provisional and must be updated after the 79 fully blind adjudication items are resolved.

## Abstract

Vision-language models are increasingly used as auditors of generated visual content, making hallucination detection a test-time safety inference problem. However, visual abnormality alone is not sufficient evidence of hallucination: an unusual feature may be explicitly required by the prompt, merely permitted by the prompt, clearly violating the prompt, genuinely ambiguous, or absent. We formulate VLM-based hallucination safety auditing as prompt-permission reasoning and introduce a five-way schema: `prompt_required`, `prompt_permitted`, `prompt_violating`, `ambiguous`, and `no_issue`. Using generated images as a controlled diagnostic safety probe, we construct a 144-sample setting that isolates eight anomaly families across authorized, violating, ambiguous, and no-issue contexts. In current-state permission-aware evaluations, three VLM auditors show clear-boundary competence: prompt-authorized abnormalities are rarely flagged as hallucinations and clear prompt violations are usually detected. Yet all three current runs over-resolve ambiguous cases, yielding zero ambiguity calibration rate. A three-rater human pilot shows a parallel safety-label problem: agreement is high on clear permission boundaries but collapses on ambiguous and no-issue/control categories, revealing annotation drift and majority-vote failure for uncertainty-sensitive labels. We therefore treat current metrics as preliminary and use the human pilot to motivate a revised guide and fully blind adjudication protocol. These results support a safe-inference framing for visual hallucination auditing, while final benchmark metrics must be recomputed after adjudication.

Provisionality note: this abstract summarizes current-state results only. Seventy-nine blind adjudication items remain pending; majority vote is not used as final gold, and final metrics will be updated after adjudication.

## 1. Introduction

Vision-language models (VLMs) and multimodal large language models (MLLMs) are increasingly deployed as test-time auditors: they inspect images, prompts, model outputs, and safety-relevant evidence in order to decide whether a system behaved reliably. In this setting, visual hallucination detection is not only a content-evaluation task; it is a safe inference problem. An auditor must decide whether a visible feature is a harmful or unreliable prompt violation, an authorized creative invention, an underdetermined case, or no issue at all.

Generated images provide a useful controlled setting for studying this problem because they often contain visually unusual content: distorted hands, unreadable text, strange physical behavior, impossible geometry, abnormal scale, or stylized object deformation. In many evaluation settings, these abnormalities are treated as evidence of hallucination or prompt failure. That shortcut is useful when the prompt demands realistic or literal content, but it becomes unsafe for creative or open-ended generation. A six-fingered hand is a defect if the prompt requests a natural human hand; it is not a hallucination if the prompt explicitly asks for a six-fingered alien performer. The same visible abnormality can therefore change safety status depending on the prompt's permission structure.

This paper studies that boundary. Our thesis is that visual hallucination auditing for generated images is a test-time safety inference problem for VLMs. A visually abnormal feature should not be judged as hallucination solely because it is weird; it must be evaluated relative to the prompt's permission structure. Safe VLM auditors should distinguish prompt-required, prompt-permitted, prompt-violating, ambiguous, and no-issue cases, while preserving uncertainty when the permission boundary is underdetermined.

We frame the problem as permission-aware hallucination safety auditing. Given an image, an evaluation prompt, and a target anomaly, the VLM auditor assigns one of five permission labels: `prompt_required`, `prompt_permitted`, `prompt_violating`, `ambiguous`, or `no_issue`. These labels then map to safety decisions: violation is hallucination, required/permitted/no-issue cases are not hallucinations, and ambiguous cases should remain uncertain rather than being forced into a binary decision.

Our current study is deliberately small and targeted. It uses generated images as a controlled diagnostic safety probe with 144 prompt-image pairs across eight anomaly axes and four condition families: intended deviations, prompt violations, ambiguous prompts, and no-issue controls. We evaluate three VLM auditors in the permission-aware setting and run a three-rater human pilot. The current results show a split pattern: clear permission boundaries are handled reasonably well, while ambiguity-sensitive categories expose both model uncertainty-calibration failures and human annotation drift.

Contributions:

1. We formulate visual hallucination auditing as a test-time safety inference problem for VLMs, where visual abnormalities must be judged relative to prompt permission rather than visual weirdness alone.
2. We introduce a five-way prompt-permission schema--`prompt_required`, `prompt_permitted`, `prompt_violating`, `ambiguous`, and `no_issue`--and construct a controlled 144-sample diagnostic benchmark for VLM safety auditors.
3. We evaluate three VLM auditors and find clear-boundary competence but systematic ambiguity over-resolution; a three-rater human pilot further shows annotation drift and majority-vote failure for uncertainty-sensitive categories, motivating blind adjudication.

Important scope note: this draft does not claim final full-benchmark performance or final model ranking. The current final-gold draft retains 65 metadata-stable clear-boundary samples and marks 79 samples as unresolved pending blind adjudication. Majority vote is not used as final gold, and final benchmark metrics will be recomputed after adjudication.

## 2. Related Work

Safe inference for large vision models increasingly concerns what a pretrained VLM should do at deployment time, after retraining is expensive or unavailable. In this setting, hallucination detection, safety alignment, prompt defense, and uncertainty calibration become test-time behaviors. Existing VLM hallucination probes such as POPE (Li et al., 2023) and HallusionBench (Guan et al., 2024) show that hallucination and visual-context reasoning failures remain central safety concerns. Our work targets this inference-time layer: rather than changing the generator or retraining the auditor, we ask whether a VLM auditor can make a safe permission-aware judgment about a visible anomaly.

Text-to-image faithfulness evaluation has increasingly moved beyond global image-text similarity. TIFA (Hu et al., 2023) evaluates faithfulness through question answering over generated images, improving interpretability by decomposing prompts into checkable questions. VQAScore and related GenAI-Bench work (Lin et al., 2024) similarly use image-to-text or VQA-style scoring to evaluate whether visual content matches complex prompts. These works provide important tools for measuring alignment, but they usually ask whether the prompt content is present, not whether an abnormal visual feature is licensed by the prompt and therefore safe to preserve.

Compositional generation benchmarks such as GenEval (Ghosh et al., 2023) and T2I-CompBench (Huang et al., 2023) focus on object presence, count, color, spatial relations, attribute binding, and other prompt-following dimensions. Our work is complementary. Rather than measuring general image-prompt alignment, we isolate one visible anomaly and ask how its hallucination safety status changes across required, permitted, violating, ambiguous, and no-issue contexts.

Visual hallucination and visual factuality work often treats generated or described visual content as incorrect when it conflicts with observed evidence or prompt requirements. Our setting adds a permission layer for safety auditing: an abnormality may be visually real and still not be an error if the prompt calls for it or licenses it. This is especially relevant for artistic and imaginative prompts, where safe auditors should not collapse authorized invention into hallucination.

Finally, annotation-disagreement research warns against flattening subjective labels into majority-vote gold. Davani et al. (2022) show that disagreement may encode systematic rater perspectives and uncertainty rather than noise. Our v1 human pilot shows the same problem in a multimodal safety-labeling task: majority vote is relatively stable for clear violations and required abnormalities, but it fails for the uncertainty-sensitive labels that define this diagnostic probe.

## 3. Test-Time Safety Inference Task

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

The central task is not aesthetic evaluation, general image quality scoring, or broad image-prompt alignment checking. The task is a test-time safety inference problem: judge the target anomaly relative to the evaluation prompt's permission structure. If the anomaly is visible and contradicts the prompt, it is a hallucination. If the prompt explicitly requires or clearly permits the anomaly, it is not a hallucination. If the prompt underdetermines permission, the safe outcome is uncertainty. If there is no target anomaly and no visible issue, the correct permission status is `no_issue`.

![Figure 1. Permission-aware VLM safety auditing pipeline.](figures/fig_pipeline.png)

Figure 1. Permission-aware VLM safety auditing pipeline. The auditor receives an image, prompt, and target anomaly at test time, then returns a permission label, hallucination decision, rationale, and confidence.

## 4. Controlled Diagnostic Safety Probe and Label Schema

We use generated images as a controlled diagnostic safety probe for VLM auditors. The current dataset has 144 prompt-image pairs, built from 64 unique images. It covers eight anomaly axes:

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

For each axis, five target-anomaly images are evaluated under three prompt contexts: violating, intended/required, and ambiguous. Three additional control images per axis are included as no-issue controls. This yields 18 prompt-image pairs per axis and 144 total rows. The goal is not to claim broad coverage of all generated-image failures, but to create a controlled safety probe where the same kind of abnormality can change hallucination status under different prompt-permission conditions.

![Figure 2. Representative generated images used as controlled visual stimuli.](figures/fig_generated_examples.png)

Figure 2. Representative generated images used as controlled visual stimuli. Each panel shows one target-anomaly image from one axis. These images are not standalone hallucination labels: target-anomaly images are reused under required, violating, and ambiguous evaluation prompts, while separate control images test `no_issue` behavior.

The generated-image setting is useful for test-time safety auditing because the visible abnormality can be held fixed while the audit prompt changes the permission boundary. For example, an extra-finger image can be a clear defect under a natural-human prompt, an authorized invention under an alien-character prompt, or an underdetermined case under an open artistic prompt. The image therefore supplies controlled visual evidence, while the final safety label must be inferred from the image-prompt-target-anomaly relation.

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

![Figure 3. Prompt-permission schema.](figures/fig_boundary_schema.png)

Figure 3. Prompt-permission schema. The same visible abnormality can be safe, unsafe, or uncertain depending on whether the prompt requires, permits, forbids, underdetermines, or lacks the target anomaly.

## 5. VLM Safety Auditor Setup

The repository contains three auditor prompt templates: image-only, prompt-conditioned, and permission-aware. The current result set reported here uses only the permission-aware setting. Therefore, this draft does not claim that permission-aware prompting outperforms image-only or prompt-conditioned prompting.

The permission-aware VLM runner sends each sample's image, evaluation prompt text, target anomaly, axis, and auditor instruction. The model is required to return JSON with the permission status, hallucination label, reason, and confidence. Raw outputs are saved one file per model call, and parsed outputs are stored as CSV files. These outputs are interpreted as test-time safety decisions made by the VLM auditor, not as training-time robustness improvements.

Current models:

- GPT-5.4;
- Claude Sonnet 4.6;
- Gemini 3.1 Pro Preview.

Current safety metrics:

- Permission Boundary Accuracy (PBA): permission-boundary safety accuracy, measured as exact match between predicted permission label and gold permission label.
- False Hallucination Rate on Intended Deviations (FHR_intended): false hallucination risk on prompt-authorized abnormalities; among gold `prompt_required` or `prompt_permitted` samples, fraction labeled hallucination `yes`.
- Creative Preservation: safe preservation of authorized abnormality, computed as `1 - FHR_intended`.
- Missed Violation Rate (MVR_violating): missed prompt-violation risk; among gold `prompt_violating` samples, fraction not labeled hallucination `yes`.
- Defect Sensitivity: violation detection sensitivity, computed as `1 - MVR_violating`.
- Ambiguity Calibration Rate (ACR): ambiguity calibration / uncertainty preservation; among gold `ambiguous` samples, fraction labeled hallucination `uncertain`.
- Control_FPR: false safety alarm on no-issue controls; planned for the final metric table but not yet output by the current metric script.
- Parse error rate: fraction of non-parseable outputs or outputs with illegal labels.

Metric caution: the current `06_compute_metrics.py` script does not yet output Control_FPR or non-ambiguous PBA, although those metrics are planned for the final paper.

## 6. Human Rating Protocol

Three human raters completed the v1 rating sheet for all 144 samples. The task asked raters to judge target-anomaly visibility and assign one permission label. The v1 human ratings are treated as a calibration pilot for the safety-label ontology, not as final gold.

After inspecting rater behavior, we revised the label guide into a v2 adjudication guide. The guide clarifies that `prompt_required` means the prompt explicitly requires the target anomaly, not that the image generally follows the prompt. It also clarifies that `no_issue` must be used for target-anomaly-free controls, and that broad style words such as surreal, dreamlike, whimsical, symbolic, artistic, fantasy, imaginative, and stylized do not automatically imply `prompt_required`.

Because ambiguous and no-issue/control cases show severe annotation drift and label ontology instability, majority vote is not used for final labels. Instead, 79 unresolved rows have been placed into a fully blind adjudicator package.

## 7. Current Results

Table 1 reports current permission-aware VLM safety-auditor results against the current metadata-defined labels. These are current-state results, not final adjudicated benchmark results or final model rankings.

| Model | FHR_intended | Creative Preservation | MVR_violating | Defect Sensitivity | ACR | PBA |
|---|---:|---:|---:|---:|---:|---:|
| GPT-5.4 | 0.000 | 1.000 | 0.025 | 0.975 | 0.000 | 0.715 |
| Claude Sonnet 4.6 | 0.025 | 0.975 | 0.000 | 1.000 | 0.000 | 0.722 |
| Gemini 3.1 Pro Preview | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 | 0.701 |

The current permission-aware auditors mostly preserve prompt-authorized abnormalities: FHR_intended, the false hallucination risk on intended deviations, is 0.000 for GPT-5.4 and Gemini and 0.025 for Claude. They also detect clear prompt violations with high sensitivity: MVR_violating, the missed prompt-violation risk, is 0.025 for GPT-5.4 and 0.000 for Claude and Gemini.

The dominant current failure mode is ambiguity calibration. All three models have ACR = 0.000. In other words, none of the three current permission-aware runs preserves the `uncertain` hallucination label for metadata-ambiguous samples. This suggests that current VLM auditors over-resolve ambiguous permission boundaries instead of preserving uncertainty. The wording should remain cautious: these are results from the current permission-aware prompt, which was later audited as permission-aware but not fully manual-faithful. This does not establish that VLMs cannot handle ambiguity in general.

The apparent PBA ceiling is mostly driven by ambiguous cases, not by failure on clear boundaries. Because non-ambiguous PBA is not yet computed in the metric script, this statement should be treated as a current interpretation rather than a final table result.

![Figure 4. Current-state VLM safety metrics.](figures/fig_vlm_metrics.png)

Figure 4. Current-state VLM safety metrics. All values are metadata-based and pre-adjudication; final metrics will be recomputed after blind adjudication.

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

The pattern is clear: humans agree on clear permission boundaries and drift on uncertainty-sensitive categories. Rater A almost never uses `ambiguous` and tends to map metadata-ambiguous cases to `prompt_permitted`. Rater B uses `prompt_required` broadly, apparently interpreting it as general prompt compliance. Rater C uses no `no_issue`, often mapping controls to `prompt_required`. These patterns are best understood as annotation drift or semantic drift in the label ontology, not as individual rater error.

Majority vote is therefore unsafe for uncertainty-sensitive safety labels. It works relatively well for clear cases, but it fails exactly where the safety audit needs to preserve uncertainty and no-issue distinctions. In the v1 ratings, majority vote matches metadata gold for 0/40 ambiguous cases and only 3/24 no-issue/control cases. Majority vote is therefore not used as final gold.

![Figure 5. Human pilot drift by condition.](figures/fig_human_drift.png)

Figure 5. Human pilot drift by condition. Clear permission boundaries have high agreement, while ambiguous and no-issue/control categories expose semantic drift and majority-vote failure.

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

These 79 blind adjudication items remain pending for final gold construction. The blind packets remove sample IDs, condition labels, majority labels, v1 rater labels, model outputs, and priority text that might reveal the intended condition. A coordinator-only mapping file is retained separately and should not be sent to adjudicators.

Final gold construction will follow these rules:

1. Retain stable metadata gold for clear-boundary rows with human support.
2. Use adjudicator labels where `adjudicator_final_permission` is filled.
3. Do not infer missing adjudicator labels.
4. Do not use simple majority vote for ambiguous or no-issue/control cases.
5. Mark every final label with `gold_source`.
6. Report unresolved cases separately or exclude them from the main exact-label metric.

## 10. Discussion

The current study supports a methodological claim for the PRCV safe-inference setting: VLM-based hallucination safety auditing should separate visual abnormality from prompt violation. This distinction matters for creative generation because prompts often intentionally request strange or impossible content. A permission-aware schema allows an auditor to preserve creative deviations while still detecting clear defects.

This work should be viewed as a first step from binary correctness checking toward permission-aware safety auditing. Generated images often contain visual inventions beyond the prompt; safe auditors should distinguish authorized invention, prompt violation, and underdetermined cases rather than collapsing all abnormality into hallucination. This is a future-looking safe-inference direction rather than a completed claim-entitlement system.

The VLM results and human pilot point to the same pressure point. Clear permission boundaries are relatively easy: models and humans both handle required/intended abnormalities and violations reasonably well. Ambiguous and no_issue/control cases are harder. Models over-resolve ambiguity by avoiding `uncertain`; humans drift because some raters treat prompt compliance as `prompt_required` and some do not preserve `no_issue`.

This has practical consequences. Safety evaluations that only report binary hallucination rates may hide whether a model is preserving creative intent, detecting violations, or forcing ambiguity into an overconfident label. Similarly, majority-vote human labels may look like a convenient gold construction method, but in this task they erase the uncertainty categories that the controlled safety probe is designed to measure.

## 11. Limitations

This is a small controlled diagnostic safety probe with 144 prompt-image pairs. The current images and prompts are targeted rather than naturally sampled from deployed text-to-image systems. The metadata contains intended rows labeled as `prompt_required`; it does not yet include a balanced set of `prompt_permitted` gold rows. This limits conclusions about the required/permitted distinction.

The current VLM results are permission-aware safety-auditor evaluations, but an implementation audit found that the VLM prompt is not fully manual-faithful. It uses the same broad schema but omits some operational guidance from the human label guide. Therefore, the current results should not be described as models following the full human annotation manual, and they should not be used to claim that permission-aware prompting outperforms image-only or prompt-conditioned prompting.

The current metrics are pre-adjudication. Final benchmark metrics, model ranking, Control_FPR, non-ambiguous PBA, final ACR, and adjudicator agreement must be updated after the 79 blind adjudication items are resolved. Current results support the safe-inference framing, but they should not be overclaimed as final full-benchmark results.

## 12. Conclusion

This work argues that not all visual weirdness is hallucination. Visual hallucination auditing for generated images should be treated as test-time safety inference for VLMs: the hallucination status of an abnormality depends on whether the prompt requires, permits, forbids, underdetermines, or lacks the target anomaly. Current permission-aware VLM auditors perform well on clear intended deviations and clear violations, but they fail to preserve ambiguity in the current run. A three-rater human pilot shows a parallel problem: clear-boundary agreement is high, while ambiguous and no-issue/control labels suffer from annotation drift and semantic instability. These current-state findings motivate permission-aware safety auditing and a blind adjudication protocol for final gold construction. Final results will be reported after adjudication.

## References

- Hu, Yushi, Benlin Liu, Jungo Kasai, Yizhong Wang, Mari Ostendorf, Ranjay Krishna, and Noah A. Smith. 2023. "TIFA: Accurate and Interpretable Text-to-Image Faithfulness Evaluation with Question Answering." In *Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)*, 20406-20417.
- Ghosh, Dhruba, Hannaneh Hajishirzi, and Ludwig Schmidt. 2023. "GenEval: An Object-Focused Framework for Evaluating Text-to-Image Alignment." In *Advances in Neural Information Processing Systems 36 (NeurIPS)*, Datasets and Benchmarks Track.
- Huang, Kaiyi, Kaiyue Sun, Enze Xie, Zhenguo Li, and Xihui Liu. 2023. "T2I-CompBench: A Comprehensive Benchmark for Open-world Compositional Text-to-Image Generation." In *Advances in Neural Information Processing Systems 36 (NeurIPS)*, Datasets and Benchmarks Track.
- Lin, Zhiqiu, Deepak Pathak, Baiqi Li, Jiayao Li, Xide Xia, Graham Neubig, Pengchuan Zhang, and Deva Ramanan. 2024. "Evaluating Text-to-Visual Generation with Image-to-Text Generation." *arXiv preprint arXiv:2404.01291*.
- Li, Yifan, Yifan Du, Kun Zhou, Jinpeng Wang, Wayne Xin Zhao, and Ji-Rong Wen. 2023. "Evaluating Object Hallucination in Large Vision-Language Models." In *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP)*.
- Guan, Tianrui, Fuxiao Liu, Xiyang Wu, Ruiqi Xian, Zongxia Li, Xiaoyu Liu, Xijun Wang, Lichang Chen, Furong Huang, Yaser Yacoob, Dinesh Manocha, and Tianyi Zhou. 2024. "HallusionBench: An Advanced Diagnostic Suite for Entangled Language Hallucination and Visual Illusion in Large Vision-Language Models." In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 14375-14385.
- Davani, Aida Mostafazadeh, Mark Diaz, and Vinodkumar Prabhakaran. 2022. "Dealing with Disagreements: Looking Beyond the Majority Vote in Subjective Annotations." *Transactions of the Association for Computational Linguistics* 10:92-110.
