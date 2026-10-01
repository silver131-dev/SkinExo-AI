#!/usr/bin/env python3
"""Reproduce EXP002-C1R transcript-reference and run-depth audit; no biology.

Official GSE251807 Salmon quantifications, ENA metadata, and GENCODE v43/v44
transcript rankings are read from Git-ignored data/raw/exp002/. This script
never generates gene counts or fits a differential-expression model.
"""

from __future__ import annotations

import csv
import gzip
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/exp002"
METADATA = ROOT / "data/metadata/GSE251807_samples.csv"
CSV_OUT = ROOT / "outputs/exp002/gse251807_transcript_universe_comparison.csv"
JSON_OUT = ROOT / "outputs/exp002/exp002_c1r_resolution.json"


def quant_rows(path: Path) -> dict[str, tuple[float, float]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    rows = {}
    with gzip.open(path, "rt", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != ["Name", "Length", "EffectiveLength", "TPM", "NumReads"]:
            raise ValueError(f"Unexpected Salmon columns: {path}")
        for row in reader:
            tx = row["Name"]
            if not re.fullmatch(r"ENST\d+\.\d+", tx) or tx in rows:
                raise ValueError(f"Invalid or duplicate transcript identifier: {tx} in {path}")
            rows[tx] = float(row["Length"]), float(row["NumReads"])
    return rows


def gencode_rankings(version: int) -> tuple[dict[str, str], dict[str, str], int]:
    path = RAW / f"gencode.v{version}.transcript_rankings.txt.gz"
    if not path.is_file():
        raise FileNotFoundError(path)
    genes: dict[str, set[str]] = defaultdict(set)
    biotypes: dict[str, set[str]] = defaultdict(set)
    with gzip.open(path, "rt", newline="") as handle:
        for row in csv.reader(handle, delimiter="\t"):
            if len(row) < 6:
                raise ValueError(f"Malformed GENCODE ranking row in {path}")
            genes[row[4]].add(row[1])
            biotypes[row[4]].add(row[5])
    ambiguous = sum(len(values) != 1 for values in genes.values())
    return (
        {tx: next(iter(values)) for tx, values in genes.items() if len(values) == 1},
        {tx: next(iter(values)) for tx, values in biotypes.items() if len(values) == 1},
        ambiguous,
    )


def unversioned(tx: str) -> str:
    return tx.rsplit(".", 1)[0]


def main() -> None:
    with METADATA.open(newline="") as handle:
        samples = list(csv.DictReader(handle))
    c1 = json.loads((ROOT / "outputs/exp002/exp002_c1_integrity.json").read_text())
    if len(samples) != 16 or c1["verified_library_count"] != 16:
        raise ValueError("C1-selected sample design is incomplete")
    if Counter((row["batch"], row["condition"]) for row in samples) != Counter({
        ("1", "CTRL_DMEM"): 4, ("1", "MSC_sEV"): 4,
        ("2", "CTRL_DMEM"): 4, ("2", "MSC_sEV"): 4,
    }):
        raise ValueError("Batch-condition layout changed since C1")

    per_batch: dict[str, set[str]] = {}
    representative_lengths: dict[str, dict[str, float]] = {}
    salmon_numreads_sums: dict[str, float] = {}
    quant_by_sample = {}
    for sample in samples:
        batch = sample["batch"]
        rows = quant_rows(RAW / sample["quantification_file"])
        ids = set(rows)
        if batch in per_batch and ids != per_batch[batch]:
            raise ValueError(f"Transcript set varies within batch {batch}")
        per_batch.setdefault(batch, ids)
        representative_lengths.setdefault(batch, {tx: length for tx, (length, _) in rows.items()})
        salmon_numreads_sums[sample["sample_name"]] = sum(count for _, count in rows.values())
        quant_by_sample[sample["sample_name"]] = rows

    batch1, batch2 = per_batch["1"], per_batch["2"]
    shared, union = batch1 & batch2, batch1 | batch2
    differing_lengths = sum(representative_lengths["1"][tx] != representative_lengths["2"][tx] for tx in shared)
    base1 = {unversioned(tx): tx for tx in batch1}
    base2 = {unversioned(tx): tx for tx in batch2}
    duplicates1, duplicates2 = len(batch1) - len(base1), len(batch2) - len(base2)
    if duplicates1 or duplicates2:
        raise ValueError("Version stripping creates within-batch identifier ambiguity")
    shared_bases = set(base1) & set(base2)
    version_pairs = {base: (base1[base], base2[base]) for base in shared_bases if base1[base] != base2[base]}

    gene43, biotype43, ambiguous43 = gencode_rankings(43)
    gene44, biotype44, ambiguous44 = gencode_rankings(44)
    if ambiguous43 or ambiguous44:
        raise ValueError("GENCODE rankings contain a transcript-to-multiple-genes mapping")
    if not shared <= gene44.keys():
        raise ValueError("GENCODE v44 does not cover all exact shared transcripts")
    shared_biotypes = Counter(biotype44[tx] for tx in shared)
    gene_conflicts = sorted(
        tx for tx in shared & gene43.keys() & gene44.keys()
        if unversioned(gene43[tx]) != unversioned(gene44[tx])
    )
    changed_version_gene_conflicts = sorted(
        base for base, (old, new) in version_pairs.items()
        if old in gene43 and new in gene44 and unversioned(gene43[old]) != unversioned(gene44[new])
    )

    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    with CSV_OUT.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "transcript_id", "classification", "batch1_present",
            "batch2_present", "matching_other_batch_version",
        ])
        for tx in sorted(union):
            in1, in2 = tx in batch1, tx in batch2
            base = unversioned(tx)
            if in1 and in2:
                category, other = "SHARED_EXACT", ""
            elif base in shared_bases:
                category = "SHARED_AFTER_VERSION_STRIP"
                other = base2[base] if in1 else base1[base]
            else:
                category, other = ("BATCH1_ONLY" if in1 else "BATCH2_ONLY"), ""
            counts[category] += 1
            writer.writerow([tx, category, in1, in2, other])

    shared_fraction = {
        name: round(sum(count for tx, (_, count) in rows.items() if tx in shared) / salmon_numreads_sums[name], 6)
        for name, rows in quant_by_sample.items()
    }
    del quant_by_sample  # Do not retain or export a biological expression matrix.

    with (RAW / "PRJNA1055484_ena_depth.tsv").open(newline="") as handle:
        depth_rows = list(csv.DictReader(handle, delimiter="\t"))
    reads_by_srr = {row["run_accession"]: int(row["read_count"]) for row in depth_rows}
    selected_read_counts = {row["sample_name"]: reads_by_srr[row["srr_id"]] for row in samples}
    if len(selected_read_counts) != 16:
        raise ValueError("ENA read-count table is incomplete")
    ev8 = next(row for row in samples if row["sample_name"] == "EV_8")
    ev8_sample_accession = ev8["biosample_id"]
    ev8_run = ev8["srr_id"]
    if ev8_run != "SRR27319309" or ev8_sample_accession != "SAMN39054792":
        raise ValueError("EV_8 linkage differs from ENA and C1")

    def annotation(version: int, mapping: dict[str, str], ambiguous: int) -> dict:
        return {
            "source": "GENCODE official transcript_rankings metadata",
            "release": f"v{version}",
            "genome_build": "GRCh38.p13" if version == 43 else "GRCh38.p14",
            "transcript_namespace": "versioned Ensembl transcript (ENST)",
            "access_url": f"https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_{version}/gencode.v{version}.transcript_rankings.txt.gz",
            "batch1_exact_coverage": len(batch1 & mapping.keys()),
            "batch1_unmapped": len(batch1 - mapping.keys()),
            "batch2_exact_coverage": len(batch2 & mapping.keys()),
            "batch2_unmapped": len(batch2 - mapping.keys()),
            "shared_exact_coverage": len(shared & mapping.keys()),
            "shared_exact_unmapped": len(shared - mapping.keys()),
            "ambiguous_transcript_to_gene_mappings": ambiguous,
            "caveat": "Candidate comparison, not proven original Salmon index; v43 build differs from reported p14" if version == 43 else "Version-exact mapping for all shared IDs, but original Salmon index release remains unverified",
        }

    result = {
        "dataset": "GSE251807",
        "checkpoint": "EXP002-C1R",
        "recipient_replication_status": "PARTIALLY_VERIFIED",
        "recipient_replication_basis": "Primary paper says RNA-seq included at least four biological replicates per treatment and RNA was harvested from 6-well NHDF cultures; individual well IDs/treatment event IDs are not deposited",
        "recipient_donor_count": 1,
        "recipient_donor_count_basis": "One documented PromoCell NHDF lot 412Z029.2",
        "ev_preparation_status": "UNKNOWN",
        "ev_preparation_count": None,
        "ev_preparation_basis": "One source-cell lot 438Z012.1 is documented, but RNA-seq EV-isolation/preparation IDs and pooling/assignment are not",
        "batch_count": 2,
        "batch_condition_counts": c1["batch_condition_counts"],
        "batch1_transcripts": len(batch1),
        "batch2_transcripts": len(batch2),
        "exact_shared_transcripts": len(shared),
        "exact_union_transcripts": len(union),
        "exact_intersection_pct_of_union": round(len(shared) / len(union) * 100, 4),
        "exact_intersection_pct_of_batch1": round(len(shared) / len(batch1) * 100, 4),
        "exact_intersection_pct_of_batch2": round(len(shared) / len(batch2) * 100, 4),
        "version_normalized_shared_transcripts": len(shared_bases),
        "version_normalization_new_pairs": len(version_pairs),
        "version_strip_duplicates_batch1": duplicates1,
        "version_strip_duplicates_batch2": duplicates2,
        "version_pair_cross_release_gene_conflicts": len(changed_version_gene_conflicts),
        "version_pair_cross_release_gene_conflict_ids": changed_version_gene_conflicts,
        "shared_exact_cross_release_gene_conflicts": len(gene_conflicts),
        "shared_exact_length_disagreements": differing_lengths,
        "transcript_namespace": "Ensembl ENST IDs with dot-version suffixes; transcript biotypes include coding and noncoding categories",
        "shared_exact_transcript_biotypes_gencode_v44": dict(sorted(shared_biotypes.items())),
        "transcript_classification_counts": dict(counts),
        "annotation_candidates": [annotation(43, gene43, ambiguous43), annotation(44, gene44, ambiguous44)],
        "authoritative_annotation": "GENCODE v44 (GRCh38.p14) maps 100% of exact shared IDs; original Salmon index release not proven",
        "recommended_harmonization_strategy": "A",
        "tx2gene_status": "EXACT_SHARED_IDS_MAPPABLE_WITH_GENCODE_V44;_ORIGINAL_INDEX_UNVERIFIED",
        "gene_counts_constructed": False,
        "shared_salmon_numreads_fraction_by_sample": shared_fraction,
        "shared_salmon_numreads_fraction_min": min(shared_fraction.values()),
        "shared_salmon_numreads_fraction_max": max(shared_fraction.values()),
        "EV8_status": "NO_OBVIOUS_ISSUE",
        "EV8_ena_read_count": selected_read_counts["EV_8"],
        "EV8_read_count_to_selected_median_ratio": round(selected_read_counts["EV_8"] / statistics.median(selected_read_counts.values()), 4),
        "EV8_salmon_numreads_sum_to_selected_median_ratio": round(salmon_numreads_sums["EV_8"] / statistics.median(salmon_numreads_sums.values()), 4),
        "EV8_run_count": 1,
        "statistical_unit": "recipient NHDF culture/well (author-reported biological replicate; provisional individual-well mapping), within one donor lot",
        "recommended_design": "~ batch + condition (provisional count-based design; no pairing or donor term)",
        "donor_generalization_possible": False,
        "ev_preparation_generalization_possible": False,
        "decision": "LIMITED_GO",
        "remaining_limitations": [
            "Individual RNA-seq well-to-library treatment-event identifiers are not deposited; separate culture assignment is inferred from the described 6-well biological replicates.",
            "One recipient donor lot; no donor-level generalization.",
            "EV preparation count, pooling, and per-well assignment are unknown; no EV-preparation-level generalization.",
            "Original Salmon index hashes, version, and exact annotation release are absent; the two batches used different transcript universes.",
            "Strategy A drops batch-specific transcripts and about 1.7–2.8% of per-sample Salmon NumReads sums; reference differences may affect estimates for retained isoforms.",
            "One of the 460 version-differing ID pairs changes gene assignment between GENCODE v43 and v44; version-normalized strategy B needs explicit conflict handling.",
            "EV_8 appears more deeply sequenced; FASTQ-level and sample-level QC are deferred to C2.",
        ],
        "overall_pass": True,
        "c1r_result": "PASS",
    }
    JSON_OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Exact shared {len(shared):,}/{len(union):,} ({result['exact_intersection_pct_of_union']}% of union)")
    print(f"Version-normalized shared {len(shared_bases):,}; duplicate stripped IDs {duplicates1}/{duplicates2}")
    print(f"GENCODE v44 exact shared coverage {len(shared & gene44.keys()):,}/{len(shared):,}; C1R {result['decision']}")


if __name__ == "__main__":
    main()
