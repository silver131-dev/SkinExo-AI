#!/usr/bin/env python3
"""EXP003-C1: integrity checks for the official hDF count matrix only.

No filtering, normalization, PCA, differential expression, pathway analysis,
HaCaT matrix reading, or CTX003 framework response writing occurs here.
"""

import csv
import gzip
import hashlib
import json
import re
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_NAME = "GSE293956_hDF_total_count.txt.gz"
SOURCE = ROOT / "data/raw/exp003" / SOURCE_NAME
SOURCE_URL = f"https://ftp.ncbi.nlm.nih.gov/geo/series/GSE293nnn/GSE293956/suppl/{SOURCE_NAME}"
SAMPLE_META = ROOT / "data/metadata/GSE293956_samples.csv"
OUT = ROOT / "outputs/exp003"
OUT.mkdir(parents=True, exist_ok=True)


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_file_columns(header, samples):
    """Map by column labels and the unique leftover _1 within each arm."""
    mapping = []
    expected = {r["sample_name"]: r for r in samples}
    seen = set()
    for column in header[1:]:
        match = re.fullmatch(r"hdf(con|exo10)(?:-([23]))?", column, re.IGNORECASE)
        if not match:
            mapping.append({"matrix_column": column, "metadata": None, "basis": "UNRECOGNIZED_COLUMN"})
            continue
        arm, suffix = match.groups()
        condition = "CONTROL" if arm.lower() == "con" else "HDF_EV"
        replicate = suffix if suffix else "1"
        sample_name = f"hDF_{'con' if condition == 'CONTROL' else 'EVs'}_{replicate}"
        sample = expected.get(sample_name)
        if not sample or sample["condition"] != condition or sample["recipient_type"] != "PRIMARY" or sample_name in seen:
            mapping.append({"matrix_column": column, "metadata": None, "basis": "NO_UNIQUE_HDF_METADATA_MATCH"})
            continue
        seen.add(sample_name)
        basis = "EXPLICIT_ARM_AND_REPLICATE_LABEL" if suffix else "UNSUFFIXED_ARM_MATCHES_ONLY_REMAINING_REPLICATE_1"
        mapping.append({"matrix_column": column, "metadata": sample, "basis": basis})
    if len(seen) != 6:
        return mapping, False
    labels = {entry["matrix_column"].lower() for entry in mapping}
    expected_labels = {"hdfcon", "hdfcon-2", "hdfcon-3", "hdfexo10", "hdfexo10-2", "hdfexo10-3"}
    complete = len(mapping) == 6 and all(entry["metadata"] for entry in mapping) and labels == expected_labels
    return mapping, complete


if not SOURCE.is_file():
    raise SystemExit(f"Missing official hDF matrix: {SOURCE}")
with SAMPLE_META.open(newline="") as handle:
    metadata = list(csv.DictReader(handle))
hdf_samples = [r for r in metadata if r["recipient_type"] == "PRIMARY" and r["processed_file"] == SOURCE_NAME]
if len(hdf_samples) != 6 or Counter(r["condition"] for r in hdf_samples) != {"CONTROL": 3, "HDF_EV": 3}:
    raise SystemExit("D0 hDF sample metadata is incomplete or has unexpected conditions")

file_size = SOURCE.stat().st_size
sha256 = checksum(SOURCE)
errors = []
try:
    with gzip.open(SOURCE, "rb") as handle:
        for _ in iter(lambda: handle.read(1024 * 1024), b""):
            pass
    gzip_integrity = "PASS"
except (OSError, EOFError) as exc:
    gzip_integrity = "FAIL"
    errors.append(f"gzip integrity failed: {exc}")

physical_data_rows = 0
valid_gene_rows = 0
padding_rows = 0
padding_first_physical_row = None
padding_last_physical_row = None
padding_patterns = Counter()
padding_started = False
biological_rows_after_padding = 0
invalid_blank_identifier_rows = 0
header = []
identifier_values = []
identifier_counts = Counter()
missing_gene_ids = 0
missing_values = 0
negative_values = 0
non_numeric_values = 0
non_integer_values = 0
malformed_rows = 0
zero_count_genes = 0
nonzero_genes = 0
library_sums = []
sample_vectors = []

