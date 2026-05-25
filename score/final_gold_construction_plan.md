# Final Gold Construction Plan

Do not construct final gold by simple majority vote.

## Inputs

- Metadata gold from `data/metadata/metadata_pairs.csv`.
- Three v1 human rating files.
- Adjudication packet: `score/prompt_permission_adjudication_packet.csv`.
- v2 label guide: `score/prompt_permission_label_guide_v2.md`.

## Gold Source Categories

Each final label should include a `gold_source` value:

- `metadata_stable_human_supported`: clear-boundary metadata gold retained with at least 2 of 3 raters agreeing.
- `adjudicated_ambiguous`: final label assigned after adjudicating an ambiguous sample.
- `adjudicated_control`: final label assigned after adjudicating a no-issue/control sample.
- `adjudicated_visibility_disagreement`: final label assigned after resolving target-anomaly visibility disagreement.
- `adjudicated_clear_boundary_disagreement`: final label assigned after a clear-boundary sample had weak human support for metadata gold.
- `unresolved_exclude_from_exact_label_main`: sample remains unresolved and should be excluded from the main exact-label metric.

## Construction Steps

1. Retain stable metadata gold for clear-boundary samples with human support.
   - Clear-boundary conditions are `violating` and `permitted`.
   - Retain metadata gold when at least 2 of 3 raters agree with metadata permission and no unresolved visibility issue exists.

2. Adjudicate all ambiguous samples.
   - Use v2 guide to decide whether the prompt truly underdetermines permission.
   - If underdetermined, final permission should be `ambiguous` and hallucination should be `uncertain`.

3. Adjudicate all no-issue/control samples.
   - If `target_anomaly=none` and no visible issue is present, final permission should be `no_issue`.
   - Do not use `prompt_required` for ordinary prompt compliance.

4. Adjudicate clear-boundary disagreements.
   - Review any `violating` or `permitted` sample where fewer than 2 raters agree with metadata gold.
   - Pay special attention to cases where raters say the target anomaly is not visible.

5. Record final fields.
   - `final_permission`
   - `final_hallucination`
   - `gold_source`
   - `adjudicator_rationale`

6. Report unresolved cases separately.
   - Optionally exclude unresolved ambiguous cases from the main exact-label metric.
   - Report ambiguity calibration on the adjudicated ambiguous subset separately.

## Metric Reporting After Final Gold

Report at least:

- PBA on all resolved samples;
- non-ambiguous PBA;
- FHR_intended;
- MVR_violating;
- ACR on adjudicated ambiguous samples;
- Control_FPR on adjudicated no-issue controls;
- parse error rate;
- number of unresolved/excluded samples.

## Important Caution

The final gold should reflect the v2 guide, not majority vote. The v1 human ratings are evidence for adjudication, but not an automatic label source.
