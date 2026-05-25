# Prompt-Permission Label Guide v2 / Prompt 权限标签指南 v2

## Decision Tree / 决策树

1. Is the target anomaly visible? / 目标异常是否可见？
   - If no target anomaly is visible and the row is a control or `target_anomaly=none`, use `no_issue`.
   - 如果目标异常不可见，且该行是 control 或 `target_anomaly=none`，使用 `no_issue`。
2. Does the prompt explicitly name and require the target anomaly? / prompt 是否明确点名并要求该目标异常？
   - If yes, use `prompt_required`.
   - 如果是，使用 `prompt_required`。
3. Does the visible anomaly contradict a normal, realistic, clear, exact, intact, plausible, or physically ordinary prompt? / 可见异常是否违背了 normal、realistic、clear、exact、intact、plausible 或物理正常的 prompt？
   - If yes, use `prompt_violating`.
   - 如果是，使用 `prompt_violating`。
4. Does the prompt clearly license the anomaly by style, concept, or scene logic, without explicitly requiring it? / prompt 是否通过风格、概念或场景逻辑清楚地允许该异常，但没有明确要求？
   - If yes, use `prompt_permitted`.
   - 如果是，使用 `prompt_permitted`。
5. If the prompt does not clearly decide the permission boundary, use `ambiguous`.
   - 如果 prompt 无法明确决定权限边界，使用 `ambiguous`。

## Label Definitions / 标签定义

### `prompt_required`

Use only when the prompt explicitly requires the target anomaly.

仅当 prompt 明确要求目标异常时使用。

Positive examples / 正例：

- "six-fingered alien-human performer" explicitly requires extra fingers.
- “六指外星人-人类角色”明确要求额外手指。
- "water flows upward in reversed gravity" explicitly requires reversed gravity.
- “反重力中水向上流”明确要求反重力。
- "soft melting clocks" explicitly requires deformed clocks.
- “柔软融化的时钟”明确要求变形时钟。

Negative examples / 反例：

- "surreal portrait" does not explicitly require six fingers.
- “超现实肖像”不等于明确要求六指。
- "dreamlike scene" does not explicitly require reversed gravity.
- “梦境场景”不等于明确要求反重力。
- "artistic" or "symbolic" does not explicitly name the target anomaly.
- “艺术性”或“象征性”不等于明确点名目标异常。

### `prompt_permitted`

Use when the prompt licenses the anomaly but does not explicitly require it.

当 prompt 允许目标异常但没有明确要求时使用。

Examples / 例子：

- "unusual hands" may permit abnormal hands without explicitly requiring six fingers.
- “奇特的手部”可能允许异常手，但没有明确要求六指。
- "experimental typography" may permit distorted text without requiring illegibility.
- “实验性字体”可能允许扭曲文字，但不一定要求不可读。
- "whimsical scale relationship" may permit scale distortion without specifying a giant teacup.
- “奇幻比例关系”可能允许比例异常，但不一定要求巨型茶杯。

### `prompt_violating`

Use when the visible target anomaly contradicts the prompt.

当可见目标异常违背 prompt 时使用。

Examples / 例子：

- Prompt asks for exactly five fingers, but extra fingers are visible.
- prompt 要求正好五根手指，但图像中可见额外手指。
- Prompt asks for readable text, but the text is illegible or distorted.
- prompt 要求可读文字，但文字不可读或扭曲。
- Prompt asks for normal gravity, but water visibly flows upward.
- prompt 要求正常重力，但水明显向上流。

### `ambiguous`

Use when the prompt underdetermines whether the target anomaly is required, permitted, or violating.

当 prompt 无法决定目标异常是被要求、被允许还是违背时使用。

Examples / 例子：

- "imaginative portrait with unusual hands" when judging six fingers.
- 判断六指时，“有奇特手部的想象肖像”可能是 ambiguous。
- "strange poetic landscape with unusual water movement" when judging reversed gravity.
- 判断反重力时，“具有异常水流的奇异诗意风景”可能是 ambiguous。

### `no_issue`

Use when `target_anomaly=none` and no visible issue is present, or when the target anomaly is absent and there is no target-anomaly problem to judge.

当 `target_anomaly=none` 且没有可见问题，或目标异常不存在且无目标异常问题可判断时使用。

Do not use `prompt_required` just because the image follows the prompt.

不要因为图像总体符合 prompt 就使用 `prompt_required`。

## Common Mistakes / 常见错误

- Treating `prompt_required` as "the image follows the prompt." / 把 `prompt_required` 误解为“图像符合 prompt”。
- Treating broad style words as explicit anomaly requirements. / 把宽泛风格词误解为明确要求异常。
- Avoiding `ambiguous` when the prompt is genuinely underdetermined. / 在权限确实不明确时不使用 `ambiguous`。
- Avoiding `no_issue` for normal controls. / 对正常 control 不使用 `no_issue`。
- Judging general image quality instead of the target anomaly. / 评价整体图像质量，而不是目标异常。

## Mapping To Hallucination / 映射到幻觉标签

| final_permission | hallucination | 中文说明 |
|---|---|---|
| `prompt_violating` | `yes` | 违背 prompt，是 hallucination |
| `prompt_required` | `no` | prompt 明确要求，不是 hallucination |
| `prompt_permitted` | `no` | prompt 允许，不是 hallucination |
| `ambiguous` | `uncertain` | 权限不明确，不确定 |
| `no_issue` | `no` | 无目标异常或无明显问题 |
