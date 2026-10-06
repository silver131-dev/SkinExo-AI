# SkinExo-AI — Live App URL Freeze (2026-10-06)

## Decision

- `LIVE_APP_URL`: **FROZEN** as https://skinexo-ai.streamlit.app/.
- Deployment platform: Streamlit Community Cloud.
- Source repository: `silver131-dev/SkinExo-AI`, branch `public-v1`.
- Entry point: `app/streamlit_app.py`.
- Public access without login: **PASS**, user-reported InPrivate test; a read-only anonymous HTTP check with in-memory cookies reached HTTP 200 without credentials.
- Live App functional QA: **PASS**, user-reported for Demo Mode, Research Mode, CTX001, CTX003, the CTX003 Response Signature, CTX002 retrieval, WHY THIS MATCH, and descriptive scientific framing.

The user-reported live QA is not a claim that this checkpoint independently replayed every browser interaction. The previous local deployment-readiness check covered Demo and Research modes across CTX001, CTX002, and CTX003 without app exceptions.

## Frozen scientific values

| CTX003 response family | State | Active components |
|---|---|---:|
| P — Proliferation | `OBSERVED_NULL` | 0 |
| M — Migration | `POSITIVE` | 4 |
| E — ECM | `OBSERVED_NULL` | 0 |
| A — Vascular / Endothelial interaction | `POSITIVE` | 1 |
| I — Immune / Inflammatory signaling | `POSITIVE` | 27 |

| CTX003 → CTX002 retrieval measure | Frozen value |
|---|---:|
| Response similarity | +0.6053 |
| Shared active components | 9 |
| Direction agreement | 100% |
| Active-union similarity | +0.8563 |
| Immune-axis similarity | +0.8045 |

The Explorer retrieves and explains **observed** contexts. These values are descriptive comparisons, not predictive performance. Scientific data, retrieval logic, Explorer A2, and the canonical Technical Report scientific content are unchanged.

## Documentation and publication boundary

README Quick Links and the Kaggle copy/paste package now include the frozen Live App URL alongside the frozen Demo Video, GitHub, and Technical Report links. The Live App is an optional additional demonstration; the required video, public repository, and Technical Report remain separate submission artifacts.

Do not modify the app, scientific data, Final video, YouTube upload, or frozen Technical Report scientific content to maintain this URL freeze. This checkpoint does not deploy, submit to Kaggle, or authorize a push. Review the lightweight documentation commit, then separately authorize publication to `public-v1` and perform Kaggle Final QA.
