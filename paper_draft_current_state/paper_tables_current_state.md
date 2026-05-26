# Paper Tables: Current State

These tables summarize current-state results only. They must be updated after the 79 fully blind adjudication rows return.

## Dataset Composition

| Item | Count |
|---|---:|
| Total prompt-image pairs | 144 |
| Unique images | 64 |
| Anomaly axes | 8 |
| Rows per axis | 18 |
| Target-anomaly images per axis | 5 |
| Control images per axis | 3 |

| Condition | Count | Current metadata permission label | Hallucination mapping |
|---|---:|---|---|
| intended / required | 40 | `prompt_required` | `no` |
| violating | 40 | `prompt_violating` | `yes` |
| ambiguous | 40 | `ambiguous` | `uncertain` |
| no_issue / control | 24 | `no_issue` | `no` |

## Label Schema

| Label | Definition | Hallucination mapping |
|---|---|---|
| `prompt_required` | prompt explicitly requires the target anomaly | `no` |
| `prompt_permitted` | prompt allows but does not require the target anomaly | `no` |
| `prompt_violating` | target anomaly contradicts the prompt | `yes` |
| `ambiguous` | permission boundary is underdetermined | `uncertain` |
| `no_issue` | no target anomaly or no visible issue | `no` |

## Current VLM Permission-Aware Metrics

Current-state results against metadata-defined labels, before final blind adjudication.

| Model | FHR_intended | Creative Preservation | MVR_violating | Defect Sensitivity | ACR | PBA | Parse error rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| GPT-5.4 | 0.000 | 1.000 | 0.025 | 0.975 | 0.000 | 0.715 | 0.000 |
| Claude Sonnet 4.6 | 0.025 | 0.975 | 0.000 | 1.000 | 0.000 | 0.722 | 0.000 |
| Gemini 3.1 Pro Preview | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 | 0.701 | 0.000 |

## Human Agreement Summary

| Metric | Result |
|---|---:|
| Three-rater exact permission agreement | 69/144 = 47.9% |
| Three-rater anomaly_visible agreement | 95/144 = 66.0% |
| Three-rater binary hallucination agreement | 107/144 = 74.3% |

## Pairwise Agreement

| Pair | Field | Agreement | Cohen kappa |
|---|---|---:|---:|
| A vs B | permission | 50.0% | 0.339 |
| A vs C | permission | 77.1% | 0.684 |
| B vs C | permission | 60.4% | 0.409 |
| A vs B | mapped hallucination | 77.8% | 0.558 |
| A vs C | mapped hallucination | 91.7% | 0.811 |
| B vs C | mapped hallucination | 78.5% | 0.579 |

## Condition-Level Agreement

| Condition | n | Permission all agree | Visibility all agree | Binary hallucination all agree | Majority matches metadata |
|---|---:|---:|---:|---:|---:|
| ambiguous | 40 | 0/40 = 0.0% | 30/40 = 75.0% | 21/40 = 52.5% | 0/40 = 0.0% |
| no_issue | 24 | 0/24 = 0.0% | 0/24 = 0.0% | 16/24 = 66.7% | 3/24 = 12.5% |
| permitted / required | 40 | 35/40 = 87.5% | 36/40 = 90.0% | 36/40 = 90.0% | 39/40 = 97.5% |
| violating | 40 | 34/40 = 85.0% | 29/40 = 72.5% | 34/40 = 85.0% | 39/40 = 97.5% |

## Rater Stance Summary

| Rater | Permission vs metadata gold | `prompt_required` | `prompt_permitted` | `prompt_violating` | `ambiguous` | `no_issue` | Main drift |
|---|---:|---:|---:|---:|---:|---:|---|
| A | 70.1% | 40 | 39 | 44 | 0 | 21 | almost no `ambiguous`; maps ambiguous to permitted |
| B | 59.0% | 80 | 1 | 39 | 19 | 5 | overuses `prompt_required` |
| C | 57.6% | 64 | 34 | 41 | 5 | 0 | uses no `no_issue`; maps controls to required |

## Current Final-Gold Draft Status

| Source | Count |
|---|---:|
| `metadata_stable` | 65 |
| `excluded_uncertain` | 79 |
| `adjudicated_ambiguous` | 0 |
| `adjudicated_control` | 0 |
| `adjudicated_disagreement` | 0 |

Resolved samples only:

| Final permission | Count |
|---|---:|
| `prompt_required` | 36 |
| `prompt_violating` | 29 |

## Pending Adjudication Breakdown

| Pending category | Count |
|---|---:|
| ambiguous | 40 |
| no_issue/control | 24 |
| violating disagreement | 11 |
| permitted disagreement | 4 |

## Metrics Not Yet Available As Final Results

| Metric | Current status |
|---|---|
| final PBA | pending blind adjudication |
| final non-ambiguous PBA | pending implementation/update after adjudication |
| final ACR | pending blind adjudication |
| final Control_FPR | not currently output by metric script; pending implementation/update |
| final model ranking | pending blind adjudication |
