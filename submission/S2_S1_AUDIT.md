# SkinExo-AI S1 narrative audit

**Audit date:** 2026-10-01

**Scope:** the pre-S2 Technical Report, Kaggle Writeup, demo storyboard, submission checklist, final QA checklist, figure manifest, and README-facing claims.

**Rule:** this audit records the state found before S2 narrative rewriting. Frozen biological results were not changed.

## Overall finding

The S1 material accurately described EXP001 at the time it was written, but it no longer described the implemented SkinExo-AI v0.3 system. Its central story was one RNA-seq analysis plus a literature framework. The completed system now includes three study-independent transcriptomic contexts, Atlas F2, Retrieval R1, and Explorer A1. S2 therefore requires a narrative replacement rather than isolated wording edits.

## File-level findings

| File | S1-era or inconsistent content | Required S2 correction |
|---|---|---|
| `technical_report.md` | States that evidence ends at EXP001-C4; treats cross-dataset validation, phenotype evidence, and explainability as unfinished; devotes most of the report to one differential-expression result. | Reframe around the context-aware platform, three verified contexts, F2 Atlas, R1 retrieval, A1 Explorer, separate phenotype anchors, and dimension-level reliability. |
| `kaggle_writeup.md` | Presents one-context EXP001 results as the project result; says no independent validation or demo exists; contains three obsolete TODO blocks. | Replace with a concise competition narrative centered on the negative universal-response result, component-level Atlas, interpretable retrieval, and offline Explorer. |
| `demo_storyboard.md` | Uses PCA, volcano, and EXP001 pathway figures as the main video; no live Explorer flow; says cross-dataset validation remains TODO. | Make the live Explorer the center of a five-minute story and specify the exact CTX003 retrieval, explanation, phenotype, and reliability clicks. |
| `SUBMISSION_CHECKLIST.md` | Stops at EXP001; cross-dataset validation and reliability are open; title, framework, retrieval, Explorer, public license, and clean release status are absent. | Record completed analysis/framework/platform checkpoints and leave publication, URLs, video, and final submission open. |
| `final_qa.md` | Checks only C1–C3.5-era numbers and has an obsolete future-results slot. | Add F2/R1/A1 numbers, claim boundaries, URL placeholders, MIT and third-party boundaries, privacy, video duration, accessibility, username, and deadline checks. |
| `figures/FIGURE_MANIFEST.md` | Figure 09 says Retrieval and Explorer are unimplemented on the master copy; final figure set is not selected. | Correct v0.3 status, retain provenance for every figure, and identify the small S2 final set separately. |
| `README.md` | Master copy describes only EXP001 and names EXP002 discovery as the next checkpoint. | Align the first-screen story with the public-v1 v0.3 README and the canonical S2 pitch, while keeping prediction claims explicitly absent. |

## Obsolete claims and TODOs

- “Current evidence ends at EXP001-C4.”
- “Cross-dataset validation” as unfinished.
- “Planned explainability” and “planned phenotype evidence.”
- “No independent validation or predictor is available,” without distinguishing completed independent-study comparison from predictive validation.
- “Next planned checkpoint: EXP002-D0.”
- Demo slots centered on a single PCA/DE/GSEA sequence.
- Figure 09 caption marking Retrieval and Explorer as future work.

The statement that predictive AI is not implemented remains correct and must be retained.

## Missing implemented material

- Three verified study-level independent contexts: GSE293186, GSE251807, and GSE293956.
- F2-2026-10-01 Response Atlas with 339 components and 1,017 records.
- Explicit `ACTIVE_POSITIVE`, `ACTIVE_NEGATIVE`, `OBSERVED_NULL`, `NOT_TESTED`, and `UNKNOWN` semantics.
- Three-context P/M/E/A/I interpretation, including the axis-versus-component distinction for I.
- Prospective CTX003 test that did not extend the provisional two-context P component.
- R1 mask-aware NES cosine, active-union cosine, directional concordance, and deterministic WHY explanations.
- A1 offline Streamlit Explorer and its tested default CTX003 retrieval.
- Separate phenotype-anchor and reliability layers.
- Public-v1 clean root release, MIT source-code license, and third-party licensing boundary.
- Seventeen passing retrieval and Explorer tests.

## Terminology drift

S1 uses “evidence framework,” “working framework,” and “SkinExo Evidence Framework” as the primary system names. S2 will standardize the public system as **SkinExo-AI: A Context-Aware Extracellular-Vesicle Response Platform**, with **Response Atlas**, **response component**, **activity state**, **mask-aware NES cosine**, **response similarity**, **phenotype anchor**, and **reliability dimension** used consistently.

## Numerical source-of-truth audit

The following S2 headline values were read from machine-readable artifacts rather than copied from prose:

- `outputs/framework/framework_f2_validation.json`: 3 contexts, 339 components, 1,017 response records, 139 active positive, 19 active negative, 852 observed null, and 7 not tested.
- `outputs/retrieval/retrieval_r1.json`: pairwise primary similarities −0.1748748, −0.2754551, and +0.6052640; CTX002–CTX003 active-union cosine +0.8563133, 9 shared active components, and 1.0 directional concordance.
- `outputs/explorer/explorer_a1.json`: Streamlit 1.64.0, offline operation, CTX003 default query, CTX002 rank 1, CTX001 rank 2, and 17 passing tests.
- `outputs/framework/framework_f2_atlas.json`: broad universal EV response `NOT_SUPPORTED` and the frozen P/M/E/A/I interpretations.

## Audit decision

**S1 narrative status: OBSOLETE BUT SCIENTIFICALLY TRACEABLE.** Replace its competition framing in S2 while retaining links to detailed checkpoint reports for the underlying analyses.
