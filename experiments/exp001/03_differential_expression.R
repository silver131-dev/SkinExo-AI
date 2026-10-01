#!/usr/bin/env Rscript
# EXP001-C3: independent DESeq2 ECEV-versus-CTRL differential expression.

suppressPackageStartupMessages(library(DESeq2))
suppressPackageStartupMessages(library(jsonlite))

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
if (length(file_arg) != 1L) stop("Run this file with Rscript")
script_path <- normalizePath(sub("^--file=", "", file_arg), mustWork = TRUE)
root <- normalizePath(file.path(dirname(script_path), "../.."), mustWork = TRUE)

read_checkpoint <- function(path) {
  checkpoint <- jsonlite::fromJSON(path)
  if (!isTRUE(checkpoint$overall_pass)) stop("Required checkpoint did not pass: ", path)
  if (!identical(checkpoint$dataset, "GSE293186")) stop("Checkpoint dataset mismatch: ", path)
  checkpoint
}
c1 <- read_checkpoint(file.path(root, "outputs/exp001/exp001_c1_integrity.json"))
c2 <- read_checkpoint(file.path(root, "outputs/exp001/exp001_c2_qc.json"))

metadata <- read.csv(file.path(root, "data/metadata/GSE293186_samples.csv"),
                     stringsAsFactors = FALSE, check.names = FALSE)
if (nrow(metadata) != 6L || !all(c("gsm_id", "count_column", "condition") %in% names(metadata))) {
  stop("Expected six complete sample metadata rows")
}
if (anyNA(metadata) || anyDuplicated(metadata$gsm_id) || anyDuplicated(metadata$count_column)) {
  stop("Missing or ambiguous sample metadata")
}
if (!identical(as.integer(table(factor(metadata$condition, levels = c("CTRL", "ECEV")))),
               c(3L, 3L))) stop("Expected CTRL=3 and ECEV=3")
c1_mapping <- setNames(c1$sample_mapping$count_column, c1$sample_mapping$gsm_id)
if (!identical(unname(c1_mapping[metadata$gsm_id]), metadata$count_column)) {
  stop("Sample metadata differs from C1 mapping")
}

matrix_path <- file.path(root, "data/raw/GSE293186_gene_count.csv.gz")
input <- read.csv(gzfile(matrix_path), stringsAsFactors = FALSE, check.names = FALSE)
if (nrow(input) != c1$matrix_rows || ncol(input) != c1$matrix_columns) {
  stop("Count matrix dimensions differ from C1")
}
if (!all(c("gene_id", "gene_name", "gene_biotype", "gene_description",
           metadata$count_column) %in% names(input))) stop("Expected columns missing from matrix")
if (anyNA(input$gene_id) || anyDuplicated(input$gene_id)) stop("Invalid gene_id values")
raw_counts <- as.matrix(input[, metadata$count_column, drop = FALSE])
if (!is.numeric(raw_counts) || anyNA(raw_counts) || any(raw_counts < 0) ||
    any(raw_counts != floor(raw_counts))) stop("Counts must be nonnegative integers")
if (!identical(as.numeric(colSums(raw_counts)),
               as.numeric(unlist(c1$library_sizes[metadata$count_column])))) {
  stop("Library sizes differ from C1")
}
rownames(raw_counts) <- input$gene_id
if (nrow(raw_counts) != c2$original_gene_count) stop("Count matrix differs from C2")

# Fixed label-blind prefilter, chosen before DE testing. Three samples corresponds
# to the smallest replicate group size, without using group labels to select genes.
filter_rule <- "raw count >= 10 in at least 3 of 6 samples"
keep <- rowSums(raw_counts >= 10L) >= 3L
filtered <- raw_counts[keep, , drop = FALSE]
if (nrow(filtered) == 0L) stop("Low-count filter retained no genes")
storage.mode(filtered) <- "integer"

coldata <- data.frame(
  condition = factor(metadata$condition, levels = c("CTRL", "ECEV")),
  row.names = metadata$count_column
)
dds <- DESeqDataSetFromMatrix(countData = filtered, colData = coldata,
                              design = ~ condition)
