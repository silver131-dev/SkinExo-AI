# SkinExo-AI — GitHub Public Final QA

**Date:** 2026-10-06

**Scope:** Public `public-v1` at `569bd25fa5e1cc0f49e9039a52da9b250b35af1f`; read-only inspection except this QA record.
**Initial judge-facing status (before documentation cleanup):** REVIEW REQUIRED. The repository and scientific artifacts were accessible, but the Technical Report URL and publication-status wording needed a separate documentation checkpoint. The initial findings remain below for audit history.

## Post-documentation-finalization QA — local candidate, 2026-10-06

**Status:** PASS for the reviewed documentation candidate; **not yet public**. Live GitHub still points to `569bd25fa5e1cc0f49e9039a52da9b250b35af1f` until a later authorized push. No Kaggle submission has occurred.

- `README.md` now puts four compact judge links immediately after the value proposition: Final Demo, Technical Report, A2 Explorer launch guide, and reproducibility. The first screen also separates today's observed-context retrieval from future capabilities. **README judge journey: PASS for the local candidate.**
- `submission/technical_report.md` retains its methods, frozen results, limitations, and provenance; it now describes A2 Demo/Research Modes, the Context → Response → Retrieve → Explain → Evidence path, observed-context-only retrieval, the Final Demo, 22 passing tests, the published repository, and explicit TODAY/NEXT/FUTURE/LONG-TERM maturity boundaries. **Technical Report: REFRESHED.**
- The canonical Technical Report URL is frozen in the Kaggle writeup and current checklists: https://github.com/silver131-dev/SkinExo-AI/blob/public-v1/submission/technical_report.md. The Final Demo URL remains https://youtu.be/optVRKKDNec.
- Exact unresolved URL placeholder tokens in current submission-facing documents: **0**; submission-blocking placeholders: **0**. The four formerly tracked Technical Report placeholder locations were resolved. This report's pre-cleanup history below describes those earlier occurrences without creating a current URL slot.
- Current stale A1 references: **0**. Current stale pre-publication references: **0**. Current stale 17-test references: **0**. The remaining A1 and 17/17 text in `submission/S2_CONSISTENCY_AUDIT.md` is explicitly dated historical evidence; the A1 mention in the refreshed Technical Report identifies the preserved Research Mode. V1 plans, old design guides, figure-source provenance, and prior checkpoint reports remain historical, not current submission status.
- External links: public GitHub root, branch Technical Report URL, and canonical YouTube ID each returned HTTP 200. The user-reported unlisted incognito playback PASS remains the playback evidence. Local Markdown targets checked: **22; broken: 0**. **Links: PASS.**
- No scientific data, retrieval implementation, Explorer behavior, analysis result, production media, video, audio, or subtitle file changed. The frozen CTX003 states and CTX003→CTX002 `+0.6053`, `9`, `1.000`, `+0.8563`, and immune-axis `+0.8045` values remain supported by the unchanged response and retrieval artifacts. `OBSERVED_NULL` remains distinct from `NOT_TESTED`; phenotype and dimension-level reliability remain separate from similarity. No present-day prediction, efficacy, aggregate-confidence, or implemented-Digital-Twin claim was added. **Scientific, numerical, and terminology audits: PASS.**
- `PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider`: **22/22 PASS**. `git diff --check`: PASS. The reviewed diff comprises only lightweight Markdown documentation; no production path or private datum was introduced.

**Next gate:** user review of the documentation-only commit, then a separately authorized `public-v1` push and Kaggle Final QA.

## Initial public QA findings — before documentation cleanup

The sections below preserve the earlier public-branch audit as a historical snapshot. Their placeholder and stale-status findings were resolved in the local candidate summarized above; they must not be read as current candidate status.

## Remote and landing page

- Public repository: https://github.com/silver131-dev/SkinExo-AI — HTTP 200; GitHub repository metadata reports `visibility: public` and `default_branch: public-v1`.
- Live `refs/heads/public-v1`: `569bd25fa5e1cc0f49e9039a52da9b250b35af1f`, matching the expected tip.
- Explicit branch landing page: https://github.com/silver131-dev/SkinExo-AI/tree/public-v1 — HTTP 200.
- The default-branch setting means the root repository route leads judges to the intended `public-v1` tree. No branch-selection issue was found.

