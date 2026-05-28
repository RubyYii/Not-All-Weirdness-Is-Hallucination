# Results Placeholders After Blind Adjudication

The following results must be updated after the 79 fully blind adjudication rows return. Do not fill these values from v1 majority vote.

## Final Gold

- Final label distribution across all resolved samples.
- Final hallucination distribution across all resolved samples.
- Gold source breakdown:
  - `metadata_stable`;
  - `adjudicated_ambiguous`;
  - `adjudicated_control`;
  - `adjudicated_disagreement`;
  - `excluded_uncertain`, if any remain.
- Number of unresolved or excluded samples.

## Model Metrics

- Final PBA by model and audit prompt type.
- Final non-ambiguous PBA.
- Final FHR_intended.
- Final Creative Preservation.
- Final MVR_violating.
- Final Defect Sensitivity.
- Final ACR on adjudicated ambiguous cases.
- Final Control_FPR on adjudicated no_issue/control cases.
- Parse error rate after any reruns.
- Axis-level metrics after final gold update.

## Model Ranking and Trade-Offs

- Final model ranking by PBA.
- Final model ranking by Creative Preservation.
- Final model ranking by Defect Sensitivity.
- Final model ranking by ACR.
- Any Pareto/frontier plot after final metrics are recomputed.
- Whether apparent model differences are meaningful or small relative to unresolved label uncertainty.

## Human and Adjudicator Analysis

- Adjudicator A vs B agreement.
- Third adjudicator or project-lead conflict resolution rate.
- Distribution of final confidence values.
- Common adjudicator issue tags.
- Final human-vs-metadata comparison.
- Final v1-rater-vs-gold comparison.
- Summary of ambiguous cases that remain unresolved.

## Paper Text To Update

- Abstract quantitative claims.
- Results section model metrics table.
- Human annotation section if adjudicator agreement changes the interpretation.
- Discussion of ambiguity calibration after final ACR is computed.
- Limitations section to state remaining unresolved cases, if any.
- Conclusion wording so it reflects final adjudicated results rather than current-state metadata results.
