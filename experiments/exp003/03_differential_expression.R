#!/usr/bin/env Rscript
# EXP003-C3: frozen hDF-EV-versus-control DESeq2 model only.
# No author DEG table, gene-set collection, or cross-context result is read.

suppressPackageStartupMessages(library(DESeq2))
suppressPackageStartupMessages(library(jsonlite))

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L) stop("Usage: 03_differential_expression.R <project_root>")
root <- normalizePath(args[[1]], mustWork = TRUE)
expout <- file.path(root, "outputs/exp003")
processed <- file.path(root, "data/processed/exp003")

read_json <- function(path) jsonlite::fromJSON(path, simplifyVector = FALSE)
c1 <- read_json(file.path(expout, "exp003_c1_integrity.json"))
c2 <- read_json(file.path(expout, "exp003_c2_qc.json"))
if (!isTRUE(c1$overall_pass) || !identical(c1$dataset, "GSE293956") ||
    !identical(c1$de_suitability, "SUITABLE_WITH_LIMITATIONS") ||
    c1$valid_gene_rows != 60675L || c1$structural_padding_rows != 987900L ||
    !isTRUE(c2$overall_pass) || !identical(c2$decision, "PASS_WITH_LIMITATIONS") ||
    !identical(c2$primary_filter, "CPM >= 1 in at least 3 of 6 samples") ||
    c2$filtered_gene_count != 13874L ||
    !identical(c2$recommended_de_design, "~ condition") ||
    !identical(c2$batch_status, "NOT_DOCUMENTED") ||
    !identical(c2$pairing_status, "NO_EVIDENCE / UNKNOWN")) {
  stop("Frozen C1/C2 checkpoints do not authorize EXP003-C3")
}

counts_file <- file.path(processed, "c3_filtered_counts.csv.gz")
coldata_file <- file.path(processed, "c3_coldata.csv")
annotation_file <- file.path(processed, "gencode_v44_gene_annotation_versionless.csv")
if (!all(file.exists(c(counts_file, coldata_file, annotation_file)))) {
  stop("Prepared C3 counts, coldata, or annotation are missing")
}
input <- read.csv(gzfile(counts_file), stringsAsFactors = FALSE, check.names = FALSE)
meta <- read.csv(coldata_file, stringsAsFactors = FALSE, check.names = FALSE)
annotation <- read.csv(annotation_file, stringsAsFactors = FALSE, check.names = FALSE,
                       na.strings = c(""))
if (nrow(input) != 13874L || ncol(input) != 7L || names(input)[1] != "gene_id" ||
    anyNA(input$gene_id) || anyDuplicated(input$gene_id)) {
  stop("Prepared count matrix does not match the frozen 13,874-gene input")
}
if (nrow(meta) != 6L || anyNA(meta$sample) || anyDuplicated(meta$sample) ||
    !identical(as.integer(table(factor(meta$condition, levels = c("CONTROL", "HDF_EV")))), c(3L, 3L)) ||
    !identical(names(input)[-1], meta$sample)) {
  stop("Prepared six-sample allocation is incomplete or reordered")
}
raw_counts <- as.matrix(input[, meta$sample, drop = FALSE])
if (!is.numeric(raw_counts) || anyNA(raw_counts) || any(!is.finite(raw_counts)) ||
    any(raw_counts < 0) || any(raw_counts != floor(raw_counts))) {
  stop("DE input is not a complete nonnegative integer count matrix")
}
storage.mode(raw_counts) <- "integer"
rownames(raw_counts) <- input$gene_id
if (any(rowSums(raw_counts) == 0L)) stop("Frozen CPM filter unexpectedly retained an all-zero gene")
if (!all(c("gene_id", "gene_symbol", "gene_biotype") %in% names(annotation)) ||
    anyNA(annotation$gene_id) || anyDuplicated(annotation$gene_id) ||
    !all(rownames(raw_counts) %in% annotation$gene_id)) {
  stop("Versionless GENCODE display annotation is incomplete or ambiguous")
}

coldata <- data.frame(
  condition = factor(meta$condition, levels = c("CONTROL", "HDF_EV")),
  row.names = meta$sample
)
design_matrix <- model.matrix(~ condition, coldata)
if (qr(design_matrix)$rank != ncol(design_matrix) || ncol(design_matrix) != 2L) {
  stop("Frozen ~ condition design is not full rank")
}

