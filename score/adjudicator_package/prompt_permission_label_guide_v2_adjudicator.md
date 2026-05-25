# Prompt-Permission Label Guide v2 For Adjudicators

## Decision Tree

1. Is the target anomaly visible?
   - If no target anomaly is visible and the row is a control or `target_anomaly=none`, use `no_issue`.
   - If visibility is unclear, mark `final_anomaly_visible=unclear` and judge permission only if possible.
2. Does the prompt explicitly name and require the target anomaly?
   - If yes, use `prompt_required`.
3. Does the visible anomaly contradict a normal, realistic, clear, exact, intact, plausible, or physically ordinary prompt?
   - If yes, use `prompt_violating`.
4. Does the prompt clearly license the anomaly by style, concept, or scene logic, without explicitly requiring it?
   - If yes, use `prompt_permitted`.
5. If the prompt does not clearly decide the permission boundary, use `ambiguous`.

## Label Definitions

### `prompt_required`

Use only when the prompt explicitly requires the target anomaly.

Positive examples:

- A prompt says "six-fingered alien-human performer" and the target anomaly is extra fingers.
- A prompt says "water flows upward in reversed gravity" and the target anomaly is reversed gravity.
- A prompt says "soft melting clocks" and the target anomaly is deformed clocks.

Negative examples:

- A prompt says "surreal portrait" but does not mention six fingers.
- A prompt says "dreamlike scene" but does not mention reversed gravity.
- A prompt says "artistic" or "symbolic" but does not name the target anomaly.

### `prompt_permitted`

Use when the prompt licenses the anomaly but does not explicitly require it.

Positive examples:

- "unusual hands" can permit abnormal hands without explicitly requiring six fingers.
- "experimental typography" can permit distorted text without requiring illegibility.
- "whimsical scale relationship" can permit scale distortion without specifying giant teacups.

Negative examples:

- If the prompt explicitly names the anomaly, prefer `prompt_required`.
- If the prompt asks for normal, realistic, clear, exact, or physically plausible content, and the target anomaly is visible, prefer `prompt_violating`.

### `prompt_violating`

Use when the visible target anomaly contradicts the prompt.

Positive examples:

- The prompt asks for exactly five fingers and extra fingers are visible.
- The prompt asks for readable text and the text is illegible or distorted.
- The prompt asks for normal gravity and water visibly flows upward.
- The prompt asks for separated person and chair, but human-chair fusion is visible.

Negative examples:

- Do not mark an anomaly as violating only because it looks strange.
- Do not mark a prompt-permitted creative anomaly as violating.

### `ambiguous`

Use when the prompt underdetermines whether the target anomaly is required, permitted, or violating.

Positive examples:

- "imaginative portrait with unusual hands" when judging six fingers.
- "strange poetic landscape with unusual water movement" when judging reversed gravity.
- "artistic scene about time and memory" when judging melting clocks, unless deformed clocks are explicitly mentioned.

Negative examples:

- If the prompt explicitly requires the anomaly, use `prompt_required`.
- If the prompt clearly licenses the anomaly, use `prompt_permitted`.
- If the prompt clearly forbids or contradicts the anomaly, use `prompt_violating`.

### `no_issue`

Use when `target_anomaly=none` and no visible issue is present, or when the target anomaly is absent and there is no target-anomaly problem to judge.

Positive examples:

- A no-issue control image with normal hands, normal text, normal scale, or normal physics.
- A target anomaly is not present and the image otherwise has no visible target-anomaly issue.

Negative examples:

- Do not use `prompt_required` just because the image follows the prompt.
- Do not invent an anomaly when the row is a no-issue control.

## Common Mistakes

- Treating `prompt_required` as "the image follows the prompt."
- Treating broad style words as explicit anomaly requirements.
- Refusing to use `ambiguous` when the prompt is genuinely underdetermined.
- Refusing to use `no_issue` for normal controls.
- Judging general image quality instead of the target anomaly.

## Mapping To Hallucination

| final_permission | hallucination |
|---|---|
| `prompt_violating` | `yes` |
| `prompt_required` | `no` |
| `prompt_permitted` | `no` |
| `ambiguous` | `uncertain` |
| `no_issue` | `no` |
