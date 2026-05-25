# Not All Weirdness Is Hallucination: Auditing Prompt-Permission Boundaries in Generated Images

**Working title:** Not All Weirdness Is Hallucination: Auditing Prompt-Permission Boundaries in Generated Images
**Target venue:** PRCV 2026 Special Session — *From Robust Training to Safe Inference: New Security Paradigms in the Era of Large Vision Models*
**Version:** v0.1, 2026-05-17
**Paper type:** small-scale diagnostic benchmark / mechanism audit / safe-inference pilot

---

## 0. One-sentence idea

In generated-image auditing, visual abnormality is not sufficient evidence of hallucination: an unusual visual element should be labelled as hallucination only if it violates the prompt's explicit or implicit permission boundary.

---

## 1. Core framing

### 1.1 Motivation

Most generated-image evaluation asks whether an image follows a prompt, whether it contains artifacts, or whether it violates commonsense. This misses a key problem in creative generation:

> In art creation, weirdness may be the goal.

For example:

| Visual anomaly | Prompt context | Correct judgement |
|---|---|---|
| Six fingers | realistic portrait, natural hands | hallucinated artifact / prompt violation |
| Six fingers | surreal six-fingered creature | intended deviation / prompt required |
| Illegible letters | readable product poster | text-rendering failure |
| Illegible letters | illegible dreamlike typography | intended stylistic effect |
| Water flows upward | realistic landscape | physical inconsistency |
| Water flows upward | reversed-gravity dream world | prompt-permitted creative setting |
| Human-chair fusion | realistic office photo | object-fusion artifact |
| Human-chair fusion | human-chair hybrid sculpture | intended creative control |

### 1.2 Key concept: Prompt-Permission Boundary

**Definition.** Given a prompt, a generated image, and a candidate unusual visual element, the *prompt-permission boundary* determines whether that element is:

1. explicitly required by the prompt;
2. stylistically or semantically permitted by the prompt;
3. violating or contradicting the prompt;
4. ambiguous under the prompt;
5. not an issue.

A visual anomaly should be labelled as hallucination only when it is **prompt-violating** or clearly **unsupported by the prompt**.

### 1.3 Key concept: Hallucination-label eligibility

Before releasing a hallucination label, an auditor should check whether the visual anomaly is eligible for that label.

This parallels the earlier release-eligibility idea from *Final Answer Is Too Late*: the relevant question is not only whether the final output looks plausible, but whether the system should have released that output at all. Here, the analogous question is not only whether an image looks weird, but whether the system should release a hallucination label for that weirdness.

---

## 2. Difference from related work

This paper should not be framed as ordinary prompt-image alignment or artifact detection.

| Existing line | Typical question | Why our question is different |
|---|---|---|
| TIFA / VQA-based faithfulness evaluation | Does the generated image satisfy prompt facts such as objects, counts, relations? | We ask whether an unusual element is allowed by the prompt before calling it hallucination. |
| GenEval-style compositional evaluation | Are object count, position, color, and co-occurrence correct? | We study the label boundary of anomaly-as-error vs anomaly-as-control. |
| I-HallA / factual image hallucination | Does the generated image faithfully convey factual information? | We focus on creative prompts where factual implausibility can be intentional. |
| WHOOPS! / commonsense-defying images | Can models explain why an image is weird? | We ask whether weirdness should be treated as hallucination at all. |
| X-AIGD / fine-grained artifact annotation | Where are perceptual artifacts and what type are they? | We ask whether artifact-like content is prompt-violating or prompt-permitted. |

**Gap statement.** Existing evaluations ask whether generated images align with prompts, contain factual hallucinations, exhibit perceptual artifacts, or violate commonsense. We instead ask whether VLM-based auditors can determine whether an apparent anomaly is **permitted by the prompt** before releasing a hallucination label.

---

## 3. Research questions and hypotheses

### RQ1. False hallucination of intended deviations

Do VLM auditors label prompt-required or prompt-permitted creative deviations as hallucinations?

**H1.** Image-only defect auditing will over-label creative deviations as hallucinations.

### RQ2. Missing true prompt violations

Do VLM auditors mistakenly excuse true prompt violations as artistic freedom?