dds <- DESeqDataSetFromMatrix(countData = raw_counts, colData = coldata,
                              design = ~ condition)
dds <- DESeq(dds, test = "Wald", quiet = TRUE)
res <- results(dds, contrast = c("condition", "HDF_EV", "CONTROL"),
               alpha = 0.05, pAdjustMethod = "BH", independentFiltering = TRUE,
               cooksCutoff = TRUE)

frame <- as.data.frame(res)
frame$gene_id <- rownames(frame)
ann <- annotation[match(frame$gene_id, annotation$gene_id), , drop = FALSE]
output <- data.frame(
  gene_id = frame$gene_id,
  gene_symbol = ann$gene_symbol,
  baseMean = frame$baseMean,
  log2FoldChange = frame$log2FoldChange,
  lfcSE = frame$lfcSE,
  stat = frame$stat,
  pvalue = frame$pvalue,
  padj = frame$padj,
  check.names = FALSE
)
output <- output[order(is.na(output$padj), output$padj,
                       is.na(output$pvalue), output$pvalue, output$gene_id), , drop = FALSE]
rownames(output) <- NULL
threshold_b <- !is.na(output$padj) & output$padj < 0.05 &
               !is.na(output$log2FoldChange) & abs(output$log2FoldChange) >= 1
write.csv(output, file.path(expout, "differential_expression_all.csv"),
          row.names = FALSE, na = "")
write.csv(output[threshold_b, , drop = FALSE],
          file.path(expout, "differential_expression_significant.csv"),
          row.names = FALSE, na = "")

# Model diagnostics. Cook's cutoff is reported descriptively using the same
# 0.99 F distribution reference used by DESeq2. No sample is removed or refit.
dispersions_final <- dispersions(dds)
disp_gene <- mcols(dds)$dispGeneEst
disp_fit <- mcols(dds)$dispFit
if (any(!is.finite(dispersions_final)) || any(dispersions_final <= 0)) {
  stop("Invalid final dispersion estimates")
}
size_factors <- sizeFactors(dds)
if (any(!is.finite(size_factors)) || any(size_factors <= 0)) {
  stop("Invalid DESeq2 size factors")
}
cooks <- assays(dds)[["cooks"]]
if (is.null(cooks) || !identical(dim(cooks), dim(dds))) stop("Missing Cook's distances")
p <- ncol(design_matrix)
cook_cutoff <- qf(0.99, p, ncol(dds) - p)
cook_exceed <- cooks > cook_cutoff
cook_exceed[is.na(cook_exceed)] <- FALSE
cook_max_sample <- apply(cooks, 1L, function(values) {
  if (all(is.na(values))) return(NA_integer_)
  which.max(replace(values, is.na(values), -Inf))
})
max_attribution <- table(factor(cook_max_sample, levels = seq_len(ncol(dds))))
result_metadata <- metadata(res)
filter_threshold <- if (is.null(result_metadata$filterThreshold)) NA_real_ else as.numeric(result_metadata$filterThreshold)
filter_theta <- if (is.null(result_metadata$filterTheta)) NA_real_ else as.numeric(result_metadata$filterTheta)
finite_pvalues <- output$pvalue[is.finite(output$pvalue)]
pvalue_hist <- hist(finite_pvalues, breaks = seq(0, 1, 0.1), plot = FALSE)$counts
beta_convergence <- mcols(dds)$betaConv
if (is.null(beta_convergence)) beta_convergence <- rep(TRUE, nrow(dds))
replacement_assays <- intersect(c("replaceCounts", "originalCounts"), assayNames(dds))
dispersion_fit_type <- attr(dispersionFunction(dds), "fitType")
if (is.null(dispersion_fit_type)) dispersion_fit_type <- "UNKNOWN"

sample_diagnostics <- lapply(seq_len(ncol(dds)), function(index) {
  values <- cooks[, index]
  list(
    sample = colnames(dds)[index],
    condition = as.character(coldata[colnames(dds)[index], "condition"]),
    size_factor = unname(size_factors[index]),
    cook_exceedance_count = unname(sum(cook_exceed[, index])),
    cook_p95 = unname(quantile(values, 0.95, na.rm = TRUE)),
    cook_p99 = unname(quantile(values, 0.99, na.rm = TRUE)),
    cook_max = max(values, na.rm = TRUE),
    maximum_cook_attribution_count = unname(as.integer(max_attribution[index]))
  )
})

