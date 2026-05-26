# Paper Revision TODO After Blind Adjudication

Use this checklist after the 79 fully blind adjudication rows return.

## Gold Construction

- Merge adjudicator A and B responses.
- Accept rows where A and B agree on `final_permission`.
- Send A/B disagreements to a third adjudicator or project-lead adjudication.
- Keep low-confidence unresolved cases as `excluded_uncertain` or route them to discussion.
- Rebuild `prompt_permission_final_gold_labels.csv`.
- Regenerate `prompt_permission_final_gold_summary.md`.
- Regenerate `prompt_permission_gold_source_breakdown.csv`.

## Metrics

- Add or verify Control_FPR in `scripts/06_compute_metrics.py`.
- Add or verify non-ambiguous PBA.
- Recompute main metrics for all available models.
- Recompute axis-level metrics.
- Update all paper tables.
- Update any frontier or heatmap figures.

## Paper Text

- Replace all "current-state" metric values with final adjudicated values where appropriate.
- Keep a separate paragraph for pre-adjudication findings if analytically useful.
- Update the abstract with final adjudicated numbers.
- Update the Results section and remove any placeholders.
- Update Discussion if final adjudication changes the interpretation of ambiguous or control cases.
- Update Limitations with remaining unresolved cases, if any.
- Verify that no text says majority vote was used as final gold.

## Human Analysis

- Report adjudicator agreement.
- Report conflict-resolution count.
- Compare v1 rater drift against final adjudicated gold.
- Decide whether to include examples of common adjudication patterns.

## Claims Gate

- Do not claim permission-aware prompting outperforms image-only until image-only and prompt-conditioned ablations are run.
- Do not claim final model ranking until final adjudicated metrics are computed.
- Do not claim models fail ambiguity in general unless reruns with manual-faithful prompts support that broader claim.
- Do not treat `prompt_required` and `prompt_permitted` distinction as fully tested unless additional permitted gold rows are added or adjudicated.

## Final Submission Hygiene

- Replace generic LaTeX with PRCV/LNCS template.
- Verify all reference metadata and BibTeX.
- Add final figures or remove figure placeholders.
- Check that adjudicator-facing files remain blind and separate from coordinator-only mappings.
- Re-run dataset validator and metrics scripts before finalizing.
