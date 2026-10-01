#!/usr/bin/env python3
"""Validate F1 registry integrity against its schemas and frozen C4 endpoint."""

import csv
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
META = ROOT / "data/metadata"
OUT = ROOT / "outputs/framework/framework_f1_validation.json"
AXES = set("PMEAI")
LAYERS = {"TRANSCRIPTOME", "FUNCTIONAL_ASSAY", "IN_VIVO", "CARGO", "LITERATURE", "SENSITIVITY"}
STATES = {"CONSERVED_COMPONENT", "CONSERVED_AXIS", "CONTEXT_DEPENDENT", "DISCORDANT", "NULL_NOT_TESTABLE", "SENSITIVITY_DEPENDENT", "UNKNOWN"}
LOCAL_EVIDENCE = {"QUALIFIED", "OBSERVED_NULL", "UNKNOWN"}
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def rows(name):
    with (META / name).open(newline="") as handle:
        reader = csv.DictReader(handle)
        check(bool(reader.fieldnames), f"{name}: missing header")
        return list(reader)


def unique(items, label):
    counts = Counter(items)
    check(all(value and count == 1 for value, count in counts.items()), f"{label}: blank or duplicate identifier")


def provenance(value, label):
    check(bool(value.strip()), f"{label}: missing provenance")
    for part in value.split(";"):
        part = part.strip()
        check(bool(part), f"{label}: empty provenance entry")
        if part and not part.startswith(("https://", "http://", "DOI:", "PMID:")) and not part.startswith("Liu et al."):
            check((ROOT / part).exists(), f"{label}: missing local source {part}")


contexts = rows("skinexo_contexts.csv")
responses = rows("skinexo_responses.csv")
components = rows("skinexo_response_components.csv")
comparisons = rows("skinexo_context_comparisons.csv")
anchors = rows("skinexo_phenotype_anchors.csv")
cargo = rows("skinexo_cargo_datasets.csv")
reliability = rows("skinexo_reliability.csv")
manifest = json.loads((ROOT / "outputs/framework/framework_f1.json").read_text())
with (ROOT / "outputs/exp002/c4_axes_exp001_vs_primary.csv").open(newline="") as handle:
    frozen = list(csv.DictReader(handle))
frozen_by_axis = {row["axis"]: row for row in frozen}

unique([r["context_id"] for r in contexts], "context IDs")
unique([r["response_id"] for r in responses], "response IDs")
unique([r["component_entry_id"] for r in components], "component entry IDs")
unique([r["comparison_id"] for r in comparisons], "comparison IDs")
unique([r["anchor_id"] for r in anchors], "anchor IDs")
unique([r["cargo_dataset_id"] for r in cargo], "cargo dataset IDs")
unique([r["reliability_id"] for r in reliability], "reliability IDs")
context_ids = {r["context_id"] for r in contexts}
context_by_id = {r["context_id"]: r for r in contexts}
ctx003_analyzed = context_by_id.get("CTX003", {}).get("study_status") == "VERIFIED"
response_keys = [(r["context_id"], r["axis"]) for r in responses]
unique([f"{a}:{b}" for a, b in response_keys], "context-axis response keys")
check(context_ids == {"CTX001", "CTX002", "CTX003"}, "context registry must contain CTX001/002/003")

for row in contexts:
    cid = row["context_id"]
    check(row["study_status"] in {"VERIFIED", "PLANNED", "EXCLUDED"}, f"{cid}: invalid study status")
    check(row["data_status"] in {"ANALYZED", "AVAILABLE_NOT_ANALYZED", "METADATA_ONLY", "UNAVAILABLE"}, f"{cid}: invalid data status")
    check(row["evidence_status"] in {"FROZEN_C4", "UNKNOWN"}, f"{cid}: invalid context evidence status")
    provenance(row["source_provenance"], cid)
    for field in ("dataset_id", "study_id", "species", "recipient_cell", "ev_source_cell", "duration_h", "treatment", "control", "major_limitations"):
        check(bool(row[field]), f"{cid}: missing {field}")
    if cid == "CTX003":
        if ctx003_analyzed:
            check(row["study_status"] == "VERIFIED" and row["data_status"] == "ANALYZED" and row["evidence_status"] == "FROZEN_C4", "CTX003: analyzed context status is inconsistent")
        else:
            check(row["study_status"] == "PLANNED" and row["data_status"] == "AVAILABLE_NOT_ANALYZED" and row["evidence_status"] == "UNKNOWN", "CTX003: planned context status is inconsistent")

