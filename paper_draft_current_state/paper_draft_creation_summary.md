# Paper Draft Creation Summary

## Files Inspected

Core score files:

- `score/human_rating_v1_agreement_summary.md`
- `score/human_rating_v1_pairwise_agreement.csv`
- `score/human_rating_v1_condition_agreement.csv`
- `score/human_rating_v1_rater_stance_summary.md`
- `score/prompt_permission_adjudication_packet.csv`
- `score/prompt_permission_adjudication_priority_summary.md`
- `score/prompt_permission_label_guide_v2.md`
- `score/final_gold_construction_plan.md`
- `score/prompt_permission_final_gold_labels.csv`
- `score/prompt_permission_final_gold_summary.md`
- `score/prompt_permission_adjudication_log.csv`
- `score/prompt_permission_gold_source_breakdown.csv`
- `score/prompt_permission_adjudicator_package_bilingual_fully_blind.zip`
- `score/adjudicator_blind_id_mapping_coordinator_only.csv`
- `score/three_model_comparison_permission_aware.csv`
- `score/three_model_axis_comparison_permission_aware.csv`
- `score/vlm_manual_consistency_audit.md`
- `score/vlm_metric_mapping_audit.csv`

Repository files:

- `README.md`
- `data/metadata/metadata_pairs.csv`
- `scripts/06_compute_metrics.py`
- local `.tex` / `.cls` search for LNCS template

Related work source checks:

- TIFA arXiv / ICCV page
- GenEval arXiv / NeurIPS page
- T2I-CompBench arXiv / NeurIPS page
- VQAScore / text-to-visual generation arXiv
- Davani et al. TACL page

## Files Generated

- `paper_draft_current_state.md`
- `paper_draft_current_state.tex`
- `paper_tables_current_state.md`
- `paper_claims_and_status.md`
- `results_placeholders_after_adjudication.md`
- `related_work_notes.md`
- `paper_revision_todo_after_adjudication.md`
- `paper_draft_creation_summary.md`

## Current Data Used

- 144 total prompt-image pairs.
- 8 anomaly axes.
- 64 unique images.
- 40 intended / required rows.
- 40 violating rows.
- 40 ambiguous rows.
- 24 no_issue/control rows.
- Three permission-aware VLM result sets:
  - GPT-5.4;
  - Claude Sonnet 4.6;
  - Gemini 3.1 Pro Preview.
- Three completed v1 human rating files summarized through agreement reports.
- Current final-gold draft:
  - 65 `metadata_stable`;
  - 79 `excluded_uncertain`;
  - 0 adjudicated rows so far.

## Results Still Pending

- Final blind adjudication for 79 rows.
- Final gold label distribution.
- Final hallucination distribution.
- Final PBA.
- Final non-ambiguous PBA.
- Final ACR.
- Final Control_FPR.
- Final model ranking.
- Final human-vs-gold comparison.
- Adjudicator agreement and conflict-resolution summary.

## Missing Files or Assumptions

- No local PRCV/LNCS LaTeX class or template was found; the LaTeX draft is generic and must be adapted.
- Current metric script does not output Control_FPR or non-ambiguous PBA.
- Current VLM results are permission-aware only; no image-only or prompt-conditioned ablation results were found.
- Current VLM prompt was previously audited as permission-aware but not fully manual-faithful.
- The 79 unresolved rows were not inferred or filled.

## Final Check

The generated draft does not present the 79 unresolved rows as final adjudicated labels. It marks all main metrics as current-state or preliminary where needed.

This draft is ready for writing and structure review, but final Results must be updated after blind adjudication returns.
