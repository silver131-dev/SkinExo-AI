"""Reusable Streamlit presentation components for Explorer A1."""

from __future__ import annotations

import html
import math
from collections import Counter
from typing import Any

import pandas as pd
import streamlit as st

from data_loader import AXIS_NAMES, CONTEXT_LABELS, INTERPRETATIONS, ExplorerData
from presentation import (
    AXIS_DISPLAY_NAMES,
    axis_display_state,
    build_context_summary,
    build_response_signature,
    humanize_activity_state,
    strongest_axis_agreement,
)


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
    return f"{marker} {humanize_activity_state(state)}"


def _context_title(context_id: str) -> str:
    return CONTEXT_LABELS.get(context_id, context_id).split(" · ", 1)[-1]


def _display_dose(value: str) -> str:
    """Shorten a documented dose for the context hero without changing its meaning."""

    clean = value.replace("ug/mL", "µg/mL")
    return clean.split(" by BCA", 1)[0].split(" (", 1)[0]


def _reliability_label(value: str) -> str:
    labels = {
        "VERIFIED": "Verified",
        "SUPPORTED": "Supported",
        "UNKNOWN": "Unknown",
        "NOT_DOCUMENTED": "Not documented",
        "NO_EVIDENCE": "Not documented",
        "LIMITED": "Limited",
        "NOT_APPLICABLE": "Not applicable",
    }
    return labels.get(value, value.replace("_", " ").title())


def _dimension_label(value: str) -> str:
    labels = {
        "study_independence": "Study independence",
        "recipient_donor_independence": "Recipient donor",
        "ev_preparation_independence": "EV preparation",
        "batch_adjustment": "Batch",
        "pairing_certainty": "Pairing",
        "control_certainty": "Control definition",
        "sample_qc": "Sample QC",
        "model_diagnostics": "Model diagnostics",
        "phenotype_support": "Phenotype timing",
    }
    return labels.get(value, value.replace("_", " ").title())


def render_product_hero() -> None:
    with st.container(border=True, key="product_hero"):
        st.markdown('<div class="skinexo-eyebrow">SkinExo Lab · Evidence-led computational biology</div>', unsafe_allow_html=True)
        st.title("SkinExo-AI")
        st.markdown(
            '<div class="product-value">Find experimentally observed EV contexts<br>'
            'with similar biological responses.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="skinexo-support">Component-level evidence · phenotype anchors · explicit reliability</div>',
            unsafe_allow_html=True,
        )


def render_product_journey() -> None:
    steps = ["Context", "Response", "Retrieve", "Explain", "Evidence"]
    content = '<span class="journey-arrow" aria-hidden="true">→</span>'.join(
        f'<span class="journey-step">{step}</span>' for step in steps
    )
    st.markdown(
        f'<nav class="product-journey" aria-label="Explorer journey">{content}</nav>',
        unsafe_allow_html=True,
    )


def render_context_hero(data: ExplorerData, context_id: str) -> None:
    details = data.context_details(context_id)
    st.markdown('<div id="context" class="anchor-target"></div>', unsafe_allow_html=True)
    with st.container(border=True, key="context_hero"):
        left, right = st.columns([2.2, 1], vertical_alignment="center")
        with left:
            st.markdown(f'<div class="section-kicker">Selected observed context</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="context-id">{_clean(context_id)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="context-route">{_clean(_context_title(context_id))}</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="context-condition"><strong>{_clean(_display_dose(details["Dose"]))}</strong>'
                f'<span>{_clean(details["Duration"])}</span><span>n = {_clean(details["Sample count"])}</span></div>',
                unsafe_allow_html=True,
            )
        with right:
            st.markdown(
                f'<div class="context-dataset">{_clean(details["Dataset"])}</div>'
                f'<div class="status-pair"><span>{_clean(details["Study status"].title())}</span>'
                f'<span>{_clean(details["Data status"].title())}</span></div>',
                unsafe_allow_html=True,
            )