# Full finite range prevents clipping of an extreme fitted fold change.
finite_lfc <- res$log2FoldChange[is.finite(res$log2FoldChange)]
ma_limit <- max(abs(finite_lfc)) * 1.05
figdir <- file.path(expout, "figures")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)
png(file.path(figdir, "fig05_ma_plot.png"), width = 1800, height = 1200, res = 180)
plotMA(res, ylim = c(-ma_limit, ma_limit), alpha = 0.05,
       main = "GSE293956 · hDF-EV vs control · DESeq2 · n = 3 vs 3")
dev.off()

model_summary <- list(
  dataset = "GSE293956",
  context_id = "CTX003",
  framework = "DESeq2 negative-binomial GLM; Wald test; Benjamini-Hochberg FDR",
  R_version = R.version.string,
  Bioconductor_version = as.character(BiocManager::version()),
  DESeq2_version = as.character(packageVersion("DESeq2")),
  samples = 6L,
  ev_samples = 3L,
  control_samples = 3L,
  design = "~ condition",
  contrast = "HDF_EV vs CONTROL",
  positive_log2fc_definition = "higher expression in hDF-EV",
  genes_before_filtering = 60675L,
  filter_rule = "CPM >= 1 in at least 3 of 6 samples",
  genes_tested = nrow(output),
  padj005 = sum(!is.na(output$padj) & output$padj < 0.05),
  thresholdB = sum(threshold_b),
  up = sum(threshold_b & output$log2FoldChange >= 1),
  down = sum(threshold_b & output$log2FoldChange <= -1),
  NA_pvalue = sum(is.na(output$pvalue)),
  NA_padj = sum(is.na(output$padj)),
  annotation_coverage_tested = sum(!is.na(output$gene_symbol) & output$gene_symbol != ""),
  annotation_source = "GENCODE v44 / GRCh38.p14 official comprehensive chromosome/patch/haplotype/scaffold GTF; versionless stable-ID display mapping; original count-generation release unknown",
  DESeq2_outlier_summary = list(
    cook_cutoff = cook_cutoff,
    cook_exceedance_gene_count = sum(rowSums(cook_exceed) > 0),
    cook_exceedance_observation_count = sum(cook_exceed),
    genes_with_NA_pvalue = sum(is.na(output$pvalue)),
    replacement_assays = as.list(replacement_assays),
    count_replacement_detected = "originalCounts" %in% assayNames(dds),
    sample_diagnostics = sample_diagnostics
  ),
  dispersion_summary = list(
    fit_type = dispersion_fit_type,
    final_min = min(dispersions_final),
    final_median = median(dispersions_final),
    final_p95 = unname(quantile(dispersions_final, 0.95)),
    final_max = max(dispersions_final),
    gene_estimate_nonfinite = sum(!is.finite(disp_gene)),
    fitted_trend_nonfinite = sum(!is.finite(disp_fit)),
    beta_nonconverged = sum(!beta_convergence)
  ),
  pvalue_distribution_summary = list(
    finite_pvalue_count = length(finite_pvalues),
    decile_breaks = as.list(seq(0, 1, 0.1)),
    decile_counts = as.list(as.integer(pvalue_hist)),
    minimum_finite_pvalue = min(finite_pvalues),
    median_finite_pvalue = median(finite_pvalues)
  ),
  independent_filtering_summary = list(
    enabled = TRUE,
    alpha = 0.05,
    filter_statistic = "baseMean",
    filter_threshold = filter_threshold,
    filter_theta = filter_theta,
    padj_NA_with_finite_pvalue = sum(is.na(output$padj) & is.finite(output$pvalue)),
    pvalue_NA = sum(is.na(output$pvalue))
  ),
  ma_plot_ylim = as.list(c(-ma_limit, ma_limit)),
  ma_plot_clipping = "none; limits cover all finite log2 fold changes"
)
jsonlite::write_json(model_summary, file.path(expout, "exp003_c3_model_summary.json"),
                     pretty = TRUE, auto_unbox = TRUE, digits = 12, na = "null")
cat(sprintf("EXP003 DESeq2 complete: %s tested; %s padj<0.05; %s threshold-B (%s up, %s down).\n",
            nrow(output), model_summary$padj005, model_summary$thresholdB,
            model_summary$up, model_summary$down))