**H2.** Prompt-conditioned auditing reduces false hallucination labels, but may over-excuse some real prompt violations when the prompt contains creative or surreal wording.

### RQ3. Permission-aware safe inference

Does a permission-aware audit prompt improve creative preservation while maintaining defect sensitivity?

**H3.** Permission-aware auditing will improve creative preservation and permission-boundary accuracy, but may expose a trade-off with missed violation rate.

### RQ4. Axis-level differences

Which kinds of weirdness are hardest to judge: low-level artifacts, physical impossibilities, object fusion, or artistic deformation?

**H4.** Artistic deformation and ambiguous creative prompts will produce higher disagreement and lower boundary accuracy than explicit text or count errors.

---

## 4. Dataset overview

### 4.1 Unit of analysis

The experimental unit is a **prompt-image pair**, not simply an image.

The same generated image can be paired with different prompt contexts:

| Image | Prompt context | Gold status |
|---|---|---|
| A six-fingered figure | realistic portrait, natural five-finger hands | prompt_violating |
| same image | surreal six-fingered creature | prompt_required |
| same image | imaginative portrait with unusual hands | ambiguous |

This counterfactual pairing isolates prompt permission from raw visual weirdness.

### 4.2 Minimum dataset size

Recommended PRCV pilot size:

| Component | Count |
|---|---:|
| Anomaly axes | 8 |
| Core anomaly images per axis | 5 |
| Core anomaly images | 40 |
| Prompt contexts per core image | 3 |
| Core prompt-image pairs | 120 |
| No-issue control pairs per axis | 3 |
| No-issue control pairs | 24 |
| Final prompt-image pairs | 144 |

Approximate number of unique images:

- 40 core anomaly images;
- 24 no-issue control images;
- total about 64 unique images;
- expanded into 144 prompt-image pairs through prompt-context pairing.

### 4.3 Gold-label distribution

| Gold permission status | Count | Gold hallucination label |
|---|---:|---|
| prompt_violating | 40 | yes |
| prompt_required / prompt_permitted | 40 | no |
| ambiguous | 40 | uncertain |
| no_issue | 24 | no |

---

## 5. Eight anomaly axes

Each axis has five core anomaly images, each paired with three prompt contexts: violating, permitted, and ambiguous.

| Axis ID | Axis | Target anomaly | Violating prompt condition | Permitted prompt condition | Ambiguous prompt condition |
|---|---|---|---|---|---|
| A1 | Anatomy | extra fingers / abnormal hands | realistic portrait, natural five-finger hands | surreal six-fingered creature | imaginative portrait with unusual hands |
| A2 | Text | unreadable or distorted text | readable product poster with exact text | illegible dreamlike typography | expressive distorted typography |
| A3 | Physics | reversed gravity / water upward | realistic landscape, normal gravity | reversed-gravity dream world | strange poetic landscape |
| A4 | Object fusion | human-chair fusion | realistic office photo, person and chair separated | human-chair hybrid sculpture | unusual relation between person and chair |
| A5 | Count / repetition | duplicated or extra objects | exactly three cups, no more | dreamlike duplicated cups | stylized repetition of cup-like shapes |
| A6 | Spatial relation / impossible geometry | spatial contradiction | dog clearly left of cat, normal room | non-Euclidean impossible room | unusual spatial composition |
| A7 | Scale / proportion | giant everyday object or tiny people | normal scale street scene | giant teacup with tiny people | whimsical scale relationship |
| A8 | Artistic deformation | melting clocks / soft object deformation | solid functional clocks | soft melting clocks in surreal dream landscape | deformed clock-like objects in dreamlike scene |

A8 may be inspired by surrealist visual logic, but the generated image should use an original composition. Do not use named artists or reproduce real artworks.

---

## 6. Prompt bank for dataset generation

Use one text-to-image generator for the main dataset to avoid mixing generator-specific failure modes. Generate 3--5 candidates per prompt and manually select images where the target anomaly is clear.

### A1. Anatomy

**Core anomaly generation prompt:**

```text
A surreal portrait of an alien-human performer with six elegant fingers on each hand, theatrical lighting, dreamlike but detailed, hands clearly visible.
```

