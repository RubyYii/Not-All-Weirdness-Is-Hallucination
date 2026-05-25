# Adjudicator Response Schema / 仲裁员填写规范

## `final_anomaly_visible 最终异常是否可见`

- `yes` = target anomaly is visible / 目标异常可见
- `no` = target anomaly is not visible / 目标异常不可见
- `unclear` = visibility is unclear / 是否可见不确定

## `final_permission 最终权限标签`

- `prompt_required`
- `prompt_permitted`
- `prompt_violating`
- `ambiguous`
- `no_issue`

## `final_confidence_1_3 最终信心1-3`

- `1` = low confidence / 低信心
- `2` = medium confidence / 中等信心
- `3` = high confidence / 高信心

## Suggested `final_issue_tag 最终问题标签`

- `clear_required`
- `clear_permitted`
- `clear_violation`
- `permission_ambiguous`
- `no_target_anomaly`
- `target_not_visible`
- `prompt_too_broad`
- `style_word_only`
- `metadata_conflict`
- `other`

## `final_rationale 最终理由`

Write one short sentence in Chinese or English explaining your decision.

请用中文或英文写一句简短理由。
