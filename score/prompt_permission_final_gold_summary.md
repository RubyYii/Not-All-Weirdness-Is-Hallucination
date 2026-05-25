# Prompt-Permission Final Gold Summary

This file summarizes the current final-gold construction pass.

Important: `prompt_permission_adjudication_packet.csv` currently contains no filled `adjudicator_final_permission` values. Following the instruction not to infer missing adjudicator labels, all packet rows without adjudicator labels are marked `excluded_uncertain`.

## Counts

| Item | Count |
|---|---:|
| Total sample rows preserved | 144 |
| Resolved final samples | 65 |
| Retained from metadata-stable clear-boundary cases | 65 |
| Adjudicated from ambiguous | 0 |
| Adjudicated from no_issue/control | 0 |
| Adjudicated from other disagreements | 0 |
| Excluded / unresolved | 79 |

## Final Permission Label Distribution

Resolved samples only:

| Final permission | Count |
|---|---:|
| `prompt_required` | 36 |
| `prompt_permitted` | 0 |
| `prompt_violating` | 29 |
| `ambiguous` | 0 |
| `no_issue` | 0 |

## Final Hallucination Label Distribution

Resolved samples only:

| Final hallucination | Count |
|---|---:|
| `yes` | 29 |
| `no` | 36 |
| `uncertain` | 0 |

## Excluded Rows By Condition

| Condition | Count |
|---|---:|
| `ambiguous` | 40 |
| `no_issue` | 24 |
| `permitted` | 4 |
| `violating` | 11 |

## Gold Source Breakdown

| Gold source | Condition | Final label available | Count |
|---|---|---:|---:|
| `excluded_uncertain` | `ambiguous` | False | 40 |
| `excluded_uncertain` | `no_issue` | False | 24 |
| `excluded_uncertain` | `permitted` | False | 4 |
| `excluded_uncertain` | `violating` | False | 11 |
| `metadata_stable` | `permitted` | True | 36 |
| `metadata_stable` | `violating` | True | 29 |

## Interpretation

The current output is a traceable final-gold draft, not a fully adjudicated final label set. It preserves all original sample IDs and metadata, keeps stable clear-boundary rows as `metadata_stable`, and marks all unfilled adjudication rows as `excluded_uncertain`.

To complete final gold, fill `adjudicator_final_permission` in the adjudication packet, then rerun this construction step.