**Violating prompt paired with same image:**

```text
A realistic studio portrait of a young woman holding a ceramic cup, natural human anatomy, five fingers on each hand, documentary photography style.
```

**Permitted prompt:**

```text
A surreal portrait of an alien-human performer with six elegant fingers on each hand, theatrical lighting, dreamlike but detailed.
```

**Ambiguous prompt:**

```text
An imaginative portrait of a mysterious performer with unusual hands, artistic studio lighting.
```

**No-issue control prompt:**

```text
A realistic studio portrait of a person holding a ceramic cup, natural human anatomy, five fingers on each hand, hands clearly visible.
```

### A2. Text

**Core anomaly generation prompt:**

```text
An abstract experimental poster with illegible dreamlike typography, distorted letters used as visual texture, avant-garde design.
```

**Violating prompt:**

```text
A clean product advertisement poster with the exact readable text "PURE WATER" in large bold letters, professional commercial design.
```

**Permitted prompt:**

```text
An abstract experimental poster with illegible dreamlike typography, distorted letters used as visual texture, avant-garde design.
```

**Ambiguous prompt:**

```text
A creative poster using expressive typography and distorted letterforms.
```

**No-issue control prompt:**

```text
A clean product advertisement poster with the exact readable text "PURE WATER" in large bold letters.
```

### A3. Physics

**Core anomaly generation prompt:**

```text
A dream world where water flows upward into the sky, reversed gravity, surreal landscape, cinematic lighting.
```

**Violating prompt:**

```text
A realistic landscape photograph of a river flowing downhill through a valley, natural gravity and realistic lighting.
```

**Permitted prompt:**

```text
A dream world where water flows upward into the sky, reversed gravity, surreal landscape, cinematic lighting.
```

**Ambiguous prompt:**

```text
A strange poetic landscape with unusual water movement and dreamlike atmosphere.
```

**No-issue control prompt:**

```text
A realistic landscape photograph of a river flowing downhill through a valley, natural gravity and realistic lighting.
```

### A4. Human-object fusion

**Core anomaly generation prompt:**

```text
A surreal sculpture of a human body gradually merging into a chair, hybrid furniture-human form, gallery installation, realistic material detail.
```

**Violating prompt:**

```text
A realistic office photo of a person sitting on a chair, the person and chair clearly separated, natural body posture.
```

**Permitted prompt:**

```text
A surreal sculpture of a human body gradually merging into a chair, hybrid furniture-human form, gallery installation.
```

**Ambiguous prompt:**

```text
An artistic scene of a person and chair forming an unusual visual relationship.
```

**No-issue control prompt:**

```text
A realistic office photo of a person sitting on a chair, the person and chair clearly separated, natural body posture.
```

### A5. Count / repetition

**Core anomaly generation prompt:**

```text
A dreamlike tabletop scene filled with repeated duplicated cups, many copies of the same cup, surreal repetition, clean composition.
```

**Violating prompt:**

```text
A realistic tabletop photograph with exactly three white cups, no other cups, clean background.
```

**Permitted prompt:**

```text
A dreamlike tabletop scene filled with repeated duplicated cups, many copies of the same cup, surreal repetition.
```

**Ambiguous prompt:**

```text
A stylized tabletop scene with repeated cup-like shapes and visual rhythm.
```

**No-issue control prompt:**

```text
A realistic tabletop photograph with exactly three white cups, no other cups, clean background.
```

### A6. Spatial relation / impossible geometry

**Core anomaly generation prompt:**

```text
A non-Euclidean impossible room where left and right directions collapse, a dog and cat appear in a paradoxical spatial relation, surreal interior.
```

**Violating prompt:**

```text
A realistic living room photo with a dog clearly on the left side of a cat, normal perspective.
```

**Permitted prompt:**

```text
A non-Euclidean impossible room where left and right directions collapse, a dog and cat appear in a paradoxical spatial relation.
```

**Ambiguous prompt:**

```text
A strange interior scene with a dog and cat arranged in an unusual spatial composition.
```

**No-issue control prompt:**

```text
A realistic living room photo with a dog clearly on the left side of a cat, normal perspective.
```

