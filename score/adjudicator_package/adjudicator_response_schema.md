# Adjudicator Response Schema

## `final_anomaly_visible`

Allowed values:

- `yes`
- `no`
- `unclear`

## `final_permission`

Allowed values:

- `prompt_required`
- `prompt_permitted`
- `prompt_violating`
- `ambiguous`
- `no_issue`

## `final_confidence_1_3`

Allowed values:

- `1` = low confidence
- `2` = medium confidence
- `3` = high confidence

## Suggested `final_issue_tag`

Allowed/suggested values:

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

## `final_rationale`

Write one short sentence explaining the decision. Mention the prompt phrase and the visible target anomaly when relevant.
