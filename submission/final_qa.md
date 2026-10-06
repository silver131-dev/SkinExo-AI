# SkinExo-AI final submission QA

This is the final pre-publication and pre-submission checklist. Completed local checkpoints are marked; publication-dependent items remain open.

## Scientific claims

- [x] Canonical title and one-line pitch match `S2_NARRATIVE_CONTRACT.md`.
- [x] Broad universal EV transcriptomic response is stated as **NOT SUPPORTED**.
- [x] P is described as a two-context shared component that did not extend to CTX003.
- [x] M is described as context-dependent/discordant.
- [x] E is described as null/not testable.
- [x] A is described as context-dependent/discordant without an angiogenesis claim.
- [x] I is described as conserved at the broad axis with context-varying components.
- [x] Study-level independence is not generalized to donor or EV-preparation independence.
- [x] Transcriptomic evidence is not presented as therapeutic efficacy, wound healing, or causal mechanism.
- [x] Predictive AI, trained machine learning, foundation model, digital twin, and agent claims are absent.

## Numbers

- [x] Contexts = 3.
- [x] Axes = 5.
- [x] Components = 339.
- [x] Response records = 1,017.
- [x] Activity states = 139 active positive, 19 active negative, 852 observed null, 7 not tested, 0 unknown.
- [x] Primary similarities = −0.1749, −0.2755, and +0.6053 for the frozen context pairs.
- [x] CTX002–CTX003 active-union cosine = +0.8563; shared active = 9; directional concordance = 1.000.
- [x] Default CTX003 ranking is CTX002 first and CTX001 second.
- [x] Automated tests = 17/17 pass.
- [x] Global Pearson/Spearman values, where used, match `framework_f2_atlas.json` and are labeled secondary/descriptive.

## Evidence layers and reliability

- [x] CTX003 CCK-8 and scratch anchors are labeled 24 h; transcriptomics is labeled 72 h.
- [x] Mouse wound/scar/collagen evidence is labeled in vivo and different model.
- [x] Phenotype evidence is not merged into NES or retrieval similarity.
- [x] Reliability is shown by dimension and is not collapsed to a percentage.
- [x] CTX003 unexplained PC1 structure is retained as a limitation.
- [x] Donor, EV-preparation, batch, pairing, and control uncertainty is stated where relevant.

## Figures

- [x] S2 core figure set is documented in `S2_FIGURE_SELECTION.md`.
- [x] Every selected figure is project-generated.
- [x] Every selected figure has a source artifact, generation script, claim, and limitation in the figure manifest.
- [x] Figure 09 uses the public-v1 v0.3 architecture status with Retrieval and Explorer implemented.
- [ ] Final rendered figure text is checked at Kaggle/technical-report display size.
- [ ] Video capture confirms UI labels and values are readable.

## Narrative consistency

- [x] Technical Report, Kaggle Writeup, storyboard, claim dictionary, and rubric mapping use the same core result.
- [x] Canonical terminology is used: Response Atlas, response component, activity state, mask-aware NES cosine, response similarity, phenotype anchor, reliability dimension.
- [x] Similarity values are never labeled accuracy, AUC, or prediction performance.
- [x] Future cargo integration, prospective validation, Organ-on-Chip, context expansion, and predictive modeling are labeled future.
- [ ] Participant completes final editorial review after URLs are known.

## URLs and accessibility

- [x] Verified public repository URL: `https://github.com/silver131-dev/SkinExo-AI`.
- [x] Canonical unlisted Demo Video URL frozen: https://youtu.be/optVRKKDNec; user incognito playback PASS.
- [ ] `[TECHNICAL_REPORT_URL]` replaced if a hosted report URL is required.
- [ ] No placeholder remains in final submitted text.
- [ ] Public repository opens without authentication.
- [x] Unlisted video opens in user incognito playback; approved bilingual captions are burned in.
- [ ] Alt text/captions and color readability are reviewed.

## License, privacy, and public repository

- [x] Original SkinExo-AI source code is MIT licensed in the clean public snapshot.
- [x] Third-party datasets, MSigDB, GENCODE, publications, and software retain their own terms.
- [x] Licensed Wiley PDF is excluded.
- [x] Raw omics and processed biological input matrices are excluded.
- [x] Public history audit found no secrets, private registration data, institutional authentication material, or stale local paths.
- [x] Local `public-v1` is one clean root commit with no master ancestry.
- [ ] GitHub repository created and `public-v1` pushed.
- [ ] Clean anonymous clone repeats tests and Explorer launch.

## Reproducibility

- [x] Frozen analysis plans and MSigDB 2026.1.Hs release are documented.
- [x] Atlas, retrieval, Explorer, provenance, and reliability artifacts needed at runtime are tracked in the public snapshot.
- [x] Explorer requires no raw data, licensed PDF, institutional network, or internet at runtime.
- [x] Local Streamlit health check passed.
- [ ] Public clean-clone commands are run after publication.

## Demo video

- [x] Final video frozen after user review PASS.
- [x] Duration is 04:58.48, below five minutes.
- [x] Real Explorer footage is preserved as the product-proof section.
- [ ] CTX003 → CTX002 +0.6053 and CTX001 −0.2755 appear correctly.
- [x] WHY explanation, phenotype/evidence distinctions, reliability, and provenance are shown in the Final review cut.
- [x] Spoken claims passed Final scientific, numerical, terminology, and maturity audits.
- [x] Captions, audio, generated-for-project music rights, and final export passed Final QA.

## Account and deadline

- [ ] Kaggle username `crd928` reconfirmed on the submitting account.
- [ ] Authoritative deadline and timezone reconfirmed in the competition portal.
- [ ] Required registration and AI/tool disclosures reconfirmed.
- [ ] Final submission receipt or confirmation captured.

## Current finalization status

The final demo and its canonical URL are frozen; the unlisted YouTube upload passed user incognito playback. Other publication and submission gates—including the Technical Report URL if required, final Kaggle QA, and the actual competition submission—remain open.
