"""Interpretable, mask-aware retrieval for the SkinExo F2 Response Atlas.

The module never imputes NOT_TESTED or UNKNOWN as zero. Phenotype anchors and
reliability records are returned as explanations and never enter similarity.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np


ACTIVITY_STATES = {"ACTIVE_POSITIVE", "ACTIVE_NEGATIVE", "OBSERVED_NULL", "NOT_TESTED", "UNKNOWN"}
ACTIVE_STATES = {"ACTIVE_POSITIVE", "ACTIVE_NEGATIVE"}
AXES = "PMEAI"


@dataclass(frozen=True)
class AtlasData:
    root: Path
    atlas_version: str
    contexts: tuple[str, ...]
    components: tuple[str, ...]
    component_axis: dict[str, str]
    records: dict[tuple[str, str], dict[str, str]]
    phenotype_anchors: dict[str, list[dict[str, str]]]
    reliability: dict[str, list[dict[str, str]]]
    context_features: dict[str, dict[str, str]]


@dataclass(frozen=True)
class ResponseMatrix:
    contexts: tuple[str, ...]
    components: tuple[str, ...]
    component_axis: np.ndarray
    values: np.ndarray
    tested_mask: np.ndarray
    active_mask: np.ndarray
    states: np.ndarray

    def context_index(self, context_id: str) -> int:
        if context_id not in self.contexts:
            raise KeyError(f"Unknown context: {context_id}")
        return self.contexts.index(context_id)


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def load_atlas(root: str | Path) -> AtlasData:
    """Load and minimally validate the F2 Atlas from a repository root."""
    root = Path(root).resolve()
    validation_path = root / "outputs/framework/framework_f2_validation.json"
    manifest_path = root / "outputs/framework/framework_f2_atlas.json"
    validation = json.loads(validation_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    if validation.get("status") != "PASS":
        raise RuntimeError("F2 validation must PASS before retrieval")
    if manifest.get("atlas_version") != "F2-2026-10-01":
        raise RuntimeError("Unsupported Atlas version")
    universe = _csv_rows(root / "data/metadata/skinexo_component_universe.csv")
    context_rows = _csv_rows(root / "data/metadata/skinexo_context_features.csv")
    response_rows = _csv_rows(root / "data/metadata/skinexo_response_atlas_long.csv")
    anchor_rows = _csv_rows(root / "data/metadata/skinexo_phenotype_anchors.csv")
    reliability_rows = _csv_rows(root / "data/metadata/skinexo_reliability.csv")
    contexts = tuple(row["context_id"] for row in context_rows)
    components = tuple(row["component_id"] for row in universe)
    if len(set(contexts)) != len(contexts) or len(set(components)) != len(components):
        raise RuntimeError("Duplicate context or component identifiers")
    component_axis = {row["component_id"]: row["axis"] for row in universe}
    records = {(row["context_id"], row["component_id"]): row for row in response_rows}
    expected = {(context, component) for context in contexts for component in components}
    if set(records) != expected:
        raise RuntimeError("Atlas context-component grid is incomplete")
    for record in response_rows:
        if record["activity_state"] not in ACTIVITY_STATES:
            raise RuntimeError(f"Invalid activity state: {record['activity_state']}")
    phenotype = {context: [] for context in contexts}
    for row in anchor_rows:
        phenotype.setdefault(row["context_id"], []).append(row)
    reliability = {context: [] for context in contexts}
    for row in reliability_rows:
        reliability.setdefault(row["context_id"], []).append(row)
    for context in contexts:
        phenotype[context] = sorted(phenotype[context], key=lambda row: row["anchor_id"])
        reliability[context] = sorted(reliability[context], key=lambda row: row["dimension"])
    return AtlasData(
        root=root, atlas_version=manifest["atlas_version"], contexts=contexts,
        components=components, component_axis=component_axis, records=records,
        phenotype_anchors=phenotype, reliability=reliability,
        context_features={row["context_id"]: row for row in context_rows},
    )


def build_response_matrix(atlas: AtlasData) -> ResponseMatrix:
    """Construct aligned NES, tested, active, and state matrices."""
    shape = (len(atlas.contexts), len(atlas.components))
    values = np.full(shape, np.nan, dtype=float)
    tested = np.zeros(shape, dtype=bool)
    active = np.zeros(shape, dtype=bool)
    states = np.empty(shape, dtype=object)
    for i, context in enumerate(atlas.contexts):
        for j, component in enumerate(atlas.components):
            record = atlas.records[(context, component)]
            states[i, j] = record["activity_state"]
            tested[i, j] = record["tested_mask"] == "1"
            active[i, j] = record["active_mask"] == "1"
            if tested[i, j]:
                values[i, j] = float(record["NES"])
            elif record["NES"] != "":
                raise RuntimeError(f"Missing-state record has NES: {context}/{component}")
    if np.any(tested & ~np.isfinite(values)) or np.any(~tested & np.isfinite(values)):
        raise RuntimeError("Response values do not align with tested mask")
    return ResponseMatrix(
        contexts=atlas.contexts, components=atlas.components,
        component_axis=np.array([atlas.component_axis[c] for c in atlas.components], dtype=object),
        values=values, tested_mask=tested, active_mask=active, states=states,
    )


def compute_shared_tested_mask(tested_a: np.ndarray, tested_b: np.ndarray) -> np.ndarray:
    """Return features tested in both contexts."""
    a = np.asarray(tested_a, dtype=bool)
    b = np.asarray(tested_b, dtype=bool)
    if a.shape != b.shape:
        raise ValueError("Tested masks must have identical shape")
    return a & b


def masked_cosine_similarity(
    vector_a: np.ndarray,
    vector_b: np.ndarray,
    shared_mask: np.ndarray,
    *,
    minimum_overlap: int = 1,
) -> dict[str, Any]:
    """Cosine over an explicit shared mask; undefined results remain None."""
    a = np.asarray(vector_a, dtype=float)
    b = np.asarray(vector_b, dtype=float)
    mask = np.asarray(shared_mask, dtype=bool)
    if a.shape != b.shape or a.shape != mask.shape:
        raise ValueError("Vectors and mask must have identical shape")
    count = int(mask.sum())
    if count < minimum_overlap:
        return {"similarity": None, "component_count": count, "status": "INSUFFICIENT_OVERLAP"}
    selected_a, selected_b = a[mask], b[mask]
    if not np.all(np.isfinite(selected_a)) or not np.all(np.isfinite(selected_b)):
        raise ValueError("Masked values must be finite; missing data cannot enter cosine")
    denominator = float(np.linalg.norm(selected_a) * np.linalg.norm(selected_b))
    if denominator == 0:
        return {"similarity": None, "component_count": count, "status": "ZERO_NORM"}
    similarity = float(np.dot(selected_a, selected_b) / denominator)
    similarity = max(-1.0, min(1.0, similarity))
    return {"similarity": similarity, "component_count": count, "status": "DEFINED"}


def active_union_similarity(
    vector_a: np.ndarray,
    vector_b: np.ndarray,
    tested_a: np.ndarray,
    tested_b: np.ndarray,
    active_a: np.ndarray,
    active_b: np.ndarray,
) -> dict[str, Any]:
    """Cosine over mutually tested features active in either context."""
    shared_tested = compute_shared_tested_mask(tested_a, tested_b)
    union = shared_tested & (np.asarray(active_a, dtype=bool) | np.asarray(active_b, dtype=bool))
    result = masked_cosine_similarity(vector_a, vector_b, union, minimum_overlap=1)
    return {"similarity": result["similarity"], "component_count": int(union.sum()), "status": result["status"], "mask": union}


def directional_concordance(
    states_a: np.ndarray,
    states_b: np.ndarray,
    tested_a: np.ndarray,
    tested_b: np.ndarray,
) -> dict[str, Any]:
    """Compare direction only where both contexts have an active component."""
    state_a = np.asarray(states_a, dtype=object)
    state_b = np.asarray(states_b, dtype=object)
    shared_tested = compute_shared_tested_mask(tested_a, tested_b)
    active_a = np.isin(state_a, list(ACTIVE_STATES))
    active_b = np.isin(state_b, list(ACTIVE_STATES))
    shared = shared_tested & active_a & active_b
    same = int(np.sum(shared & (state_a == state_b)))
    opposite = int(np.sum(shared & (state_a != state_b)))
    total = same + opposite
    return {
        "shared_active_components": total, "same_direction_active": same,
        "opposite_direction_active": opposite,
        "directional_concordance": None if total == 0 else float(same / total),
        "status": "UNDEFINED_NO_SHARED_ACTIVE" if total == 0 else "DEFINED",
        "mask": shared,
    }


def axis_similarity(matrix: ResponseMatrix, context_a: str, context_b: str, axis: str) -> dict[str, Any]:
    """Return mask-aware similarity and active-direction counts for one axis."""
    if axis not in AXES:
        raise ValueError(f"Invalid axis: {axis}")
    ia, ib = matrix.context_index(context_a), matrix.context_index(context_b)
    axis_mask = matrix.component_axis == axis
    shared = compute_shared_tested_mask(matrix.tested_mask[ia], matrix.tested_mask[ib]) & axis_mask
    cosine = masked_cosine_similarity(matrix.values[ia], matrix.values[ib], shared, minimum_overlap=2)
    direction = directional_concordance(
        matrix.states[ia, axis_mask], matrix.states[ib, axis_mask],
        matrix.tested_mask[ia, axis_mask], matrix.tested_mask[ib, axis_mask],
    )
    return {
        "axis": axis, "shared_tested_components": int(shared.sum()),
        "shared_active_components": direction["shared_active_components"],
        "same_direction_components": direction["same_direction_active"],
        "opposite_direction_components": direction["opposite_direction_active"],
        "axis_NES_cosine": cosine["similarity"], "status": cosine["status"],
    }


def _component_record(atlas: AtlasData, matrix: ResponseMatrix, query: str, target: str, index: int) -> dict[str, Any]:
    iq, it = matrix.context_index(query), matrix.context_index(target)
    component = matrix.components[index]
    return {
        "component_id": component, "axis": atlas.component_axis[component],
        "query_state": str(matrix.states[iq, index]), "target_state": str(matrix.states[it, index]),
        "query_NES": None if not matrix.tested_mask[iq, index] else float(matrix.values[iq, index]),
        "target_NES": None if not matrix.tested_mask[it, index] else float(matrix.values[it, index]),
        "joint_NES_magnitude": float(abs(matrix.values[iq, index]) + abs(matrix.values[it, index])),
        "query_term": atlas.records[(query, component)]["representative_term_id"],
        "target_term": atlas.records[(target, component)]["representative_term_id"],
    }


def _rank_records(atlas, matrix, query, target, indices: Iterable[int], limit=10):
    values = [_component_record(atlas, matrix, query, target, int(index)) for index in indices]
    return sorted(values, key=lambda row: (-row["joint_NES_magnitude"], row["component_id"]))[:limit]


def explain_pair(atlas: AtlasData, matrix: ResponseMatrix, query: str, target: str, *, limit: int = 10) -> dict[str, Any]:
    """Create deterministic component, phenotype, and reliability explanations."""
    if query == target:
        raise ValueError("Query and target must differ")
    iq, it = matrix.context_index(query), matrix.context_index(target)
    shared_tested = compute_shared_tested_mask(matrix.tested_mask[iq], matrix.tested_mask[it])
    primary = masked_cosine_similarity(matrix.values[iq], matrix.values[it], shared_tested, minimum_overlap=2)
    active = active_union_similarity(
        matrix.values[iq], matrix.values[it], matrix.tested_mask[iq], matrix.tested_mask[it],
        matrix.active_mask[iq], matrix.active_mask[it],
    )
    direction = directional_concordance(
        matrix.states[iq], matrix.states[it], matrix.tested_mask[iq], matrix.tested_mask[it]
    )
    q_state, t_state = matrix.states[iq], matrix.states[it]
    q_active = matrix.active_mask[iq]
    t_active = matrix.active_mask[it]
    shared_positive = np.flatnonzero(shared_tested & (q_state == "ACTIVE_POSITIVE") & (t_state == "ACTIVE_POSITIVE"))
    shared_negative = np.flatnonzero(shared_tested & (q_state == "ACTIVE_NEGATIVE") & (t_state == "ACTIVE_NEGATIVE"))
    discordant = np.flatnonzero(shared_tested & q_active & t_active & (q_state != t_state))
    query_only = np.flatnonzero(shared_tested & q_active & ~t_active)
    target_only = np.flatnonzero(shared_tested & ~q_active & t_active)
    null_differences = np.flatnonzero(shared_tested & ((q_state == "OBSERVED_NULL") ^ (t_state == "OBSERVED_NULL")))
    axis_details = {axis: axis_similarity(matrix, query, target, axis) for axis in AXES}
    limitations = [
        "Similarity uses transcriptomic NES only; phenotype and reliability are attached but unscored",
        "Only three verified contexts exist; ranks are a descriptive demonstration, not predictive validation",
        "Shared-tested masks differ by pair; missing/not-tested components are excluded rather than imputed",
        atlas.context_features[query]["major_limitations"],
        atlas.context_features[target]["major_limitations"],
    ]
    return {
        "query": query, "target": target,
        "primary_similarity": primary["similarity"], "primary_status": primary["status"],
        "shared_tested_components": int(shared_tested.sum()),
        "active_similarity": active["similarity"], "active_similarity_status": active["status"],
        "active_union_components": active["component_count"],
        "shared_active_components": direction["shared_active_components"],
        "same_direction_active": direction["same_direction_active"],
        "opposite_direction_active": direction["opposite_direction_active"],
        "directional_concordance": direction["directional_concordance"],
        "shared_positive_components": _rank_records(atlas, matrix, query, target, shared_positive, limit),
        "shared_negative_components": _rank_records(atlas, matrix, query, target, shared_negative, limit),
        "discordant_components": _rank_records(atlas, matrix, query, target, discordant, limit),
        "query_only_active": _rank_records(atlas, matrix, query, target, query_only, limit),
        "target_only_active": _rank_records(atlas, matrix, query, target, target_only, limit),
        "observed_null_differences": _rank_records(atlas, matrix, query, target, null_differences, limit),
        "axis_explanations": axis_details,
        "phenotype_anchors": {
            "query": atlas.phenotype_anchors.get(query, []),
            "target": atlas.phenotype_anchors.get(target, []),
        },
        "reliability_query": atlas.reliability.get(query, []),
        "reliability_target": atlas.reliability.get(target, []),
        "limitations": limitations,
    }


def retrieve_contexts(atlas: AtlasData, matrix: ResponseMatrix, query: str) -> list[dict[str, Any]]:
    """Rank every other known context by primary mask-aware cosine."""
    matrix.context_index(query)
    results = [explain_pair(atlas, matrix, query, target) for target in matrix.contexts if target != query]
    results.sort(key=lambda row: (
        row["primary_similarity"] is None,
        -(row["primary_similarity"] if row["primary_similarity"] is not None else -float("inf")),
        row["target"],
    ))
    for rank, row in enumerate(results, 1):
        row["rank"] = rank
    return results
