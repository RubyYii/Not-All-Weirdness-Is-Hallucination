# Human Rating v1 Agreement Summary

This report summarizes three completed human rating files for the 144 prompt-permission samples. It is an agreement audit, not a final-gold construction step.

## Headline Results

| Agreement target | Count | Rate |
|---|---:|---:|
| Three-rater exact permission agreement | 69/144 | 47.9% |
| Three-rater anomaly_visible agreement | 95/144 | 66.0% |
| Three-rater mapped hallucination agreement | 107/144 | 74.3% |

## Agreement By Condition

| Condition | n | Permission all agree | Visibility all agree | Mapped hallucination all agree |
|---|---:|---:|---:|---:|
| ambiguous | 40 | 0/40 = 0.0% | 30/40 = 75.0% | 21/40 = 52.5% |
| no_issue | 24 | 0/24 = 0.0% | 0/24 = 0.0% | 16/24 = 66.7% |
| permitted | 40 | 35/40 = 87.5% | 36/40 = 90.0% | 36/40 = 90.0% |
| violating | 40 | 34/40 = 85.0% | 29/40 = 72.5% | 34/40 = 85.0% |

Key pattern: agreement is high on clear boundaries (`violating` and `permitted`) but collapses on uncertainty-sensitive categories (`ambiguous` and `no_issue`).

## Permission Label Counts By Rater

| Rater | prompt_required | prompt_permitted | prompt_violating | ambiguous | no_issue |
|---|---:|---:|---:|---:|---:|
| A | 40 | 39 | 44 | 0 | 21 |
| B | 80 | 1 | 39 | 19 | 5 |
| C | 64 | 34 | 41 | 5 | 0 |

## Interpretation

Do not construct final gold by simple majority vote. Majority voting performs well for clear-boundary samples, but it fails on the two categories most central to this benchmark:

- `ambiguous`: no sample had three-rater exact permission agreement.
- `no_issue`: no sample had three-rater exact permission agreement.

These samples need adjudication under a clarified v2 guide.