component_by_key = {(r["context_id"], r["component_id"]): r for r in components}
ctx003_gsea = {}
if ctx003_analyzed:
    with (ROOT / "outputs/exp003/c4_gsea_all.csv").open(newline="") as handle:
        ctx003_gsea = {row["term_id"]: row for row in csv.DictReader(handle)}
for row in components:
    key = row["component_entry_id"]
    check(row["context_id"] in context_ids and row["axis"] in AXES and row["component_id"].startswith(row["axis"]), f"{key}: invalid context/axis/component")
    check(row["evidence_status"] in LOCAL_EVIDENCE and row["evidence_layer"] in LAYERS, f"{key}: invalid evidence")
    check(row["evidence_layer"] == "TRANSCRIPTOME", f"{key}: component must be transcriptomic")
    check(bool(row["mapped_term_ids"]) and bool(row["source_checkpoint"]), f"{key}: missing mapped terms or checkpoint")
    try:
        evidence = json.loads(row["term_evidence_json"])
        check(isinstance(evidence, list) and bool(evidence), f"{key}: missing term evidence")
        qualified = {e["term_id"] for e in evidence if e["qualified"]}
        check(qualified == set(filter(None, row["qualified_term_ids"].split(";"))), f"{key}: qualified-term mismatch")
        check((row["evidence_status"] == "QUALIFIED") == bool(qualified), f"{key}: evidence status mismatch")
        if row["context_id"] == "CTX003" and ctx003_analyzed:
            check(row["source_checkpoint"] == "EXP003-C4", f"{key}: wrong CTX003 checkpoint")
            for term in evidence:
                result = ctx003_gsea.get(term["term_id"])
                if term.get("eligible"):
                    check(result is not None, f"{key}: eligible term absent from CTX003 GSEA")
                    if result is not None:
                        check(abs(float(term["NES"]) - float(result["NES"])) < 1e-12 and abs(float(term["FDR"]) - float(result["FDR"])) < 1e-12, f"{key}: CTX003 term evidence differs from GSEA")
                        expected_qualified = float(result["FDR"]) < 0.05 and result["leading_edge_coherent"] == "True"
                        check(bool(term["qualified"]) == expected_qualified, f"{key}: CTX003 qualification rule mismatch")
                else:
                    check(result is None and not term["qualified"], f"{key}: ineligible CTX003 term has result/qualification")
    except (ValueError, KeyError, TypeError) as exc:
        errors.append(f"{key}: invalid term evidence: {exc}")

if ctx003_analyzed:
    component_ids_by_context = {cid: {r["component_id"] for r in components if r["context_id"] == cid} for cid in context_ids}
    check(all(len(ids) == 339 for ids in component_ids_by_context.values()), "analyzed component grid must have 339 IDs per context")
    check(len({frozenset(ids) for ids in component_ids_by_context.values()}) == 1, "component vocabulary differs across analyzed contexts")
else:
    check(all(r["context_id"] in {"CTX001", "CTX002"} for r in components), "planned context component leakage")

for row in responses:
    rid, cid, axis = row["response_id"], row["context_id"], row["axis"]
    check(cid in context_ids and axis in AXES, f"{rid}: invalid context or axis")
    check(row["evidence_status"] in LOCAL_EVIDENCE and row["evidence_layer"] in LAYERS, f"{rid}: invalid evidence status/layer")
    check(row["evidence_layer"] == "TRANSCRIPTOME" and bool(row["source_checkpoint"]), f"{rid}: missing transcriptome layer or checkpoint")
    if cid == "CTX003" and not ctx003_analyzed:
        check(row["evidence_status"] == "UNKNOWN" and row["direction"] == "UNKNOWN" and row["source_checkpoint"] == "PLANNED_EXP003", f"{rid}: CTX003 transcriptomic state leakage")
        for field in ("NES", "FDR", "representative_term_id", "key_terms", "component_ids", "leading_edge_genes"):
            check(row[field] == "", f"{rid}: CTX003 {field} must be blank")
    else:
        expected_checkpoint = {"CTX001": "EXP001-C4", "CTX002": "EXP002-C4", "CTX003": "EXP003-C4"}[cid]
        check(row["source_checkpoint"] == expected_checkpoint, f"{rid}: wrong frozen checkpoint")
        component_ids = set(filter(None, row["component_ids"].split(";")))
        expected = {c["component_id"] for c in components if c["context_id"] == cid and c["axis"] == axis and c["evidence_status"] == "QUALIFIED"}
        check(component_ids == expected, f"{rid}: active component IDs differ from component table")
        qualified = {t for c in components if c["context_id"] == cid and c["axis"] == axis for t in c["qualified_term_ids"].split(";") if t}
        check(set(filter(None, row["key_terms"].split(";"))) == qualified, f"{rid}: qualified terms differ from component table")
        check((row["evidence_status"] == "QUALIFIED") == bool(expected), f"{rid}: response evidence status mismatch")
        check(bool(row["NES"]) == bool(expected) and bool(row["FDR"]) == bool(expected), f"{rid}: numeric presence mismatch")
        if row["representative_term_id"]:
            check(row["representative_term_id"] in qualified, f"{rid}: representative term not qualified")

