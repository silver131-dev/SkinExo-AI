#!/usr/bin/env Rscript
# EXP002-C3: frozen tximport -> DESeq2 primary and EV_8 sensitivity models.
# No EXP001 data, GSEA, or cross-study results are read here.

suppressPackageStartupMessages(library(DESeq2))
suppressPackageStartupMessages(library(tximport))
suppressPackageStartupMessages(library(jsonlite))

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L || !args[[2]] %in% c("preflight", "run")) {
  stop("Usage: 03_differential_expression.R <project_root> <preflight|run>")
}
root <- normalizePath(args[[1]], mustWork = TRUE)
mode <- args[[2]]
read_json <- function(path) jsonlite::fromJSON(path, simplifyVector = FALSE)
expout <- file.path(root, "outputs/exp002")
c1 <- read_json(file.path(expout, "exp002_c1_integrity.json"))
c1r <- read_json(file.path(expout, "exp002_c1r_resolution.json"))
c2 <- read_json(file.path(expout, "exp002_c2_qc.json"))
c2r <- read_json(file.path(expout, "exp002_c2r_ev8_review.json"))
if (!identical(c1$dataset, "GSE251807") || !identical(c1$decision, "REVIEW REQUIRED") ||
    !identical(c1r$decision, "LIMITED_GO") || !isTRUE(c1r$overall_pass) ||
    !identical(c2$c1r_decision, "LIMITED_GO") ||
    !identical(c2$primary_filter, "CPM >= 1 in at least 4 of 16 samples") ||
    !identical(c2r$c2_final_status, "PASS WITH LIMITATIONS") ||
    !isTRUE(c2r$overall_pass) || !identical(c2r$EV8_decision, "RETAIN") ||
    isTRUE(c2r$technical_defect_found) ||
    !identical(c2r$primary_design, "~ batch + condition") ||
    !identical(c2r$sensitivity_design, "~ batch + condition") ||
    c2r$primary_sample_count != 16L || c2r$sensitivity_sample_count != 15L) {
  stop("Frozen C1/C1R/C2/C2R checkpoints do not authorize this analysis")
}
plan <- readLines(file.path(root, "docs/checkpoints/EXP002_C2_ANALYSIS_PLAN.md"), warn = FALSE)
endpoints <- readLines(file.path(root, "docs/checkpoints/EXP002_VALIDATION_ENDPOINTS.md"), warn = FALSE)
required_plan <- c("189,509 exact shared", "countsFromAbundance", "~ batch + condition",
                   "estimated gene count", "≥10 in at least 4", "RETAINED", "15-sample")
if (!all(vapply(required_plan, function(x) any(grepl(x, plan, fixed = TRUE)), logical(1))) ||
    !any(grepl("primary endpoint: P / M / E / A / I", endpoints, ignore.case = TRUE)) ||
    !any(grepl("all-16-sample", endpoints, fixed = TRUE))) {
  stop("Frozen C2 analysis or validation plan text does not match expected design")
}

meta <- read.csv(file.path(root, "data/metadata/GSE251807_samples.csv"),
                 stringsAsFactors = FALSE, check.names = FALSE)
if (nrow(meta) != 16L || anyDuplicated(meta$sample_name) || anyDuplicated(meta$gsm_id) ||
    !identical(as.integer(table(factor(meta$condition, levels = c("CTRL_DMEM", "MSC_sEV")))), c(8L, 8L)) ||
    !identical(as.integer(table(factor(meta$batch, levels = c(1, 2)))), c(8L, 8L)) ||
    !identical(meta$sample_name[meta$sample_name == "EV_8"], "EV_8")) {
  stop("Sample metadata does not match frozen allocation")
}
if (!all(as.matrix(table(meta$batch, meta$condition)) == 4L)) stop("Batch/condition imbalance in frozen primary metadata")
txi <- readRDS(file.path(root, "data/processed/exp002/tximport_shared_gencode_v44.rds"))
if (!identical(txi$countsFromAbundance, "no") ||
    !identical(dim(txi$counts), c(37307L, 16L)) ||
    !identical(colnames(txi$counts), meta$sample_name) ||
    !identical(dim(txi$abundance), dim(txi$counts)) ||
    !identical(dim(txi$length), dim(txi$counts)) ||
    anyDuplicated(rownames(txi$counts))) {
  stop("tximport object does not match frozen Strategy-A representation")
}
for (part in c("counts", "abundance", "length")) {
  x <- txi[[part]]
  if (any(!is.finite(x)) || any(x < 0)) stop("Invalid tximport ", part)
}
if (any(txi$counts != round(txi$counts))) {
  cat("Input counts are fractional Salmon estimates; DESeqDataSetFromTximport will round internally.\n")
}
agg <- read.csv(file.path(expout, "exp002_c2_aggregation_qc.csv"), stringsAsFactors = FALSE)
if (!identical(agg$sample, meta$sample_name) ||
    any(abs(colSums(txi$counts) - agg$retained_salmon_numreads_sum) > 0.02)) {
  stop("tximport totals differ from C2 aggregation QC")
}

