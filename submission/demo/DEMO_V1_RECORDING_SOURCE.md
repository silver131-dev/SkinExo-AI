# SkinExo-AI DEMO-V1 authoritative recording source

## Frozen identity

| Field | Value |
|---|---|
| Product | SkinExo-AI |
| Visual version | VISUAL-V1 |
| Demo version | DEMO-V1-D1 |
| Framework | F2-2026-10-01 |
| Retrieval | R1 |
| Explorer | A1 + VISUAL-V1 presentation layer |
| Target runtime | 4:55 |
| Scenes | 6 |
| Keyframes | 30 |
| Narration words | 621 |
| Claim audit | PASS — 51/51 narration sentences mapped |
| Tests | PASS — 17/17 |
| Explorer smoke test | PASS |
| Git branch | `public-v1` |
| Recording commit | `PENDING` until the freeze commit completes |

## Self-reference policy

The authoritative recording commit is the Git commit that first contains this manifest with the commit message:

`SkinExo-AI v0.3.1: freeze visual system and demo production package`

Its exact hash is recorded in the DEMO-FREEZE-C1 completion report and must be copied into the recording log before capture. This file intentionally retains `PENDING` to avoid creating an endless self-referential commit cycle.

## Frozen retrieval display

| Query | Target | Rank | Response similarity |
|---|---|---:|---:|
| CTX003 | CTX002 | 1 | `+0.6053` |
| CTX003 | CTX001 | 2 | `−0.2755` |

CTX002–CTX003 secondary explanation values:

- active-union cosine: `+0.8563`;
- shared active components: `9`; and
- directional concordance: `1.000`.

These are descriptive response-similarity metrics, not probabilities, confidence, accuracy, or predictive performance.

## Frozen production sources

- `DEMO_V1_TIMING.md`
- `DEMO_V1_KEYFRAMES.md`
- `DEMO_V1_NARRATION.md`
- `DEMO_V1_CLAIM_AUDIT.md`
- `DEMO_V1_ONSCREEN_TEXT.md`
- `EXPLORER_RECORDING_PLAN.md`
- `DEMO_V1_ASSET_MANIFEST.md`
- `DEMO_V1_GENERATIVE_VISUAL_PROMPTS.md`
- `DEMO_V1_MOTION_PLAN.md`
- `DEMO_V1_EDIT_PLAN.md`
- `DEMO_V1_CAPTIONS.md`
- `DEMO_V1_THUMBNAIL_SPEC.md`
- `DEMO_V1_RECORDING_CHECKLIST.md`

The Explorer presentation source is `app/streamlit_app.py`, `app/components.py`, and `app/design_tokens.py`. Data loading and retrieval remain in their previously validated modules.

## Validation record

- Public-safety audit: PASS
- Scientific immutability audit: PASS
- F1 framework validation: PASS
- F2 Atlas validation: PASS
- R1 checkpoint: PASS
- A1 checkpoint: PASS
- Explorer AppTest: PASS
- Streamlit health endpoint: PASS
- Final plates generated: NO
- Explorer footage recorded: NO
- Final video assembled: NO

## Recording rule

Do not record from a dirty working tree. Before DEMO-V1-D2 capture, verify that `git rev-parse HEAD` equals the authoritative freeze hash from the DEMO-FREEZE-C1 report and that `git status --short` is empty.
