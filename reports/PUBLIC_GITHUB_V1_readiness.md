# SkinExo-AI PUBLIC-GITHUB-V1

## Objective

Prepare the DEV-C2 v0.3 checkpoint for a public AI4S competition repository without creating a GitHub repository, adding a remote, pushing, deploying, adding biology, or changing frozen numerical results.

## Public Repository Scope

The candidate public tree contains project code, reproducible analysis scripts, small study metadata, project-generated result tables and figures, the F2 Response Atlas, R1 retrieval artifacts, and the A1 Explorer. Raw sequencing archives, official full input count matrices, licensed publications, reference GMT files, private environments, and authentication material are excluded.

## README

The root README now presents the problem, implemented system, three-context result, Explorer, Quick Start, repository structure, source accessions, methods, validation, limitations, reproducibility boundary, competition role, attribution, and licensing status. It uses the current architecture and Response Atlas figures.

## Runtime

The documented runtime was checked with Python 3.12.3 and Streamlit 1.64.0. `pip install --dry-run -r requirements.txt` resolves against the tested environment, `pip check` reports no broken requirements, the retrieval CLI runs for CTX003, and the Streamlit health endpoint returns `ok`.

## Explorer

The Explorer loads three contexts and 339 components from tracked artifacts. CTX003 retrieves CTX002 first and CTX001 second. The A1 validator passes its UI render, response Atlas, retrieval, explanation, phenotype, reliability, provenance, and offline-data checks.

## Tests

`pytest` runs 17 tests successfully. The suite covers R1 mask semantics and reproducibility plus Explorer contexts, component count, frozen rankings, phenotype/reliability loading, tracked-data boundaries, invalid context handling, and default Streamlit rendering.

## Data Availability

`docs/compliance/PUBLIC_DATA_AVAILABILITY.md` records GSE293186, GSE251807, and GSE293956 as the analyzed public accessions and GSE293957 as deferred/unanalyzed cargo metadata. It distinguishes source archives from the small derived artifacts retained for reproducibility and the offline demo.

## Artifact Provenance

`docs/compliance/PUBLIC_ARTIFACT_PROVENANCE.md` maps every Atlas, retrieval, and Explorer artifact used at runtime to its context basis, checkpoint, method, and generation script.

## Privacy

The current candidate tree and all reachable blobs were scanned without printing matched content. No high-confidence credential, token, password, cookie, private email, phone/WhatsApp, or registration-form data was found. Commit metadata uses a GitHub noreply address.

Three internal access-planning files were removed from the candidate tree. They contain no credential or authentication material. The public orphan branch does not inherit DEV-C1/DEV-C2 history, while local `master` preserves the development record.

## Licensing

The standard MIT License applies to eligible original SkinExo-AI source code and project-authored documentation. `docs/compliance/THIRD_PARTY_LICENSES.md` explicitly preserves the separate terms for GEO/NCBI, ENA, MSigDB, GENCODE, publications, institutional-access literature, and third-party software. The project license does not relicense those materials.

No licensed PDF exists in the current tree or reachable history. MSigDB GMT files are excluded and their release/terms are documented.

## Git History Audit

All three commits were audited:

- DEV-C0: `bccfbaf`
- DEV-C1: `dc3d813`
- DEV-C2: `afcf6dd`

No licensed PDF, raw omics archive, official input count matrix, credential, personal registration record, or institutional authentication material is present in local development history. Local `master` retains three removed noncredential institutional workflow notes and an old A1 checkpoint with a generic local interpreter path. The orphan `public-v1` root does not inherit those commits.

## File-Size Audit

No current or historical blob exceeds 10 MB; none exceeds 50 MB. The largest blob is the 8.58 MB EXP002 transcript-universe comparison table, a derived technical QA artifact retained for checkpoint provenance. Competition figures are below 1 MB each.

## Portability

The current Explorer and CLI use repository-relative path resolution. The A1 checkpoint test command was made portable. No current runtime artifact contains an absolute machine path. Virtual environments, caches, editor folders, OS files, environment files, raw data, and institutional literature storage are ignored.

## Limitations

- Only three verified contexts are represented.
- CTX001 and CTX003 have three samples per condition.
- Donor and EV-preparation independence are incomplete or unknown.
- CTX003 retains unexplained PC1 structure and undocumented batch.
- Retrieval is descriptive, not predictive validation.
- Phenotype anchors can differ in timepoint or model from transcriptomics.
- No therapeutic efficacy, angiogenesis, human wound-healing efficacy, trained predictive model, or agent is claimed.

## Remaining Publication Blockers

**NONE.** The MIT license is explicit and the clean `public-v1` root snapshot excludes the development history that contained removed workflow notes and a stale local path.

## V1 Decision

**PASS after PUBLIC-RELEASE-C1 validation.** README, Quick Start, runtime, tests, tracked-artifact closure, data boundaries, provenance, privacy scan, licensing, file-size limits, figures, GitHub metadata, and clean public history are ready. No repository, remote, push, or deployment has been created.
