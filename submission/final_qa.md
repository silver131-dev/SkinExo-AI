# SkinExo-AI final submission QA — working checklist

All checks are initially open for independent participant review. A draft or source file existing in the repository does not complete the final submission check.

## Scientific accuracy

- [ ] Every biological claim is supported by a cited primary study or explicitly marked as a hypothesis.
- [ ] Pathway, phenotype, and skin-repair claims reflect completed work only.
- [ ] Skin-on-chip work is described as future validation only.

## Statistical accuracy

- [ ] C1–C3.5 values in the report, Writeup, figures, and demo match checkpoint JSON files.
- [ ] DE contrast, sign convention, filtering, and adjusted-p thresholds are stated correctly.
- [ ] PCA and author concordance are not presented as causal or independent validation.

## Data provenance

- [ ] GEO accession and both supplementary file URLs have been checked against the current GEO record.
- [ ] Author DEG archive is described as QA-only, never as the DE model input.
- [ ] External dataset accessions and reuse constraints are reviewed.

## Reproducibility

- [ ] Python and R environment records match the actual published scripts.
- [ ] Clean-checkout instructions work with separately acquired GEO inputs.
- [ ] Published outputs can be regenerated with documented commands and versions.

## AI/tool disclosure

- [ ] Codex assistance and material software tools are disclosed in the required location.
- [ ] AI-assisted prose, citations, and metadata are independently checked by the participant.
- [ ] No predictive AI capability or performance is claimed before one exists.

## Figure rights

- [ ] Every selected figure is team-generated or has documented reuse permission.
- [ ] Figure captions state the checkpoint, method, thresholds, and limitations.
- [ ] No literature image, icon, or video asset is included without rights review.

## Repository cleanliness

- [ ] `data/raw/`, `data/processed/`, `.venv/`, `.r-env/`, and temporary files are excluded from publication.
- [ ] `git status` and intended tracked files have been reviewed before any commit.
- [ ] Public repository contains no credentials, confidential information, or restricted material.

## Demo accuracy

- [ ] Video is at most five minutes and every result shown exists in a passed checkpoint.
- [ ] The reserved future-results slot is replaced or clearly marked unfinished.
- [ ] Spoken claims, captions, citations, and figure rights have been reviewed.

## Writeup consistency

- [ ] Kaggle Writeup agrees with the technical report and final figures.
- [ ] TODO blocks are replaced only with completed, verified results.
- [ ] Public visibility and possible CC BY 4.0 terms are checked in official rules.

## Technical report consistency

- [ ] Final abstract and title are approved by the participant.
- [ ] All referenced scripts, data links, and source citations resolve.
- [ ] Claims and limitations agree with C1–C3.5 and any later completed checkpoints.
