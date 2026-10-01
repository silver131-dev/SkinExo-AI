"""SkinExo-AI Context-Aware EV Response Explorer A1."""

from __future__ import annotations

import os
import tempfile

os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "skinexo_explorer_mpl"))

import streamlit as st

from components import (
    render_atlas,
    render_component_explorer,
    render_context_card,
    render_phenotype,
    render_provenance,
    render_reliability,
    render_response_overview,
    render_retrieval,
    render_similarity,
)
from data_loader import CONTEXT_LABELS, ROOT, load_explorer_data


st.set_page_config(page_title="SkinExo-AI Explorer", page_icon="🧬", layout="wide")
st.markdown("""
<style>
  .block-container {padding-top: 2rem; padding-bottom: 3rem;}
  [data-testid="stMetricValue"] {font-size: 1.05rem; white-space: normal;}
  [data-testid="stMetricLabel"] {font-weight: 650;}
  div[data-testid="stExpander"] {border: 1px solid #d9e1e8;}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def cached_data():
    return load_explorer_data(ROOT)


try:
    data = cached_data()
except FileNotFoundError as exc:
    st.error(f"Explorer data is incomplete. {exc}")
    st.info("Rebuild FRAMEWORK-F2 and RETRIEVAL-R1, then restart the app.")
    st.stop()
except (RuntimeError, ValueError) as exc:
    st.error(f"Explorer cannot start because a validated checkpoint is unavailable: {exc}")
    st.stop()

st.title("SkinExo-AI")
st.markdown("### Context-Aware Extracellular-Vesicle Response Explorer")
st.write("Compare EV-induced cellular responses across experimental contexts using component-level transcriptomic evidence, phenotype anchors, and reliability metadata.")
st.caption("Same recipient cell + different EV contexts = different transcriptomic responses. Context matters.")

tabs = st.tabs(["Context Explorer", "Response Atlas", "Context Similarity", "About"])

with tabs[0]:
    context_ids = list(data.atlas.contexts)
    default_index = context_ids.index("CTX003") if "CTX003" in context_ids else 0
    context_id = st.selectbox("Select Context", context_ids, index=default_index, format_func=lambda value: CONTEXT_LABELS.get(value, value))
    try:
        render_context_card(data, context_id)
        render_response_overview(data, context_id)
        render_component_explorer(data, context_id)
        st.divider()
        render_retrieval(data, context_id)
        st.divider()
        render_phenotype(data, context_id)
        render_reliability(data, context_id)
        render_provenance(data, context_id)
    except ValueError as exc:
        st.error(f"Invalid context selection: {exc}")
    except KeyError as exc:
        st.error(f"A required Atlas field is missing: {exc}")

with tabs[1]:
    render_atlas(data)

with tabs[2]:
    render_similarity(data)

with tabs[3]:
    st.header("What SkinExo-AI implements")
    st.markdown("""
- **Response Atlas:** implemented — F2, three verified study contexts and 339 stable components.
- **Retrieval:** implemented — R1 mask-aware, interpretable baseline.
- **Explorer:** implemented — A1 local competition demo.
- **Predictive AI:** not implemented.
- **Agent:** not implemented.
""")
    st.warning("Only three verified contexts exist. Similarity is descriptive retrieval among observed studies, not prediction or proof of generalization.")
    st.code("streamlit run app/streamlit_app.py", language="bash")