dds <- DESeq(dds, test = "Wald", quiet = TRUE)
res <- results(dds, contrast = c("condition", "ECEV", "CTRL"),
               alpha = 0.05, pAdjustMethod = "BH")

annotation_fields <- intersect(
  c("gene_id", "gene_name", "gene_biotype", "gene_description", "gene_chr",
    "gene_start", "gene_end", "gene_strand", "gene_length", "tf_family"),
  names(input)
)
annotation <- input[match(rownames(res), input$gene_id), annotation_fields, drop = FALSE]
names(annotation)[names(annotation) == "gene_name"] <- "gene_symbol"
if (!"gene_symbol" %in% names(annotation)) annotation$gene_symbol <- NA_character_
output <- cbind(annotation, as.data.frame(res))
output <- output[order(is.na(output$padj), output$padj,
                       is.na(output$pvalue), output$pvalue, output$gene_id), , drop = FALSE]
rownames(output) <- NULL

outdir <- file.path(root, "outputs/exp001")
figdir <- file.path(outdir, "figures")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)
write.csv(output, file.path(outdir, "differential_expression_all.csv"), row.names = FALSE, na = "")
significant <- !is.na(output$padj) & output$padj < 0.05 &
               !is.na(output$log2FoldChange) & abs(output$log2FoldChange) >= 1
write.csv(output[significant, , drop = FALSE],
          file.path(outdir, "differential_expression_significant.csv"),
          row.names = FALSE, na = "")

# Use the full finite fold-change range: no gene is clipped from the MA plot.
max_abs_lfc <- max(abs(output$log2FoldChange[is.finite(output$log2FoldChange)]))
ylim <- c(-max_abs_lfc, max_abs_lfc) * 1.05
png(file.path(figdir, "fig05_ma_plot.png"), width = 1800, height = 1200, res = 180)
plotMA(res, ylim = ylim, alpha = 0.05,
       main = "GSE293186 DESeq2 MA plot: ECEV vs CTRL")
dev.off()

# Blind variance-stabilizing transform is used only for the heatmap display.
top_ids <- head(output$gene_id[significant], 30L)
if (length(top_ids) > 0L) {
  transformed <- vst(dds, blind = TRUE)
  heatmap_values <- as.data.frame(assay(transformed)[top_ids, metadata$count_column,
                                                   drop = FALSE])
  heatmap_values <- cbind(gene_id = top_ids, heatmap_values)
} else {
  heatmap_values <- data.frame(gene_id = character())
  for (sample in metadata$count_column) heatmap_values[[sample]] <- numeric()
}
write.csv(heatmap_values, file.path(outdir, "de_heatmap_expression.csv"),
          row.names = FALSE, na = "")

summary <- list(
  dataset = "GSE293186",
  experiment = "EXP001",
  checkpoint = "EXP001-C3 Differential Expression",
  framework = "DESeq2 negative-binomial GLM; Wald test; Benjamini-Hochberg FDR",
  r_version = R.version.string,
  bioconductor_version = as.character(BiocManager::version()),
  deseq2_version = as.character(packageVersion("DESeq2")),
  contrast = "ECEV_72h vs CTRL_72h",
  positive_log2fc_means = "higher expression in ECEV",
  filter_rule = filter_rule,
  genes_before_filtering = nrow(raw_counts),
  genes_after_filtering = nrow(filtered),
  genes_tested = nrow(output),
  padj_lt_0_05 = sum(!is.na(output$padj) & output$padj < 0.05),
  threshold_b_total = sum(significant),
  threshold_b_up = sum(significant & output$log2FoldChange >= 1),
  threshold_b_down = sum(significant & output$log2FoldChange <= -1),
  pvalue_na = sum(is.na(output$pvalue)),
  padj_na = sum(is.na(output$padj)),
  heatmap_gene_count = length(top_ids),
  ma_plot_ylim = ylim,
  ma_plot_clipping = "none: ylim covers all finite log2FoldChange values"
)
jsonlite::write_json(summary, file.path(outdir, "deg_summary.json"),
                     pretty = TRUE, auto_unbox = TRUE)
cat("DESeq2 complete:", nrow(output), "genes tested;", sum(significant),
    "pass padj < 0.05 and abs(log2FC) >= 1\n")
