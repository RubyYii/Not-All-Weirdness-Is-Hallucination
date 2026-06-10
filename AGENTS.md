# AGENTS.md - PRCV Finalization Rules

## Current Task

Finalize the PRCV paper "Not All Weirdness Is Hallucination: Permission-Aware Safety Auditing for Vision-Language Models".

## Hard Scope

This is a PRCV-only finalization task.

Do not work on:
- VULCA or VULCA-GEM
- Vision Banana reproduction
- Qwen-Image-Edit
- SAM or segmentation baselines
- LoRA training
- new image-generation experiments
- new model API runs

Do not change raw data labels or parsed model outputs.
Do not add new experiments.

## Scientific Claim Boundary

Preserve the current claim boundary:
- compact controlled diagnostic probe, not a large-scale benchmark
- S2-only permission-aware auditor results
- 144 total samples, 140 retained samples, 4 excluded unresolved samples
- retained labels: 69 prompt-required, 8 prompt-permitted, 39 prompt-violating, 24 no-issue, 0 ambiguous
- ambiguity preservation is not evaluated as a final metric
- UPambiguous and AORambiguous are N/A / not estimable when retained ambiguous n = 0
- prompt-permitted n = 8 is underpowered and should be interpreted cautiously
- observed zero-error cells are observed rates on the compact retained set, not population-level zero risk

The paper may claim that:
- generated-image hallucination auditing should be treated as prompt-permission reasoning
- visual abnormality alone is insufficient evidence of hallucination
- the five-way schema is prompt-required, prompt-permitted, prompt-violating, ambiguous, no-issue
- the current results evaluate clear permission-boundary behavior under S2 permission-aware auditor instruction
- binary hallucination accuracy can hide finer permission-boundary miscalibration

The paper must not claim:
- full ambiguity preservation evaluation
- completed S0-S3 prompt-ablation results
- large-scale benchmark status
- population-level zero risk
- definitive model leaderboard
- general proof that VLMs solve hallucination auditing
- results from new experiments not present in the repository

## Editing Style

Prefer conservative, minimal edits.
Prioritize scientific accuracy, claim discipline, and submission readiness.
Preserve the existing paper structure unless a small change is necessary for consistency.

## Done Means

- manuscript patched conservatively
- metrics checked against repository outputs
- PDF builds
- no anonymity, private-path, API-key, or local-machine metadata leak
- final checklist/report produced