if gzip_integrity == "PASS":
    with gzip.open(SOURCE, "rt", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        try:
            header = next(reader)
        except StopIteration:
            errors.append("matrix is empty")
        if header:
            library_sums = [0] * (len(header) - 1)
            sample_vectors = [[] for _ in header[1:]]
            for row in reader:
                physical_data_rows += 1
                if len(row) != len(header):
                    malformed_rows += 1
                    errors.append(f"physical data row {physical_data_rows}: {len(row)} columns; expected {len(header)}")
                    continue
                identifier = row[0].strip()
                cells = [cell.strip() for cell in row[1:]]
                # The deposited file fills an Excel-sized sheet. Remove only a
                # contiguous trailing row when its identifier is blank and every
                # expression cell is structurally empty/NA. Zero-count genes have
                # a nonblank identifier and therefore can never match this rule.
                padding_tokens = {"", "NA", "N/A", "#N/A", "NULL"}
                is_structural_padding = not identifier and all(cell.upper() in padding_tokens for cell in cells)
                if is_structural_padding:
                    padding_started = True
                    padding_rows += 1
                    padding_first_physical_row = padding_first_physical_row or physical_data_rows
                    padding_last_physical_row = physical_data_rows
                    padding_patterns[tuple(cells)] += 1
                    continue
                if padding_started:
                    biological_rows_after_padding += 1
                    errors.append(f"non-padding row found after trailing padding at physical data row {physical_data_rows}")
                if not identifier or identifier.upper() in {"NA", "N/A", "#N/A", "NULL"}:
                    missing_gene_ids += 1
                    invalid_blank_identifier_rows += 1
                else:
                    valid_gene_rows += 1
                    identifier_counts[identifier] += 1
                    identifier_values.append(identifier)
                numeric_row = []
                valid_row = True
                for index, value in enumerate(cells):
                    if not value or value.upper() in {"NA", "N/A", "#N/A", "NULL"}:
                        missing_values += 1
                        valid_row = False
                        sample_vectors[index].append(None)
                        continue
                    try:
                        number = Decimal(value)
                    except InvalidOperation:
                        non_numeric_values += 1
                        valid_row = False
                        sample_vectors[index].append(None)
                        continue
                    if not number.is_finite():
                        non_numeric_values += 1
                        valid_row = False
                        sample_vectors[index].append(None)
                        continue
                    if number < 0:
                        negative_values += 1
                        valid_row = False
                    if number != number.to_integral_value():
                        non_integer_values += 1
                        valid_row = False
                    if number >= 0 and number == number.to_integral_value():
                        integer = int(number)
                        library_sums[index] += integer
                        numeric_row.append(integer)
                        sample_vectors[index].append(integer)
                    else:
                        sample_vectors[index].append(number)
                if valid_row and len(numeric_row) == len(header) - 1:
                    if all(value == 0 for value in numeric_row):
                        zero_count_genes += 1
                    else:
                        nonzero_genes += 1

expression_columns = header[1:] if header else []
sample_mapping, mapping_complete = count_file_columns(header, hdf_samples) if header else ([], False)
if not mapping_complete:
    errors.append("six hDF matrix columns did not map one-to-one to D0 metadata")
if len(header) != 7:
    errors.append(f"unexpected matrix width: {len(header)} rather than 7")
if len(expression_columns) != len(set(expression_columns)):
    errors.append("duplicate sample column names")
if any("hacat" in c.lower() for c in expression_columns):
    errors.append("HaCaT column found in hDF matrix")

ensembl = [bool(re.fullmatch(r"ENSG[0-9]+(?:\.[0-9]+)?", gene)) for gene in identifier_values]
if identifier_values and all(ensembl):
    namespace = "Ensembl gene ID"
    versioned = any("." in gene for gene in identifier_values)
elif identifier_values and any(ensembl):
    namespace = "MIXED"
    versioned = any("." in gene for gene in identifier_values if gene.startswith("ENSG"))
else:
    namespace = "OTHER_OR_UNKNOWN"
    versioned = False

duplicate_gene_ids = sum(count - 1 for count in identifier_counts.values() if count > 1)
duplicate_gene_examples = [gene for gene, count in identifier_counts.items() if count > 1][:10]
duplicate_sample_pairs = []
for left in range(len(sample_vectors)):
    for right in range(left + 1, len(sample_vectors)):
        if sample_vectors[left] == sample_vectors[right]:
            duplicate_sample_pairs.append([expression_columns[left], expression_columns[right]])

integral_counts = not any((missing_values, negative_values, non_numeric_values, non_integer_values, malformed_rows))
count_type = "RAW_INTEGER_COUNTS_COMPATIBLE" if integral_counts else "REVIEW_REQUIRED_NONINTEGER_OR_INVALID"
if not integral_counts:
    errors.append("count values are missing, invalid, negative, or non-integer")
if missing_gene_ids or duplicate_gene_ids or namespace != "Ensembl gene ID":
    errors.append("gene identifiers are missing, duplicated, or not exclusively Ensembl")
if duplicate_sample_pairs:
    errors.append("exact duplicate sample columns found")
if physical_data_rows != valid_gene_rows + padding_rows + invalid_blank_identifier_rows:
    errors.append("physical row accounting does not reconcile")
if valid_gene_rows and integral_counts and zero_count_genes + nonzero_genes != valid_gene_rows:
    errors.append("zero/nonzero row totals do not equal valid gene rows")
if not padding_rows or padding_first_physical_row != valid_gene_rows + 1 or padding_last_physical_row != physical_data_rows:
    errors.append("structural padding is absent, interleaved, or not a single trailing block")
if biological_rows_after_padding:
    errors.append("biological rows occur after structural padding begins")

mapping_rows = []
for entry in sample_mapping:
    sample = entry["metadata"]
    mapping_rows.append({
        "matrix_column": entry["matrix_column"],
        "gsm_id": sample["gsm_id"] if sample else "UNKNOWN",
        "srr_id": sample["srr_id"] if sample else "UNKNOWN",
        "biosample_id": sample["biosample_id"] if sample else "UNKNOWN",
        "sample_name": sample["sample_name"] if sample else "UNKNOWN",
        "condition": sample["condition"] if sample else "UNKNOWN",
        "mapping_status": "VERIFIED" if sample and mapping_complete else "REVIEW_REQUIRED",
    })
with (OUT / "c1_sample_mapping.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["matrix_column", "gsm_id", "srr_id", "biosample_id", "sample_name", "condition", "mapping_status"])
    writer.writeheader()
    writer.writerows(mapping_rows)

library_rows = []
for index, column in enumerate(expression_columns):
    sample = sample_mapping[index]["metadata"] if index < len(sample_mapping) else None
    library_rows.append({"sample": sample["sample_name"] if sample else column,
                         "condition": sample["condition"] if sample else "UNKNOWN", "library_size": library_sums[index]})
with (OUT / "c1_library_sizes.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["sample", "condition", "library_size"])
    writer.writeheader()
    writer.writerows(library_rows)

minimum = min(library_sums) if library_sums else None
maximum = max(library_sums) if library_sums else None
ratio = maximum / minimum if minimum and maximum is not None else None
if minimum == 0:
    errors.append("at least one library has zero total counts")

de_suitability = "SUITABLE_WITH_LIMITATIONS" if not errors else "REVIEW_REQUIRED"
result = {
    "dataset": "GSE293956", "context_id": "CTX003", "source_file": str(SOURCE.relative_to(ROOT)),
    "source_url": SOURCE_URL, "sha256": sha256, "file_size_bytes": file_size,
    "gzip_integrity": gzip_integrity, "delimiter": "TAB", "header": header,
    "original_physical_data_rows": physical_data_rows, "valid_gene_rows": valid_gene_rows,
    "matrix_rows": valid_gene_rows, "matrix_columns": len(header),
    "structural_padding_rows": padding_rows,
    "structural_padding_first_physical_row": padding_first_physical_row,
    "structural_padding_last_physical_row": padding_last_physical_row,
    "structural_padding_pattern_count": len(padding_patterns),
    "structural_padding_patterns": [
        {"expression_cells": list(pattern), "row_count": count}
        for pattern, count in sorted(padding_patterns.items())
    ],
    "structural_padding_rule": "exclude only a contiguous trailing row with blank gene identifier and every expression cell blank or one of NA/N/A/#N/A/NULL; retain every nonblank gene identifier including all-zero genes",
    "original_source_preserved": True,
    "gene_identifier_column": header[0] if header else None,
    "gene_identifier_namespace": namespace, "gene_identifier_versioned": versioned,
    "expression_columns": expression_columns, "annotation_columns": [],
    "hdf_samples": len(mapping_rows), "ev_samples": sum(r["condition"] == "HDF_EV" for r in mapping_rows),
    "control_samples": sum(r["condition"] == "CONTROL" for r in mapping_rows),
    "sample_mapping_complete": mapping_complete,
    "mapping_basis": {entry["matrix_column"]: entry["basis"] for entry in sample_mapping},
    "missing_values": missing_values, "negative_values": negative_values,
    "non_numeric_values": non_numeric_values, "non_integer_values": non_integer_values,
    "missing_gene_ids": missing_gene_ids, "invalid_blank_identifier_rows": invalid_blank_identifier_rows,
    "biological_rows_after_padding": biological_rows_after_padding,
    "duplicate_gene_ids": duplicate_gene_ids,
    "duplicate_gene_id_examples": duplicate_gene_examples,
    "duplicate_sample_columns": len(duplicate_sample_pairs), "duplicate_sample_column_pairs": duplicate_sample_pairs,
    "duplicate_sample_column_names": len(expression_columns) - len(set(expression_columns)),
    "malformed_rows": malformed_rows, "count_type": count_type,
    "zero_count_genes": zero_count_genes, "nonzero_genes": nonzero_genes,
    "library_sizes": [
        {"matrix_column": expression_columns[i], "sample": library_rows[i]["sample"],
         "condition": library_rows[i]["condition"], "library_size": value}
        for i, value in enumerate(library_sums)
    ],
    "library_size_min": minimum, "library_size_max": maximum, "library_size_ratio": ratio,
    "recipient_donor_count": "UNKNOWN", "recipient_donor_mapping": "UNKNOWN",
    "ev_preparation_count": "UNKNOWN", "ev_preparation_to_library_mapping": "UNKNOWN",
    "control_definition": "control-labeled hDF without recorded EV; exact RNA-seq medium and vehicle UNKNOWN",
    "pairing": "UNKNOWN", "de_suitability": de_suitability,
    "limitations": [
        "Donor number, pooling, and donor-to-library map remain unknown",
        "Independent EV preparation number and preparation-to-library map remain unknown",
        "Exact RNA-seq control medium, vehicle, and recipient EV-depleted-serum status remain unknown",
        "Pairing and batch structure remain unknown",
        "Unnumbered hdfcon and hdfexo10 columns map to replicate-1 labels by one-to-one elimination, not a deposited column-to-GSM key",
        "The deposited worksheet-sized file contains a contiguous trailing structural padding block; the parser excludes only blank-identifier blank/NA rows and preserves all zero-count genes",
        "C1 assesses matrix integrity only; no filtering, normalization, or DE design has been selected",
    ],
    "errors": errors, "overall_pass": not errors,
}
(OUT / "exp003_c1_integrity.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: result[k] for k in ["original_physical_data_rows", "valid_gene_rows", "structural_padding_rows", "structural_padding_pattern_count", "matrix_columns", "gene_identifier_namespace", "gene_identifier_versioned", "missing_values", "negative_values", "non_numeric_values", "non_integer_values", "duplicate_gene_ids", "duplicate_sample_columns", "zero_count_genes", "nonzero_genes", "library_size_ratio", "de_suitability", "overall_pass"]}, indent=2))
sys.exit(0 if result["overall_pass"] else 1)
