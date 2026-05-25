# Prompt-Permission Label Guide v2

This guide is for adjudicating human ratings in the prompt-permission boundary experiment. Judge only the target anomaly against the given evaluation prompt. Do not judge image beauty or general generation quality.

## Core Decision Order

1. Identify the target anomaly.
2. Decide whether the target anomaly is clearly visible.
3. Judge whether the evaluation prompt explicitly requires, clearly permits, clearly forbids, or underdetermines that target anomaly.
4. Assign exactly one `permission_status`.
5. Map the permission status to the hallucination label.

## Label Definitions

### `prompt_required`

Use only when the prompt explicitly requires the target anomaly.

This does not mean general prompt compliance. A picture can follow the prompt overall without the prompt explicitly requiring the target anomaly.

Examples:

- "a six-fingered alien-human performer" explicitly requires extra fingers.
- "water flows upward in reversed gravity" explicitly requires reversed gravity.
- "soft melting clocks" explicitly requires deformed clocks.

### `prompt_permitted`

Use when the prompt licenses the target anomaly but does not explicitly require it.

The prompt gives a style, concept, or scene logic that makes the anomaly acceptable, but the exact target anomaly is not mandatory.

Examples:

- "surreal alien performer with unusual hands" may permit extra fingers without explicitly requiring six fingers.
- "experimental typography" may permit distorted or illegible text without requiring a specific unreadable string.

### `prompt_violating`

Use when the visible target anomaly contradicts the prompt.

Typical cues:

- the prompt asks for normal, realistic, clear, plausible, intact, physically ordinary, or exact content;
- the target anomaly is visible;
- the anomaly conflicts with that requirement.

Examples:

- five-finger natural human hands requested, but extra fingers are visible;
- exact readable text requested, but text is distorted or illegible;
- normal gravity requested, but water visibly flows upward.

### `ambiguous`

Use when the permission status is underdetermined.

This is a real label, not a failure. Use it when the prompt is too vague to decide whether the target anomaly is required, permitted, or violating.

Examples:

- "imaginative portrait with unusual hands" may not specify whether six fingers are required or simply possible.
- "a strange poetic landscape with unusual water movement" may not clearly require reversed gravity.
- "artistic scene about time and memory" may not clearly require melting clocks unless deformed clocks are explicitly mentioned.

### `no_issue`

Use when `target_anomaly=none` and no visible issue is present.

Also use when the target anomaly is absent and there is no visible target-anomaly problem to judge.

Do not label a normal control image as `prompt_required` merely because it follows the prompt. `prompt_required` is reserved for prompts that explicitly require the target anomaly.

## Broad Style Terms

Broad style words do not automatically imply `prompt_required`.

The following terms may permit an anomaly or leave the case ambiguous, but they do not by themselves explicitly require the target anomaly:

- surreal
- dreamlike
- whimsical
- symbolic
- artistic
- fantasy
- imaginative
- stylized

Ask: does the prompt explicitly name the target anomaly, or does it only create a style context where the anomaly might be acceptable?

## Mapping To Hallucination

| permission_status | hallucination label |
|---|---|
| `prompt_violating` | `yes` |
| `prompt_required` | `no` |
| `prompt_permitted` | `no` |
| `ambiguous` | `uncertain` |
| `no_issue` | `no` |

## Majority Vote Rule

Do not use simple majority vote for uncertainty-sensitive categories.

Majority vote is especially unsafe for:

- `ambiguous`;
- `no_issue`;
- samples with target anomaly visibility disagreement.

For those samples, adjudicate using the definitions above and record a short rationale.