def render_experimental_details(data: ExplorerData, context_id: str) -> None:
    details = data.context_details(context_id)
    with st.expander("Experimental details", icon=":material/science:", type="compact"):
        fields = [
            "Species", "Dataset", "Dose", "Duration", "Sample count", "Study status",
            "Data status", "Treatment / control", "Batch", "Pairing", "Recipient donor",
            "EV preparation", "Experimental system", "Omics", "Statistical design",
        ]
        rows = "".join(
            f'<div class="detail-row"><span>{_clean(label)}</span><strong>{_clean(details[label])}</strong></div>'
            for label in fields
        )
        st.markdown(f'<div class="detail-list">{rows}</div>', unsafe_allow_html=True)
        st.caption(f"Key limitations: {details['Key limitations']}")


def render_biological_summary(data: ExplorerData, context_id: str) -> None:
    summary = build_context_summary(context_id, data)
    st.markdown('<div id="response" class="anchor-target"></div>', unsafe_allow_html=True)
    left, right = st.columns([1.04, 1.2], gap="medium")
    with left:
        with st.container(border=True, height="stretch", key="biological_summary"):
            st.markdown('<div class="section-kicker">Biological summary</div>', unsafe_allow_html=True)
            st.markdown(f'<p class="summary-copy">{_clean(summary["sentence"])}</p>', unsafe_allow_html=True)
            top = summary["top_retrieval"]
            if top:
                st.markdown(
                    f'<div class="summary-retrieval"><span>Most similar observed context</span>'
                    f'<strong>{_clean(top["target"])} · {_clean(_fmt(top["primary_similarity"], 4))}</strong></div>',
                    unsafe_allow_html=True,
                )
            counts = summary["reliability_counts"]
            caveat = " · ".join(
                f"{count} {_reliability_label(status).lower()}" for status, count in counts.items()
            )
            st.caption(f"Reliability considerations · {summary['reliability_dimension_count']} dimensions · {caveat}")
    with right:
        render_response_signature(data, context_id)


def render_response_signature(data: ExplorerData, context_id: str) -> None:
    rows = []
    for item in build_response_signature(data, context_id):
        css_state = {
            "Positive": "positive",
            "Negative": "negative",
            "Mixed · positive dominant": "mixed",
            "Observed null": "null",
            "Not tested": "not-tested",
            "Unknown": "unknown",
        }.get(item["state"], "unknown")
        count = f' · {item["active_count"]} active' if item["active_count"] else ""
        microcopy = ""
        if item["state"] == "Observed null":
            microcopy = '<small>No component met the pre-specified activity criteria.</small>'
        rows.append(
            f'<div class="signature-row signature-{css_state}">'
            f'<span class="signature-symbol">{_clean(item["symbol"])}</span>'
            f'<span class="signature-name"><strong>{_clean(item["name"])}</strong>'
            f'<small>{_clean(item["axis"])}</small></span>'
            f'<span class="signature-state">{_clean(item["state"] + count)}</span>{microcopy}</div>'
        )
    st.markdown(
        '<section class="signature-card"><div class="section-kicker">Primary findings · response signature</div>'
        + "".join(rows)
        + '<div class="signature-legend">Symbols, text, counts, and border patterns encode state; color is supplementary.</div></section>',
        unsafe_allow_html=True,
    )


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


def render_retrieval_hero(data: ExplorerData, context_id: str) -> dict[str, Any] | None:
    ranked = data.retrieve(context_id)
    if not ranked:
        st.info("No other observed contexts are available for retrieval.")
        return None
    result = ranked[0]
    st.markdown('<div id="retrieve" class="anchor-target"></div>', unsafe_allow_html=True)
    with st.container(border=True, key="retrieval_hero"):
        st.markdown('<div class="section-kicker">Most similar observed context</div>', unsafe_allow_html=True)
        identity, metric = st.columns([1.55, 0.75], gap="large", vertical_alignment="center")
        with identity:
            st.markdown(f'<div class="retrieval-context">{_clean(result["target"])}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="retrieval-route">{_clean(_context_title(result["target"]))}</div>', unsafe_allow_html=True)
            st.caption("Retrieved from experimentally observed contexts; descriptive, not predictive.")
        with metric:
            st.markdown('<div class="retrieval-metric-label">Response similarity</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="retrieval-value">{_clean(_fmt(result["primary_similarity"], 4))}</div>', unsafe_allow_html=True)
            st.caption("Mask-aware NES cosine across jointly tested response components.")
        cards = st.columns(3)
        values = [
            (str(result["shared_active_components"]), "Shared active components", "Shared activity only"),
            (f'{result["directional_concordance"] * 100:.0f}%', "Direction agreement", "Among shared active components"),
            (_fmt(result["active_similarity"], 4), "Active-union similarity", "Cosine; not a percentage"),
        ]
        for column, (value, label, note) in zip(cards, values):
            with column:
                st.markdown(
                    f'<div class="retrieval-evidence-card"><strong>{_clean(value)}</strong>'
                    f'<span>{_clean(label)}</span><small>{_clean(note)}</small></div>',
                    unsafe_allow_html=True,
                )
    return result


