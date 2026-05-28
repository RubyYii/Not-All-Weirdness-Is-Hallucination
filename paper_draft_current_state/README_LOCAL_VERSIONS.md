# Local Version Layout

Current source of truth:

- `CURRENT_PRCV_SUBMISSION/`

Use this folder for the current PRCV/LNCS submission version. It contains the current `.tex`, `.bib`, figures, compiled PDF, and submission zip.

Archived material:

- `archive_previous_drafts_2026-05-28/`

This folder keeps older current-state drafts, notes, and old LaTeX build artifacts. These files are preserved for traceability but should not be treated as the active paper version.

Tools:

- `tools/make_figures.py`

This script regenerates the current figures into `CURRENT_PRCV_SUBMISSION/figures/`.

Temporary leftover:

- `build/paper_draft_current_state.pdf`

This is an old generic-article PDF. It could not be moved during cleanup because another process was using it. After closing any PDF viewer that has it open, move it into `archive_previous_drafts_2026-05-28/old_build_artifacts/` or delete it if no longer needed.

Preference:

- Do not place paper PDFs, zips, or build artifacts in OneDrive paths. Keep them under `E:\project\Not All Weirdness Is Hallucination\...`.
