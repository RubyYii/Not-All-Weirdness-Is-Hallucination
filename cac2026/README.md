# Analysis supplement

A Prompt Is Not Ground Truth: Human Validation of Local Target States in Generated Images
Camera-ready analysis package, 19 September 2026.

## Reproduce the results

Python 3.9 or newer is sufficient; no additional packages, images, network access, or private files are required. From this directory run:

```text
python reproduce_public.py --output reproduction_check.json
```

The script checks the 200-item identity and metadata in both supplied matrices, re-derives every majority/outcome and all summary statistics, compares them with `analysis_results.json`, verifies every stratified-count row, and checks the 12 R2 changes against the correction audit. A mismatch raises an error. The optional output is a machine-readable report with hashes of the public inputs.

## Analysis policy and headline results

The original Stage-1 ratings, locked before prompt reveal, are primary. The 12 post-return rater-confirmed changes are sensitivity data because their blindness after prompt reveal is not established. Primary outcomes: 174 matches, 15 mismatches, five uncertain majorities and six no-majority cases. Primary exact agreement: 150/200; Fleiss kappa: 0.674903; Gwet AC1: 0.757421. Sensitivity outcomes: 176 matches, 14 mismatches, four uncertain majorities and six no-majority cases.

All three raters were paper authors; R1, R2 and R3 are pseudonymous column identifiers, not an independent external panel. The interface withheld the prompt and expected role at response time. That procedure does not establish absence of prior familiarity or a causal benefit of hiding the prompt.

## Files

- `locked_primary_ratings.csv`: original 200 x 3 ratings, metadata and recorded outcomes.
- `rater_confirmed_sensitivity_ratings.csv`: sensitivity matrix, with 12 R2 cells changed.
- `coordinator_state_map.csv`: design-assigned requested states and lineage; kept separate from the displayed annotation materials during collection.
- `correction_audit.csv`: all 12 changes and their consequences. Ten improve exact agreement; two change the majority and the outcome.
- `stratified_counts.csv`: condition, family, lineage and crossed summaries for both analyses.
- `analysis_results.json`: original archived statistics and historical private-input hashes, preserved unchanged.
- `reproduce_public.py`: dependency-free public-input reproduction script. Its statistical definitions are retained from the accepted analysis; the public-file validation and entry point were added for this release.

## Interpretation and provenance

The images and full prompts are not included. Numerical reproduction cannot independently verify image content, the historical rater procedure, or hashes of private inputs not in this package. `analysis_results.json` retains those historical hashes as provenance; the new reproduction report separately hashes the actual public files it reads. No historical hash is represented as newly verified.

The 87.0% rate describes the assembled 200-image collection. The complement includes 7.5% definite mismatches and 5.5% unresolved cases. Source lineage does not identify a stable generator version. The study does not evaluate an AI image judge or demonstrate improved control through corrective feedback.