### A7. Scale / proportion

**Core anomaly generation prompt:**

```text
A surreal city street where tiny people walk around a giant teacup, playful scale distortion, dreamlike realism.
```

**Violating prompt:**

```text
A realistic street photograph with people, cars, and a normal-sized teacup on a cafe table, natural scale.
```

**Permitted prompt:**

```text
A surreal city street where tiny people walk around a giant teacup, playful scale distortion, dreamlike realism.
```

**Ambiguous prompt:**

```text
A whimsical street scene with unusual scale relationships between people and everyday objects.
```

**No-issue control prompt:**

```text
A realistic street photograph with people, cars, and a normal-sized teacup on a cafe table, natural scale.
```

### A8. Artistic deformation

**Core anomaly generation prompt:**

```text
A surreal dream landscape with soft melting clocks draped over stones and branches, symbolic distortion of time, original composition, not imitating any existing artwork.
```

**Violating prompt:**

```text
A realistic still-life photograph of solid metal clocks on a wooden table, all clocks intact, functional, and not deformed.
```

**Permitted prompt:**

```text
A surreal dream landscape with soft melting clocks draped over stones and branches, symbolic distortion of time, original composition.
```

**Ambiguous prompt:**

```text
An artistic scene about time and memory with deformed clock-like objects in a dreamlike setting.
```

**No-issue control prompt:**

```text
A realistic still-life photograph of solid metal clocks on a wooden table, all clocks intact, functional, and not deformed.
```

---

## 7. Data construction workflow

### Step 1. Generate core anomaly images

For each axis:

1. Use the **core anomaly generation prompt**.
2. Generate 3--5 candidate images per intended sample.
3. Select 5 images where the target anomaly is clear.
4. Avoid images with multiple unrelated defects.
5. Save selected images as:

```text
images/core/A1_01.png
images/core/A1_02.png
...
images/core/A8_05.png
```

### Step 2. Create counterfactual prompt-image pairs

For each core image, create three rows:

```text
A1_01_violating
A1_01_permitted
A1_01_ambiguous
```

The image file is the same; the paired prompt and gold label differ.

### Step 3. Generate no-issue controls

For each axis, generate 3 no-issue control images using the no-issue prompt.

Save as:

```text
images/control/A1_C01.png
...
images/control/A8_C03.png
```

### Step 4. Annotator verification

Before model evaluation, two annotators verify:

1. target anomaly visibility;
2. prompt permission status;
3. gold hallucination label;
4. whether the sample should be excluded.

### Step 5. Model evaluation

Run each prompt-image pair through selected VLM auditors under three audit settings:

1. image-only target-aware audit;
2. prompt-conditioned target-aware audit;
3. permission-aware target-aware audit.

Optional appendix: open audit without target anomaly to test whether the VLM notices the anomaly spontaneously.

---

## 8. Annotation schema

Create `metadata_pairs.csv` with one row per prompt-image pair.

| Field | Type | Example |
|---|---|---|
| sample_id | string | A1_03_permitted |
| image_id | string | A1_03 |
| image_path | string | images/core/A1_03.png |
| axis_id | string | A1 |
| axis_name | string | anatomy |
| prompt_condition | enum | violating / permitted / ambiguous / no_issue |
| prompt_text | string | A surreal portrait... |
| target_anomaly | string | six fingers on each hand |
| expected_visibility | enum | visible / unclear / not_visible |
| permission_status_gold | enum | prompt_required / prompt_permitted / prompt_violating / ambiguous / no_issue |
| hallucination_gold | enum | yes / no / uncertain |
| annotator_1_label | enum | same label set |
| annotator_2_label | enum | same label set |
| final_label | enum | resolved label |
| short_reason | string | Prompt explicitly requests six fingers. |
| include_in_main | bool | TRUE / FALSE |

### Label mapping

| permission_status_gold | hallucination_gold |
|---|---|
| prompt_required | no |
| prompt_permitted | no |
| prompt_violating | yes |
| ambiguous | uncertain |
| no_issue | no |

---

## 9. Human review manual

### 9.1 Reviewer role

You are not judging whether the image is beautiful, realistic, or artistically successful. You are judging whether a specified unusual visual element is allowed by the prompt.