check(set(response_keys) == {(cid, axis) for cid in context_ids for axis in AXES}, "response grid must cover three contexts and five axes")

expected_states = {"P": "CONSERVED_COMPONENT", "M": "DISCORDANT", "E": "NULL_NOT_TESTABLE", "A": "DISCORDANT", "I": "CONSERVED_AXIS"}
expected_pairs = {("CTX001", "CTX002")}
if ctx003_analyzed:
    expected_pairs |= {("CTX001", "CTX003"), ("CTX002", "CTX003")}
check(len(comparisons) == 5 * len(expected_pairs), "comparison grid does not cover every analyzed pair/axis")
for row in comparisons:
    axis = row["axis"]
    pair = (row["context_a"], row["context_b"])
    check(axis in AXES and pair in expected_pairs, f"{row['comparison_id']}: invalid comparison context/axis")
    check(row["framework_state"] in STATES, f"{row['comparison_id']}: invalid framework state")
    if pair == ("CTX001", "CTX002"):
        check(row["framework_state"] == expected_states.get(axis), f"{axis}: invalid frozen F1 state")
        check(row["prior_c4_status"] == frozen_by_axis[axis]["outcome"], f"{axis}: frozen C4 status changed")
    elif ctx003_analyzed:
        expected_new = {
            ("CTX001", "CTX003"): {"P": "NULL_NOT_TESTABLE", "M": "DISCORDANT", "E": "NULL_NOT_TESTABLE", "A": "DISCORDANT", "I": "CONSERVED_AXIS"},
            ("CTX002", "CTX003"): {"P": "NULL_NOT_TESTABLE", "M": "CONSERVED_AXIS", "E": "NULL_NOT_TESTABLE", "A": "CONSERVED_AXIS", "I": "CONSERVED_COMPONENT"},
        }
        check(row["framework_state"] == expected_new[pair][axis] and row["source_checkpoint"] == "EXP003-C4", f"{row['comparison_id']}: CTX003 comparison differs from frozen C4")
    check(bool(row["source_checkpoint"]) and bool(row["limitations"]), f"{axis}: missing comparison provenance/limits")
check({(r["context_a"], r["context_b"], r["axis"]) for r in comparisons} == {(a, b, axis) for a, b in expected_pairs for axis in AXES}, "comparison axes/pairs incomplete")
f1_pair = {(r["context_a"], r["context_b"], r["axis"]): r for r in comparisons}
check(f1_pair[("CTX001", "CTX002", "P")]["shared_component"] == "P081", "P shared component must be P081")
check(f1_pair[("CTX001", "CTX002", "I")]["shared_component"] == "NONE", "I must not claim shared active component")
for row in comparisons:
    for token in filter(None, row["shared_component"].split(";")):
        if token == "NONE":
            continue
        component_id = token.removesuffix("_OPPOSITE_DIRECTION")
        check((row["context_a"], component_id) in component_by_key and (row["context_b"], component_id) in component_by_key, f"{row['comparison_id']}: shared component reference missing")

for row in anchors:
    aid = row["anchor_id"]
    check(row["context_id"] in context_ids and row["axis"] in AXES, f"{aid}: invalid context/axis")
    check(row["evidence_level"] in LAYERS and row["evidence_level"] in {"FUNCTIONAL_ASSAY", "IN_VIVO"}, f"{aid}: invalid phenotype layer")
    check(row["causal_status"] in {"ASSOCIATED", "PREDICTED", "FUNCTIONALLY_SUPPORTED", "CAUSALLY_VALIDATED"}, f"{aid}: invalid causal status")
    check(row["causal_status"] != "CAUSALLY_VALIDATED", f"{aid}: unsupported causal validation")
    for field in ("phenotype", "assay", "species", "recipient_or_model", "treatment", "dose", "time", "source", "limitations"):
        check(bool(row[field]), f"{aid}: missing {field}")
    if row["evidence_level"] == "IN_VIVO":
        check(row["species"] == "Mus musculus" and "mouse" in row["recipient_or_model"], f"{aid}: mouse model conflated with human recipient")

