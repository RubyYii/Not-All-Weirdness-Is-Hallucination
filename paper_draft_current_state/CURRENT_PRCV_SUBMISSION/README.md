# PRCV/LNCS Submission

This folder is the source of truth for the PRCV safe-inference paper.

Main files:

- `paper_prcv_lncs.tex`: LNCS-format paper source.
- `references.bib`: bibliography used by the paper.
- `figures/fig_task_schema.pdf`: unified task/schema figure.
- `figures/fig_diagnostic_examples.pdf`: 2x4 diagnostic probe examples.
- `figures/fig_gold_results.pdf`: final-gold construction and observed S2 results.
- `paper_prcv_lncs.pdf`: compiled PDF.
- `prcv_lncs_submission_package.zip`: zip package containing the TeX, BibTeX, figures, README, and PDF.

Metric naming note:

- `UP_ambiguous` / `AOR_ambiguous` are reported as N/A in the retained result set, not as 0.
- No retained final-gold sample is labeled as `ambiguous`; therefore ambiguity preservation is not evaluated in the retained metric set.

Status note:

- This version is a result draft for a compact, model-blind resolved PRCV/LNCS diagnostic probe.
- It reports a 144-sample controlled setting with 140 retained final-gold samples and 4 excluded unresolved samples.
- It reports existing S2 permission-aware results for GPT-5.4, Claude Sonnet 4.6, and Gemini 3.1 Pro Preview.
- It does not claim a completed S0-S3 prompt ablation, complete ambiguity-calibration benchmark, or definitive leaderboard.