### 9.2 What reviewers see

For each sample, reviewers receive:

1. the generated image;
2. the paired prompt;
3. the target anomaly description;
4. an empty label form.

### 9.3 Reviewer tasks

For each sample, answer:

1. Is the target anomaly visible?
2. Does the prompt explicitly require it?
3. Does the prompt stylistically or semantically permit it?
4. Does it violate the prompt?
5. Is the prompt too ambiguous to decide?
6. Should it be labelled as hallucination?

### 9.4 Visibility labels

| Label | Definition |
|---|---|
| visible | The target anomaly is clearly present. |
| unclear | The anomaly may be present but is hard to verify. |
| not_visible | The target anomaly is absent. |

Exclude samples with `not_visible`. Flag `unclear` for discussion.

### 9.5 Permission labels

| Label | Definition | Example |
|---|---|---|
| prompt_required | The prompt explicitly asks for the anomaly. | Prompt asks for six fingers; image has six fingers. |
| prompt_permitted | The prompt does not explicitly require the anomaly, but the requested style/intent permits it. | Prompt asks for surreal body transformation; image has body distortion. |
| prompt_violating | The anomaly contradicts the prompt's requirements. | Prompt asks for natural five-finger hands; image has six fingers. |
| ambiguous | The prompt is too vague to decide whether the anomaly is allowed. | Prompt says “creative portrait with unusual hands.” |
| no_issue | No target anomaly or no problem under the prompt. | Normal five-finger hands under realistic prompt. |

### 9.6 Hallucination-label rule

Use this mapping:

| Permission label | Hallucination label |
|---|---|
| prompt_required | no |
| prompt_permitted | no |
| prompt_violating | yes |
| ambiguous | uncertain |
| no_issue | no |

### 9.7 Decision rules

1. **Do not penalize intentional weirdness.** If the prompt clearly requests a strange element, do not label it hallucination.
2. **Do not excuse every weird element as art.** If the prompt demands realism, natural anatomy, readable text, normal physics, exact count, or clear separation, violations should be labelled hallucination.
3. **Use ambiguous when intent is under-specified.** If the prompt says only “creative,” “artistic,” “dreamlike,” or “unusual,” and the anomaly is not explicitly required, use ambiguous unless the style clearly permits it.
4. **Judge the target anomaly only.** Ignore unrelated minor defects unless they make the sample unusable.
5. **Do not judge aesthetic quality.** A visually ugly but prompt-required anomaly is still not hallucination.
6. **Do not use external art-history knowledge.** Judge the prompt and image only.

### 9.8 Reviewer agreement

Minimum requirement:

- two annotators independently label all pairs;
- compute percent agreement for `permission_status_gold` and `hallucination_gold`;
- resolve disagreements by discussion;
- record final labels.

Optional:

- compute Cohen's kappa for the 5-way permission label;
- report per-axis disagreement rates.

### 9.9 Reviewer CSV fields

Each reviewer fills only:

```text
sample_id
anomaly_visible
permission_status
hallucination_label
confidence_1_3
comment
reviewer_name
```

Confidence scale:

| Score | Meaning |
|---|---|
| 1 | low confidence |
| 2 | medium confidence |
| 3 | high confidence |

---

## 10. VLM auditor evaluation

### 10.1 Models

Use 2--3 VLM auditors for PRCV minimum version.

Recommended types:

1. one strong closed-source model;
2. one strong open-source or locally runnable VLM;
3. one additional model if time permits.

Keep the paper model-agnostic until actual runs are completed. Report exact model names and access dates in the final paper.

### 10.2 Audit setting S1: Image-only target-aware audit

Purpose: measure defect bias when the prompt is absent.

```text
You are auditing a generated image.

Target unusual visual element: {target_anomaly}

Inspect the image and decide whether this target element should be labelled as a visual hallucination, artifact, or defect.

Return valid JSON only:
{
  "target_anomaly_visible": "yes | no | unclear",
  "should_label_as_hallucination": "yes | no | uncertain",
  "reason": "...",
  "confidence": "high | medium | low"
}
```

### 10.3 Audit setting S2: Prompt-conditioned target-aware audit