for row in cargo:
    check(row["context_id"] in context_ids and row["data_status"] == "AVAILABLE_NOT_ANALYZED" and row["evidence_layer"] == "CARGO" and row["causal_link_status"] == "NONE", f"{row['cargo_dataset_id']}: invalid cargo placeholder")
    provenance(row["source_provenance"], row["cargo_dataset_id"])
check([r["cargo_dataset_id"] for r in cargo] == ["GSE293957"], "cargo registry must contain only GSE293957")

reliability_dimensions = {"study_independence", "recipient_donor_independence", "ev_preparation_independence", "batch_adjustment", "sample_qc", "sensitivity_stability", "annotation_certainty", "phenotype_support", "cross_context_replication"}
if ctx003_analyzed:
    reliability_dimensions |= {"pairing_certainty", "control_certainty", "model_diagnostics", "pathway_evidence"}
check({(r["context_id"], r["dimension"]) for r in reliability} == {(cid, dimension) for cid in context_ids for dimension in reliability_dimensions}, "reliability dimension grid incomplete")
for row in reliability:
    rid = row["reliability_id"]
    check(row["context_id"] in context_ids and row["dimension"] in reliability_dimensions, f"{rid}: invalid reliability context/dimension")
    check(row["status"] in {"VERIFIED", "LIMITED", "UNKNOWN", "NOT_APPLICABLE"} and bool(row["detail"]), f"{rid}: invalid reliability status/detail")
    provenance(row["source_provenance"], rid)
check(next(r for r in reliability if r["context_id"] == "CTX002" and r["dimension"] == "recipient_donor_independence")["status"] == "LIMITED", "CTX002 donor independence overclaimed")
check(all(r["status"] == "UNKNOWN" for r in reliability if r["dimension"] == "ev_preparation_independence"), "EV preparation independence overclaimed")
if ctx003_analyzed:
    check(next(r for r in reliability if r["context_id"] == "CTX003" and r["dimension"] == "study_independence")["status"] == "VERIFIED", "CTX003 study independence not registered")
    check(next(r for r in reliability if r["context_id"] == "CTX003" and r["dimension"] == "control_certainty")["status"] == "UNKNOWN", "CTX003 control certainty overclaimed")

check(manifest["framework_version"] == "F1" and manifest["source_checkpoint"] == "DEV-C1", "manifest version/checkpoint mismatch")
# The F1 manifest is a frozen baseline snapshot. Post-EXP003 metadata evolution is
# validated above without rewriting the F1 checkpoint counts before FRAMEWORK-F2.
check(manifest["contexts_registered"] == 3 and manifest["verified_contexts"] == 2 and manifest["planned_contexts"] == 1, "frozen F1 manifest context counts changed")
check(set(manifest["axes"]) == AXES and set(manifest["evidence_states"]) == STATES and set(manifest["evidence_layers"]) == LAYERS, "manifest vocabularies mismatch")
check(manifest["comparison_count"] == 5 and manifest["phenotype_anchor_count"] == len(anchors), "frozen F1 manifest evidence counts changed")
check(manifest["cargo_datasets_registered"] == [r["cargo_dataset_id"] for r in cargo], "manifest cargo mismatch")
check(manifest["reliability_dimension_count"] == 9 and manifest["reliability_record_count"] == 27, "frozen F1 manifest reliability counts changed")
check(manifest["retrieval_status"] == "PLANNED" and manifest["explorer_status"] == "PLANNED" and manifest["predictive_ai_status"] == "NOT_IMPLEMENTED", "manifest claims exceed F1")

result = {
    "status": "PASS" if not errors else "FAIL",
    "framework_version": "F1",
    "source_checkpoint": "DEV-C1",
    "validation_mode": "POST_EXP003_C4" if ctx003_analyzed else "F1_BASELINE",
    "counts": {"contexts": len(contexts), "responses": len(responses), "component_entries": len(components), "comparisons": len(comparisons), "phenotype_anchors": len(anchors), "cargo_datasets": len(cargo), "reliability_records": len(reliability)},
    "errors": errors,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
sys.exit(0 if not errors else 1)
