# Human Rating v1 Rater Stance Summary

## Rater-Level Tendencies

| Rater | Permission vs metadata gold | required | permitted | violating | ambiguous | no_issue | anomaly_visible counts |
|---|---:|---:|---:|---:|---:|---:|---|
| A (A_strawberry) | 70.1% | 40 | 39 | 44 | 0 | 21 | yes=123, no=20, unclear=1 |
| B (B_5_18) | 59.0% | 80 | 1 | 39 | 19 | 5 | yes=101, no=31, unclear=12 |
| C (C_CHW) | 57.6% | 64 | 34 | 41 | 5 | 0 | yes=139, no=5, unclear=0 |

## Rater A: A_strawberry

Rater A is closest to metadata gold overall, especially on clear `violating` and `permitted` cases. However, A almost never uses `ambiguous`; nearly all metadata-ambiguous samples are mapped to `prompt_permitted`. This suggests A treats broad style permission as sufficient, rather than preserving underdetermined permission.

## Rater B: B_5_18

Rater B overuses `prompt_required`. The pattern suggests that B may interpret `prompt_required` as general prompt compliance, rather than as "the prompt explicitly requires the target anomaly." B also marks many `no_issue` controls as `prompt_required`, which conflicts with the guide.

## Rater C: C_CHW

Rater C is close to A on many target-anomaly cases and uses `prompt_permitted` frequently for broad style permission. However, C never uses `no_issue`; all no-issue controls are mapped mostly to `prompt_required`. This is a clear label-definition drift for controls.

## Consequence

These tendencies are diagnostically useful, but no individual rater should be treated as final gold without adjudication. The strongest use of v1 ratings is to identify which samples require adjudication and which clear-boundary samples have stable human support.
