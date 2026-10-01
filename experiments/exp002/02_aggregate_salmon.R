#!/usr/bin/env Rscript
# EXP002-C2: Salmon-aware gene aggregation only; no differential expression.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("Usage: 02_aggregate_salmon.R <project_root>")
root <- normalizePath(args[[1]], mustWork = TRUE)
if (!requireNamespace("tximport", quietly = TRUE)) stop("Bioconductor tximport is required")
processed <- file.path(root, "data", "processed", "exp002")
manifest <- read.csv(file.path(processed, "shared_quant_manifest.csv"), stringsAsFactors = FALSE)
tx2gene <- read.csv(file.path(processed, "tx2gene_gencode_v44_shared.csv"), stringsAsFactors = FALSE)
qc <- read.csv(file.path(root, "outputs", "exp002", "exp002_c2_aggregation_qc.csv"), stringsAsFactors = FALSE)
if (nrow(manifest) != 16 || nrow(tx2gene) != 189509 || anyDuplicated(tx2gene$transcript_id)) {
  stop("Unexpected manifest or exact-shared mapping")
}
if (!identical(manifest$sample, qc$sample)) stop("Manifest and QC sample order mismatch")
files <- file.path(root, manifest$shared_quant_file)
names(files) <- manifest$sample
if (!all(file.exists(files))) stop("Filtered Salmon file missing")

# Base R importer reads compressed quant.sf exports without an extra R package.
read_quant <- function(file) {
  read.delim(gzfile(file), header = TRUE, sep = "\t", check.names = FALSE,
             stringsAsFactors = FALSE, quote = "", comment.char = "")
}
txi <- tximport::tximport(
  files, type = "salmon", tx2gene = tx2gene[, c("transcript_id", "gene_id")],
  countsFromAbundance = "no", ignoreTxVersion = FALSE, importer = read_quant
)
if (nrow(txi$counts) != length(unique(tx2gene$gene_id)) || ncol(txi$counts) != 16) {
  stop("Unexpected gene-level matrix dimensions")
}
if (!identical(colnames(txi$counts), manifest$sample)) stop("Gene-level sample order mismatch")
if (any(!is.finite(txi$counts)) || any(txi$counts < 0)) stop("Invalid estimated gene counts")
if (any(!is.finite(txi$abundance)) || any(txi$abundance < 0)) stop("Invalid gene TPM")
if (any(!is.finite(txi$length)) || any(txi$length < 0)) stop("Invalid gene effective length")
count_delta <- abs(colSums(txi$counts) - qc$retained_salmon_numreads_sum)
if (any(count_delta > 0.02)) stop("Gene-level estimated-count totals differ from retained Salmon NumReads")

saveRDS(txi, file.path(processed, "tximport_shared_gencode_v44.rds"), compress = "xz")
write.csv(txi$counts, gzfile(file.path(processed, "estimated_gene_counts.csv.gz")), quote = FALSE)
write.csv(txi$abundance, gzfile(file.path(processed, "gene_abundance_tpm.csv.gz")), quote = FALSE)
write.csv(txi$length, gzfile(file.path(processed, "gene_effective_length.csv.gz")), quote = FALSE)
cat(sprintf("tximport %s: %s shared transcripts -> %s genes x %s samples\n",
            as.character(packageVersion("tximport")), nrow(tx2gene), nrow(txi$counts), ncol(txi$counts)))