Purpose: test ordinary prompt-image auditing.

```text
You are auditing a generated image against its text prompt.

Text prompt:
{prompt_text}

Target unusual visual element:
{target_anomaly}

Decide whether the target unusual element violates the prompt or should be considered acceptable under the prompt.

Return valid JSON only:
{
  "target_anomaly_visible": "yes | no | unclear",
  "permission_status": "prompt_required | prompt_permitted | prompt_violating | ambiguous | no_issue",
  "should_label_as_hallucination": "yes | no | uncertain",
  "reason": "...",
  "confidence": "high | medium | low"
}
```

### 10.4 Audit setting S3: Permission-aware target-aware audit

Purpose: test the proposed safe-inference framing.

```text
You are auditing a generated image. Do not label unusual content as hallucination merely because it looks strange.

Text prompt:
{prompt_text}

Target unusual visual element:
{target_anomaly}

First decide whether the target element is:
- explicitly required by the prompt,
- stylistically or semantically permitted by the prompt,
- violating or contradicting the prompt,
- ambiguous under the prompt,
- or not an issue.

Only label the target element as hallucination if it violates or is not permitted by the prompt.

Return valid JSON only:
{
  "target_anomaly_visible": "yes | no | unclear",
  "permission_status": "prompt_required | prompt_permitted | prompt_violating | ambiguous | no_issue",
  "should_label_as_hallucination": "yes | no | uncertain",
  "visible_evidence": ["..."],
  "prompt_permission_evidence": ["..."],
  "missing_or_ambiguous_context": ["..."],
  "reason": "...",
  "confidence": "high | medium | low"
}
```

### 10.5 Optional open-audit appendix

Use this only if time permits.

```text
Given the prompt and generated image, identify any unusual visual elements and decide whether each is prompt-required, prompt-permitted, prompt-violating, ambiguous, or not an issue.
Return JSON.
```

This is more realistic but harder to parse. The main paper should rely on target-aware auditing to isolate permission reasoning.

---

## 11. Metrics

Let:

- `required_or_permitted` = samples with gold label prompt_required or prompt_permitted;
- `violating` = samples with gold label prompt_violating;
- `ambiguous` = samples with gold label ambiguous;
- `no_issue` = samples with gold label no_issue.

### 11.1 Permission Boundary Accuracy (PBA)

```text
PBA = number of samples with correct predicted permission_status / total samples
```

Report overall and per axis.

### 11.2 False Hallucination Rate on Intended Deviations (FHR-intended)

```text
FHR_intended = required_or_permitted samples predicted hallucination=yes / total required_or_permitted samples
```

Lower is better.

### 11.3 Creative Preservation Rate (CPR)

```text
CPR = 1 - FHR_intended
```

Higher means the auditor better preserves prompt-authorized creative weirdness.

### 11.4 Missed Violation Rate (MVR)

```text
MVR = violating samples not predicted hallucination=yes / total violating samples
```

Lower is better.

### 11.5 Defect Sensitivity (DS)

```text
DS = 1 - MVR
```

Higher means the auditor catches prompt-violating artifacts.

### 11.6 Ambiguity Calibration Rate (ACR)

```text
ACR = ambiguous samples predicted hallucination=uncertain / total ambiguous samples
```

Higher means the auditor is better at not over-deciding vague prompts.

### 11.7 No-issue False Alarm Rate (NIFAR)

```text
NIFAR = no_issue samples predicted hallucination=yes / total no_issue samples
```

Lower is better.

### 11.8 Creative Preservation--Defect Sensitivity Frontier

Plot each model and audit setting as a point:

```text
x-axis = Creative Preservation Rate = 1 - FHR_intended
y-axis = Defect Sensitivity = 1 - MVR
```

Ideal region: upper-right.

Interpretation:

- high DS but low CPR = strict defect-biased auditor;
- high CPR but low DS = over-permissive creativity-biased auditor;
- high DS and high CPR = permission-sensitive auditor;
- low ACR = poor ambiguity handling.

---

## 12. Analysis plan

### 12.1 Main tables

**Table 1. Dataset composition**

