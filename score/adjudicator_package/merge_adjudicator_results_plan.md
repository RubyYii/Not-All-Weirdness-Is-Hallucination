# Merge Adjudicator Results Plan

This plan explains how to merge `adjudicator_A_packet.csv` and `adjudicator_B_packet.csv` after they are completed.

## Merge Rules

1. If A and B agree on `final_permission`, accept that label.
2. If A and B disagree on `final_permission`, send the row to a third adjudicator or project-lead adjudication.
3. If both adjudicators mark low confidence (`final_confidence_1_3=1`), keep `excluded_uncertain` or send the row to discussion.
4. Do not use majority vote from v1 raters to override adjudicators.
5. Preserve `gold_source`.

## Gold Source After Merge

- If an ambiguous row is resolved, use `adjudicated_ambiguous`.
- If a no-issue/control row is resolved, use `adjudicated_control`.
- If a violating/permitted disagreement row is resolved, use `adjudicated_disagreement`.
- If unresolved, keep `excluded_uncertain`.

## Required Output After Merge

The merged file should include:

- `sample_id`
- `final_permission`
- `final_hallucination`
- `gold_source`
- adjudicator agreement status
- final rationale
