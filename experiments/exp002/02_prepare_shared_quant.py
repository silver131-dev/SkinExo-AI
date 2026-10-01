#!/usr/bin/env python3
"""Prepare exact-shared GSE251807 Salmon tables for tximport; no DE.

The complete official quant.sf exports and GENCODE metadata remain under
Git-ignored data/raw/exp002. Derived transcript tables and tx2gene mapping
are written only to Git-ignored data/processed/exp002.
"""

from __future__ import annotations

import csv
import gzip
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/exp002"
PROCESSED = ROOT / "data/processed/exp002"
METADATA = ROOT / "data/metadata/GSE251807_samples.csv"
C1R = ROOT / "outputs/exp002/exp002_c1r_resolution.json"
UNIVERSE = ROOT / "outputs/exp002/gse251807_transcript_universe_comparison.csv"
HEADER = ["Name", "Length", "EffectiveLength", "TPM", "NumReads"]


def main() -> None:
    checkpoint = json.loads(C1R.read_text())
    if checkpoint["dataset"] != "GSE251807" or checkpoint["decision"] != "LIMITED_GO":
        raise ValueError("EXP002-C1R does not authorize restricted Strategy A QC")
    with METADATA.open(newline="") as handle:
        samples = list(csv.DictReader(handle))
    if len(samples) != 16 or len({r["gsm_id"] for r in samples}) != 16:
        raise ValueError("Unexpected sample metadata")
    with UNIVERSE.open(newline="") as handle:
        shared = {r["transcript_id"] for r in csv.DictReader(handle) if r["classification"] == "SHARED_EXACT"}
    if len(shared) != 189509 or len(shared) != checkpoint["exact_shared_transcripts"]:
        raise ValueError("Exact-shared transcript set differs from C1R")

    gene_by_tx: dict[str, str] = {}
    with gzip.open(RAW / "gencode.v44.transcript_rankings.txt.gz", "rt", newline="") as handle:
        for row in csv.reader(handle, delimiter="\t"):
            if row[4] in shared:
                tx, gene = row[4], row[1]
                if tx in gene_by_tx and gene_by_tx[tx] != gene:
                    raise ValueError(f"Ambiguous GENCODE mapping for {tx}")
                gene_by_tx[tx] = gene
    if set(gene_by_tx) != shared:
        raise ValueError(f"Unmapped shared transcripts: {len(shared - gene_by_tx.keys())}")
    PROCESSED.mkdir(parents=True, exist_ok=True)
    quant_dir = PROCESSED / "shared_quant"
    quant_dir.mkdir(exist_ok=True)
    with (PROCESSED / "tx2gene_gencode_v44_shared.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["transcript_id", "gene_id"])
        writer.writerows((tx, gene_by_tx[tx]) for tx in sorted(shared))
    tx_per_gene = Counter(gene_by_tx.values())

    manifest = []
    qc = []
    for sample in samples:
        original = RAW / sample["quantification_file"]
        destination = quant_dir / f"{sample['sample_name']}.quant.sf.gz"
        source_total = kept_total = 0.0
        source_tpm = kept_tpm = 0.0
        kept: dict[str, list[str]] = {}
        with gzip.open(original, "rt", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if reader.fieldnames != HEADER:
                raise ValueError(f"Unexpected Salmon header: {original}")
            for row in reader:
                tx = row["Name"]
                count, tpm = float(row["NumReads"]), float(row["TPM"])
                if not math.isfinite(count) or count < 0 or not math.isfinite(tpm) or tpm < 0:
                    raise ValueError(f"Invalid Salmon estimate: {original} {tx}")
                source_total += count
                source_tpm += tpm
                if tx in shared:
                    if tx in kept:
                        raise ValueError(f"Duplicate transcript: {original} {tx}")
                    kept[tx] = [row[col] for col in HEADER]
                    kept_total += count
                    kept_tpm += tpm
        if set(kept) != shared:
            raise ValueError(f"Missing exact-shared IDs in {original}: {len(shared - kept.keys())}")
        with gzip.open(destination, "wt", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
            writer.writerow(HEADER)
            writer.writerows(kept[tx] for tx in sorted(shared))
        manifest.append({
            "sample": sample["sample_name"], "gsm_id": sample["gsm_id"],
            "condition": sample["condition"], "batch": sample["batch"],
            "source_quant_file": str(original.relative_to(ROOT)),
            "shared_quant_file": str(destination.relative_to(ROOT)),
        })
        excluded = source_total - kept_total
        qc.append({
            "sample": sample["sample_name"], "gsm_id": sample["gsm_id"],
            "condition": sample["condition"], "batch": sample["batch"],
            "original_salmon_numreads_sum": round(source_total, 3),
            "retained_salmon_numreads_sum": round(kept_total, 3),
            "excluded_salmon_numreads_sum": round(excluded, 3),
            "retained_percentage": round(100 * kept_total / source_total, 4),
            "excluded_percentage": round(100 * excluded / source_total, 4),
            "original_salmon_tpm_sum": round(source_tpm, 3),
            "retained_salmon_tpm_sum": round(kept_tpm, 3),
            "shared_transcripts_used": len(shared),
            "mapped_genes": len(tx_per_gene),
            "unmapped_transcripts": 0,
            "ambiguous_mappings": 0,
            "min_transcripts_per_gene": min(tx_per_gene.values()),
            "max_transcripts_per_gene": max(tx_per_gene.values()),
            "median_transcripts_per_gene": sorted(tx_per_gene.values())[len(tx_per_gene) // 2],
        })
    with (PROCESSED / "shared_quant_manifest.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=manifest[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest)
    out = ROOT / "outputs/exp002/exp002_c2_aggregation_qc.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=qc[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(qc)
    print(f"Prepared {len(samples)} shared Salmon tables; {len(shared):,} transcripts map to {len(tx_per_gene):,} genes")
    print(f"Retained NumReads range: {min(r['retained_percentage'] for r in qc):.4f}%–{max(r['retained_percentage'] for r in qc):.4f}%")


if __name__ == "__main__":
    main()
