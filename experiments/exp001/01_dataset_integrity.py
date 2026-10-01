"""EXP001-C1: verify the unmodified GSE293186 gene count archive and sample sheet."""

from __future__ import annotations

import csv
import gzip
import json
import math
from pathlib import Path

import pandas as pd


DATASET = "GSE293186"
EXPECTED_SAMPLES = {
    "GSM8878107": "CTRL_72h_1",
    "GSM8878108": "CTRL_72h_2",
    "GSM8878109": "CTRL_72h_3",
    "GSM8878110": "ECEV_72h_1",
    "GSM8878111": "ECEV_72h_2",
    "GSM8878112": "ECEV_72h_3",
}
# These non-count fields were observed in the official matrix header.
GENE_ANNOTATIONS = {
    "gene_name", "gene_chr", "gene_start", "gene_end", "gene_strand",
    "gene_length", "gene_biotype", "gene_description", "tf_family",
}
REQUIRED_METADATA = {
    "gsm_id", "count_column", "sample_name", "condition", "time_h",
    "replicate", "cell_type", "species", "treatment", "source_accession",
}
MISSING_TOKENS = {"", "NA", "N/A", "NaN", "nan", "null", "NULL"}
SOURCE_URL = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186"
SAMPLE_SOURCE_URL = (
    "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?"
    "acc=GSE293186&targ=gsm&view=brief&form=text"
)
COUNT_URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE293nnn/GSE293186/"
    "suppl/GSE293186_gene_count.csv.gz"
)


def project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "experiments" / "exp001").is_dir() and (parent / "data").is_dir():
            return parent
    raise RuntimeError("Could not locate the SkinExo-AI project root")


def verify_gzip(path: Path) -> tuple[list[str], str]:
    """Read through the entire stream so gzip's checksum and trailer are checked."""
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as stream:
        first_line = stream.readline()
        if not first_line:
            raise ValueError("Count archive is empty")
        delimiter = csv.Sniffer().sniff(first_line, delimiters=",\t;").delimiter
        header = next(csv.reader([first_line], delimiter=delimiter))
        for _ in stream:
            pass
    if len(header) != len(set(header)):
        raise ValueError("Duplicate count-matrix column names; sample mapping is ambiguous")
    return header, delimiter


def validate_metadata(metadata: pd.DataFrame, header: list[str]) -> tuple[list[dict], bool]:
    missing_fields = REQUIRED_METADATA - set(metadata.columns)
    if missing_fields:
        raise ValueError(f"Missing metadata fields: {sorted(missing_fields)}")
    if len(metadata) != 6:
        raise ValueError(f"Expected exactly six metadata rows, found {len(metadata)}")
    if metadata[list(REQUIRED_METADATA)].isna().any().any():
        raise ValueError("Required metadata contains missing values")
    for field in ("gsm_id", "count_column", "sample_name"):
        if metadata[field].duplicated().any():
            raise ValueError(f"Duplicate {field} in metadata; sample mapping is ambiguous")
    if set(metadata["gsm_id"]) != set(EXPECTED_SAMPLES):
        raise ValueError("Metadata GSM IDs differ from the six verified GEO records")
    if set(metadata["count_column"]) - set(header):
        raise ValueError("Metadata count column(s) absent from matrix header")

    mapping = []
    for row in metadata.to_dict("records"):
        gsm = row["gsm_id"]
        title = EXPECTED_SAMPLES[gsm]
        condition, duration, replicate = title.split("_")
        treatment = (
            "Exosome-depleted media" if condition == "CTRL"
            else "ECEVs in exosome-depleted media"
        )
        expected = {
            "sample_name": title,
            "count_column": title,
            "condition": condition,
            "time_h": "72",
            "replicate": replicate,
            "cell_type": "Dermal fibroblasts",
            "species": "Homo sapiens",
            "treatment": treatment,
            "source_accession": DATASET,
        }
        for field, value in expected.items():
            if str(row[field]) != value:
                raise ValueError(
                    f"Metadata mismatch for {gsm}, {field}: {row[field]!r} != {value!r}"
                )
        mapping.append({
            "gsm_id": gsm,
            "count_column": row["count_column"],
            "sample_name": row["sample_name"],
            "condition": row["condition"],
        })
    return mapping, True


