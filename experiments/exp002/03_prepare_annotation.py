#!/usr/bin/env python3
"""Extract stable gene IDs, symbols, and types from official GENCODE v44 GTF."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/raw/exp002/gencode.v44.chr_patch_hapl_scaff.annotation.gtf.gz"
TARGET = ROOT / "data/processed/exp002/gencode_v44_gene_annotation.csv"
MANIFEST = ROOT / "configs/exp002_c3_annotation_source.json"
FIELDS = ("gene_id", "gene_name", "gene_type")


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Official GENCODE v44 GTF not available: {SOURCE}")
    patterns = {key: re.compile(r'(?:^|;\s*)' + key + r' "([^"]+)"') for key in FIELDS}
    genes: dict[str, tuple[str, str]] = {}
    digest = hashlib.sha256()
    with SOURCE.open("rb") as raw:
        for chunk in iter(lambda: raw.read(1 << 20), b""):
            digest.update(chunk)
    # Reading through EOF validates the compressed stream and its gzip CRC.
    with gzip.open(SOURCE, "rt") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9 or fields[2] != "gene":
                continue
            attrs = fields[8]
            values = {key: match.group(1) if (match := pattern.search(attrs)) else None
                      for key, pattern in patterns.items()}
            if any(value is None for value in values.values()):
                raise ValueError(f"GENCODE gene feature lacks required attributes: {attrs[:120]}")
            gene_id = values["gene_id"]
            annotation = (values["gene_name"], values["gene_type"])
            if gene_id in genes and genes[gene_id] != annotation:
                raise ValueError(f"Conflicting GENCODE annotation for {gene_id}")
            genes[gene_id] = annotation
    if len(genes) < 50_000:
        raise ValueError(f"Unexpectedly few official GENCODE gene features: {len(genes)}")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with TARGET.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("gene_id", "gene_symbol", "gene_biotype"))
        for gene_id in sorted(genes):
            writer.writerow((gene_id, *genes[gene_id]))
    manifest = {
        "dataset": "GSE251807",
        "annotation": "GENCODE v44 comprehensive chromosome, patch, haplotype, and scaffold gene annotation",
        "genome_build": "GRCh38.p14",
        "source_url": "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.chr_patch_hapl_scaff.annotation.gtf.gz",
        "source_sha256": digest.hexdigest(),
        "compressed_bytes": SOURCE.stat().st_size,
        "gene_features": len(genes),
        "use": "Annotation of stable gene IDs only; original author Salmon index release remains unverified",
        "local_source_ignored_by_git": "data/raw/exp002/gencode.v44.chr_patch_hapl_scaff.annotation.gtf.gz",
        "local_derived_annotation_ignored_by_git": "data/processed/exp002/gencode_v44_gene_annotation.csv",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"GENCODE v44 annotation: {len(genes)} gene features; SHA-256 {digest.hexdigest()}")


if __name__ == "__main__":
    main()
