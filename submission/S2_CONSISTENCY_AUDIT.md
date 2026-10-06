# SkinExo-AI S2 consistency audit

**Audit date:** 2026-10-01

**Historical scope note:** The A1/17-test and pre-publication findings below describe the original S2 audit. Current submission status is Explorer A2, 22/22 passing tests, published `public-v1`, and frozen Demo Video and Technical Report URLs. The original scientific-value audit is unchanged.

## Scope

This audit covers `README.md`, the S2 Technical Report, Kaggle Writeup, demo storyboard, narrative contract, rubric mapping, claim dictionary, figure selection, figure manifest, submission checklist, and final QA document.

## Numbers audit — PASS

Headline values were read directly from machine-readable artifacts and checked programmatically.

| Value | Verified value | Source of truth |
|---|---:|---|
| Verified contexts | 3 | `outputs/framework/framework_f2_validation.json` |
| Axes | 5 | `outputs/framework/framework_f2_atlas.json` |
| Response components | 339 | `outputs/framework/framework_f2_validation.json` |
| Response records | 1,017 | `outputs/framework/framework_f2_validation.json` |
| Active positive | 139 | `outputs/framework/framework_f2_validation.json` |
| Active negative | 19 | `outputs/framework/framework_f2_validation.json` |
| Observed null | 852 | `outputs/framework/framework_f2_validation.json` |
| Not tested | 7 | `outputs/framework/framework_f2_validation.json` |
| Unknown | 0 | F2 total minus the validated activity-state counts; also explicit in `framework_f2_atlas.json` |
| CTX001–CTX002 primary cosine | −0.1749 | `outputs/retrieval/retrieval_r1.json` |
| CTX001–CTX003 primary cosine | −0.2755 | `outputs/retrieval/retrieval_r1.json` |
| CTX002–CTX003 primary cosine | +0.6053 | `outputs/retrieval/retrieval_r1.json` |
| CTX002–CTX003 active-union cosine | +0.8563 | `outputs/retrieval/retrieval_r1.json` |
| CTX002–CTX003 shared active | 9 | `outputs/retrieval/retrieval_r1.json` |
| CTX002–CTX003 directional concordance | 1.000 | `outputs/retrieval/retrieval_r1.json` |
| Retrieval/Explorer tests | 17/17 pass | `outputs/explorer/explorer_a1.json` |

Rounded display values were checked against full-precision JSON values. No performance metric was inferred from a similarity or correlation.

## Terminology audit — PASS

The competition-facing documents consistently use:

- Context-Aware Extracellular-Vesicle Response Platform;
- Response Atlas;
- response component;
- activity state;
- mask-aware NES cosine;
- response similarity;
- phenotype anchor; and
- reliability dimension.

The canonical title appears in the README, Technical Report, Kaggle Writeup, demo storyboard, and narrative contract. The canonical one-line pitch appears in the README, Technical Report, Kaggle Writeup, and narrative contract.

## Scientific claim audit — PASS

- Universal response is `NOT_SUPPORTED`.
- P is limited to a two-context shared component.
- M and A are context-dependent/discordant.
- E is null/not testable.
- I is conserved at the broad axis with context-varying components.
- Study independence is not generalized to donor or EV-preparation independence.
- Phenotype evidence remains separate and retains time/model mismatch.
- Vascular/endothelial transcriptomic evidence is not converted into an angiogenesis claim.
- Retrieval is descriptive and is not labeled accuracy, AUC, or predictive validation.
- Predictive AI, agent, therapeutic prediction, cargo causality, and clinical efficacy are not claimed.

## Narrative audit — PASS

The documents follow the same sequence: fragmented EV evidence → three contexts → universal response not supported → context-aware Atlas → retrieval → WHY explanation → phenotype/reliability → offline Explorer. Stale S1 claims and TODO framing appear only in `S2_S1_AUDIT.md`, where they are quoted as historical findings.

## Figure audit — PASS

The core S2 figures are architecture, Response Atlas, context retrieval, and similarity matrix. The architecture figure is the already audited PUBLIC-GITHUB-V1 version, which marks Response Atlas, reliability, Retrieval R1, and Explorer A1 as implemented and predictive AI as absent. Every selected figure has source artifacts, a generation script or provenance path, the supported claim, and limitations in the figure manifest. No paper-owned figure is selected.

## Link and placeholder audit

- Local Markdown link check: **PASS**, zero broken local links.
- GitHub URL: `https://github.com/silver131-dev/SkinExo-AI` is verified and frozen.
- Demo video URL: pending at the original S2 audit; subsequently frozen on 2026-10-06 as https://youtu.be/optVRKKDNec (unlisted; user incognito playback PASS).
- Technical Report URL: pending at the original S2 audit; subsequently frozen as https://github.com/silver131-dev/SkinExo-AI/blob/public-v1/submission/technical_report.md.

The current final QA and submission checklist record URL freeze; Kaggle portal rendering and submission remain separate gates.

## Frozen-result integrity — PASS

No file under `outputs/` or frozen biological metadata under `data/metadata/` was modified by S2. Reference SHA-256 values remain:

- `outputs/exp003/c4_gsea_all.csv`: `b5124d5cfd9b05b94eb270d6e7b35e15399242641bf1e798d47f8baae91bad8d`
- `outputs/exp003/exp003_c4_pathways.json`: `fb61abcd3dd7467d8423790bb208d4f10dc8e26aa663f569b4e2570a13eea75a`
- `data/metadata/skinexo_response_components.csv`: `296f73a03284f4e218f882fa5aee4956b484fdf97073f1ec6b62dc16ad3d5adc`

## Public release awareness

At this audit's 2026-10-01 checkpoint, the clean local `public-v1` root commit existed at `1e768499c86d52245058059568e4b7a48cf6faa4` but had not been pushed. It was subsequently published at https://github.com/silver131-dev/SkinExo-AI.

## Decision

**S2 narrative consistency at the audit checkpoint: PASS.** GitHub publication, the Final Demo Video, and both public URLs have since been completed. Clean-clone verification, final portal QA, and competition submission remain separate gates.