def _component_names(data: ExplorerData, rows: list[dict[str, Any]], limit: int = 4) -> list[str]:
    return [
        data.universe.get(row["component_id"], {}).get("component_name", row["component_id"])
        for row in rows[:limit]
    ]


def render_why_match(
    data: ExplorerData,
    context_id: str,
    result: dict[str, Any],
    *,
    expanded: bool,
) -> None:
    target = result["target"]
    shared_rows = result["shared_positive_components"] + result["shared_negative_components"]
    strongest = strongest_axis_agreement(result)
    st.markdown('<div id="explain" class="anchor-target"></div>', unsafe_allow_html=True)
    if expanded:
        panel = st.container(border=True, key=f"why_{context_id}_{target}_demo")
    else:
        panel = st.expander(
            f"WHY THIS MATCH? · {context_id} and {target}",
            expanded=False,
            icon=":material/hub:",
            key=f"why_{context_id}_{target}_research",
        )
    with panel:
        if expanded:
            st.markdown('<div class="section-kicker">Why this match?</div>', unsafe_allow_html=True)
        st.markdown(
            f'<p class="why-lead"><strong>{_clean(context_id)} and {_clean(target)} share '
            f'{result["shared_active_components"]} active response components with the same direction of activity.</strong></p>',
            unsafe_allow_html=True,
        )
        if strongest:
            st.caption(
                f"Their closest stored axis-level NES agreement is {strongest['name']} "
                f"({_fmt(strongest['similarity'], 4)} across {strongest['shared_tested_components']} jointly tested components)."
            )
        st.caption(
            "A shared broad response axis does not imply that every active component is conserved. "
            "The component evidence below makes that distinction explicit."
        )

        shared, direction, differences = st.columns([1.2, 0.8, 1], gap="medium")
        with shared:
            st.markdown("**Shared response programs**")
            names = _component_names(data, shared_rows)
            if names:
                for name in names:
                    st.markdown(f'<div class="program-chip">↑ {_clean(name)}</div>', unsafe_allow_html=True)
                if len(shared_rows) > len(names):
                    st.caption(f"+ {len(shared_rows) - len(names)} more shared active components")
            else:
                st.caption("No shared active response component.")
        with direction:
            st.markdown("**Directional agreement**")
            st.markdown(
                f'<div class="why-number">{result["directional_concordance"] * 100:.0f}%</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                f'{result["same_direction_active"]} same direction · '
                f'{result["opposite_direction_active"]} opposite direction'
            )
        with differences:
            st.markdown("**Context-specific evidence**")
            st.markdown(
                f'<div class="difference-line"><strong>{len(result["query_only_active"])}</strong> {_clean(context_id)}-specific active</div>'
                f'<div class="difference-line"><strong>{len(result["target_only_active"])}</strong> {_clean(target)}-specific active</div>'
                f'<div class="difference-line"><strong>{len(result["observed_null_differences"])}</strong> active / observed-null differences</div>',
                unsafe_allow_html=True,
            )

        st.caption(
            f"Phenotype anchors: {len(result['phenotype_anchors'].get('query', []))} for {context_id}, "
            f"{len(result['phenotype_anchors'].get('target', []))} for {target}; attached for interpretation, not scored."
        )

    with st.expander("Inspect component-level explanation", icon=":material/table_view:", type="compact"):
        st.markdown("#### Shared response components")
        shared_cols = st.columns(2)
        with shared_cols[0]:
            _render_evidence_group(data, "↑ Shared positive", result["shared_positive_components"], "same positive direction")
        with shared_cols[1]:
            _render_evidence_group(data, "↓ Shared negative", result["shared_negative_components"], "same negative direction")
        st.markdown("#### Context-specific and observed-null differences")
        difference_cols = st.columns(2)
        with difference_cols[0]:
            _render_evidence_group(data, f"{context_id}-specific active", result["query_only_active"], "query-only activity")
            _render_evidence_group(data, "Discordant active", result["discordant_components"], "opposite active direction")
        with difference_cols[1]:
            _render_evidence_group(data, f"{target}-specific active", result["target_only_active"], "target-only activity")
            _render_evidence_group(data, "Observed-null differences", result["observed_null_differences"], "active versus observed null")
        st.markdown("#### Axis-level similarity")
        render_axis_comparison(result)


