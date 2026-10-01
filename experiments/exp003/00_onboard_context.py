#!/usr/bin/env python3
"""Build EXP003-D0 design records from saved GEO/ENA metadata, without omics analysis."""

import csv
import gzip
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "data/metadata/exp003_d0_sources"
META = ROOT / "data/metadata"
OUT = ROOT / "outputs/exp003"
UNKNOWN = "UNKNOWN"


def parse_soft(path):
    records = []
    current = None
    with gzip.open(path, "rt") as handle:
        for line in handle:
            line = line.strip()
            if line.startswith("^SAMPLE = "):
                current = {"gsm_id": line.split(" = ", 1)[1]}
                records.append(current)
            elif current and line.startswith("!Sample_"):
                key, value = line[1:].split(" = ", 1)
                current.setdefault(key, []).append(value)
    return records


def one(record, key):
    return record.get(key, [UNKNOWN])[0]


def relation(record, prefix):
    for value in record.get("Sample_relation", []):
        if value.startswith(prefix):
            return value.rsplit("/", 1)[-1] if prefix == "BioSample:" else value.rsplit("=", 1)[-1]
    return UNKNOWN


def characteristic(record, name):
    for value in record.get("Sample_characteristics_ch1", []):
        if value.lower().startswith(name.lower() + ":"):
            return value.split(":", 1)[1].strip()
    return UNKNOWN


geo = parse_soft(SOURCES / "GSE293956_family.soft.gz")
with (SOURCES / "PRJNA1247494_ena_runs.tsv").open(newline="") as handle:
    ena = list(csv.DictReader(handle, delimiter="\t"))
ena_by_experiment = {r["experiment_accession"]: r for r in ena}
assert len(geo) == 12 and len(ena) == 12 and len(ena_by_experiment) == 12

fields = [
    "gsm_id", "srr_id", "sra_experiment_id", "biosample_id", "bioproject_id", "sample_name",
    "recipient_cell", "recipient_type", "condition", "treatment", "ev_source", "dose",
    "duration_h", "control_definition", "control_medium", "vehicle", "ev_depleted_serum_status",
    "donor", "biological_replicate", "replicate_label_from_title", "technical_replicate", "batch",
    "sequencing_run", "processed_file", "raw_file", "raw_available", "processed_available", "notes",
]
samples = []
for record in geo:
    gsm = record["gsm_id"]
    title = one(record, "Sample_title")
    experiment = relation(record, "SRA:")
    biosample = relation(record, "BioSample:")
    run = ena_by_experiment[experiment]
    assert run["sample_accession"] == biosample, f"{gsm}: GEO/ENA BioSample mismatch"
    assert one(record, "Sample_library_strategy") == run["library_strategy"] == "RNA-Seq"
    recipient = "hDF" if title.startswith("hDF_") else "HaCaT"
    assert recipient in ("hDF", "HaCaT")
    is_ev = characteristic(record, "treatment") == "EVs"
    assert characteristic(record, "treatment") in ("EVs", "control")
    assert title.endswith("_1") or title.endswith("_2") or title.endswith("_3")
    processed = "GSE293956_hDF_total_count.txt.gz" if recipient == "hDF" else "GSE293956_HaCaT_total_count.txt.gz"
    samples.append(dict(
        gsm_id=gsm, srr_id=run["run_accession"], sra_experiment_id=experiment,
        biosample_id=biosample, bioproject_id="PRJNA1247494", sample_name=title,
        recipient_cell="primary human dermal fibroblast" if recipient == "hDF" else "HaCaT human keratinocyte",
        recipient_type="PRIMARY" if recipient == "hDF" else "CELL_LINE",
        condition="HDF_EV" if is_ev else "CONTROL", treatment="hDF-EV" if is_ev else "control label; no EV recorded",
        ev_source="human dermal fibroblast", dose="10 ug/mL protein (paper; GEO dose not numeric)" if is_ev else "0 hDF-EV; vehicle UNKNOWN",
        duration_h="72 (paper); GEO states 3 days", control_definition="control label; precise RNA-seq control medium and vehicle UNKNOWN",
        control_medium=UNKNOWN, vehicle=UNKNOWN, ev_depleted_serum_status="UNKNOWN_FOR_RNA_SEQ_RECIPIENT_CULTURE",
        donor=UNKNOWN, biological_replicate=UNKNOWN, replicate_label_from_title=title.rsplit("_", 1)[-1],
        technical_replicate=UNKNOWN, batch=UNKNOWN, sequencing_run=run["run_accession"],
        processed_file=processed, raw_file=run["fastq_ftp"], raw_available="YES", processed_available="YES",
        notes="GEO identifies cell type and control/EV label; suffix is not proof of biological independence. Dose from Liu et al. DOI 10.1002/cbin.70063, not numeric in GEO. Raw files listed by official ENA; no reads downloaded.",
    ))

