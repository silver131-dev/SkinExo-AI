#!/usr/bin/env python3
"""EXP002-C1 design and transcript-quantification integrity; no biological analysis.

Inputs are the official GSE251807 GEO SOFT record, ENA run metadata,
16 GEO per-sample Salmon quantification files, the GEO normalized-count
supplement (header only), and the curated sample metadata. All source
files live in the Git-ignored data/raw/exp002 directory.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/exp002"
METADATA = ROOT / "data/metadata/GSE251807_samples.csv"
OUT = ROOT / "outputs/exp002/exp002_c1_integrity.json"
QUANT_HEADER = ["Name", "Length", "EffectiveLength", "TPM", "NumReads"]


def need(path: Path) -> Path:
    if not path.is_file() or path.stat().st_size == 0:
        raise FileNotFoundError(f"Required nonempty C1 input missing: {path}")
    return path


def read_geo_samples(path: Path) -> dict[str, dict[str, list[str]]]:
    samples: dict[str, dict[str, list[str]]] = {}
    current: dict[str, list[str]] | None = None
    with gzip.open(need(path), "rt") as handle:
        text = handle.read()
    if "^SERIES = GSE251807" not in text or "PRJNA1055484" not in text:
        raise ValueError("GEO source record is not the expected GSE251807/BioProject")
    for line in text.splitlines():
        if line.startswith("^SAMPLE = "):
            gsm = line.split(" = ", 1)[1]
            if gsm in samples:
                raise ValueError(f"Duplicate GSM in GEO record: {gsm}")
            current = defaultdict(list)
            samples[gsm] = current
        elif current is not None and line.startswith("!Sample_"):
            key, value = line[1:].split(" = ", 1)
            current[key].append(value)
    if len(samples) != 32:
        raise ValueError(f"Expected 32 GEO samples across all secretome arms; found {len(samples)}")
    return samples


def read_runs(path: Path) -> dict[str, dict[str, str]]:
    with need(path).open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 32 or len({r["run_accession"] for r in rows}) != 32:
        raise ValueError("Expected 32 unique ENA/SRA runs across the GEO study")
    if len({r["experiment_accession"] for r in rows}) != 32:
        raise ValueError("Repeated SRA experiment: potential resequencing must be resolved")
    if len({r["sample_accession"] for r in rows}) != 32:
        raise ValueError("Repeated BioSample: potential technical replication must be resolved")
    return {r["experiment_accession"]: r for r in rows}


def inspect_quant(path: Path) -> tuple[dict, set[str]]:
    digest = hashlib.sha256()
    seen: set[str] = set()
    totals = {"NumReads": 0.0, "TPM": 0.0}
    missing = negative = nonnumeric = zero_estimate = 0
    with gzip.open(need(path), "rt", newline="") as handle:
        header = handle.readline()
        digest.update(header.encode())
        if header.rstrip("\r\n").split("\t") != QUANT_HEADER:
            raise ValueError(f"Unexpected Salmon header in {path.name}: {header!r}")
        for line_number, line in enumerate(handle, start=2):
            digest.update(line.encode())
            row = line.rstrip("\r\n").split("\t")
            if len(row) != 5:
                raise ValueError(f"Malformed {path.name} line {line_number}")
            identifier = row[0]
            if not re.fullmatch(r"ENST\d+\.\d+", identifier):
                raise ValueError(f"Unexpected transcript ID {identifier!r} in {path.name}")
            if identifier in seen:
                raise ValueError(f"Duplicate transcript ID {identifier} in {path.name}")
            seen.add(identifier)
            for col, value in zip(QUANT_HEADER[1:], row[1:]):
                if value == "" or value.upper() in {"NA", "NAN", "NULL"}:
                    missing += 1
                    continue
                try:
                    number = float(value)
                except ValueError:
                    nonnumeric += 1
                    continue
                if not math.isfinite(number):
                    nonnumeric += 1
                elif number < 0:
                    negative += 1
                elif col == "Length" and number == 0:
                    raise ValueError(f"Zero transcript length in {path.name} line {line_number}")
                elif col in totals:
                    totals[col] += number
                    if col == "NumReads" and number == 0:
                        zero_estimate += 1
    if missing or negative or nonnumeric:
        raise ValueError(
            f"Invalid quantification in {path.name}: missing={missing}, "
            f"negative={negative}, nonnumeric={nonnumeric}"
        )
    return {
        "transcript_rows": len(seen),
        "estimated_assigned_fragments": totals["NumReads"],
        "tpm_sum": totals["TPM"],
        "zero_estimate_transcripts": zero_estimate,
        "missing": missing,
        "negative": negative,
        "nonnumeric": nonnumeric,
        "sha256_uncompressed": digest.hexdigest(),
    }, seen


def main() -> None:
    geo = read_geo_samples(RAW / "GSE251807_family.soft.gz")
    runs = read_runs(RAW / "PRJNA1055484_ena_runinfo.tsv")
    with need(METADATA).open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 16:
        raise ValueError(f"Expected exactly 16 selected libraries; got {len(rows)}")
    for field in ("gsm_id", "srr_id", "sra_experiment_id", "biosample_id", "sample_name", "condition", "batch", "quantification_file", "recipient_donor_lot", "ev_donor_lot"):
        if field not in rows[0]:
            raise ValueError(f"Missing required metadata column {field}")
    for field in ("gsm_id", "srr_id", "sra_experiment_id", "biosample_id", "sample_name", "quantification_file"):
        if len({r[field] for r in rows}) != 16:
            raise ValueError(f"Ambiguous/duplicate {field} in selected metadata")

    expected = {gsm for gsm, x in geo.items() if x["Sample_title"][0].startswith(("EV_", "DMEM_"))}
    if {r["gsm_id"] for r in rows} != expected:
        raise ValueError("Selected GSMs do not exactly match the GEO EV + DMEM arms")
    by_batch: dict[str, Counter] = defaultdict(Counter)
    transcript_sets_by_batch: dict[str, set[str]] = {}
    transcript_set_fingerprints: dict[str, str] = {}
    quant_stats: dict[str, dict] = {}
    hashes: set[str] = set()
    for row in rows:
        gsm = row["gsm_id"]
        source = geo[gsm]
        title = source["Sample_title"][0]
        expected_condition = "MSC_sEV" if title.startswith("EV_") else "CTRL_DMEM"
        batch = next(x.split(": ", 1)[1] for x in source["Sample_characteristics_ch1"] if x.startswith("batch: "))
        source_file_url = source["Sample_supplementary_file_1"][0]
        source_file_name = source_file_url.rsplit("/", 1)[-1]
        srx = next(x.rsplit("=", 1)[-1] for x in source["Sample_relation"] if x.startswith("SRA: "))
        biosample = next(x.rsplit("/", 1)[-1] for x in source["Sample_relation"] if x.startswith("BioSample: "))
        run = runs[srx]
        if (
            row["sample_name"] != title
            or row["condition"] != expected_condition
            or row["batch"] != batch
            or row["quantification_file"] != source_file_name
            or row["sra_experiment_id"] != srx
            or row["biosample_id"] != biosample
            or row["srr_id"] != run["run_accession"]
            or row["recipient_donor_lot"] != "412Z029.2"
            or (expected_condition == "MSC_sEV" and row["ev_donor_lot"] != "438Z012.1")
            or row["time_h"] != "48"
            or row["biological_replicate"] != gsm
        ):
            raise ValueError(f"Metadata conflict with GEO/ENA for {gsm}")
        if run["sample_accession"] != biosample or run["study_accession"] != "PRJNA1055484":
            raise ValueError(f"SRA/BioSample linkage conflict for {gsm}")
        if run["library_strategy"] != "RNA-Seq" or run["instrument_model"] != "Illumina NovaSeq 6000":
            raise ValueError(f"Unexpected library strategy or instrument for {gsm}")
        by_batch[batch][expected_condition] += 1
        stats, ids = inspect_quant(RAW / source_file_name)
        fingerprint = hashlib.sha256("\n".join(sorted(ids)).encode()).hexdigest()
        if batch in transcript_set_fingerprints and fingerprint != transcript_set_fingerprints[batch]:
            raise ValueError(f"Different transcript ID sets within batch {batch}: {gsm}")
        transcript_set_fingerprints[batch] = fingerprint
        transcript_sets_by_batch.setdefault(batch, ids)
        if stats["sha256_uncompressed"] in hashes:
            raise ValueError(f"Identical quantification content found for {gsm}")
        hashes.add(stats["sha256_uncompressed"])
        quant_stats[title] = stats
    if dict(by_batch) != {
        "1": Counter({"CTRL_DMEM": 4, "MSC_sEV": 4}),
        "2": Counter({"CTRL_DMEM": 4, "MSC_sEV": 4}),
    }:
        raise ValueError(f"Condition and batch design differs from expected balanced layout: {by_batch}")

    batch1_ids = transcript_sets_by_batch["1"]
    batch2_ids = transcript_sets_by_batch["2"]
    shared_ids = batch1_ids & batch2_ids
    batch1_only = batch1_ids - batch2_ids
    batch2_only = batch2_ids - batch1_ids

    with gzip.open(need(RAW / "GSE251807_normalised_counts.csv.gz"), "rt") as handle:
        reader = csv.reader(handle)
        normalized_columns = next(reader)
        first_gene_row = next(reader)
    if len(normalized_columns) != 33 or normalized_columns[0] != "":
        raise ValueError("Unexpected normalized gene-level supplement header")
    if len(set(normalized_columns[1:])) != 32:
        raise ValueError("Duplicate sample columns in normalized gene-level supplement")
    if not first_gene_row[0].startswith("ENSG") or not any(float(v) % 1 for v in first_gene_row[1:]):
        raise ValueError("GEO normalized supplement does not match the expected gene ID / fractional-value structure")
    for row in rows:
        expected_name = row["sample_name"].replace("EV_", "sEV_", 1)
        if expected_name not in normalized_columns:
            raise ValueError(f"Missing normalized-supplement column for {row['sample_name']}")

    library_sizes = {name: round(s["estimated_assigned_fragments"], 3) for name, s in sorted(quant_stats.items())}
    vals = list(library_sizes.values())
    warnings = [
        "One recipient NHDF product lot (412Z029.2): 16 libraries are not 16 independent human donors.",
        "One documented MSC EV-source product lot (438Z012.1); number/assignment of independent EV isolations is not stated.",
        "Culture-well biological replicates are author-reported, but well-to-library and any within-batch pairing identifiers are not deposited.",
        "Salmon index transcriptome, annotation release, transcript-to-gene map, and Salmon version are not stated; gene-level estimated counts were not reconstructed.",
        "NumReads sums are estimated assigned fragments, not raw sequencing library-size/read-depth measurements.",
        "GEO gene-level supplement contains normalized noninteger values and is unsuitable as raw count input.",
    ]
    if batch1_only or batch2_only:
        warnings.append(
            f"Batch-specific Salmon transcript reference sets differ: {len(batch1_ids):,} IDs in batch 1, "
            f"{len(batch2_ids):,} in batch 2, {len(shared_ids):,} shared; exact annotation/index provenance "
            "must be resolved before gene-level reconstruction."
        )
    if max(vals) / statistics.median(vals) > 1.75:
        deepest = max(library_sizes, key=library_sizes.get)
        warnings.append(
            f"{deepest} has {library_sizes[deepest]:,.0f} estimated assigned fragments, "
            f"{max(vals) / statistics.median(vals):.2f} times the median; sequencing-depth QC is needed in C2."
        )
    result = {
        "dataset": "GSE251807",
        "checkpoint": "EXP002-C1",
        "study_independent_from_EXP001": True,
        "expected_library_count": 16,
        "verified_library_count": 16,
        "treatment_library_count": 8,
        "control_library_count": 8,
        "recipient_donor_count": 1,
        "recipient_donor_count_basis": "One documented adult NHDF commercial donor lot 412Z029.2",
        "ev_donor_count": 1,
        "ev_donor_count_basis": "One documented individual-donor hBM-MSC commercial lot 438Z012.1",
        "ev_preparation_count": None,
        "batch_count": 2,
        "batch_condition_counts": {batch: dict(counts) for batch, counts in sorted(by_batch.items())},
        "biological_unit_count": 16,
        "biological_unit_count_basis": "Author-reported biological replicates: separately cultured NHDF wells; not independent human donors",
        "technical_replicate_count": 0,
        "technical_replicate_count_basis": "No repeats identified: one unique GSM, BioSample, SRX, and SRR per library; undisclosed technical splits cannot be ruled out",
        "paired_design": "NOT_DOCUMENTED",
        "condition_batch_confounding": False,
        "condition_donor_confounding": False,
        "condition_donor_confounding_note": "Both arms share the only documented recipient donor lot; donor effect is not estimable",
        "quantification_type": "Salmon transcript-level TPM, effective length, and estimated NumReads",
        "sequencing_platform": "Illumina NovaSeq 6000",
        "library_strategy": "RNA-Seq; cDNA selection per ENA",
        "salmon_version": None,
        "reference_annotation": "GRCh38.p14 assembly reported; exact transcriptome/annotation release unknown",
        "transcript_identifier_type": "versioned Ensembl transcript ID (ENST)",
        "transcript_count_per_library_by_batch": {batch: len(ids) for batch, ids in sorted(transcript_sets_by_batch.items())},
        "transcript_set_sha256_by_batch": dict(sorted(transcript_set_fingerprints.items())),
        "transcript_ids_shared_between_batches": len(shared_ids),
        "transcript_ids_unique_to_batch_1": len(batch1_only),
        "transcript_ids_unique_to_batch_2": len(batch2_only),
        "transcript_reference_same_between_batches": not (batch1_only or batch2_only),
        "tx2gene_mapping_status": "BLOCKED_DIFFERENT_BATCH_TRANSCRIPT_SETS_AND_UNKNOWN_EXACT_ANNOTATION_RELEASE",
        "gene_level_counts_reconstructed": False,
        "normalized_gene_matrix_is_raw_counts": False,
        "missing_values": sum(s["missing"] for s in quant_stats.values()),
        "negative_values": sum(s["negative"] for s in quant_stats.values()),
        "nonnumeric_values": sum(s["nonnumeric"] for s in quant_stats.values()),
        "duplicate_libraries": 0,
        "library_sizes": library_sizes,
        "sample_mapping": {r["gsm_id"]: {"srr_id": r["srr_id"], "sample_name": r["sample_name"], "condition": r["condition"], "batch": r["batch"]} for r in rows},
        "quantification_completeness": {
            "all_16_official_files_present_and_readable": True,
            "all_files_have_expected_columns": True,
            "within_batch_transcript_sets_identical": True,
            "between_batch_transcript_sets_identical": not (batch1_only or batch2_only),
        },
        "library_size_min": min(vals),
        "library_size_median": round(statistics.median(vals), 3),
        "library_size_max": max(vals),
        "library_size_ratio": round(max(vals) / min(vals), 4),
        "candidate_design_formula": "~ batch + condition (provisional; only after EV-preparation and culture-unit clarification)",
        "primary_statistical_unit": "independently cultured recipient NHDF well within one donor lot (provisional)",
        "major_warnings": warnings,
        "overall_pass": False,
        "decision": "REVIEW REQUIRED",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"GSE251807: {len(rows)} of 16 quantifications verified; batch transcript rows: 1={len(batch1_ids):,}, 2={len(batch2_ids):,}")
    print(f"Cross-batch transcript IDs: shared={len(shared_ids):,}, only batch 1={len(batch1_only):,}, only batch 2={len(batch2_only):,}")
    print(f"Batch allocation: {result['batch_condition_counts']}")
    print(f"Estimated assigned fragments: min={min(vals):,.0f}, median={statistics.median(vals):,.0f}, max={max(vals):,.0f}")
    print(f"EXP002-C1 decision: {result['decision']}; checkpoint: {OUT}")


if __name__ == "__main__":
    main()
