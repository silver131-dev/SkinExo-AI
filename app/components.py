"""Reusable Streamlit presentation components for Explorer A1."""

from __future__ import annotations

import html
import math
from typing import Any

import pandas as pd
import streamlit as st

from data_loader import AXIS_NAMES, CONTEXT_LABELS, INTERPRETATIONS, ExplorerData


STATE_MARKERS = {
    "ACTIVE_POSITIVE": ("↑", "state-positive"),
    "ACTIVE_NEGATIVE": ("↓", "state-negative"),
    "OBSERVED_NULL": ("∅", "state-null"),
    "NOT_TESTED": ("◇", "state-not-tested"),
    "UNKNOWN": ("?", "state-not-tested"),
}

AXIS_STATUS_MARKERS = {
    "POSITIVE": ("↑", "state-positive"),
    "NEGATIVE": ("↓", "state-negative"),
    "NO_QUALIFIED_COMPONENT": ("∅", "state-null"),
    "POSITIVE_DOMINANT_WITH_OPPOSING_COMPONENTS": ("↕", "state-mixed"),
}


def _fmt(value, digits=3):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "Insufficient comparable evidence"
    return f"{float(value):+.{digits}f}"


def _component_list(rows, empty="None"):
    if not rows:
        return empty
    return ", ".join(row["component_id"] for row in rows)


def _clean(value: Any) -> str:
    return html.escape(str(value))


def _state_label(state: str) -> str:
    marker = STATE_MARKERS.get(state, ("?", "state-not-tested"))[0]
    return f"{marker} {state}"


def _evidence_row(data: ExplorerData, row: dict[str, Any], relation: str) -> str:
    component_id = row["component_id"]
    name = data.universe.get(component_id, {}).get("component_name", component_id)
    query_nes = _fmt(row.get("query_NES"))
    target_nes = _fmt(row.get("target_NES"))
    return (
        '<div class="evidence-row">'
        f'<strong>{_clean(component_id)} · {_clean(name)}</strong><br>'
        f'<span class="evidence-meta">{_clean(relation)} · axis {_clean(row.get("axis", ""))} · '
        f'query {_clean(row.get("query_state", ""))} ({_clean(query_nes)}) · '
        f'target {_clean(row.get("target_state", ""))} ({_clean(target_nes)})</span>'
        '</div>'
    )


def _render_evidence_group(data: ExplorerData, title: str, rows: list[dict[str, Any]], relation: str) -> None:
    st.markdown(f"**{title}**")
    if not rows:
        st.caption("None among shared-tested components.")
        return
    for row in rows:
        st.markdown(_evidence_row(data, row, relation), unsafe_allow_html=True)


def render_context_card(data: ExplorerData, context_id: str):
    card = data.context_card(context_id)
    st.markdown(f'<div class="section-kicker">Selected context · {_clean(context_id)}</div>', unsafe_allow_html=True)
    st.subheader(CONTEXT_LABELS.get(context_id, context_id))
    st.caption("Experimental conditions remain part of the evidence. Missing metadata stays visible.")
    cols = st.columns(4)
    for index, label in enumerate(["EV source", "Recipient", "Species", "Dataset"]):
        cols[index].metric(label, card[label])
    cols = st.columns(5)
    for index, label in enumerate(["Dose", "Duration", "Sample count", "Study status", "Data status"]):
        cols[index].metric(label, card[label])
    st.warning(f"**Key limitations · retained in interpretation:** {card['Key limitations']}", icon="⚠️")