with (META / "GSE293956_samples.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(samples)

counts = Counter(("hDF" if r["recipient_type"] == "PRIMARY" else "HaCaT", r["condition"]) for r in samples)
assert counts == {("hDF", "HDF_EV"): 3, ("hDF", "CONTROL"): 3, ("HaCaT", "HDF_EV"): 3, ("HaCaT", "CONTROL"): 3}

contexts_file = META / "skinexo_contexts.csv"
with contexts_file.open(newline="") as handle:
    context_reader = csv.DictReader(handle)
    context_fields = context_reader.fieldnames
    contexts = list(context_reader)
assert context_fields and len(contexts) == 3
ctx003 = next(r for r in contexts if r["context_id"] == "CTX003")
ctx003.update(
    recipient_cell="primary human dermal fibroblast", recipient_tissue="human preputial dermis",
    recipient_primary_or_cell_line="PRIMARY", recipient_donor_count=UNKNOWN,
    ev_source_cell="human dermal fibroblast", ev_source_tissue="human preputial dermis",
    ev_preparation_count=UNKNOWN, ev_type="hDF-derived EV", dose="10 ug/mL EV protein by BCA (paper; GEO dose not numeric)",
    duration_h="72", omics_type="bulk RNA-seq", omics_platform="Illumina NovaSeq 6000 (GPL24676); GRCh38; HISAT2 v2.1.0 per GEO",
    treatment="hDF-EV; 10 ug/mL by paper methods", control="control-labeled hDF without recorded EV; medium/vehicle UNKNOWN",
    sample_count="6", treatment_n="3", control_n="3", batch_count=UNKNOWN,
    statistical_design="NOT_FIT; pairing and batch structure UNKNOWN", data_status="AVAILABLE_NOT_ANALYZED",
    study_status="PLANNED", evidence_status="UNKNOWN",
    major_limitations="RNA-seq control medium/vehicle and recipient EV-depleted-serum status UNKNOWN; donor and EV-preparation independence UNKNOWN; sample suffixes do not prove biological replication; numeric 10 ug/mL dose in paper but not GEO; count matrix not inspected until C1; HaCaT separate",
    source_provenance="data/metadata/exp003_d0_sources/GSE293956_family.soft.gz;data/metadata/exp003_d0_sources/PRJNA1247494_ena_runs.tsv;reports/EXP003_D0_context_onboarding.md;https://pubmed.ncbi.nlm.nih.gov/40728022/",
)
with contexts_file.open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=context_fields)
    writer.writeheader()
    writer.writerows(contexts)

linkage = {
    "CCK-8 proliferation": {"classification": "SAME_EV_DIFFERENT_TIME", "recipient": "hDF", "dose": "graded; 10 ug/mL among tested doses", "time": "24 h", "note": "Human hDF assay; 24 h differs from 72 h RNA-seq"},
    "scratch migration": {"classification": "SAME_EV_DIFFERENT_TIME", "recipient": "hDF", "dose": "10 ug/mL", "time": "24 h", "note": "Human hDF assay; 24 h differs from 72 h RNA-seq"},
    "ERK1/ERK2 qPCR": {"classification": "SAME_EV_DIFFERENT_TIME", "recipient": "hDF", "dose": "10 ug/mL", "time": "24 h", "note": "Targeted mRNA assay, not a functional phenotype or 72 h transcriptome result"},
    "mouse wound closure": {"classification": "SAME_EV_DIFFERENT_MODEL", "recipient": "mouse excisional wound", "dose": "5 uL of 10 ug/uL EV preparation", "time": "days 0-8", "note": "Whole-wound in-vivo model"},
    "scar length": {"classification": "SAME_EV_DIFFERENT_MODEL", "recipient": "mouse excisional wound", "dose": "5 uL of 10 ug/uL EV preparation", "time": "day 14", "note": "Mouse histology, not hDF RNA-seq phenotype"},
    "collagen deposition": {"classification": "SAME_EV_DIFFERENT_MODEL", "recipient": "mouse excisional wound", "dose": "5 uL of 10 ug/uL EV preparation", "time": "day 14", "note": "Mouse histology, not hDF RNA-seq phenotype"},
    "cytokine array": {"classification": "SAME_EV_DIFFERENT_MODEL", "recipient": "mouse wound tissue", "dose": "5 uL of 10 ug/uL EV preparation", "time": "day 1", "note": "Mouse growth-factor array, not recipient hDF assay"},
}

