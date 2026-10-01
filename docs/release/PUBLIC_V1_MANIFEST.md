# SkinExo-AI public-v1 snapshot manifest

This manifest defines the only paths eligible for staging into the clean `public-v1` root commit. The snapshot is built from the audited PUBLIC-RELEASE-C1 working tree and does not inherit the `master` commit graph.

## Included top-level files

- `.gitignore`
- `.gitattributes`
- `README.md`
- `LICENSE`
- `requirements.txt`

## Included directories

- `app/` — Streamlit Explorer source and app guide
- `configs/` — frozen analysis configurations and environment records
- `data/metadata/` — public study metadata and derived Atlas/phenotype/reliability tables
- `docs/checkpoints/` — scientific analysis plans and checkpoint manifests
- `docs/compliance/` — public data, provenance, licensing, software, and release boundaries
- `docs/demo/` — Explorer walkthrough and screenshot plan
- `docs/framework/` — context, response, evidence, Atlas, reliability, and retrieval specifications
- `docs/literature/` — public-source search/provenance notes retained after the institutional-content cleanup
- `docs/release/` — public snapshot and GitHub metadata
- `docs/REPRODUCIBILITY.md`
- `experiments/` — reproducible scientific, framework, retrieval, Explorer, and release scripts
- `outputs/` — project-generated derived results and checkpoint artifacts
- `reports/` — project-authored checkpoint and release reports
- `scripts/` — command-line retrieval entry point
- `src/` — reusable SkinExo-AI source package
- `submission/` — project-authored competition materials and figures
- `tests/` — retrieval and Explorer tests

## Explicit exclusions

The following paths or file classes must not be staged:

- `.git/` and the `master` history;
- `.venv/`, `.r-env/`, `.env`, and `.env.*`;
- `data/raw/`;
- `data/processed/`;
- `data/literature/institutional/`;
- institutional access manifests, harvest notes, authentication material, or licensed article files;
- raw FASTQ/SRA/BAM/CRAM archives and official full GEO count matrices;
- MSigDB GMT caches and GENCODE source annotation files;
- licensed PDFs and publisher figures;
- `__pycache__/`, `*.pyc`, test caches, editor settings, OS files, temporary files, partial downloads, and swap files.

## Staging rule

The public root is staged only with these manifest paths:

```text
.gitignore
.gitattributes
README.md
LICENSE
requirements.txt
app
configs
data/metadata
docs
experiments
outputs
reports
scripts
src
submission
tests
```

`git add -A` is not permitted for the public snapshot.
