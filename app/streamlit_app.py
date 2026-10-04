"""SkinExo-AI Context-Aware EV Response Explorer A2."""

from __future__ import annotations

import os
import tempfile

os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "skinexo_explorer_mpl"))

import streamlit as st

from components import (
    render_atlas,
    render_biological_summary,
    render_component_explorer,
    render_context_card,
    render_context_hero,
    render_evidence_snapshot,
    render_experimental_details,
    render_phenotype,
    render_product_hero,
    render_product_journey,
    render_provenance,
    render_reliability,
    render_reliability_snapshot,
    render_response_overview,
    render_retrieval,
    render_retrieval_hero,
    render_similarity,
    render_why_match,
)
from data_loader import CONTEXT_LABELS, ROOT, load_explorer_data
from design_tokens import explorer_css


st.set_page_config(
    page_title="SkinExo-AI Explorer",
    page_icon=":material/biotech:",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(explorer_css(), unsafe_allow_html=True)


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

render_product_hero()
render_product_journey()

mode_col, context_col = st.columns([0.72, 1.45], gap="large", vertical_alignment="bottom")
with mode_col:
    view_mode = st.segmented_control(
        "Explorer mode",
        ["Demo", "Research"],
        default="Demo",
        required=True,
        key="mode",
        bind="query-params",
        width="stretch",
    )
with context_col:
    context_ids = list(data.atlas.contexts)
    context_id = st.selectbox(
        "Select Context",
        context_ids,
        index=context_ids.index("CTX003") if "CTX003" in context_ids else 0,
        format_func=lambda value: CONTEXT_LABELS.get(value, value),
        key="context",
        bind="query-params",
    )

tabs = st.tabs(["Context Explorer", "Response Atlas", "Context Similarity", "About"])

with tabs[0]:
    try:
        if view_mode == "Demo":
            render_context_hero(data, context_id)
            render_experimental_details(data, context_id)
            render_biological_summary(data, context_id)
            top_result = render_retrieval_hero(data, context_id)
            if top_result:
                render_why_match(data, context_id, top_result, expanded=True)
            render_evidence_snapshot(data, context_id)
            render_reliability_snapshot(data, context_id)
            with st.expander("Advanced research details", icon=":material/manage_search:"):
                st.caption("Full component, phenotype, and reliability records remain available without changing the demo summary.")
                render_component_explorer(data, context_id)
                render_phenotype(data, context_id)
                render_reliability(data, context_id)
            render_provenance(data, context_id)
        else:
            render_context_card(data, context_id)
            render_response_overview(data, context_id)
            render_component_explorer(data, context_id)
            render_retrieval(data, context_id)
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
    st.markdown('<div class="section-kicker">System boundary</div>', unsafe_allow_html=True)
    st.header("What SkinExo-AI implements")
    st.markdown("""
- **Response Atlas:** implemented — F2, three verified study contexts and 339 stable components.
- **Retrieval:** implemented — R1 mask-aware, interpretable baseline.
- **Explorer:** implemented — A2 product demo mode plus preserved research mode.
- **Predictive AI:** not implemented.
- **Agent:** not implemented.
""")
    st.warning("Only three verified contexts exist. Similarity is descriptive retrieval among observed studies, not prediction or proof of generalization.")