# Frozen condition-blind low-count rule; repeated independently in sensitivity.
filter_rule <- "Salmon estimated gene count >= 10 in at least 4 included libraries"
keep_primary <- rowSums(txi$counts >= 10) >= 4L
keep_sensitivity <- rowSums(txi$counts[, colnames(txi$counts) != "EV_8", drop = FALSE] >= 10) >= 4L
if (sum(keep_primary) < 5000L || sum(keep_sensitivity) < 5000L) stop("Unexpected low-count filter collapse")

annotation_file <- file.path(root, "data/processed/exp002/gencode_v44_gene_annotation.csv")
if (!file.exists(annotation_file)) stop("Official GENCODE v44 gene annotation must be prepared first")
annotation <- read.csv(annotation_file, stringsAsFactors = FALSE)
if (!all(c("gene_id", "gene_symbol", "gene_biotype") %in% names(annotation)) ||
    anyDuplicated(annotation$gene_id) ||
    !all(rownames(txi$counts) %in% annotation$gene_id)) {
  stop("GENCODE v44 gene annotation is incomplete or ambiguous for the tximport genes")
}
annotation_source <- "GENCODE v44 official chromosome/patch/haplotype/scaffold GTF gene features (compatible mapping; original Salmon index unknown)"

prepare_txi <- function(keep, selected) {
  subset <- txi
  for (part in c("counts", "abundance", "length")) {
    subset[[part]] <- txi[[part]][keep, selected, drop = FALSE]
  }
  if (any(subset$length <= 0 & subset$counts > 0)) {
    stop("Positive estimated counts have zero effective gene length")
  }
  subset
}
make_coldata <- function(selected) {
  rows <- meta[match(selected, meta$sample_name), , drop = FALSE]
  if (anyNA(rows$sample_name)) stop("Selected sample mapping failed")
  data.frame(batch = factor(rows$batch, levels = c(1, 2)),
             condition = factor(rows$condition, levels = c("CTRL_DMEM", "MSC_sEV")),
             row.names = rows$sample_name)
}
for (selected in list(meta$sample_name, meta$sample_name[meta$sample_name != "EV_8"])) {
  design_matrix <- model.matrix(~ batch + condition, make_coldata(selected))
  if (qr(design_matrix)$rank != ncol(design_matrix)) stop("Design matrix is rank deficient")
}

if (mode == "preflight") {
  cat(sprintf("Preflight PASS: %s genes x %s samples; primary filter %s; sensitivity filter %s; model rank 3 in both.\n",
              nrow(txi$counts), ncol(txi$counts), sum(keep_primary), sum(keep_sensitivity)))
  # Test the documented tximport constructor before any model fitting.
  probe <- DESeqDataSetFromTximport(prepare_txi(keep_primary, meta$sample_name),
                                    colData = make_coldata(meta$sample_name),
                                    design = ~ batch + condition)
  if (nrow(probe) != sum(keep_primary) || !"avgTxLength" %in% assayNames(probe)) {
    stop("DESeq2 tximport constructor did not retain gene-length information")
  }
  cat("DESeqDataSetFromTximport PASS: estimated counts and avgTxLength present; no DE model fitted.\n")
  quit(save = "no")
}

diagnose <- function(dds, res) {
  dispersion <- dispersions(dds)
  if (any(!is.finite(dispersion)) || any(dispersion <= 0)) stop("Invalid fitted dispersions")
  norm <- normalizationFactors(dds)
  if (is.null(norm) || any(!is.finite(norm)) || any(norm <= 0)) {
    stop("Expected positive gene-length-aware normalization factors")
  }
  cooks <- assays(dds)[["cooks"]]
  if (is.null(cooks) || !identical(dim(cooks), dim(dds))) stop("Missing DESeq2 Cook's distances")
  # Standard DESeq2 cutoff for diagnostic context. Actual results() handling is kept at its default.
  p <- ncol(model.matrix(design(dds), as.data.frame(colData(dds))))
  cutoff <- qf(0.99, p, ncol(dds) - p)
  cooks_exceed <- cooks > cutoff
  cooks_exceed[is.na(cooks_exceed)] <- FALSE
  replacement_assays <- intersect(c("replaceCounts", "originalCounts"), assayNames(dds))
  pvalue <- res$pvalue
  padj <- res$padj
  finite_p <- pvalue[is.finite(pvalue)]
  list(
    dispersion_min = min(dispersion), dispersion_median = median(dispersion),
    dispersion_p95 = unname(quantile(dispersion, 0.95)), dispersion_max = max(dispersion),
    normalization_factor_min = min(norm), normalization_factor_max = max(norm),
    cook_cutoff_diagnostic = cutoff,
    cook_exceedance_gene_count = sum(rowSums(cooks_exceed) > 0),
    cook_exceedance_observation_count = sum(cooks_exceed),
    cook_exceedance_by_sample = as.list(setNames(as.integer(colSums(cooks_exceed)), colnames(dds))),
    replacement_assays = as.list(replacement_assays),
    original_count_replacement_detected = "originalCounts" %in% assayNames(dds),
    pvalue_na = sum(is.na(pvalue)), padj_na = sum(is.na(padj)),
    padj_na_with_finite_pvalue = sum(is.na(padj) & is.finite(pvalue)),
    pvalue_histogram_deciles = as.list(as.integer(hist(finite_p, breaks = seq(0, 1, 0.1), plot = FALSE)$counts)),
    finite_pvalue_count = length(finite_p)
  )
}

