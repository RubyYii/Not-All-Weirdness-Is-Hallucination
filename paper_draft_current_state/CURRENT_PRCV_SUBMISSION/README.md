# Current PRCV/LNCS Submission

This folder is the current source of truth for the PRCV safe-inference paper.

Main files:

- `paper_prcv_lncs.tex`: current LNCS-format paper source.
- `references.bib`: bibliography used by the paper.
- `figures/`: all figures referenced by the paper.
- `paper_prcv_lncs.pdf`: compiled current PDF.
- `prcv_lncs_submission_package.zip`: zip package containing the current TeX, BibTeX, figures, and PDF.

Metric naming note:

- The previous visual label `ACR` has been replaced in the main presentation with `UP` / `Uncertainty Preservation`.
- `UP = 0.000` means that the current VLM runs did not preserve `uncertain` on metadata-ambiguous samples. It is not an overall accuracy score.

Status note:

- This version is current-state and pre-adjudication.
- 79 blind adjudication items remain pending.
- Majority vote is not used as final gold.
- Final benchmark metrics should be recomputed after adjudication.
