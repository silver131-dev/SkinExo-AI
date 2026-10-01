#!/usr/bin/env python3
"""Validate the F2 three-context response atlas without altering source results."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
META = ROOT / "data/metadata"
OUT = ROOT / "outputs/framework/framework_f2_validation.json"
AXES = set("PMEAI")
STATES = {"ACTIVE_POSITIVE", "ACTIVE_NEGATIVE", "OBSERVED_NULL", "NOT_TESTED", "UNKNOWN"}
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def rows(path):
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        check(bool(reader.fieldnames), f"{path.name}: missing header")
        return list(reader), list(reader.fieldnames or [])


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split(value):
    return [item for item in str(value).split(";") if item]


contexts, _ = rows(META / "skinexo_contexts.csv")
features, _ = rows(META / "skinexo_context_features.csv")
universe, _ = rows(META / "skinexo_component_universe.csv")
atlas, _ = rows(META / "skinexo_response_atlas_long.csv")
matrix, matrix_fields = rows(META / "skinexo_response_matrix.csv")
axes, _ = rows(META / "skinexo_axis_summary.csv")
source_components, _ = rows(META / "skinexo_response_components.csv")
anchors, _ = rows(META / "skinexo_phenotype_anchors.csv")
reliability, _ = rows(META / "skinexo_reliability.csv")
cargo, _ = rows(META / "skinexo_cargo_datasets.csv")
manifest = json.loads((ROOT / "outputs/framework/framework_f2_atlas.json").read_text())

context_ids = {row["context_id"] for row in contexts}
check(context_ids == {"CTX001", "CTX002", "CTX003"}, "atlas must contain exactly CTX001/002/003")
check(len(contexts) == 3 and all(row["study_status"] == "VERIFIED" and row["data_status"] == "ANALYZED" for row in contexts), "three contexts must be unique, verified, and analyzed")
check(len(features) == 3 and {row["context_id"] for row in features} == context_ids, "context feature table does not cover three contexts")
for row in features:
    check(bool(row["ev_source"] and row["recipient"] and row["major_limitations"]), f"{row['context_id']}: incomplete context features")
    check(row["study_independence"] == "VERIFIED", f"{row['context_id']}: study independence not verified")
    check("UNKNOWN" in row["ev_preparation_status"], f"{row['context_id']}: EV-preparation uncertainty lost")

component_ids = [row["component_id"] for row in universe]
check(len(universe) == 339 and len(set(component_ids)) == 339, "component universe must contain 339 unique IDs")
check({row["axis"] for row in universe} == AXES, "component universe axis vocabulary mismatch")
for row in universe:
    check(row["component_id"].startswith(row["axis"]), f"{row['component_id']}: axis prefix mismatch")
    check(row["status"] == "FROZEN_F2", f"{row['component_id']}: component is not frozen F2")
    for field in ("component_name", "source_database", "source_term_id", "source_term_name", "definition"):
        check(bool(row[field]), f"{row['component_id']}: missing {field}")

source_by_key = {(row["context_id"], row["component_id"]): row for row in source_components}
check(len(source_by_key) == 3 * 339, "source component grid is incomplete or duplicated")
universe_by_id = {row["component_id"]: row for row in universe}
for (context, component), source in source_by_key.items():
    check(context in context_ids and component in universe_by_id, f"{context}/{component}: invalid source reference")
    check(source["axis"] == universe_by_id[component]["axis"], f"{context}/{component}: axis mismatch")
    check(source["mapped_term_ids"] == universe_by_id[component]["source_term_id"], f"{context}/{component}: universe term mapping changed")

atlas_keys = [(row["context_id"], row["component_id"]) for row in atlas]
check(len(atlas) == 1017 and len(set(atlas_keys)) == len(atlas_keys), "duplicate or missing context-component Atlas records")
check(set(atlas_keys) == {(context, component) for context in context_ids for component in component_ids}, "Atlas is not the complete context-component product")
anchor_by_id = {row["anchor_id"]: row for row in anchors}
reliability_by_id = {row["reliability_id"]: row for row in reliability}
counts = Counter()
atlas_by_key = {}
for row in atlas:
    key = (row["context_id"], row["component_id"])
    atlas_by_key[key] = row
    state = row["activity_state"]
    counts[state] += 1
    check(row["context_id"] in context_ids and row["component_id"] in universe_by_id, f"{key}: invalid context/component")
    check(row["axis"] == universe_by_id.get(row["component_id"], {}).get("axis"), f"{key}: invalid axis")
    check(state in STATES, f"{key}: invalid activity state")
    check(row["evidence_layer"] == "TRANSCRIPTOME", f"{key}: invalid evidence layer")
    check(bool(row["source_checkpoint"] and row["provenance"]), f"{key}: missing provenance")
    source = source_by_key.get(key)
    evidence = json.loads(source["term_evidence_json"]) if source else []
    tested = [item for item in evidence if item.get("eligible", True) and item.get("NES") is not None and item.get("FDR") is not None]
    if row["tested_mask"] == "1":
        try:
            nes, fdr = float(row["NES"]), float(row["FDR"])
            check(-1e-15 <= fdr <= 1.0, f"{key}: FDR outside [0,1]")
            check(any(item["term_id"] == row["representative_term_id"] and abs(float(item["NES"]) - nes) < 1e-12 and abs(float(item["FDR"]) - fdr) < 1e-12 for item in tested), f"{key}: representative statistics differ from frozen evidence")
        except ValueError:
            errors.append(f"{key}: tested record lacks numeric NES/FDR")
        check(state in {"ACTIVE_POSITIVE", "ACTIVE_NEGATIVE", "OBSERVED_NULL"}, f"{key}: tested record has missing state")
    else:
        check(row["NES"] == row["FDR"] == row["representative_term_id"] == "", f"{key}: untested/unknown record has numeric evidence")
        check(state in {"NOT_TESTED", "UNKNOWN"}, f"{key}: untested mask/state mismatch")
    if state == "OBSERVED_NULL":
        check(source and source["evidence_status"] == "OBSERVED_NULL" and bool(tested), f"{key}: observed null is not a tested source null")
        check(row["active_mask"] == "0", f"{key}: observed null marked active")
    elif state == "NOT_TESTED":
        check(source and not tested, f"{key}: NOT_TESTED has source test evidence")
    elif state.startswith("ACTIVE_"):
        expected_direction = state.removeprefix("ACTIVE_")
        check(source and source["evidence_status"] == "QUALIFIED" and source["direction"] == expected_direction, f"{key}: active state differs from frozen component")
        check(row["direction"] == expected_direction and row["active_mask"] == "1", f"{key}: active masks/direction invalid")
    for anchor_id in split(row["phenotype_anchor"]):
        anchor = anchor_by_id.get(anchor_id)
        check(anchor is not None, f"{key}: missing phenotype anchor {anchor_id}")
        if anchor:
            check(anchor["context_id"] == row["context_id"] and anchor["axis"] == row["axis"], f"{key}: phenotype link crosses context/axis")
    references = split(row["reliability_reference"])
    check(len(references) == 13 and len(set(references)) == 13, f"{key}: reliability vector incomplete")
    for reference in references:
        rel = reliability_by_id.get(reference)
        check(rel is not None and rel["context_id"] == row["context_id"], f"{key}: invalid reliability reference {reference}")

schema_text = (ROOT / "docs/framework/ATLAS_SCHEMA.md").read_text()
check("OBSERVED_NULL" in schema_text and "UNKNOWN" in schema_text and "NOT_TESTED" in schema_text, "missingness states are not documented distinctly")
check(counts["OBSERVED_NULL"] > 0 and counts["UNKNOWN"] == 0, "current analyzed Atlas null/unknown counts are inconsistent")

check(len(matrix) == 3 and matrix_fields == ["context_id"] + component_ids, "wide response matrix schema mismatch")
for matrix_row in matrix:
    context = matrix_row["context_id"]
    for component in component_ids:
        try:
            cell = json.loads(matrix_row[component])
            record = atlas_by_key[(context, component)]
            check(cell["activity_state"] == record["activity_state"] and cell["tested_mask"] == int(record["tested_mask"]) and cell["active_mask"] == int(record["active_mask"]), f"{context}/{component}: matrix/long mismatch")
            expected_nes = None if record["NES"] == "" else float(record["NES"])
            expected_fdr = None if record["FDR"] == "" else float(record["FDR"])
            check(cell["NES"] == expected_nes and cell["FDR"] == expected_fdr, f"{context}/{component}: matrix statistics mismatch")
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f"{context}/{component}: invalid matrix cell: {exc}")

check(len(axes) == 15 and {(row["context_id"], row["axis"]) for row in axes} == {(context, axis) for context in context_ids for axis in AXES}, "axis summary grid incomplete")
for row in axes:
    records = [item for item in atlas if item["context_id"] == row["context_id"] and item["axis"] == row["axis"]]
    positive = sum(item["activity_state"] == "ACTIVE_POSITIVE" for item in records)
    negative = sum(item["activity_state"] == "ACTIVE_NEGATIVE" for item in records)
    check(int(row["positive_component_count"]) == positive and int(row["negative_component_count"]) == negative and int(row["active_component_count"]) == positive + negative, f"{row['context_id']}/{row['axis']}: axis counts mismatch")
    check(bool(row["reliability_notes"] and row["source_checkpoint"]), f"{row['context_id']}/{row['axis']}: axis provenance incomplete")

check(atlas_by_key[("CTX001", "P081")]["activity_state"] == "ACTIVE_POSITIVE", "P081 is not active positive in CTX001")
check(atlas_by_key[("CTX002", "P081")]["activity_state"] == "ACTIVE_POSITIVE", "P081 is not active positive in CTX002")
check(atlas_by_key[("CTX003", "P081")]["activity_state"] == "OBSERVED_NULL", "P081 CTX003 null not preserved")
active_i = {context: {row["component_id"] for row in atlas if row["context_id"] == context and row["axis"] == "I" and row["active_mask"] == "1"} for context in context_ids}
check(bool(active_i["CTX002"] & active_i["CTX003"]), "CTX002/CTX003 inflammatory component sharing lost")
check(not (active_i["CTX001"] & active_i["CTX002"] & active_i["CTX003"]), "unsupported three-context inflammatory component conservation")

check(manifest.get("framework_version") == "F2" and manifest.get("atlas_version") == "F2-2026-10-01", "manifest version mismatch")
expected_manifest = {
    "contexts": 3, "verified_contexts": 3, "axes": 5, "component_count": 339,
    "response_records": 1017, "tested_response_records": 1010,
    "observed_null_records": 852, "not_tested_records": 7, "unknown_records": 0,
    "phenotype_anchor_count": 5, "reliability_record_count": 39,
}
for field, value in expected_manifest.items():
    check(manifest.get(field) == value, f"manifest {field} mismatch")
check(set(manifest.get("activity_states", [])) == STATES, "manifest activity vocabulary mismatch")
check(manifest.get("P_interpretation") == "TWO_CONTEXT_SHARED_COMPONENT", "P interpretation changed")
check(manifest.get("M_interpretation") == "CONTEXT_DEPENDENT_DISCORDANT" and manifest.get("A_interpretation") == "CONTEXT_DEPENDENT_DISCORDANT", "M/A interpretation changed")
check(manifest.get("E_interpretation") == "NULL_NOT_TESTABLE" and manifest.get("I_interpretation") == "CONSERVED_AXIS_CONTEXT_VARIANT", "E/I interpretation changed")
check(manifest.get("broad_universal_EV_response") == "NOT_SUPPORTED", "universal response overclaimed")
check(manifest.get("retrieval_status") == manifest.get("explorer_status") == manifest.get("predictive_AI_status") == "NOT_IMPLEMENTED", "future capability overclaimed")
source_paths = {"contexts": META / "skinexo_contexts.csv", "components": META / "skinexo_response_components.csv", "responses": META / "skinexo_responses.csv", "reliability": META / "skinexo_reliability.csv"}
for label, path in source_paths.items():
    check(manifest.get("source_hashes", {}).get(label) == sha256(path), f"manifest source hash mismatch: {label}")

check(len(cargo) == 1 and cargo[0]["cargo_dataset_id"] == "GSE293957" and cargo[0]["data_status"] == "AVAILABLE_NOT_ANALYZED" and cargo[0]["causal_link_status"] == "NONE", "GSE293957 cargo boundary violated")
leaks = [str(path.relative_to(ROOT)) for path in (ROOT / "outputs").rglob("*") if path.is_file() and "293957" in path.name]
check(not leaks, f"GSE293957 analysis output leakage: {leaks}")

for path in [
    ROOT / "submission/figures/fig08_context_aware_response_atlas.png",
    ROOT / "submission/figures/fig09_skinexo_platform_architecture.png",
    ROOT / "reports/FRAMEWORK_F2_three_context_response_atlas.md",
]:
    check(path.exists() and path.stat().st_size > 0, f"missing/empty artifact: {path.name}")

result = {
    "status": "PASS" if not errors else "FAIL",
    "framework_version": "F2", "atlas_version": "F2-2026-10-01",
    "counts": {
        "contexts": len(contexts), "components": len(universe), "response_records": len(atlas),
        "tested_response_records": sum(row["tested_mask"] == "1" for row in atlas),
        "activity_states": dict(sorted(counts.items())), "axis_summaries": len(axes),
        "phenotype_anchors": len(anchors), "reliability_records": len(reliability),
    },
    "checks": {
        "no_fourth_context": context_ids == {"CTX001", "CTX002", "CTX003"},
        "null_unknown_distinct": "OBSERVED_NULL" in STATES and "UNKNOWN" in STATES,
        "GSE293957_analysis_leakage": "NONE" if not leaks else leaks,
        "retrieval_implemented": False,
    },
    "errors": errors,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
sys.exit(0 if not errors else 1)