fit_one <- function(label, selected, keep) {
  input <- prepare_txi(keep, selected)
  coldata <- make_coldata(selected)
  dds <- DESeqDataSetFromTximport(input, colData = coldata, design = ~ batch + condition)
  if (!"avgTxLength" %in% assayNames(dds)) stop("Gene length information absent after tximport construction")
  dds <- DESeq(dds, test = "Wald", quiet = TRUE)
  res <- results(dds, contrast = c("condition", "MSC_sEV", "CTRL_DMEM"),
                 alpha = 0.05, pAdjustMethod = "BH")
  frame <- as.data.frame(res)
  frame$gene_id <- rownames(frame)
  annotation <- annotation[match(frame$gene_id, annotation$gene_id), , drop = FALSE]
  output <- data.frame(gene_id = frame$gene_id,
                       gene_symbol = annotation$gene_symbol,
                       gene_biotype = annotation$gene_biotype,
                       frame[, c("baseMean", "log2FoldChange", "lfcSE", "stat", "pvalue", "padj")],
                       check.names = FALSE)
  output <- output[order(is.na(output$padj), output$padj,
                         is.na(output$pvalue), output$pvalue, output$gene_id), , drop = FALSE]
  rownames(output) <- NULL
  b <- !is.na(output$padj) & output$padj < 0.05 &
       !is.na(output$log2FoldChange) & abs(output$log2FoldChange) >= 1
  write.csv(output, file.path(expout, paste0("differential_expression_", label, "_all.csv")),
            row.names = FALSE, na = "")
  write.csv(output[b, , drop = FALSE],
            file.path(expout, paste0("differential_expression_", label, "_significant.csv")),
            row.names = FALSE, na = "")
  d <- diagnose(dds, res)
  list(
    sample_count = length(selected), sample_names = as.list(selected),
    genes_before_filtering = nrow(txi$counts), genes_filtered_in = sum(keep),
    genes_tested = nrow(output), genes_excluded = nrow(txi$counts) - sum(keep),
    padj005 = sum(!is.na(output$padj) & output$padj < 0.05),
    thresholdB = sum(b), up = sum(b & output$log2FoldChange >= 1),
    down = sum(b & output$log2FoldChange <= -1),
    diagnostics = d,
    result = res
  )
}

primary <- fit_one("primary", meta$sample_name, keep_primary)
cat(sprintf("Primary: %s tested; %s padj<0.05; %s threshold-B\n",
            primary$genes_tested, primary$padj005, primary$thresholdB))
sensitivity <- fit_one("sensitivity", meta$sample_name[meta$sample_name != "EV_8"], keep_sensitivity)
cat(sprintf("Sensitivity: %s tested; %s padj<0.05; %s threshold-B\n",
            sensitivity$genes_tested, sensitivity$padj005, sensitivity$thresholdB))

figdir <- file.path(expout, "figures")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)
finite_lfc <- primary$result$log2FoldChange[is.finite(primary$result$log2FoldChange)]
ylim <- c(-1, 1) * max(abs(finite_lfc)) * 1.05
png(file.path(figdir, "fig05_primary_ma_plot.png"), width = 1800, height = 1200, res = 180)
plotMA(primary$result, ylim = ylim, alpha = 0.05,
       main = "GSE251807: MSC-sEV vs DMEM (DESeq2, batch adjusted)")
dev.off()
primary$result <- NULL
sensitivity$result <- NULL
summary <- list(
  dataset = "GSE251807", checkpoint = "EXP002-C3",
  framework = "tximport estimated Salmon gene counts + gene-length offset; DESeq2 negative-binomial GLM/Wald; BH FDR",
  R_version = R.version.string,
  Bioconductor_version = as.character(BiocManager::version()),
  DESeq2_version = as.character(packageVersion("DESeq2")),
  tximport_version = as.character(packageVersion("tximport")),
  counts_from_abundance = txi$countsFromAbundance,
  annotation_source = annotation_source,
  gene_symbol_available = any(!is.na(annotation$gene_symbol)),
  design = "~ batch + condition", contrast = "MSC_sEV vs CTRL_DMEM",
  positive_log2fc_definition = "higher expression after MSC-sEV exposure",
  filter_rule = filter_rule,
  primary = primary, sensitivity = sensitivity,
  ma_plot_ylim = as.list(ylim), ma_plot_clipping = "none; full finite log2FC range"
)
jsonlite::write_json(summary, file.path(expout, "exp002_c3_model_summary.json"),
                     pretty = TRUE, auto_unbox = TRUE, digits = 12)