| Axis | Violating | Permitted | Ambiguous | No-issue | Total |
|---|---:|---:|---:|---:|---:|
| A1 | 5 | 5 | 5 | 3 | 18 |
| ... | ... | ... | ... | ... | ... |
| Total | 40 | 40 | 40 | 24 | 144 |

**Table 2. Overall metrics by model and audit setting**

| Model | Audit setting | PBA | FHR-intended | MVR | ACR | NIFAR |
|---|---|---:|---:|---:|---:|---:|

**Table 3. Per-axis permission boundary accuracy**

| Axis | Model A | Model B | Model C |
|---|---:|---:|---:|

### 12.2 Main figures

**Figure 1. Concept diagram**

Visual abnormality -> prompt-permission check -> hallucination-label eligibility.

**Figure 2. Dataset design**

Same core image paired with violating / permitted / ambiguous prompts.

**Figure 3. Creative Preservation--Defect Sensitivity Frontier**

x = CPR, y = DS.

**Figure 4. Qualitative examples**

Show one example for each of four axes:

- anatomy;
- text;
- physics;
- artistic deformation.

### 12.3 Result narrative

The target narrative should not be “permission-aware prompting is always better.” A stronger narrative is:

> Permission-aware auditing exposes a trade-off between defect sensitivity, creative preservation, and ambiguity calibration.

This mirrors the earlier release-eligibility framing: safe inference is not a single refusal rate or a single strictness level. It is a boundary decision.

---

## 13. Paper outline

### 13.1 Introduction

- Generated-image evaluation often treats weirdness as evidence of failure.
- In artistic generation, weirdness can be intentional.
- The hallucination label is therefore not image-intrinsic; it is prompt-conditional.
- Introduce prompt-permission boundary and hallucination-label eligibility.

### 13.2 Related Work

Suggested subsections:

1. Text-to-image prompt-image alignment: TIFA, GenEval, VQAScore / GenAI-Bench.
2. Image hallucination in TTI: I-HallA.
3. Commonsense-defying generated images: WHOOPS!.
4. AI-generated image artifact detection: X-AIGD.
5. Safe inference and release eligibility: connect to the prior *Final Answer Is Too Late* framing.

### 13.3 Method

- Dataset design.
- Eight anomaly axes.
- Counterfactual prompt-image pairing.
- Human annotation.
- VLM auditor settings.
- Metrics.

### 13.4 Results

- Overall metrics.
- Per-axis metrics.
- Frontier plot.
- Qualitative failures.

### 13.5 Discussion

- Why image-only defect audit is insufficient.
- Why prompt-conditioned audit still struggles with implicit artistic permission.
- Why hallucination-label eligibility is a safe-inference problem.
- Limitations: small pilot, generated images selected by authors, target-aware setting, no downstream user study.

### 13.6 Conclusion

- Not all weirdness is hallucination.
- Generated-image auditing should check prompt permission before releasing hallucination labels.

---

## 14. Implementation checklist

### Data generation

- [ ] Finalize 8 axes.
- [ ] Generate 5 core anomaly images per axis.
- [ ] Generate 3 no-issue control images per axis.
- [ ] Save all images using stable filenames.
- [ ] Create metadata CSV.
- [ ] Exclude images with unclear or multiple unrelated anomalies.

### Annotation

- [ ] Prepare reviewer CSV.
- [ ] Ask two annotators to review all 144 pairs.
- [ ] Compute agreement.
- [ ] Resolve disagreements.
- [ ] Freeze `metadata_pairs_final.csv`.

### VLM evaluation

- [ ] Select 2--3 VLM auditors.
- [ ] Run S1 image-only target-aware audit.
- [ ] Run S2 prompt-conditioned target-aware audit.
- [ ] Run S3 permission-aware target-aware audit.
- [ ] Parse JSON outputs.
- [ ] Save parse errors separately.

### Analysis

- [ ] Compute PBA, FHR-intended, CPR, MVR, DS, ACR, NIFAR.
- [ ] Compute per-axis metrics.
- [ ] Generate frontier plot.
- [ ] Select qualitative examples.

### Writing

