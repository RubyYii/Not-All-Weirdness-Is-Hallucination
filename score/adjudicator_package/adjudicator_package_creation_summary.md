# Adjudicator Package Creation Summary

## Packet Rows

| File | Rows |
|---|---:|
| `adjudicator_A_packet.csv` | 79 |
| `adjudicator_B_packet.csv` | 79 |
| `coordinator_only_adjudication_context.csv` | 79 |

## Condition Breakdown

| Condition | Count |
|---|---:|
| `ambiguous` | 40 |
| `no_issue` | 24 |
| `permitted` | 4 |
| `violating` | 11 |

## Priority Breakdown

| Priority | Count |
|---|---:|
| `HIGH` | 66 |
| `MEDIUM` | 13 |

## Generated Files

- `README_for_adjudicators.md`
- `prompt_permission_label_guide_v2_adjudicator.md`
- `adjudicator_A_packet.csv`
- `adjudicator_B_packet.csv`
- `adjudicator_response_schema.md`
- `coordinator_only_adjudication_context.csv`
- `merge_adjudicator_results_plan.md`
- `adjudicator_package_manifest.csv`
- `adjudicator_package_creation_summary.md`

## Quality Checks

- `adjudicator_A_packet.csv` has exactly 79 rows: PASS.
- `adjudicator_B_packet.csv` has exactly 79 rows: PASS.
- A and B packets have identical `adjudication_item_id` and `sample_id` ordering: PASS.
- Blind packets do not contain model predictions: PASS.
- Blind packets do not contain majority-vote recommended answers: PASS.
- Coordinator-only file is marked unsafe to send to adjudicators in the manifest: PASS.
- Existing v1 rating files were not overwritten: PASS.
- Existing final gold labels were not changed: PASS.

## Missing Source Columns

None

## Assumptions

- The unresolved rows are the rows currently marked `excluded_uncertain` in `prompt_permission_final_gold_labels.csv`.
- Image access will be resolved by the relative `image_path` column against the project root.
- Coordinator-only context may include v1 rater labels and majority context; blind packets do not.