def render_evidence_snapshot(data: ExplorerData, context_id: str) -> None:
    st.markdown('<div id="evidence" class="anchor-target"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">Evidence snapshot</div>', unsafe_allow_html=True)
    st.subheader("Evidence remains layered")
    transcriptome_h = data.atlas.context_features[context_id]["duration_h"]
    anchors = data.phenotype(context_id)
    cck8 = next((row for row in anchors if row["assay"].lower() == "cck-8"), None)
    scratch = next((row for row in anchors if "scratch" in row["assay"].lower()), None)
    transcriptomic, phenotype, reliability = st.columns(3, gap="medium")
    with transcriptomic:
        with st.container(border=True, height="stretch"):
            st.markdown("**Transcriptomic evidence**")
            st.markdown(f'<div class="snapshot-time">{_clean(transcriptome_h)} h</div>', unsafe_allow_html=True)
            st.caption("Bulk RNA-seq response; component states and NES values drive retrieval.")
    with phenotype:
        with st.container(border=True, height="stretch"):
            st.markdown("**Related phenotype anchors**")
            if cck8:
                st.markdown(f'CCK-8 · **{_clean(cck8["time"]) }**')
            if scratch:
                st.markdown(f'Scratch assay · **{_clean(scratch["time"]) }**')
            if not cck8 and not scratch:
                st.caption("No directly related functional-assay anchors registered.")
            else:
                st.caption("Different experimental timepoint · explanatory evidence, not a causal link.")
    with reliability:
        with st.container(border=True, height="stretch"):
            st.markdown("**Reliability context**")
            rows = data.reliability(context_id)
            status_counts = Counter(row["status"] for row in rows)
            st.markdown(f'<div class="snapshot-time">{len(rows)}</div>', unsafe_allow_html=True)
            st.caption("Dimensions reviewed separately; no aggregate score.")
            st.caption(" · ".join(f"{count} {_reliability_label(status).lower()}" for status, count in sorted(status_counts.items())))


