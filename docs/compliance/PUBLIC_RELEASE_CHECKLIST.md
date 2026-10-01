# Public release checklist

Checked for PUBLIC-GITHUB-V1 against source checkpoint DEV-C2 (`afcf6dd1c81520bbfdcad333f7f01ab6b9c3089b`).

| Check | Current status | Evidence / action |
|---|---|---|
| Credentials, tokens, passwords, cookies | PASS | Current tree and all reachable blobs scanned by `experiments/release/01_public_repo_audit.py`; no high-confidence secret pattern found |
| Private email | PASS | No email in repository content; Git commit identity uses a GitHub `users.noreply.github.com` address |
| Phone / WhatsApp / registration data | PASS | No personal registration or messaging-channel data found |
| Licensed PDFs | PASS | No PDF blob or tracked PDF path in current tree or reachable history |
| Raw omics data | PASS | No raw sequencing path or FASTQ/SRA/BAM/CRAM blob tracked |
| Full processed input matrices | PASS | No official count matrix or sample-level quantification input is tracked; derived DE/GSEA result tables are retained |
| Institutional-only material | PASS | Internal access-planning files were removed; the orphan `public-v1` snapshot does not inherit their development history |
| Absolute runtime paths | PASS | A1 checkpoint test command made portable; audit must report none in the candidate tree |
| Environment and cache files | PASS | `.venv`, `.r-env`, caches, bytecode, and temporary files are ignored |
| Files over 10 MB | PASS | No current or historical Git blob exceeds 10 MB |
| Explorer artifact closure | PASS | All runtime artifacts listed by `app/data_loader.py` are tracked |
| Runtime without raw/PDF/network | PASS | Explorer data tests and Streamlit smoke test validate the offline contract |
| Project source-code license | PASS | Standard MIT License selected for eligible original SkinExo-AI code and project-authored documentation |
| Third-party rights boundary | PASS WITH ATTRIBUTION | Public accessions and MSigDB are documented; external materials retain their own terms |

## Publication status

The MIT license and third-party boundary are documented. The clean orphan `public-v1` snapshot is the only branch intended for a future public repository; local `master` retains the complete private development history.

Publication blockers: **NONE**. GitHub repository creation, remote configuration, push, and deployment remain separate future actions and were not performed.