def render_response_overview(data: ExplorerData, context_id: str):
    st.markdown('<div class="section-kicker">Response profile</div>', unsafe_allow_html=True)
    st.subheader("P/M/E/A/I Response Overview")
    st.caption("Status is encoded with text and symbols as well as color. Axis summaries do not replace component evidence.")
    columns = st.columns(5)
    for column, row in zip(columns, data.axes_for_context(context_id)):
        with column:
            with st.container(border=True):
                marker, style = AXIS_STATUS_MARKERS.get(row["axis_status"], ("?", "state-not-tested"))
                st.markdown(
                    f'<span class="axis-letter">{_clean(row["axis"])}</span>'
                    f'<strong>{_clean(row["axis_name"])}</strong>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<span class="evidence-badge {style}">{marker} '
                    f'{_clean(row["axis_status"])}</span>',
                    unsafe_allow_html=True,
                )
                st.caption(
                    f"{row['active_component_count']} active · "
                    f"{row['positive_component_count']} positive · {row['negative_component_count']} negative"
                )
                if row["phenotype_available"]:
                    st.markdown(f"◆ **{row['phenotype_anchor_count']} phenotype anchor(s)**")
                else:
                    st.caption("◇ No phenotype anchor registered")


def render_component_explorer(data: ExplorerData, context_id: str):
    st.markdown('<div class="section-kicker">Component-level evidence</div>', unsafe_allow_html=True)
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
    st.markdown(
        " ".join(
            f'<span class="evidence-badge {STATE_MARKERS[state][1]}">{_state_label(state)}</span>'
            for state in states
        ),
        unsafe_allow_html=True,
    )
    if not filtered:
        st.info("No components match the selected activity states.")
        return
    frame = pd.DataFrame(filtered)
    frame["state_marker"] = frame["activity_state"].map(_state_label)
    frame = frame.rename(columns={
        "component_id": "Component", "component_name": "Name", "activity_state": "Activity state",
        "state_marker": "State marker",
        "direction": "Direction", "source_database": "Database", "source_term": "Source term",
        "source_checkpoint": "Checkpoint",
    })
    st.dataframe(
        frame[["Component", "Name", "State marker", "Activity state", "NES", "FDR", "Direction", "Database", "Source term", "Checkpoint"]],
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
    st.markdown('<div class="section-kicker">Interpretable retrieval</div>', unsafe_allow_html=True)
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
                st.markdown(f'<div class="rank-kicker">Rank {result["rank"]} · retrieved context</div>', unsafe_allow_html=True)
                st.markdown(f"### {result['target']}")
                st.caption(CONTEXT_LABELS[result["target"]].split(" · ", 1)[-1])
                st.metric("Response similarity", _fmt(result["primary_similarity"], 4))
                st.metric("Active-response similarity", _fmt(result["active_similarity"], 4))
                st.caption(
                    f"{result['shared_tested_components']} shared tested · "
                    f"{result['shared_active_components']} shared active · "
                    f"directional concordance {_fmt(result['directional_concordance'])}"
                )
    target_options = [result["target"] for result in ranked]
    target = st.selectbox("Explain retrieved target", target_options, index=0, format_func=lambda value: CONTEXT_LABELS[value])
    result = next(item for item in ranked if item["target"] == target)
    with st.expander(f"WHY THIS MATCH? · {context_id} vs {target}", expanded=False):
        st.markdown("#### Shared response components")
        shared_cols = st.columns(2)
        with shared_cols[0]:
            _render_evidence_group(data, "↑ Shared positive", result["shared_positive_components"], "same positive direction")
        with shared_cols[1]:
            _render_evidence_group(data, "↓ Shared negative", result["shared_negative_components"], "same negative direction")

        st.markdown("#### Where the contexts differ")
        difference_cols = st.columns(2)
        with difference_cols[0]:
            _render_evidence_group(data, "↕ Discordant components", result["discordant_components"], "opposite active direction")
            _render_evidence_group(data, f"◌ {context_id}-only active", result["query_only_active"], "query-only activity")
        with difference_cols[1]:
            _render_evidence_group(data, f"◌ {target}-only active", result["target_only_active"], "target-only activity")
            _render_evidence_group(data, "∅ Observed-null differences", result["observed_null_differences"], "active versus observed null")

        st.markdown("#### Phenotype evidence · attached, not scored")
        phenotype_columns = st.columns(2)
        for column, label in zip(phenotype_columns, ("query", "target")):
            anchors = result["phenotype_anchors"].get(label, [])
            with column:
                st.markdown(f"**{result[label]}**")
                if anchors:
                    for anchor in anchors:
                        st.markdown(
                            f'<span class="evidence-badge state-not-tested">◆ '
                            f'{_clean(anchor.get("axis", ""))} · {_clean(anchor.get("assay", "Phenotype anchor"))}</span>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.caption("No phenotype anchors registered.")

        st.markdown("#### Reliability · visible, not scored")
        reliability_columns = st.columns(2)
        for column, context, rows in zip(
            reliability_columns,
            (context_id, target),
            (result["reliability_query"], result["reliability_target"]),
        ):
            with column:
                st.markdown(f"**{context}**")
                for row in rows:
                    st.markdown(
                        f'<div class="evidence-row"><strong>{_clean(row["dimension"].replace("_", " ").title())}</strong> '
                        f'<span class="evidence-badge state-not-tested">{_clean(row["status"])}</span></div>',
                        unsafe_allow_html=True,
                    )
        for limitation in result["limitations"]:
            st.caption(f"◇ {limitation}")
    st.markdown("#### Compare by axis")
    render_axis_comparison(result)


def render_phenotype(data: ExplorerData, context_id: str):
    st.markdown('<div class="section-kicker">Separate evidence layer</div>', unsafe_allow_html=True)
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
            st.markdown(f"**◆ {anchor['axis']} · {anchor['assay']}** — `{label}`")
            cols = st.columns(4)
            cols[0].write(f"**Phenotype:** {anchor['phenotype']}")
            cols[1].write(f"**Time:** {anchor['time']}")
            cols[2].write(f"**Dose:** {anchor['dose']}")
            cols[3].write(f"**Direction:** {anchor['effect_direction']}")
            if anchor["evidence_level"] == "FUNCTIONAL_ASSAY" and anchor["time"].strip() != f"{transcriptome_h} h":
                st.warning(f"Different timepoint: phenotype {anchor['time']} vs transcriptome {transcriptome_h} h.", icon="⏱️")
            st.caption(anchor["limitations"])


def render_reliability(data: ExplorerData, context_id: str):
    st.markdown('<div class="section-kicker">Interpretation boundary</div>', unsafe_allow_html=True)
    st.subheader("Reliability & Limitations")
    st.caption("Dimensions remain separate. No combined reliability percentage is computed.")
    rows = data.reliability(context_id)
    if not rows:
        st.warning("No reliability dimensions are registered for this context.")
        return
    columns = st.columns(3)
    for index, row in enumerate(rows):
        with columns[index % 3]:
            with st.container(border=True):
                st.markdown(f"**{row['dimension'].replace('_', ' ').title()}**")
                st.markdown(
                    f'<span class="evidence-badge state-not-tested">◇ {_clean(row["status"])}</span>',
                    unsafe_allow_html=True,
                )
                st.caption(row["detail"])


def render_provenance(data: ExplorerData, context_id: str):
    provenance = data.provenance(context_id)
    with st.expander("Evidence Provenance"):
        st.caption("Trace every displayed interpretation to its public dataset and frozen analysis checkpoint.")
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
    st.markdown('<div class="section-kicker">Three verified study contexts</div>', unsafe_allow_html=True)
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
                st.markdown(f'<span class="axis-letter">{axis}</span><strong>{AXIS_NAMES[axis]}</strong>', unsafe_allow_html=True)
                st.write(INTERPRETATIONS[axis])
    st.info("Broad universal EV response: **NOT SUPPORTED**")


def render_similarity(data: ExplorerData):
    st.markdown('<div class="section-kicker">R1 descriptive baseline</div>', unsafe_allow_html=True)
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
    st.dataframe(table.style.format("{:+.4f}"), width="stretch")
    rows = []
    for query, target in [("CTX001", "CTX002"), ("CTX001", "CTX003"), ("CTX002", "CTX003")]:
        result = next(item for item in data.retrieve(query) if item["target"] == target)
        rows.append({
            "Pair": f"{query} ↔ {target}", "Primary": result["primary_similarity"],
            "Active union": result["active_similarity"], "Shared tested": result["shared_tested_components"],
            "Shared active": result["shared_active_components"],
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
