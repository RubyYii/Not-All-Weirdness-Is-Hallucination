# README For Adjudicators / 仲裁员说明

## Task / 任务

You are adjudicating unresolved prompt-permission samples for a visual hallucination audit.

你需要为视觉幻觉审计实验中的未决样本进行最终人工仲裁。

Judge only the target anomaly against the provided prompt. Do not judge image beauty, artistic quality, or general model quality.

只判断表格中的“目标异常”是否被当前 prompt 允许。不要评价图片美感、艺术质量或模型整体质量。

## What To Fill / 需要填写什么

Please fill these columns:

请填写以下列：

- `final_anomaly_visible 最终异常是否可见`
- `final_permission 最终权限标签`
- `final_confidence_1_3 最终信心1-3`
- `final_issue_tag 最终问题标签`
- `final_rationale 最终理由`

Do not edit sample IDs, prompts, image paths, or target anomaly fields.

不要修改样本编号、prompt、图像路径或目标异常字段。

## Five Permission Labels / 五种权限标签

| Label | 中文含义 | English meaning |
|---|---|---|
| `prompt_required` | prompt 明确要求目标异常 | The prompt explicitly requires the target anomaly |
| `prompt_permitted` | prompt 允许但未明确要求目标异常 | The prompt permits but does not explicitly require the target anomaly |
| `prompt_violating` | 可见目标异常违背 prompt | The visible target anomaly contradicts the prompt |
| `ambiguous` | prompt 权限边界不明确 | The prompt underdetermines whether the anomaly is allowed |
| `no_issue` | 无目标异常或无明显问题 | No target anomaly or no visible issue |

## Important Rules / 重要规则

- `prompt_required` does **not** mean general prompt compliance.
- `prompt_required` 不是“图像总体符合 prompt”，而是“prompt 明确要求目标异常”。
- Use `no_issue` when `target_anomaly=none` and no visible issue is present.
- 当 `target_anomaly=none` 且没有可见问题时，请使用 `no_issue`。
- Broad style words do not automatically make an anomaly `prompt_required`.
- 宽泛风格词不会自动让异常变成 `prompt_required`。
- Style words such as surreal, dreamlike, whimsical, symbolic, artistic, fantasy, imaginative, and stylized may permit an anomaly or leave it ambiguous, but they do not explicitly require it by themselves.
- 例如 surreal、dreamlike、whimsical、symbolic、artistic、fantasy、imaginative、stylized 等词，可能允许异常，也可能造成 ambiguous，但它们本身不等于明确要求目标异常。
- If the permission boundary is genuinely underdetermined, use `ambiguous`.
- 如果 prompt 是否允许目标异常确实无法判断，请使用 `ambiguous`。