- [ ] Draft Introduction and Related Work.
- [ ] Write Methods from frozen protocol.
- [ ] Insert results tables and figures.
- [ ] Write Discussion around safe inference and hallucination-label eligibility.
- [ ] Prepare final PRCV special session submission.

---

## 15. Suggested timeline for a June 20 deadline

| Date range | Task |
|---|---|
| Day 1 | Freeze concept, axes, prompts, metadata schema. |
| Day 2--3 | Generate images and select 40 core anomaly images + 24 controls. |
| Day 4 | Build prompt-image pair CSV. |
| Day 5--6 | Human annotation and disagreement resolution. |
| Day 7--8 | Run VLM auditor experiments. |
| Day 9 | Parse outputs and compute metrics. |
| Day 10 | Generate tables and figures. |
| Day 11--13 | Write first full draft. |
| Day 14--16 | Revise framing, related work, limitations. |
| Day 17 | Internal review by collaborator. |
| Day 18--19 | Final edits, formatting, submission. |

---

## 16. Main risks and mitigations

| Risk | Why it matters | Mitigation |
|---|---|---|
| The task is seen as ordinary prompt-image alignment. | Reviewers may compare only with TIFA/GenEval. | Emphasize prompt-permission boundary and hallucination-label eligibility. |
| Counterfactual prompt pairing looks artificial. | Same image is paired with multiple prompts. | Explain that this isolates permission reasoning, not generator performance. Add optional true-generation-failure sanity subset if time permits. |
| Prompt B is too easy because it explicitly requires the anomaly. | Models may just read prompt keywords. | Include ambiguous condition and per-axis analysis. |
| VLM misses the target anomaly. | Permission judgement becomes confounded. | Use target-aware primary audit; optional open-audit appendix. |
| Human labels are subjective. | Especially for artistic permission. | Use two annotators, clear decision rules, agreement reporting. |
| Paper overclaims. | PRCV pilot scale is small. | Frame as diagnostic pilot, not comprehensive benchmark. |

---

## 17. Minimal abstract draft

Text-to-image evaluation often treats visual anomalies as generation failures. In creative image generation, however, visual implausibility may be intentional rather than erroneous. This paper studies prompt-permission boundaries in generated-image auditing: whether a vision-language model can distinguish prompt-violating hallucinations from prompt-permitted creative deviations. We construct a small paired stress test in which the same apparent anomaly, such as distorted anatomy, illegible typography, reversed physics, object fusion, scale distortion, or artistic deformation, is presented under different prompt contexts: realism-constrained, creativity-permitted, or ambiguous. We evaluate multiple VLMs as generated-image auditors under image-only, prompt-conditioned, and permission-aware settings. Our pilot analysis measures false hallucination labelling on intended deviations, missed hallucination on prompt-violating artifacts, ambiguity calibration, and the creative-preservation versus defect-sensitivity frontier. The results aim to show that safe inference for generated-image auditing should not only ask whether an image looks unreasonable, but whether the apparent unreasonableness violates the user's generative intent.

---

## 18. Reference notes

Use these as related-work anchors:

1. TIFA: Accurate and Interpretable Text-to-Image Faithfulness Evaluation with Question Answering. https://arxiv.org/abs/2303.11897
2. GenEval: An Object-Focused Framework for Evaluating Text-to-Image Alignment. https://arxiv.org/abs/2310.11513
3. I-HallA: Evaluating Image Hallucination in Text-to-Image Generation with Question-Answering. https://arxiv.org/abs/2409.12784
4. WHOOPS!: Breaking Common Sense: A Vision-and-Language Benchmark of Synthetic and Compositional Images. https://arxiv.org/abs/2303.07274
5. X-AIGD: Unveiling Perceptual Artifacts: A Fine-Grained Benchmark for Interpretable AI-Generated Image Detection. https://arxiv.org/abs/2601.19430
6. Internal conceptual reference: Final Answer Is Too Late: Prompt-as-Intervention for Evidence-Bounded Multimodal Interpretation.
7. PRCV 2026 Special Session target: From Robust Training to Safe Inference: New Security Paradigms in the Era of Large Vision Models.

---

## 19. Final positioning sentence

This paper does not ask whether generated images are weird. It asks whether VLM auditors know when weirdness is allowed.
