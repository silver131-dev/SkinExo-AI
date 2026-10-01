"""Reusable Streamlit presentation components for Explorer A1."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd
import streamlit as st

from data_loader import AXIS_NAMES, CONTEXT_LABELS, INTERPRETATIONS, ExplorerData


STATE_COLORS = {
    "ACTIVE_POSITIVE": "#B84C2D",
    "ACTIVE_NEGATIVE": "#2F6F9F",
    "OBSERVED_NULL": "#66707A",
    "NOT_TESTED": "#8B6D3E",
    "UNKNOWN": "#7B5B8E",
}


def _fmt(value, digits=3):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "Insufficient comparable evidence"
    return f"{float(value):+.{digits}f}"


def _component_list(rows, empty="None"):
    if not rows:
        return empty
    return ", ".join(row["component_id"] for row in rows)


def render_context_card(data: ExplorerData, context_id: str):
    card = data.context_card(context_id)
    st.subheader("Experimental Context")
    cols = st.columns(4)
    for index, label in enumerate(["EV source", "Recipient", "Species", "Dataset"]):
        cols[index].metric(label, card[label])
    cols = st.columns(5)
    for index, label in enumerate(["Dose", "Duration", "Sample count", "Study status", "Data status"]):
        cols[index].metric(label, card[label])
    st.warning(f"**Key limitations:** {card['Key limitations']}", icon="⚠️")


def render_response_overview(data: ExplorerData, context_id: str):
    st.subheader("P/M/E/A/I Response Overview")
    columns = st.columns(5)
    for column, row in zip(columns, data.axes_for_context(context_id)):
        with column:
            with st.container(border=True):
                st.markdown(f"### {row['axis']} · {row['axis_name']}")
                status = row["axis_status"].replace("_", " ").title()
                st.markdown(f"**{status}**")
                st.caption(
                    f"{row['active_component_count']} active · "
                    f"{row['positive_component_count']} positive · {row['negative_component_count']} negative"
                )
                if row["phenotype_available"]:
                    st.markdown(f"🟣 **{row['phenotype_anchor_count']} phenotype anchor(s)**")
                else:
                    st.caption("No phenotype anchor registered")


def render_component_explorer(data: ExplorerData, context_id: str):
    st.subheader("Component Explorer")
    axis = st.radio(
        "Select axis",
        options=list(AXIS_NAMES),
        format_func=lambda value: f"{value} · {AXIS_NAMES[value]}",
        horizontal=True,
        key="component_axis",
    )
    components = data.components_for_axis(context_id, axis)
    states = ["ACTIVE_POSITIVE", "ACTIVE_NEGATIVE", "OBSERVED_NULL", "NOT_TESTED", "UNKNOWN"]
    selected_states = st.multiselect("Activity states", states, default=[state for state in states if any(row["activity_state"] == state for row in components)])
    filtered = [row for row in components if row["activity_state"] in selected_states]
    if not filtered:
        st.info("No components match the selected activity states.")
        return
    frame = pd.DataFrame(filtered).rename(columns={
        "component_id": "Component", "component_name": "Name", "activity_state": "Activity state",
        "direction": "Direction", "source_database": "Database", "source_term": "Source term",
        "source_checkpoint": "Checkpoint",
    })
    st.dataframe(
        frame[["Component", "Name", "Activity state", "NES", "FDR", "Direction", "Database", "Source term", "Checkpoint"]],
        hide_index=True, width="stretch", height=min(610, 44 + 35 * len(frame)),
        column_config={
            "NES": st.column_config.NumberColumn(format="%.3f"),
            "FDR": st.column_config.NumberColumn(format="%.3g"),
        },
    )
    st.caption("Blank NES/FDR means NOT_TESTED or UNKNOWN. OBSERVED_NULL retains tested NES/FDR and is not missing evidence.")


def render_axis_comparison(result: dict[str, Any]):
    rows = []
    for axis in "PMEAI":
        detail = result["axis_explanations"][axis]
        rows.append({
            "Axis": f"{axis} · {AXIS_NAMES[axis]}",
            "Similarity": "Insufficient comparable evidence" if detail["axis_NES_cosine"] is None else f"{detail['axis_NES_cosine']:+.3f}",
            "Shared tested": detail["shared_tested_components"],
            "Shared active": detail["shared_active_components"],
            "Same direction": detail["same_direction_components"],
            "Opposite direction": detail["opposite_direction_components"],
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


def render_retrieval(data: ExplorerData, context_id: str):
    st.subheader("Response Similarity")
    st.caption("Mask-aware NES cosine on shared-tested components. This is retrieval among observed contexts, not a prediction score.")
    ranked = data.retrieve(context_id)
    if not ranked:
        st.info("No other contexts are available for retrieval.")
        return
    summary_cols = st.columns(len(ranked))
    for column, result in zip(summary_cols, ranked):
        with column:
            with st.container(border=True):
                st.markdown(f"### Rank {result['rank']} · {result['target']}")
                st.metric("Primary similarity", _fmt(result["primary_similarity"]))
                st.metric("Active-response similarity", _fmt(result["active_similarity"]))
                st.caption(
                    f"{result['shared_tested_components']} shared tested · "
                    f"{result['shared_active_components']} shared active · "
                    f"directional concordance {_fmt(result['directional_concordance'])}"
                )
    target_options = [result["target"] for result in ranked]
    target = st.selectbox("Explain retrieved target", target_options, index=0, format_func=lambda value: CONTEXT_LABELS[value])
    result = next(item for item in ranked if item["target"] == target)
    with st.expander(f"WHY THIS MATCH? · {context_id} vs {target}", expanded=True):
        categories = [
            ("Shared positive components", result["shared_positive_components"]),
            ("Shared negative components", result["shared_negative_components"]),
            ("Discordant components", result["discordant_components"]),
            ("Query-only active components", result["query_only_active"]),
            ("Target-only active components", result["target_only_active"]),
            ("Observed-null differences", result["observed_null_differences"]),
        ]
        for title, rows in categories:
            st.markdown(f"**{title}**")
            if rows:
                frame = pd.DataFrame(rows)
                st.dataframe(
                    frame[["component_id", "axis", "query_state", "target_state", "query_NES", "target_NES", "joint_NES_magnitude"]],
                    hide_index=True, width="stretch",
                )
            else:
                st.caption("None among shared-tested components.")
    st.markdown("#### Compare by axis")
    render_axis_comparison(result)


def render_phenotype(data: ExplorerData, context_id: str):
    st.subheader("Phenotype Evidence")
    st.caption("Phenotype anchors are explanatory evidence and do not enter transcriptomic similarity.")
    anchors = data.phenotype(context_id)
    if not anchors:
        st.info("No phenotype anchors are registered for this context.")
        return
    transcriptome_h = data.atlas.context_features[context_id]["duration_h"]
    for anchor in anchors:
        with st.container(border=True):
            label = "IN VIVO / different model" if anchor["evidence_level"] == "IN_VIVO" else anchor["evidence_level"].replace("_", " ")
            st.markdown(f"**{anchor['axis']} · {anchor['assay']}** — `{label}`")
            cols = st.columns(4)
            cols[0].write(f"**Phenotype:** {anchor['phenotype']}")
            cols[1].write(f"**Time:** {anchor['time']}")
            cols[2].write(f"**Dose:** {anchor['dose']}")
            cols[3].write(f"**Direction:** {anchor['effect_direction']}")
            if anchor["evidence_level"] == "FUNCTIONAL_ASSAY" and anchor["time"].strip() != f"{transcriptome_h} h":
                st.warning(f"Different timepoint: phenotype {anchor['time']} vs transcriptome {transcriptome_h} h.", icon="⏱️")
            st.caption(anchor["limitations"])


def render_reliability(data: ExplorerData, context_id: str):
    st.subheader("Reliability & Limitations")
    st.caption("Dimensions remain separate. No combined reliability percentage is computed.")
    rows = data.reliability(context_id)
    if not rows:
        st.warning("No reliability dimensions are registered for this context.")
        return
    frame = pd.DataFrame([{
        "Dimension": row["dimension"].replace("_", " ").title(),
        "Status": row["status"], "Detail": row["detail"],
    } for row in rows])
    st.dataframe(frame, hide_index=True, width="stretch")


def render_provenance(data: ExplorerData, context_id: str):
    provenance = data.provenance(context_id)
    with st.expander("Evidence Provenance"):
        st.markdown(f"**Dataset:** {provenance['dataset']}")
        st.markdown(f"**Study:** {provenance['study_id']}")
        st.markdown(f"**Source checkpoint:** {provenance['source_checkpoint']}")
        st.markdown(f"**Analysis method:** {provenance['analysis_method']}")
        st.markdown(f"**Gene-set release:** {provenance['gene_set_release']}")
        if provenance["sources"]:
            st.markdown("**Registry sources:**")
            for source in provenance["sources"]:
                st.code(source, language=None)
        if provenance["study_references"]:
            st.markdown("**Phenotype study references:**")
            for reference in provenance["study_references"]:
                st.write(reference)


def render_atlas(data: ExplorerData):
    st.header("Three-Context Response Atlas")
    st.write("Same recipient cell, different EV contexts, different response programs. Therefore, context matters.")
    rows = []
    for context in data.atlas.contexts:
        for axis in "PMEAI":
            source = data.axis_summaries[(context, axis)]
            rows.append({
                "Context": context, "Axis": f"{axis} · {AXIS_NAMES[axis]}",
                "Axis status": source["axis_status"].replace("_", " ").title(),
                "Active components": int(source["active_component_count"]),
                "Positive": int(source["positive_component_count"]),
                "Negative": int(source["negative_component_count"]),
                "Phenotype anchors": int(source["phenotype_anchor_count"]),
                "Three-context interpretation": INTERPRETATIONS[axis],
            })
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=575)
    st.markdown("#### Frozen three-context interpretation")
    cols = st.columns(5)
    for column, axis in zip(cols, "PMEAI"):
        with column:
            with st.container(border=True):
                st.markdown(f"**{axis} · {AXIS_NAMES[axis]}**")
                st.write(INTERPRETATIONS[axis])
    st.info("Broad universal EV response: **NOT SUPPORTED**")


def render_similarity(data: ExplorerData):
    st.header("Context Similarity")
    st.caption("Descriptive retrieval baseline; n = 3 contexts. No predictive validation.")
    metric = st.radio("Similarity view", ["Primary mask-aware cosine", "Active-union cosine"], horizontal=True)
    field = "primary_similarity" if metric.startswith("Primary") else "active_similarity"
    contexts = list(data.atlas.contexts)
    table = pd.DataFrame(index=contexts, columns=contexts, dtype=float)
    for query in contexts:
        table.loc[query, query] = 1.0
        for result in data.retrieve(query):
            table.loc[query, result["target"]] = result[field]
    st.dataframe(table.style.format("{:+.4f}").background_gradient(cmap="RdBu_r", vmin=-1, vmax=1), width="stretch")
    rows = []
    for query, target in [("CTX001", "CTX002"), ("CTX001", "CTX003"), ("CTX002", "CTX003")]:
        result = next(item for item in data.retrieve(query) if item["target"] == target)
        rows.append({
            "Pair": f"{query} ↔ {target}", "Primary": result["primary_similarity"],
            "Active union": result["active_similarity"], "Shared tested": result["shared_tested_components"],
            "Shared active": result["shared_active_components"],
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