def render_reliability_snapshot(data: ExplorerData, context_id: str) -> None:
    st.markdown('<div id="reliability" class="anchor-target"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">Reliability snapshot</div>', unsafe_allow_html=True)
    st.subheader("Uncertainty stays visible")
    rows = data.reliability(context_id)
    focus_dimensions = [
        "study_independence", "recipient_donor_independence", "ev_preparation_independence",
        "batch_adjustment", "pairing_certainty", "control_certainty", "sample_qc",
        "model_diagnostics", "phenotype_support",
    ]
    by_dimension = {row["dimension"]: row for row in rows}
    cards = []
    for dimension in focus_dimensions:
        row = by_dimension.get(dimension)
        if not row:
            continue
        state = row["status"].lower().replace("_", "-")
        cards.append(
            f'<div class="reliability-item reliability-{_clean(state)}">'
            f'<span>{_clean(_dimension_label(dimension))}</span>'
            f'<strong>{_clean(_reliability_label(row["status"]))}</strong>'
            f'<small>{_clean(row["detail"])}</small></div>'
        )
    st.markdown(f'<div class="reliability-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
    st.caption("Unknown, not documented, and unresolved evidence are preserved intentionally; they are not treated as biological zero.")
    with st.expander("View all reliability dimensions", icon=":material/fact_check:", type="compact"):
        for row in rows:
            st.markdown(
                f'<div class="detail-row"><span>{_clean(_dimension_label(row["dimension"]))}</span>'
                f'<strong>{_clean(_reliability_label(row["status"]))}</strong></div>',
                unsafe_allow_html=True,
            )
            st.caption(row["detail"])


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
    with st.expander("Reliability considerations", icon=":material/info:", type="compact"):
        st.caption(card["Key limitations"])


def render_response_overview(data: ExplorerData, context_id: str):
    st.markdown('<div class="section-kicker">Response profile</div>', unsafe_allow_html=True)
    st.subheader("P/M/E/A/I response overview")
    st.caption("Status is encoded with text and symbols as well as color. Axis summaries do not replace component evidence.")
    columns = st.columns(5)
    for column, row in zip(columns, data.axes_for_context(context_id)):
        with column:
            with st.container(border=True):
                marker, style = AXIS_STATUS_MARKERS.get(row["axis_status"], ("?", "state-not-tested"))
                display_status = axis_display_state(data, context_id, row["axis"])
                st.markdown(
                    f'<strong class="axis-name">{_clean(AXIS_DISPLAY_NAMES[row["axis"]])}</strong>'
                    f'<span class="axis-letter">{_clean(row["axis"])}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<span class="evidence-badge {style}">{marker} '
                    f'{_clean(display_status)}</span>',
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
    st.subheader("Component explorer")
    axis = st.segmented_control(
        "Select axis",
        options=list(AXIS_NAMES),
        format_func=lambda value: f"{value} · {AXIS_NAMES[value]}",
        default="P",
        required=True,
        key="component_axis",
    )
    components = data.components_for_axis(context_id, axis)
    states = ["ACTIVE_POSITIVE", "ACTIVE_NEGATIVE", "OBSERVED_NULL", "NOT_TESTED", "UNKNOWN"]
    selected_states = st.multiselect(
        "Activity states",
        states,
        default=[state for state in states if any(row["activity_state"] == state for row in components)],
        format_func=humanize_activity_state,
    )
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
                "Axis status": axis_display_state(data, context, axis),
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
    contexts = list(data.atlas.contexts)
    query = st.selectbox(
        "Query context",
        contexts,
        index=contexts.index("CTX003") if "CTX003" in contexts else 0,
        format_func=lambda value: CONTEXT_LABELS[value],
        key="similarity_query",
    )
    top = data.retrieve(query)[0]
    cols = st.columns([0.8, 1.25, 0.75])
    cols[0].metric("Query", query)
    cols[1].metric("Top observed match", f"{top['target']} · {_context_title(top['target'])}")
    cols[2].metric("Response similarity", _fmt(top["primary_similarity"], 4))
    st.caption(
        f"WHY: {top['shared_active_components']} shared active components · "
        f"{top['directional_concordance'] * 100:.0f}% directional agreement. "
        "Open Context Explorer for the component-level explanation."
    )
    with st.expander("Advanced similarity matrix", icon=":material/grid_view:", expanded=False):
        metric = st.segmented_control(
            "Similarity view",
            ["Primary mask-aware cosine", "Active-union cosine"],
            default="Primary mask-aware cosine",
            required=True,
            key="similarity_metric",
        )
        field = "primary_similarity" if metric.startswith("Primary") else "active_similarity"
        table = pd.DataFrame(index=contexts, columns=contexts, dtype=float)
        for row_query in contexts:
            table.loc[row_query, row_query] = 1.0
            for result in data.retrieve(row_query):
                table.loc[row_query, result["target"]] = result[field]
        st.dataframe(table.style.format("{:+.4f}"), width="stretch")
        rows = []
        for first, target in [("CTX001", "CTX002"), ("CTX001", "CTX003"), ("CTX002", "CTX003")]:
            result = next(item for item in data.retrieve(first) if item["target"] == target)
            rows.append({
                "Pair": f"{first} ↔ {target}", "Primary": result["primary_similarity"],
                "Active union": result["active_similarity"], "Shared tested": result["shared_tested_components"],
                "Shared active": result["shared_active_components"],
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
