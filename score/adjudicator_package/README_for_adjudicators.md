# README For Adjudicators

You are adjudicating unresolved prompt-permission samples for a visual hallucination audit.

Your task is to judge only the target anomaly against the provided prompt. Do not judge image beauty, artistic quality, or model quality in general.

## What To Fill

For each row, fill:

- `final_anomaly_visible`
- `final_permission`
- `final_confidence_1_3`
- `final_issue_tag`
- `final_rationale`

Leave sample metadata unchanged.

## Permission Labels

- `prompt_required`: the prompt explicitly requires the target anomaly.
- `prompt_permitted`: the prompt licenses the anomaly but does not explicitly require it.
- `prompt_violating`: the visible anomaly contradicts the prompt.
- `ambiguous`: the prompt underdetermines whether the anomaly is allowed.
- `no_issue`: no target anomaly or no visible issue is present.

## Important Rules

- `prompt_required` does not mean general prompt compliance.
- Use `no_issue` when `target_anomaly=none` and no visible issue is present.
- Broad style words do not automatically make an anomaly `prompt_required`.
- Style words such as surreal, dreamlike, whimsical, symbolic, artistic, fantasy, imaginative, and stylized may permit an anomaly or leave it ambiguous, but they do not explicitly require the target anomaly by themselves.
- If the permission boundary is genuinely underdetermined, use `ambiguous`.

Use `prompt_permission_label_guide_v2_adjudicator.md` for the full guide.
