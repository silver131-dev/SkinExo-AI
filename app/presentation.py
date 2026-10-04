"""Deterministic, UI-neutral presentation helpers for Explorer A2.

All summaries are derived from the frozen Atlas, R1 retrieval output, and
dimension-level reliability records. This module performs no scientific
analysis and has no network or stochastic dependency.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from data_loader import AXIS_NAMES, ExplorerData


AXIS_DISPLAY_NAMES = {
    "P": "Proliferation",
    "M": "Migration",
    "E": "ECM Remodeling",
    "A": "Vascular / Endothelial Interaction",
    "I": "Immune Signaling",
}

ACTIVITY_STATE_LABELS = {
    "ACTIVE_POSITIVE": "Positive",
    "ACTIVE_NEGATIVE": "Negative",
    "OBSERVED_NULL": "Observed null",
    "NOT_TESTED": "Not tested",
    "UNKNOWN": "Unknown",
}

AXIS_STATUS_LABELS = {
    "POSITIVE": "Positive",
    "NEGATIVE": "Negative",
    "POSITIVE_DOMINANT_WITH_OPPOSING_COMPONENTS": "Mixed · positive dominant",
    "NO_QUALIFIED_COMPONENT": "Observed null",
}

STATE_SYMBOLS = {
    "Positive": "↑",
    "Negative": "↓",
    "Mixed · positive dominant": "↕",
    "Observed null": "○",
    "Not tested": "◇",
    "Unknown": "?",
}

SUMMARY_AXIS_NAMES = {
    "P": "Proliferation",
    "M": "Migration",
    "E": "ECM remodeling",
    "A": "Vascular / endothelial interaction",
    "I": "Inflammatory / immune-signaling response",
}


def humanize_activity_state(state: str) -> str:
    """Return a stable human-facing label without changing the stored enum."""

    return ACTIVITY_STATE_LABELS.get(state, state.replace("_", " ").title())


def axis_display_state(data: ExplorerData, context_id: str, axis: str) -> str:
    """Resolve a human-facing axis state while keeping null and untested distinct."""

    row = data.axis_summaries[(context_id, axis)]
    stored_status = row["axis_status"]
    if stored_status != "NO_QUALIFIED_COMPONENT":
        return AXIS_STATUS_LABELS.get(stored_status, stored_status.replace("_", " ").title())

    component_states = {
        record["activity_state"] for record in data.components_for_axis(context_id, axis)
    }
    if "OBSERVED_NULL" in component_states:
        return "Observed null"
    if component_states and component_states <= {"NOT_TESTED"}:
        return "Not tested"
    return "Unknown"


def build_response_signature(data: ExplorerData, context_id: str) -> list[dict[str, Any]]:
    """Build the five-row P/M/E/A/I signature from the frozen axis records."""

    data.validate_context(context_id)
    signature = []
    for axis in "PMEAI":
        row = data.axis_summaries[(context_id, axis)]
        state = axis_display_state(data, context_id, axis)
        signature.append(
            {
                "axis": axis,
                "name": AXIS_DISPLAY_NAMES[axis],
                "framework_name": AXIS_NAMES[axis],
                "state": state,
                "symbol": STATE_SYMBOLS.get(state, "?"),
                "active_count": int(row["active_component_count"]),
                "positive_count": int(row["positive_component_count"]),
                "negative_count": int(row["negative_component_count"]),
                "stored_axis_status": row["axis_status"],
            }
        )
    return signature


def build_context_summary(
    context_id: str,
    data: ExplorerData,
) -> dict[str, Any]:
    """Create the deterministic executive story for one observed context."""

    signature = build_response_signature(data, context_id)
    active = [row for row in signature if row["active_count"] > 0]
    active.sort(key=lambda row: (-row["active_count"], "PMEAI".index(row["axis"])))
    observed_null = [row for row in signature if row["state"] == "Observed null"]
    not_tested = [row for row in signature if row["state"] == "Not tested"]
    ranked = data.retrieve(context_id)
    top = ranked[0] if ranked else None
    reliability_counts = Counter(row["status"] for row in data.reliability(context_id))

    clauses: list[str] = []
    if active:
        largest = active[0]
        clauses.append(
            f"{SUMMARY_AXIS_NAMES[largest['axis']]} is the largest active response family "
            f"({largest['active_count']} active components)"
        )
        if len(active) > 1:
            other_names = [SUMMARY_AXIS_NAMES[row["axis"]] for row in active[1:]]
            if len(other_names) == 1:
                joined = other_names[0]
            elif len(other_names) == 2:
                joined = f"{other_names[0]} and {other_names[1]}"
            else:
                joined = ", ".join(other_names[:-1]) + f", and {other_names[-1]}"
            clauses.append(f"{joined} also show transcriptomic activity")
    if observed_null:
        null_names = [SUMMARY_AXIS_NAMES[row["axis"]] for row in observed_null]
        joined = " and ".join(null_names)
        clauses.append(f"{joined} are observed null")
    if not_tested:
        names = " and ".join(SUMMARY_AXIS_NAMES[row["axis"]] for row in not_tested)
        clauses.append(f"{names} are not tested")

    sentence = "; ".join(clauses) + "." if clauses else "No active response family is recorded."
    if top:
        sentence += f" {top['target']} is the closest observed context."

    return {
        "context_id": context_id,
        "sentence": sentence,
        "signature": signature,
        "largest_active_axis": active[0] if active else None,
        "active_axes": active,
        "observed_null_axes": observed_null,
        "not_tested_axes": not_tested,
        "top_retrieval": top,
        "reliability_counts": dict(sorted(reliability_counts.items())),
        "reliability_dimension_count": sum(reliability_counts.values()),
        "aggregate_confidence_score": False,
    }


def strongest_axis_agreement(result: dict[str, Any]) -> dict[str, Any] | None:
    """Return the largest stored axis-level cosine, without reinterpreting it."""

    candidates = []
    for axis in "PMEAI":
        detail = result["axis_explanations"][axis]
        similarity = detail["axis_NES_cosine"]
        if similarity is not None:
            candidates.append((float(similarity), axis))
    if not candidates:
        return None
    similarity, axis = max(candidates)
    return {
        "axis": axis,
        "name": AXIS_DISPLAY_NAMES[axis],
        "similarity": similarity,
        "shared_tested_components": result["axis_explanations"][axis][
            "shared_tested_components"
        ],
    }
