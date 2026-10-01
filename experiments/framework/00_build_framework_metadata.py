#!/usr/bin/env python3
"""Materialize F1 metadata from frozen C4 results and verified design metadata.

This script reads only existing checkpoints. It performs no omics analysis and
does not fetch data. Its fixed study-design and phenotype entries are documented
in the framework schemas and the DEV-C1 literature harvest.
"""

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
META = ROOT / "data/metadata"
AXES = "PMEAI"


def read_csv(path):
    with (ROOT / path).open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name, rows, fields):
    with (META / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


contexts = [
    dict(context_id="CTX001", dataset_id="GSE293186", study_id="Yuan_et_al_2026", study_status="VERIFIED", role="EXP001", species="Homo sapiens", recipient_cell="primary human dermal fibroblast", recipient_tissue="skin dermis", recipient_primary_or_cell_line="PRIMARY", recipient_donor_count="UNKNOWN", ev_source_cell="endothelial cell", ev_source_tissue="UNKNOWN", ev_type="endothelial-cell-derived EV", ev_preparation_count="UNKNOWN", dose="UNKNOWN", duration_h="72", experimental_system="IN_VITRO_CULTURE", omics_type="bulk RNA-seq", omics_platform="GEO gene-count matrix; sequencer UNKNOWN", treatment="ECEVs in exosome-depleted media", control="exosome-depleted media", sample_count="6", treatment_n="3", control_n="3", batch_count="UNKNOWN", statistical_design="DESeq2 ~ condition; CTRL reference", data_status="ANALYZED", phenotype_available="YES_PRIMARY_STUDY; NOT_REGISTERED_AT_F1", cargo_data_available="UNKNOWN", evidence_status="FROZEN_C4", major_limitations="Three samples per arm; recipient-donor and EV-preparation independence UNKNOWN; transcriptomic pathway associations are not phenotypes", source_provenance="data/metadata/GSE293186_samples.csv;reports/EXP001_C1_dataset_integrity.md;reports/EXP001_C4_pathway_analysis.md;https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186"),
    dict(context_id="CTX002", dataset_id="GSE251807", study_id="Lei_et_al_2025", study_status="VERIFIED", role="EXP002", species="Homo sapiens", recipient_cell="primary normal human dermal fibroblast", recipient_tissue="skin dermis", recipient_primary_or_cell_line="PRIMARY", recipient_donor_count="1 documented donor lot", ev_source_cell="human bone-marrow mesenchymal stromal cell", ev_source_tissue="bone marrow", ev_type="small EV fraction", ev_preparation_count="UNKNOWN", dose="30 ug/mL sEV-fraction protein by BCA", duration_h="48", experimental_system="IN_VITRO_CULTURE", omics_type="bulk RNA-seq", omics_platform="Illumina NovaSeq 6000; Salmon transcript quantification", treatment="MSC-sEV fraction in DMEM 1% Pen/Strep", control="DMEM 1% Pen/Strep", sample_count="16", treatment_n="8", control_n="8", batch_count="2", statistical_design="DESeq2 ~ batch + condition; primary includes EV_8; sensitivity excludes EV_8", data_status="ANALYZED", phenotype_available="UNKNOWN", cargo_data_available="UNKNOWN", evidence_status="FROZEN_C4", major_limitations="One documented recipient donor lot; EV-preparation independence UNKNOWN; batch-specific transcript universes; EV_8 sensitivity warning; independent-study same-cell-type comparison, not independent-donor validation", source_provenance="data/metadata/GSE251807_samples.csv;reports/EXP002_C1R_design_quantification_resolution.md;reports/EXP002_C4_cross_study_pathway_validation.md;https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE251807"),
    dict(context_id="CTX003", dataset_id="GSE293956", study_id="Liu_et_al_2025", study_status="PLANNED", role="EXP003 candidate", species="Homo sapiens", recipient_cell="human dermal fibroblast", recipient_tissue="skin dermis", recipient_primary_or_cell_line="UNKNOWN", recipient_donor_count="UNKNOWN", ev_source_cell="human dermal fibroblast", ev_source_tissue="skin dermis", ev_type="hDF-derived EV", ev_preparation_count="UNKNOWN", dose="10 ug/mL", duration_h="72", experimental_system="IN_VITRO_CULTURE", omics_type="bulk RNA-seq", omics_platform="GEO GPL24676; detailed assay design pending EXP003-D0", treatment="hDF-EV", control="UNKNOWN", sample_count="UNKNOWN", treatment_n="UNKNOWN", control_n="UNKNOWN", batch_count="UNKNOWN", statistical_design="UNKNOWN", data_status="AVAILABLE_NOT_ANALYZED", phenotype_available="YES_PRIMARY_STUDY", cargo_data_available="YES_GSE293957", evidence_status="UNKNOWN", major_limitations="Study-design metadata only; 12 GEO samples span hDF and HaCaT and hDF subset has not been onboarded; no SkinExo transcriptomic response or causal cargo link", source_provenance="docs/literature/EXP003_D0_SOURCE_LOG.md;https://pubmed.ncbi.nlm.nih.gov/40728022/;https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293956"),
]
write_csv("skinexo_contexts.csv", contexts, list(contexts[0]))

primary = read_csv("outputs/exp002/c4_components_exp001_vs_primary.csv")
sensitivity = read_csv("outputs/exp002/c4_components_exp001_vs_sensitivity.csv")
sens_by_key = {(row["axis"], row["component_id"]): row for row in sensitivity if row["fit"] == "sensitivity"}
gsea = {
    "CTX001": {row["term_id"]: row for row in read_csv("outputs/exp001/c4_gsea_all.csv")},
    "CTX002": {row["term_id"]: row for row in read_csv("outputs/exp002/c4_gsea_primary_all.csv")},
}

component_rows = []
for row in primary:
    context_id = "CTX001" if row["fit"] == "EXP001" else "CTX002"
    term_evidence = json.loads(row["term_evidence_json"])
    qualified = [term["term_id"] for term in term_evidence if term["qualified"]]
    sens_row = sens_by_key.get((row["axis"], row["component_id"])) if context_id == "CTX002" else None
    component_rows.append(dict(
        component_entry_id=f"{context_id}_{row['component_id']}",
        component_id=row["component_id"], context_id=context_id, axis=row["axis"],
        mapped_term_ids=row["term_ids"], qualified_term_ids=";".join(qualified),
        direction=row["direction"], evidence_status="QUALIFIED" if qualified else "OBSERVED_NULL",
        term_evidence_json=row["term_evidence_json"],
        sensitivity_direction=sens_row["direction"] if sens_row else "NOT_APPLICABLE",
        sensitivity_qualified_term_ids=";".join(t["term_id"] for t in json.loads(sens_row["term_evidence_json"]) if t["qualified"]) if sens_row else "",
        evidence_layer="TRANSCRIPTOME", source_checkpoint="EXP001-C4" if context_id == "CTX001" else "EXP002-C4",
    ))
write_csv("skinexo_response_components.csv", component_rows, list(component_rows[0]))

axis_rows = read_csv("outputs/exp002/c4_axes_exp001_vs_primary.csv")
axis_by_id = {row["axis"]: row for row in axis_rows}
response_rows = []
for context_id in ("CTX001", "CTX002"):
    for axis in AXES:
        entries = [r for r in component_rows if r["context_id"] == context_id and r["axis"] == axis]
        active = [r for r in entries if r["evidence_status"] == "QUALIFIED"]
        qualified_ids = sorted({term for r in active for term in r["qualified_term_ids"].split(";") if term})
        exemplar = min((gsea[context_id][term] for term in qualified_ids), key=lambda r: (float(r["padj"]), -abs(float(r["NES"])), r["term_id"])) if qualified_ids else None
        leading_edge = sorted({gene for term in qualified_ids for gene in gsea[context_id][term]["leading_edge_genes"].split(";") if gene})
        dominant = axis_by_id[axis]["dominant_first" if context_id == "CTX001" else "dominant_second"]
        negative = any(r["direction"] == "NEGATIVE" for r in active)
        positive = any(r["direction"] == "POSITIVE" for r in active)
        direction = (dominant + "_DOMINANT_WITH_OPPOSING_COMPONENTS") if positive and negative else (dominant if active else "NO_QUALIFIED_COMPONENT")
        limitations = "Transcriptomic association only; no phenotype inferred; related terms overlap"
        if context_id == "CTX001":
            limitations += "; n=3/arm; donor and EV-preparation independence UNKNOWN"
        else:
            limitations += "; one documented recipient donor lot; EV-preparation independence UNKNOWN; EV_8 retained in primary"
        if axis == "A": limitations += "; vascular/endothelial term family is not a direct angiogenesis assay"
        if axis == "E" and context_id == "CTX002": limitations += "; observed null despite common eligible terms"
        response_rows.append(dict(
            response_id=f"RSP_{context_id}_{axis}", context_id=context_id, axis=axis,
            direction=direction, evidence_status="QUALIFIED" if active else "OBSERVED_NULL", evidence_layer="TRANSCRIPTOME",
            primary_evidence_type="GSEA_PRERANK", representative_term_id=exemplar["term_id"] if exemplar else "",
            NES=exemplar["NES"] if exemplar else "", FDR=exemplar["padj"] if exemplar else "",
            key_terms=";".join(qualified_ids), component_ids=";".join(r["component_id"] for r in active),
            leading_edge_genes=";".join(leading_edge),
            sensitivity_status="NOT_APPLICABLE" if context_id == "CTX001" else "CROSS_STUDY_AXIS_OUTCOME_STABLE_EV8_EXCLUDED",
            phenotype_anchor_status="NOT_REGISTERED_AT_F1", evidence_confidence="QUALIFIED_WITH_DESIGN_LIMITATIONS" if active else "OBSERVED_NULL_WITH_ADEQUATE_COVERAGE",
            limitations=limitations, source_checkpoint="EXP001-C4" if context_id == "CTX001" else "EXP002-C4",
        ))

for axis in AXES:
    response_rows.append(dict(response_id=f"RSP_CTX003_{axis}", context_id="CTX003", axis=axis,
        direction="UNKNOWN", evidence_status="UNKNOWN", evidence_layer="TRANSCRIPTOME", primary_evidence_type="UNKNOWN",
        representative_term_id="", NES="", FDR="", key_terms="", component_ids="", leading_edge_genes="",
        sensitivity_status="UNKNOWN", phenotype_anchor_status="SEPARATE_AUTHOR_REPORTED_P_AND_M" if axis in "PM" else "UNKNOWN",
        evidence_confidence="UNKNOWN", limitations="Planned context; no SkinExo transcriptomic analysis; author phenotype does not determine transcriptomic direction", source_checkpoint="PLANNED_EXP003"))
write_csv("skinexo_responses.csv", response_rows, list(response_rows[0]))

comparison_states = {"P": "CONSERVED_COMPONENT", "M": "DISCORDANT", "E": "NULL_NOT_TESTABLE", "A": "DISCORDANT", "I": "CONSERVED_AXIS"}
comparison_rows = []
for axis in AXES:
    previous = axis_by_id[axis]
    comparison_rows.append(dict(
        comparison_id=f"CMP_CTX001_CTX002_{axis}", context_a="CTX001", context_b="CTX002", axis=axis,
        prior_c4_status=previous["outcome"], framework_state=comparison_states[axis],
        shared_component="P081" if axis == "P" else ("M026_OPPOSITE_DIRECTION" if axis == "M" else "NONE"),
        same_direction="YES_COMPONENT" if axis == "P" else ("YES_AXIS_ONLY" if axis == "I" else "NO" if axis in "MA" else "NOT_TESTABLE"),
        sensitivity_stable="YES_AXIS_OUTCOME", phenotype_support="NOT_ASSESSED_AT_F1",
        limitations={
            "P": "Candidate shared positive component P081 across two contexts; different qualified terms within component; opposing component evidence; entire axis not universally conserved; distinct EV sources and times",
            "M": "Opposite dominant directions; shared M026 is directly opposite; transcriptomic signal is not a fibroblast migration assay",
            "E": "Common eligible terms; EXP002 observed null with no qualified component",
            "A": "Opposite dominant vascular/endothelial components; no shared active component; no direct angiogenesis phenotype",
            "I": "Positive dominant directions arise from different active components; zero shared active components; thematic axis overlap only",
        }[axis] + "; one EXP002 recipient donor lot; EV-preparation independence UNKNOWN",
        source_checkpoint="EXP002-C4",
    ))
write_csv("skinexo_context_comparisons.csv", comparison_rows, list(comparison_rows[0]))

anchor_common = dict(context_id="CTX003", treatment="hDF-EV", replicate_information="UNKNOWN", causal_status="FUNCTIONALLY_SUPPORTED", source="Liu et al. 2025 DOI:10.1002/cbin.70063; PMID:40728022; docs/literature/EXP003_D0_SOURCE_LOG.md")
anchors = [
    dict(anchor_id="ANC_CTX003_P_CCK8", axis="P", phenotype="hDF viability/proliferation readout", assay="CCK-8", species="Homo sapiens", recipient_or_model="human dermal fibroblast culture", dose="graded hDF-EV doses; 10 ug/mL strongest reported", time="24 h", effect_direction="INCREASED", effect_summary="Author reported highest effect at 10 ug/mL among tested doses; CCK-8 measures metabolic viability proxy, not division directly", statistical_support="Author reported effect; exact p-value and test not transcribed at F1", evidence_level="FUNCTIONAL_ASSAY", limitations="Same study as planned CTX003 transcriptomics; exact dose series and replicate details UNKNOWN"),
    dict(anchor_id="ANC_CTX003_M_SCRATCH", axis="M", phenotype="hDF scratch closure", assay="scratch assay", species="Homo sapiens", recipient_or_model="human dermal fibroblast culture", dose="10 ug/mL", time="24 h", effect_direction="INCREASED", effect_summary="Author reported enhanced hDF migration/scratch closure", statistical_support="Author reported effect; exact p-value and test not transcribed at F1", evidence_level="FUNCTIONAL_ASSAY", limitations="Scratch closure may reflect both motility and proliferation; same study as planned transcriptomics"),
    dict(anchor_id="ANC_CTX003_WOUND_CLOSURE", axis="M", phenotype="early excisional wound closure", assay="mouse wound imaging", species="Mus musculus", recipient_or_model="mouse excisional skin wound", dose="UNKNOWN", time="early wound period; exact time UNKNOWN", effect_direction="FASTER_CLOSURE", effect_summary="Author reported accelerated early wound closure", statistical_support="Author reported effect; exact p-value and test not transcribed at F1", evidence_level="IN_VIVO", limitations="Whole-wound outcome; not human fibroblast migration or transcriptomic axis validation"),
    dict(anchor_id="ANC_CTX003_SCAR", axis="E", phenotype="scar length", assay="mouse wound histology", species="Mus musculus", recipient_or_model="mouse excisional skin wound", dose="UNKNOWN", time="UNKNOWN", effect_direction="UNKNOWN", effect_summary="Scar length reported as an in-vivo endpoint; directional effect not encoded without figure-level verification", statistical_support="UNKNOWN", evidence_level="IN_VIVO", causal_status="ASSOCIATED", limitations="Mouse whole-wound outcome; no human fibroblast ECM transcriptomic validation"),
    dict(anchor_id="ANC_CTX003_COLLAGEN", axis="E", phenotype="collagen deposition", assay="mouse wound histology", species="Mus musculus", recipient_or_model="mouse excisional skin wound", dose="UNKNOWN", time="UNKNOWN", effect_direction="UNKNOWN", effect_summary="Collagen deposition reported as an in-vivo endpoint; directional effect not encoded without figure-level verification", statistical_support="UNKNOWN", evidence_level="IN_VIVO", causal_status="ASSOCIATED", limitations="Mouse tissue endpoint; deposition is not a regenerative or anti-fibrotic classification"),
]
anchors = [{**anchor_common, **row} for row in anchors]
write_csv("skinexo_phenotype_anchors.csv", anchors, list(anchors[0]))

cargo = [dict(cargo_dataset_id="GSE293957", context_id="CTX003", data_status="AVAILABLE_NOT_ANALYZED", evidence_layer="CARGO", cargo_type="hDF-EV miRNA profiling by Affymetrix miRNA-4 array", platform="GPL19117", sample_count="3", future_experiment="EXP006 candidate", causal_link_status="NONE", source_provenance="docs/literature/EXP003_D0_SOURCE_LOG.md;https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293957")]
write_csv("skinexo_cargo_datasets.csv", cargo, list(cargo[0]))

reliability_source = {
    "CTX001": "reports/EXP001_C1_dataset_integrity.md;reports/EXP001_C4_pathway_analysis.md;reports/EXP002_C4_cross_study_pathway_validation.md",
    "CTX002": "reports/EXP002_C1R_design_quantification_resolution.md;reports/EXP002_C3_differential_expression.md;reports/EXP002_C4_cross_study_pathway_validation.md",
    "CTX003": "docs/literature/EXP003_D0_SOURCE_LOG.md;https://pubmed.ncbi.nlm.nih.gov/40728022/",
}
reliability_facts = {
    "study_independence": [("VERIFIED", "Independent Yuan study versus CTX002"), ("VERIFIED", "Independent Lei study versus CTX001"), ("NOT_APPLICABLE", "Separate Liu study; no SkinExo transcriptomic comparison yet")],
    "recipient_donor_independence": [("UNKNOWN", "Recipient donor count and independence unknown"), ("LIMITED", "One documented recipient donor lot"), ("UNKNOWN", "Recipient donor count unknown")],
    "ev_preparation_independence": [("UNKNOWN", "Independent EV preparation count unknown"), ("UNKNOWN", "Independent EV preparation count and assignment unknown"), ("UNKNOWN", "Independent EV preparation count unknown")],
    "batch_adjustment": [("UNKNOWN", "C3 design ~ condition; batch metadata unknown"), ("VERIFIED", "Two balanced batches adjusted in primary ~ batch + condition model"), ("UNKNOWN", "Statistical design unknown before EXP003-D0")],
    "sample_qc": [("VERIFIED", "C1/C2 passed; three treatment and three control samples"), ("LIMITED", "C1R/C2R completed; EV_8 retained after review"), ("NOT_APPLICABLE", "No SkinExo sample onboarding or QC")],
    "sensitivity_stability": [("NOT_APPLICABLE", "No EXP001 sensitivity fit in F1 comparison"), ("LIMITED", "All five C4 axis outcomes stable with EV_8 exclusion; C3 effect-tail sensitivity warning remains"), ("UNKNOWN", "No SkinExo analysis")],
    "annotation_certainty": [("VERIFIED", "Frozen MSigDB 2026.1.Hs and predefined C4 term map"), ("LIMITED", "Same frozen term map; batch-specific transcript reference harmonization limitations"), ("UNKNOWN", "No SkinExo annotation review")],
    "phenotype_support": [("LIMITED", "Primary study assays reported; no F1 anchor registered"), ("UNKNOWN", "No F1 phenotype anchor registered"), ("LIMITED", "Author-reported hDF and mouse assays; not linked to SkinExo RNA-seq results")],
    "cross_context_replication": [("LIMITED", "P candidate shared component; I axis-only overlap; M/A discordant; E null"), ("LIMITED", "Same two-context comparison; recipient donor and EV preparation limits"), ("NOT_APPLICABLE", "No biological comparison with CTX003")],
}
reliability_rows = []
for dimension, facts in reliability_facts.items():
    for context_id, (status, detail) in zip(("CTX001", "CTX002", "CTX003"), facts):
        reliability_rows.append(dict(reliability_id=f"REL_{context_id}_{dimension.upper()}", context_id=context_id,
            dimension=dimension, status=status, detail=detail, source_provenance=reliability_source[context_id]))
write_csv("skinexo_reliability.csv", reliability_rows, list(reliability_rows[0]))

manifest = dict(framework_version="F1", contexts_registered=len(contexts), verified_contexts=2, planned_contexts=1,
    axes=list(AXES), evidence_states=["CONSERVED_COMPONENT", "CONSERVED_AXIS", "CONTEXT_DEPENDENT", "DISCORDANT", "NULL_NOT_TESTABLE", "SENSITIVITY_DEPENDENT", "UNKNOWN"],
    evidence_layers=["TRANSCRIPTOME", "FUNCTIONAL_ASSAY", "IN_VIVO", "CARGO", "LITERATURE", "SENSITIVITY"],
    comparison_count=len(comparison_rows), phenotype_anchor_count=len(anchors), cargo_datasets_registered=["GSE293957"],
    reliability_dimension_count=len(reliability_facts), reliability_record_count=len(reliability_rows),
    reliability_model_status="IMPLEMENTED_DIMENSIONAL", retrieval_status="PLANNED", explorer_status="PLANNED", predictive_ai_status="NOT_IMPLEMENTED", source_checkpoint="DEV-C1")
with (ROOT / "outputs/framework/framework_f1.json").open("w") as handle:
    json.dump(manifest, handle, indent=2)
    handle.write("\n")
