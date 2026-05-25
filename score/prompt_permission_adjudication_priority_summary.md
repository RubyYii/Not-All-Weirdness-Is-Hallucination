# Prompt-Permission Adjudication Priority Summary

## Packet Size

The adjudication packet contains 79 unique samples.

| Priority | Count |
|---|---:|
| HIGH | 66 |
| MEDIUM | 13 |
| LOW | 0 |

## Included Samples By Condition

| Condition | Count |
|---|---:|
| ambiguous | 40 |
| no_issue | 24 |
| permitted | 4 |
| violating | 11 |

## Why These Samples Are Included

The packet includes:

- all 40 `ambiguous` samples;
- all 24 `no_issue` / control samples;
- clear-boundary `violating` or `permitted` samples where fewer than 2 of 3 raters agree with metadata gold;
- samples with anomaly visibility disagreement that may affect permission interpretation.

## Majority Vote Safety

| Item | Count |
|---|---:|
| No majority permission label | 12 |
| Majority not considered safe | 79 |

Simple majority is unsafe here because it fails exactly where uncertainty matters most. In the v1 ratings, no `ambiguous` sample and no `no_issue` sample had three-rater exact permission agreement.

## Recommended Adjudication Order

1. Resolve all `no_issue` controls first, using the v2 rule that `target_anomaly=none` with no visible issue must be `no_issue`.
2. Resolve all `ambiguous` samples next, explicitly deciding whether the prompt underdetermines permission.
3. Review clear-boundary samples where fewer than 2 raters support metadata gold.
4. Review visibility-disagreement samples where the visible target anomaly is uncertain.