## README and judge journey

The opening of `README.md` identifies SkinExo-AI, the context-fragmentation problem, the implemented v0.3 response Atlas/retrieval/Explorer, and the non-predictive boundary. It does **not** put the Demo Video, Explorer launch path, or Technical Report link on the first screen: the Explorer description starts around line 65, launch instructions around line 76, and the Technical Report and Demo links occur around lines 158–160. The report is discoverable after scrolling, and there is no hosted Explorer URL; the documented route is to clone and launch the offline Streamlit app. **README: REVIEW REQUIRED for first-screen navigation, not scientific content.**

Judge path: GitHub landing → README **PASS**; README → Demo **PASS after scrolling**; README → Explorer instructions **PASS after scrolling/local setup**; README → Technical Report **PASS after scrolling**; Technical Report → limitations/provenance **PASS**. The path is navigable but not frictionless, so **judge journey: REVIEW REQUIRED**.

## Public link audit

| Link or reference | Locations / evidence | Status |
|---|---|---|
| GitHub repository and clone URL | `README.md`, `submission/SUBMISSION_CHECKLIST.md`, `submission/final_qa.md`, `submission/kaggle_writeup.md`; public root HTTP 200 and live branch verified | PASS |
| Demo Video `https://youtu.be/optVRKKDNec` | `README.md`, `submission/kaggle_writeup.md`, `submission/SUBMISSION_CHECKLIST.md`, `submission/S2_RUBRIC_MAPPING.md`, `submission/final_qa.md`, and storyboard; HTTP 200 redirect to matching YouTube ID; user-reported unlisted incognito playback PASS | PASS |
| README's relative Technical Report link | `submission/technical_report.md` is tracked; public `public-v1` GitHub file URL HTTP 200 | PASS as a link; content REVIEW REQUIRED |
| README's local figures, compliance/reproducibility documents, claim documents, and license | Referenced targets are tracked in `public-v1` | PASS |
| Kaggle writeup's relative figures | Referenced figures 08–10 are tracked | PASS |
| Kaggle writeup Technical Report URL | `submission/kaggle_writeup.md:146` contained the literal Technical Report URL placeholder token | PLACEHOLDER — submission-blocking at initial audit |

No tested public link returned a broken or private response. A successful HTTP response does not independently reproduce the user's video playback test.

## Technical Report

- **Path:** `submission/technical_report.md` (tracked and publicly accessible).
- **Title:** *SkinExo-AI: A Context-Aware Extracellular-Vesicle Response Platform*.
- **Completeness:** A full 17-section scientific report with abstract, methods, Atlas/retrieval results, Explorer, evidence limits, validation, reproducibility, and future work; four referenced figures are tracked. Scientific narrative is substantially complete.
- **Judge suitability:** REVIEW REQUIRED for freshness. `submission/technical_report.md:134` calls the Explorer A1, `:166` reports the earlier 17/17 test checkpoint, and `:174` says public GitHub publishing is pending. The public branch now contains Explorer A2, 22 passing tests, and is already published. These are status/version discrepancies, not changes to scientific values. The Kaggle writeup also says publishing is pending (`submission/kaggle_writeup.md:124`) and reports 17/17 tests (`:118`). `submission/S2_RUBRIC_MAPPING.md:9–10` and `submission/final_qa.md:28` retain older A1/17-test checkpoint wording. The historical figure manifest describes the A1 architecture figure; that is an artifact provenance statement, not a current scientific-value error.
- **README:** already links the tracked report at `README.md:158`.
- **Kaggle writeup:** has a Technical Report heading but only a placeholder at `submission/kaggle_writeup.md:146`.

Candidate URLs (both returned HTTP 200):

1. **Recommended for Kaggle after documentation freshness review — PUBLIC-V1:** https://github.com/silver131-dev/SkinExo-AI/blob/public-v1/submission/technical_report.md
2. **Immutable audit permalink — COMMIT-PINNED:** https://github.com/silver131-dev/SkinExo-AI/blob/569bd25fa5e1cc0f49e9039a52da9b250b35af1f/submission/technical_report.md

