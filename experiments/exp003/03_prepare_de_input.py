#!/usr/bin/env python3
"""Prepare the frozen EXP003-C3 raw-count input without fitting DE.

The source parser is the validated C1/C2 parser: it excludes only the single
contiguous blank-identifier, blank/NA trailing block. The frozen CPM rule is
then applied without condition labels. No author DEG result is read.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/raw/exp003/GSE293956_hDF_total_count.txt.gz"
C1_PATH = ROOT / "outputs/exp003/exp003_c1_integrity.json"
C2_PATH = ROOT / "outputs/exp003/exp003_c2_qc.json"
PLAN_PATH = ROOT / "docs/checkpoints/EXP003_C2_ANALYSIS_PLAN.md"
ENDPOINTS_PATH = ROOT / "docs/checkpoints/EXP003_VALIDATION_ENDPOINTS.md"
MAPPING_PATH = ROOT / "outputs/exp003/c1_sample_mapping.csv"
PROCESSED = ROOT / "data/processed/exp003"
COUNTS_OUT = PROCESSED / "c3_filtered_counts.csv.gz"
COLdata_OUT = PROCESSED / "c3_coldata.csv"
ANNOTATION_OUT = PROCESSED / "gencode_v44_gene_annotation_versionless.csv"
ANNOTATION_SOURCE = ROOT / "data/raw/exp002/gencode.v44.chr_patch_hapl_scaff.annotation.gtf.gz"
ANNOTATION_CONFIG = ROOT / "configs/exp003_c3_annotation_source.json"
PADDING_TOKENS = {"", "NA", "N/A", "#N/A", "NULL"}
EXPECTED_FILTER = "CPM >= 1 in at least 3 of 6 samples"
EXPECTED_SOURCE_SHA256 = "f30d382112d04c9e3f147fc350f8f58e6306da414a617b5cd4dd52c1fd8ec76d"
EXPECTED_ANNOTATION_SHA256 = "7b1daec735b6fbd376f530d7f3ee021ca18da72b29e3b9f72b3a0f89ee8e306d"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_frozen_checkpoints() -> tuple[dict, dict]:
    c1 = json.loads(C1_PATH.read_text())
    c2 = json.loads(C2_PATH.read_text())
    if not (
        c1.get("dataset") == "GSE293956"
        and c1.get("context_id") == "CTX003"
        and c1.get("overall_pass") is True
        and c1.get("de_suitability") == "SUITABLE_WITH_LIMITATIONS"
        and c1.get("original_physical_data_rows") == 1_048_575
        and c1.get("valid_gene_rows") == 60_675
        and c1.get("structural_padding_rows") == 987_900
        and c1.get("sha256") == EXPECTED_SOURCE_SHA256
    ):
        raise RuntimeError("C1 checkpoint does not authorize the frozen C3 input")
    if not (
        c2.get("dataset") == "GSE293956"
        and c2.get("context_id") == "CTX003"
        and c2.get("overall_pass") is True
        and c2.get("decision") == "PASS_WITH_LIMITATIONS"
        and c2.get("genes_before_filtering") == 60_675
        and c2.get("primary_filter") == EXPECTED_FILTER
        and c2.get("de_filter_rule") == EXPECTED_FILTER
        and c2.get("filtered_gene_count") == 13_874
        and c2.get("recommended_de_design") == "~ condition"
        and c2.get("contrast") == "hDF-EV vs control"
        and c2.get("positive_log2fc_definition") == "higher expression in hDF-EV"
        and c2.get("batch_status") == "NOT_DOCUMENTED"
        and c2.get("pairing_status") == "NO_EVIDENCE / UNKNOWN"
    ):
        raise RuntimeError("C2 checkpoint does not match the frozen C3 design/filter")
    plan = PLAN_PATH.read_text()
    endpoints = ENDPOINTS_PATH.read_text()
    required_plan = [
        "CPM ≥ 1 in at least 3 of the 6 libraries",
        "Primary design: `~ condition`",
        "Contrast: `HDF_EV` versus `CONTROL`",
        "standard result-level independent filtering",
        "No pairing, donor, EV-preparation, or batch term",
    ]
    if not all(text in plan for text in required_plan):
        raise RuntimeError("Frozen C2 analysis-plan text is incomplete or inconsistent")
    if not all(text in endpoints for text in ["P —", "M —", "E —", "A —", "I —"]):
        raise RuntimeError("Frozen validation endpoints are incomplete")
    return c1, c2


def load_valid_matrix(path: Path):
    genes: list[str] = []
    rows: list[list[int]] = []
    physical_rows = 0
    padding_rows = 0
    padding_started = False
    first_padding = None
    last_padding = None
    patterns: set[tuple[str, ...]] = set()
    with gzip.open(path, "rt", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        if len(header) != 7:
            raise RuntimeError(f"Expected seven source columns, found {len(header)}")
        for row in reader:
            physical_rows += 1
            if len(row) != len(header):
                raise RuntimeError(f"Malformed physical source row {physical_rows}")
            identifier = row[0].strip()
            cells = [cell.strip() for cell in row[1:]]
            padding = not identifier and all(cell.upper() in PADDING_TOKENS for cell in cells)
            if padding:
                padding_started = True
                padding_rows += 1
                first_padding = first_padding or physical_rows
                last_padding = physical_rows
                patterns.add(tuple(cells))
                continue
            if padding_started:
                raise RuntimeError(f"Non-padding row after trailing padding at row {physical_rows}")
            if not identifier or identifier.upper() in PADDING_TOKENS:
                raise RuntimeError(f"Invalid biological identifier at row {physical_rows}")
            values: list[int] = []
            for cell in cells:
                if not re.fullmatch(r"0|[1-9][0-9]*", cell):
                    raise RuntimeError(f"Invalid nonnegative integer at row {physical_rows}")
                values.append(int(cell))
            genes.append(identifier)
            rows.append(values)
    structure = {
        "physical_rows": physical_rows,
        "valid_rows": len(genes),
        "padding_rows": padding_rows,
        "first_padding": first_padding,
        "last_padding": last_padding,
        "padding_pattern_count": len(patterns),
    }
    return header, genes, np.asarray(rows, dtype=np.int64), structure


def gtf_attributes(value: str) -> dict[str, str]:
    fields = {}
    for item in value.rstrip(";").split("; "):
        key, _, raw = item.partition(" ")
        if key and raw:
            fields[key] = raw.strip('"')
    return fields


def prepare_annotation(gtf_path: Path) -> dict[str, tuple[str, str]]:
    if sha256(gtf_path) != EXPECTED_ANNOTATION_SHA256:
        raise RuntimeError("Official GENCODE v44 annotation checksum mismatch")
    annotation: dict[str, tuple[str, str]] = {}
    with gzip.open(gtf_path, "rt") as handle:
        for line in handle:
            if not line or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 9 or parts[2] != "gene":
                continue
            attributes = gtf_attributes(parts[8])
            versioned = attributes.get("gene_id", "")
            stable = versioned.split(".", 1)[0]
            value = (attributes.get("gene_name", ""), attributes.get("gene_type", ""))
            if not re.fullmatch(r"ENSG[0-9]+", stable) or not all(value):
                raise RuntimeError("Incomplete GENCODE gene feature")
            if stable in annotation and annotation[stable] != value:
                raise RuntimeError(f"Conflicting versionless GENCODE annotation: {stable}")
            annotation[stable] = value
    if len(annotation) != 70_116:
        raise RuntimeError(f"Unexpected GENCODE v44 gene-feature count: {len(annotation)}")
    return annotation


def main() -> None:
    c1, c2 = require_frozen_checkpoints()
    if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("Official hDF count source checksum changed")
    header, genes, counts, structure = load_valid_matrix(SOURCE)
    expected_structure = {
        "physical_rows": 1_048_575,
        "valid_rows": 60_675,
        "padding_rows": 987_900,
        "first_padding": 60_676,
        "last_padding": 1_048_575,
        "padding_pattern_count": 1,
    }
    if structure != expected_structure or len(set(genes)) != len(genes):
        raise RuntimeError(f"C1 parser invariants failed: {structure}")
    if counts.sum(axis=0).tolist() != [x["library_size"] for x in c1["library_sizes"]]:
        raise RuntimeError("Library sums differ from C1")

    with MAPPING_PATH.open(newline="") as handle:
        mapping = list(csv.DictReader(handle))
    mapped = {row["matrix_column"]: row for row in mapping}
    if set(mapped) != set(header[1:]) or any(row["mapping_status"] != "VERIFIED" for row in mapping):
        raise RuntimeError("C1 column mapping is incomplete")
    sample_rows = [mapped[column] for column in header[1:]]
    if [row["condition"] for row in sample_rows].count("CONTROL") != 3 or [row["condition"] for row in sample_rows].count("HDF_EV") != 3:
        raise RuntimeError("Expected three control and three hDF-EV libraries")

    library_sizes = counts.sum(axis=0)
    cpm = counts.astype(np.float64) / library_sizes[np.newaxis, :] * 1_000_000.0
    keep = (cpm >= 1.0).sum(axis=1) >= 3
    if int(keep.sum()) != c2["filtered_gene_count"] or int(keep.sum()) != 13_874:
        raise RuntimeError(f"Frozen CPM filter retained {int(keep.sum())}, expected 13,874")

    annotation = prepare_annotation(ANNOTATION_SOURCE)
    all_coverage = sum(gene in annotation for gene in genes)
    tested_genes = [gene for gene, retain in zip(genes, keep) if retain]
    tested_coverage = sum(gene in annotation for gene in tested_genes)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    with gzip.open(COUNTS_OUT, "wt", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["gene_id"] + [row["sample_name"] for row in sample_rows])
        for gene, values in zip(tested_genes, counts[keep, :]):
            writer.writerow([gene] + values.tolist())
    with COLdata_OUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sample", "matrix_column", "gsm_id", "condition"])
        writer.writeheader()
        for column, row in zip(header[1:], sample_rows):
            writer.writerow({"sample": row["sample_name"], "matrix_column": column,
                             "gsm_id": row["gsm_id"], "condition": row["condition"]})
    with ANNOTATION_OUT.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["gene_id", "gene_symbol", "gene_biotype"])
        for gene in genes:
            symbol, biotype = annotation.get(gene, ("", ""))
            writer.writerow([gene, symbol, biotype])

    annotation_manifest = {
        "dataset": "GSE293956",
        "context_id": "CTX003",
        "annotation": "GENCODE v44 comprehensive chromosome, patch, haplotype, and scaffold gene annotation",
        "genome_build": "GRCh38.p14",
        "source_url": "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.chr_patch_hapl_scaff.annotation.gtf.gz",
        "source_sha256": EXPECTED_ANNOTATION_SHA256,
        "source_gene_features": len(annotation),
        "mapping_key": "versionless stable Ensembl gene ID; GENCODE version suffix removed only from annotation IDs",
        "valid_matrix_gene_rows": len(genes),
        "valid_matrix_annotation_coverage": all_coverage,
        "tested_genes": len(tested_genes),
        "tested_gene_annotation_coverage": tested_coverage,
        "tested_gene_annotation_fraction": tested_coverage / len(tested_genes),
        "analysis_universe_changed_for_annotation": False,
        "use": "Gene symbol and biotype display annotation only; the original count-generation annotation release is unknown",
        "local_source_reused": str(ANNOTATION_SOURCE.relative_to(ROOT)),
        "local_derived_annotation_ignored_by_git": str(ANNOTATION_OUT.relative_to(ROOT)),
    }
    ANNOTATION_CONFIG.write_text(json.dumps(annotation_manifest, indent=2) + "\n")
    print(json.dumps({
        "checkpoint_validation": "PASS",
        "structure": structure,
        "genes_before_filtering": len(genes),
        "genes_tested": len(tested_genes),
        "annotation_coverage": tested_coverage,
        "counts_output": str(COUNTS_OUT.relative_to(ROOT)),
    }, indent=2))


if __name__ == "__main__":
    main()
