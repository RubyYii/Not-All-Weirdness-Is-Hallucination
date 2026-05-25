# Adjudicator Response Schema / 仲裁员填写规范

## `final_anomaly_visible 最终异常是否可见`

Allowed values / 可选值：

- `yes` = target anomaly is visible / 目标异常可见
- `no` = target anomaly is not visible / 目标异常不可见
- `unclear` = visibility is unclear / 是否可见不确定

## `final_permission 最终权限标签`

Allowed values / 可选值：

- `prompt_required`
- `prompt_permitted`
- `prompt_violating`
- `ambiguous`
- `no_issue`

## `final_confidence_1_3 最终信心1-3`

Allowed values / 可选值：

- `1` = low confidence / 低信心
- `2` = medium confidence / 中等信心
- `3` = high confidence / 高信心

## Suggested `final_issue_tag 最终问题标签`

Suggested values / 建议值：

- `clear_required` = 明确要求
- `clear_permitted` = 明确允许
- `clear_violation` = 明确违背
- `permission_ambiguous` = 权限不明确
- `no_target_anomaly` = 无目标异常
- `target_not_visible` = 目标异常不可见
- `prompt_too_broad` = prompt 太宽泛
- `style_word_only` = 只有风格词支撑
- `metadata_conflict` = 与原始 metadata 判断冲突
- `other` = 其他

## `final_rationale 最终理由`

Write one short sentence in Chinese or English explaining your decision.

请用中文或英文写一句简短理由，说明你的判断依据。