The branch URL is preferable for Kaggle because it can display approved corrections without changing the submission URL. The pinned URL preserves the current, stale publication-status wording. **No `TECHNICAL_REPORT_URL` was written into existing files in this checkpoint.**

## Placeholder audit

At the initial audit, the literal Technical Report URL placeholder token occurred in **4** submission-facing documents tracked on `public-v1`.

| File and line | Interpretation |
|---|---|
| `submission/kaggle_writeup.md:146` | Current submission text; **blocking** until URL freeze. |
| `submission/SUBMISSION_CHECKLIST.md:47` | Open workflow checklist; intentional pending gate. |
| `submission/S2_CONSISTENCY_AUDIT.md:75` | Historical audit/status note; intentional pending gate. |
| `submission/final_qa.md:61` | Open final-QA checklist; intentional pending gate. |

`DEMO_VIDEO_URL` and `PUBLIC_GITHUB_URL` occur only as names/status language in the reviewed current documents; no unresolved literal placeholder for either remains. `submission/S2_S1_AUDIT.md` quotes older TODO findings as historical evidence. V1 production checklists mention avoiding placeholders rather than containing a current submission URL slot. A local, untracked D2 caption draft contains `TBD` timing, but it is **not published on `public-v1`**. No `YOUR_` or `example.com` placeholder was found in the current submission-facing tracked files. **Submission-blocking placeholders: 1.**

## Public-safety audit

- No tracked `.mp4`, `.mov`, `.mkv`, `.wav`, `.aac`, or `.mp3` production media or generated audio; local production media remains untracked and unpublished.
- No symlink entries in the public tree; no environment-specific symlink.
- Largest tracked blob is an intended derived analysis CSV at 8,583,556 bytes; reachable public history has no blob over 10 MB.
- The repository's read-only history scanner found no credential/token pattern, non-`users.noreply.github.com` email, local absolute machine path, or private registration data in reachable public history. Its sole `institutional_authentication` hit is a **false positive**: `submission/final_qa.md:73` says the audit found **no** such material.
- `.streamlit/config.toml` holds portable UI/theme/client settings, not a local host, credential, or private path.

**Public safety: PASS** within the scope of the tracked branch and scanner/manual checks.

## Scientific and numerical consistency

Current capability remains **Observed Response Retrieval / implemented**. The public scientific report and README explicitly distinguish descriptive similarity from prediction and reject current therapeutic-efficacy, aggregate-confidence, and digital-twin claims. The public report labels cargo integration and predictive modeling as future work. EV Candidate Screening, Response Prediction, and the Skin–EV Response Digital Twin are **not claimed as implemented** in public-facing tracked documentation, but their complete TODAY/NEXT/FUTURE/LONG-TERM maturity ladder is chiefly in local, untracked V2 planning documents rather than the first-screen README. This is a discoverability gap, not a false current-capability claim. No current predictive-AI claim was found.

Frozen `data/metadata/skinexo_responses.csv` and `skinexo_axis_summary.csv` give CTX003 P `OBSERVED_NULL/0`, M `POSITIVE/4`, E `OBSERVED_NULL/0`, A `POSITIVE/1`, I `POSITIVE/27`. `outputs/retrieval/r1_pairwise_similarity.csv` gives CTX003→CTX002 primary `0.6052640111` (shown as `+0.6053`), shared active `9`, directional concordance `1.0` (100%), active-union `0.8563132845` (`+0.8563`), and immune-axis similarity `0.8044861328` (`+0.8045`). The report/writeup show the same applicable rounded retrieval figures; the A2 artifact records no scientific-value or retrieval-algorithm change.

**Scientific consistency: PASS. Numerical consistency: PASS.** The outdated public-status and test-count wording above is a documentation-freshness issue, not a frozen scientific-value discrepancy.

## Tests and next gate

`PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider`: **22 passed**. No existing file was modified, and no commit or push was performed.

Before Kaggle submission: decide and freeze the branch-based Technical Report URL, replace the Kaggle writeup placeholder, and review the stale A1/17-tests/publication-pending wording plus first-screen README navigation in an expressly authorized documentation checkpoint. Then perform Kaggle final QA.
