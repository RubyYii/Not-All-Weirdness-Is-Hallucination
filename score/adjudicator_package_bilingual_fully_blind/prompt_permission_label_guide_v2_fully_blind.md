# Prompt-Permission Label Guide v2 / Prompt 权限标签指南 v2

## Decision Tree / 决策树

1. Is the target anomaly visible? / 目标异常是否可见？
   - If the target anomaly is absent and there is no visible target-anomaly issue, use `no_issue`.
   - 如果目标异常不存在，且没有可见的目标异常问题，使用 `no_issue`。
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

## Labels / 标签

| Label | 中文定义 | English definition |
|---|---|---|
| `prompt_required` | prompt 明确要求目标异常 | The prompt explicitly requires the target anomaly |
| `prompt_permitted` | prompt 允许目标异常但未明确要求 | The prompt permits but does not explicitly require the anomaly |
| `prompt_violating` | 可见目标异常违背 prompt | The visible target anomaly contradicts the prompt |
| `ambiguous` | prompt 权限边界不明确 | The prompt underdetermines whether the anomaly is allowed |
| `no_issue` | 无目标异常或无明显目标异常问题 | No target anomaly or no visible target-anomaly issue |

## Common Mistakes / 常见错误

- `prompt_required` does not mean the image generally follows the prompt.
- `prompt_required` 不是“图像总体符合 prompt”。
- Broad style words do not automatically imply `prompt_required`.
- 宽泛风格词不会自动意味着 `prompt_required`。
- Use `ambiguous` when permission is genuinely underdetermined.
- 权限确实不明确时，请使用 `ambiguous`。
- Use `no_issue` when the target anomaly is absent and there is no visible issue.
- 目标异常不存在且无可见问题时，请使用 `no_issue`。

## Broad Style Words / 宽泛风格词

Words such as surreal, dreamlike, whimsical, symbolic, artistic, fantasy, imaginative, and stylized may permit an anomaly or leave it ambiguous, but they do not explicitly require the target anomaly by themselves.

surreal、dreamlike、whimsical、symbolic、artistic、fantasy、imaginative、stylized 等词可能允许异常，也可能造成 ambiguous，但这些词本身不等于明确要求目标异常。

## Mapping To Hallucination / 映射到幻觉标签

| final_permission | hallucination | 中文说明 |
|---|---|---|
| `prompt_violating` | `yes` | 违背 prompt，是 hallucination |
| `prompt_required` | `no` | prompt 明确要求，不是 hallucination |
| `prompt_permitted` | `no` | prompt 允许，不是 hallucination |
| `ambiguous` | `uncertain` | 权限不明确，不确定 |
| `no_issue` | `no` | 无目标异常或无明显问题 |