def main() -> int:
    root = project_root()
    count_path = root / "data/raw/GSE293186_gene_count.csv.gz"
    metadata_path = root / "data/metadata/GSE293186_samples.csv"
    output_path = root / "outputs/exp001/exp001_c1_integrity.json"
    report_path = root / "reports/EXP001_C1_dataset_integrity.md"

    if not count_path.is_file():
        raise FileNotFoundError(f"Required count file missing: {count_path}")
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Required metadata file missing: {metadata_path}")

    header, delimiter = verify_gzip(count_path)
    metadata = pd.read_csv(metadata_path, dtype=str)
    mapping, metadata_ok = validate_metadata(metadata, header)

    gene_candidates = [col for col in header if col.lower() in {"gene_id", "geneid", "ensembl_gene_id"}]
    if len(gene_candidates) != 1:
        raise ValueError(f"Cannot identify a unique gene ID column: {gene_candidates}")
    gene_col = gene_candidates[0]
    sample_cols = [item["count_column"] for item in mapping]
    unexpected = [
        col for col in header
        if col != gene_col and col not in sample_cols and col not in GENE_ANNOTATIONS
    ]

    matrix = pd.read_csv(count_path, sep=delimiter, compression="gzip", dtype=str, keep_default_na=False)
    if list(matrix.columns) != header:
        raise ValueError("Loaded columns differ from archive header")
    gene_ids = matrix[gene_col].str.strip()
    missing_gene_ids = int(gene_ids.isin(MISSING_TOKENS).sum())
    duplicate_gene_ids = int(gene_ids[~gene_ids.isin(MISSING_TOKENS)].duplicated().sum())

    counts = pd.DataFrame(index=matrix.index)
    missing_counts = 0
    non_numeric_counts = 0
    negative_counts = 0
    non_integer_counts = 0
    library_sizes = {}
    for col in sample_cols:
        raw = matrix[col].str.strip()
        missing = raw.isin(MISSING_TOKENS)
        numeric = pd.to_numeric(raw.mask(missing), errors="coerce")
        finite = numeric.map(lambda x: pd.isna(x) or math.isfinite(float(x)))
        non_numeric = (~missing & (numeric.isna() | ~finite))
        missing_counts += int(missing.sum())
        non_numeric_counts += int(non_numeric.sum())
        negative_counts += int((numeric < 0).sum())
        non_integer_counts += int((numeric.notna() & finite & (numeric % 1 != 0)).sum())
        counts[col] = numeric
        library_sizes[col] = (
            int(numeric.sum()) if not (missing | non_numeric).any() else None
        )

    zero_count_genes = int(counts.eq(0).all(axis=1).sum())
    ctrl_count = int((metadata["condition"] == "CTRL").sum())
    ecev_count = int((metadata["condition"] == "ECEV").sum())
    sample_mapping_ok = len(sample_cols) == 6 and len(set(sample_cols)) == 6 and not unexpected
    numeric_ok = non_numeric_counts == 0 and non_integer_counts == 0
    missing_values = missing_counts + missing_gene_ids
    overall_pass = all([
        metadata_ok, sample_mapping_ok, numeric_ok, ctrl_count == 3, ecev_count == 3,
        missing_values == 0, negative_counts == 0, duplicate_gene_ids == 0,
    ])

    warnings = []
    if unexpected:
        warnings.append(f"Unexpected matrix columns: {', '.join(unexpected)}")
    if missing_values:
        warnings.append(f"Missing required gene IDs/count values: {missing_values}")
    if non_numeric_counts:
        warnings.append(f"Non-numeric count values: {non_numeric_counts}")
    if non_integer_counts:
        warnings.append(f"Non-integer count values: {non_integer_counts}")
    if negative_counts:
        warnings.append(f"Negative counts: {negative_counts}")
    if duplicate_gene_ids:
        warnings.append(f"Duplicate gene IDs beyond first occurrence: {duplicate_gene_ids}")
    if zero_count_genes:
        warnings.append(f"{zero_count_genes} genes have zero counts in all six samples; retained for C1")

    result = {
        "dataset": DATASET,
        "experiment": "EXP001",
        "checkpoint": "EXP001-C1 Dataset Integrity",
        "matrix_rows": int(matrix.shape[0]),
        "matrix_columns": int(matrix.shape[1]),
        "gene_identifier_column": gene_col,
        "sample_count": len(sample_cols),
        "ctrl_count": ctrl_count,
        "ecev_count": ecev_count,
        "sample_mapping": mapping,
        "library_sizes": library_sizes,
        "missing_values": missing_values,
        "missing_gene_ids": missing_gene_ids,
        "missing_count_values": missing_counts,
        "non_numeric_counts": non_numeric_counts,
        "non_integer_counts": non_integer_counts,
        "negative_counts": negative_counts,
        "duplicate_gene_ids": duplicate_gene_ids,
        "zero_count_genes": zero_count_genes,
        "unexpected_sample_columns": unexpected,
        "gzip_ok": True,
        "metadata_ok": metadata_ok,
        "sample_mapping_ok": sample_mapping_ok,
        "numeric_ok": numeric_ok,
        "overall_pass": overall_pass,
        "delimiter": delimiter,
        "matrix_header": header,
        "count_file_bytes": count_path.stat().st_size,
        "warnings": warnings,
        "source_urls": {"series": SOURCE_URL, "samples": SAMPLE_SOURCE_URL, "count_file": COUNT_URL},
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    decision = "PASS" if overall_pass else "REVIEW REQUIRED"
    mapping_lines = [
        f"| {item['gsm_id']} | {item['count_column']} | {item['condition']} |"
        for item in mapping
    ]
    size_lines = [f"| {col} | {size:,} |" if size is not None else f"| {col} | NA |"
                  for col, size in library_sizes.items()]
    check_lines = [
        f"- Gzip readable and checksum valid: **yes**",
        f"- Metadata and six-column mapping valid: **{'yes' if metadata_ok and sample_mapping_ok else 'no'}**",
        f"- Missing gene IDs/count values: **{missing_values}**",
        f"- Non-numeric / non-integer count values: **{non_numeric_counts} / {non_integer_counts}**",
        f"- Negative counts: **{negative_counts}**",
        f"- Duplicate gene IDs (beyond first occurrence): **{duplicate_gene_ids}**",
        f"- Zero-count genes across all six samples: **{zero_count_genes}**",
        f"- Unexpected sample columns: **{unexpected or 'none'}**",
    ]
    report = f"""# SkinExo-AI EXP001-C1

## Dataset

GSE293186 — gene-count matrix for EXP001. This checkpoint checks data integrity only.

## Biological Design

Primary human dermal fibroblasts (*Homo sapiens*), three controls in exosome-depleted media and three samples treated with endothelial-cell-derived extracellular vesicles (ECEVs) in exosome-depleted media for 72 hours.

## Source Provenance

- [NCBI GEO series]({SOURCE_URL}) — design, six accessions and supplementary files.
- [NCBI GEO sample SOFT records]({SAMPLE_SOURCE_URL}) — individual titles, organism, cell type, treatments and protocol.
- [Official count archive]({COUNT_URL}) — downloaded to `data/raw/GSE293186_gene_count.csv.gz` ({count_path.stat().st_size:,} bytes).
- GEO also lists `GSE293186_ECEV_72hvsCTRL_72h_deg_all.csv.gz`; it was not downloaded or analyzed.

## Count Matrix Structure

- Format: gzip-compressed CSV; delimiter: comma.
- Shape: **{matrix.shape[0]:,} rows × {matrix.shape[1]} columns**.
- Gene identifier: `{gene_col}`.
- Header: `{', '.join(header)}`.
- Six biological sample columns and nine gene-annotation columns; no normalization or filtering applied.

## Sample Mapping

| GEO sample | Count column | Condition |
| --- | --- | --- |
{chr(10).join(mapping_lines)}

Full verified sample metadata is in `data/metadata/GSE293186_samples.csv`.

## Library Sizes

Sum of raw counts across every row for each sample:

| Count column | Library size |
| --- | ---: |
{chr(10).join(size_lines)}

## Integrity Checks

{chr(10).join(check_lines)}

## Issues / Warnings

{chr(10).join('- ' + warning for warning in warnings) if warnings else '- None.'}

## C1 Decision

**{decision}**. No biological effect is inferred at this checkpoint.
"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(f"Header: {header}")
    print("Sample mapping:")
    for item in mapping:
        print(f"  {item['gsm_id']} -> {item['count_column']} ({item['condition']})")
    print(f"Matrix: {matrix.shape[0]} rows x {matrix.shape[1]} columns")
    print(f"C1 result: {decision}")
    print(f"JSON: {output_path}")
    print(f"Report: {report_path}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
