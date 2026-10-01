# Retrieval contract

**Status: R1 BASELINE IMPLEMENTED. Atlas F2 supplies the stable representation; RETRIEVAL-R1 ranks observed contexts without training a predictive model.**

R1 input: a known F2 context and its component response representation with NES, `tested_mask`, `active_mask`, direction, missingness, and evidence-layer tags. Units and dose basis remain context metadata; unknown and untested response values remain missing rather than imputed as zero.

R1 output: ranked observed contexts, primary and active-response similarity, shared and discordant components, axis summaries, phenotype anchors, and the separate reliability dimensions in [Reliability schema](RELIABILITY_SCHEMA.md). Every result retains study and experimental context and distinguishes axis resemblance from component agreement. Observed null is tested evidence; unknown and untested states are excluded by masks.

Implemented baseline: raw representative component NES with cosine similarity over mutually tested components, plus active-union cosine, directional concordance, and axis-aware cosine. Phenotype and reliability never enter the score. F2 contains three observed contexts, which is insufficient to claim retrieval performance or generalization. No PCA retrieval or prediction is implemented. Full rules are frozen in [RETRIEVAL_R1_SPEC.md](RETRIEVAL_R1_SPEC.md).