onboarding = {
    "dataset": "GSE293956", "context_id": "CTX003", "study_verified": True,
    "study_title": "Mechanism of action of hDF-EVs on fibroblasts and keratinocytes [RNA-seq]",
    "primary_paper": "Liu et al. 2025; DOI 10.1002/cbin.70063; PMID 40728022",
    "bioproject": "PRJNA1247494", "sra_study": "SRP576981", "platform": "Illumina NovaSeq 6000 (GPL24676)",
    "independence_status": "INDEPENDENT", "independence_from": {"CTX001": "INDEPENDENT", "CTX002": "INDEPENDENT"},
    "total_samples": len(samples), "hdf_samples": 6, "hdf_ev_samples": 3, "hdf_control_samples": 3,
    "hacaT_samples": 6, "hacaT_ev_samples": 3, "hacaT_control_samples": 3,
    "recipient_donor_count": UNKNOWN, "ev_preparation_count": UNKNOWN,
    "dose": "10 ug/mL EV protein by BCA in paper; numeric dose not in GEO", "duration_h": "72 h in paper; 3 days in GEO",
    "control_definition": "GEO control label; paper calls untreated control; exact RNA-seq medium, vehicle, and EV-depleted-serum status UNKNOWN",
    "raw_data_available": True, "processed_data_available": True,
    "processed_files": [
        {"filename": "GSE293956_hDF_total_count.txt.gz", "bytes": 491697, "format": "gzip text; author-described raw counts", "scope": "hDF sample-resolved matrix; header uninspected", "data_level": "processed"},
        {"filename": "GSE293956_HaCaT_total_count.txt.gz", "bytes": 467504, "format": "gzip text; author-described raw counts", "scope": "HaCaT sample-resolved matrix; header uninspected", "data_level": "processed"},
    ],
    "normalized_counts_available": "NOT_LISTED_IN_GEO", "tpm_fpkm_available": "NOT_LISTED_IN_GEO",
    "deg_table_available": "NOT_LISTED_IN_GEO", "preferred_reconstruction_route": "A",
    "preferred_reconstruction_description": "Official hDF raw gene-count matrix, subject to C1 header, integer, gene-ID, and sample mapping checks",
    "phenotype_anchor_linkage": linkage,
    "cargo_companion_dataset": {"dataset_id": "GSE293957", "status": "AVAILABLE_NOT_ANALYZED", "same_study": True,
        "same_ev_source": True, "exact_ev_preparation_linkage": UNKNOWN, "platform": "Affymetrix miRNA-4 Array (GPL19117)", "sample_count": 3,
        "source": "data/metadata/exp003_d0_sources/GSE293957_brief.txt"},
    "framework_schema_complete": True, "eligibility_decision": "ELIGIBLE_WITH_LIMITATIONS",
    "limitations": [
        "Exact RNA-seq control medium, vehicle, and EV-depleted-serum status unresolved",
        "Recipient donor count, pooling, and donor-to-library mapping unresolved",
        "Independent EV preparation count, pooling, and preparation-to-library mapping unresolved",
        "GEO gives three-day exposure but no numeric dose; 10 ug/mL is from the primary paper",
        "Replicate labels 1-3 do not demonstrate independent biological replicates or pairing",
        "Official hDF count matrix is listed but remains uninspected until EXP003-C1",
    ],
    "overall_pass": True, "source_checkpoint": "FRAMEWORK-F1",
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "exp003_d0_context_onboarding.json").write_text(json.dumps(onboarding, indent=2) + "\n")
