# SkinExo-AI EXP002-C2R

## Objective

Adjudicate the EV_8 sample using technical records and unsupervised sample QC before any EXP002 differential expression, GSEA, or EXP001–EXP002 outcome comparison. The exclusion rules in [`configs/exp002_c2r_technical_criteria.json`](../configs/exp002_c2r_technical_criteria.json) were written before the metrics below were calculated. This review is reproducible with `.venv/bin/python experiments/exp002/02r_ev8_technical_review.py`. Per-sample metrics are in [`exp002_c2r_sample_technical_qc.csv`](../outputs/exp002/exp002_c2r_sample_technical_qc.csv); the complete machine-readable decision is in [`exp002_c2r_ev8_review.json`](../outputs/exp002/exp002_c2r_ev8_review.json).

## Why EV_8 Was Reviewed

EXP002-C2 classified EV_8 as `QC_REVIEW_NEEDED`: its exact-shared tximport estimated gene total was 1.80 times the 16-sample median, and it was distant in the first two PCs under three condition-blind feature choices. C2 retained the sample and did not establish a technical defect. The C1R dataset decision was `LIMITED_GO`; that generalization limit remains.

## Identity Chain

| Link or check | Authoritative/local evidence | Result |
| --- | --- | --- |
| GEO sample → name, condition, batch | [GSM7988524](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM7988524) and locally cached GSE251807 family SOFT: `EV_8`, NHDF exposed to small EVs, batch 2 | PASS |
| GEO sample → BioSample | GEO relation and [SAMN39054792](https://www.ebi.ac.uk/ena/browser/view/SAMN39054792), alias `GSM7988524`, title `EV_8`, EV treatment, batch 2 | PASS |
| GEO sample → SRA experiment | GEO relation and [SRX22996563](https://www.ncbi.nlm.nih.gov/sra?term=SRX22996563) | PASS |
| Experiment → run → BioSample | [ENA run record SRR27319309](https://www.ebi.ac.uk/ena/browser/view/SRR27319309) and locally cached PRJNA1055484 run table: one run with experiment `SRX22996563` and BioSample `SAMN39054792` | PASS |
| GEO sample → Salmon file | GEO supplementary URL, local file `GSM7988524_EV_8.quant.sf.gz.tabular.txt.gz`, and project metadata filename agree; gzip readable to EOF; columns and estimates valid | PASS |
| Salmon file → C2 aggregation | Full-file Salmon `NumReads` sum agrees with the original Salmon total recorded in C2 to rounding tolerance | PASS |
| Duplicate accession or byte-identical quantification | Selected GSM, BioSample, SRX, SRR, and quantification filenames are unique; EV_8 compressed quant file SHA-256 differs from the other 15 | PASS |

The identity chain supports the supplied mapping. It cannot prove distinct culture wells from accession uniqueness alone; the C1R culture-replication limitation remains.

## Sequencing Depth

ENA reports **54,035,352 read_count**, **16,210,605,600 base_count**, and **7,880,774,013 combined FASTQ bytes** for EV_8. The original Salmon `NumReads` sum is **95,330,727.150**; the exact-shared gene-level estimated-count total is **92,722,948.482**. Neither number is an original integer gene count.

| Quantity | EV_8 / all-16 median | EV_8 / EV median | EV_8 / batch-2 EV median |
| --- | ---: | ---: | ---: |
| ENA read_count | 1.837 | 1.837 | 1.654 |
| ENA base_count | 1.837 | 1.837 | 1.654 |
| Combined FASTQ bytes | 1.842 | 1.842 | 1.650 |
| Original Salmon NumReads sum | 1.811 | 1.811 | 1.609 |
| Exact-shared estimated gene total | 1.803 | 1.803 | 1.608 |

All five measures track a deeper run. High depth alone is not evidence of technical failure.

## Quantification

The descriptive ratio `original Salmon NumReads sum / ENA read_count` is **1.764** for EV_8, versus **1.778** across all 16 and **1.805** among batch-2 EV samples (medians). EV_8 is 0.992 and 0.977 times those medians. Its exact-shared transcript retention is **97.2645%**, comparable to other batch-2 EV libraries. No unusual EV_8-specific loss appears in these summaries.

**This ratio is not a mapping efficiency.** ENA `read_count` and Salmon estimated `NumReads` may differ in read, pair, and fragment definitions; the ratio exceeds one throughout the dataset. Original Salmon mapping-rate logs and the exact author index remain unavailable. No FASTQ files were downloaded or reprocessed.

## Expression Distribution

Metrics use the C2 reconstructed gene-level estimated counts, with 37,307 mapped genes. Detection uses CPM ≥1; shape measures use library-size CPM or count proportions, so deeper sequencing is not by itself interpreted as altered expression.

| Measure | EV_8 | Batch-2 EV median | All-sample median |
| --- | ---: | ---: | ---: |
| Genes with CPM ≥1 | 13,206 | 13,209.5 | 13,235 |
| Genes with nonzero estimates | 18,932 | 18,442.5 | 18,465.5 |
| Zero-gene fraction | 0.4925 | 0.5057 | 0.5050 |
| Median log2(CPM+1), CPM ≥1 genes | 4.615 | 4.660 | 4.668 |
| 90th percentile log2(CPM+1) | 6.999 | 7.020 | 7.026 |
| 99th percentile log2(CPM+1) | 9.492 | 9.521 | 9.552 |
| Top 10 genes' count fraction | 0.1405 | 0.1349 | 0.1262 |
| Top 100 genes' count fraction | 0.3216 | 0.3055 | 0.3025 |
| Normalized count entropy | 0.7450 | 0.7514 | 0.7533 |

The higher top-gene fractions are modest against batch-2 EV peers. The jointly preregistered catastrophic-distribution review trigger (less than half the batch-2 EV median detected genes **and** more than twice its top-10 fraction) was not met. These summaries do not establish that every gene is unaffected by technical variation.

## Correlation

Pearson correlations use the frozen C2 log2(CPM+1) matrix with 13,724 condition-blind filtered genes.

- EV_8 versus same-batch EV_5/6/7: **0.9850 / 0.9846 / 0.9840**, mean **0.9845**.
- EV_8 versus other-batch EV_1–4: mean **0.9481**; lowest, EV_3 at **0.9448**.
- EV_8 versus controls: mean **0.9657**; batch-2 controls are 0.9793–0.9824.
- Its nearest correlation neighbor is **EV_5** (0.9850). Its mean correlation with all other samples is **0.9648**, within the 16-sample range **0.9634–0.9708**. Its mean correlation with batch-2 samples is **0.9820**, the lowest of the 16 within-batch means but close to the next values.

Correlation is descriptive sample QC, not a basis for treatment-effect inference or exclusion by itself.

## PCA Extremeness

The predeclared distance is Euclidean nearest-neighbor distance in **PC1–PC2 only**, divided by the median nearest-neighbor distance of all 16 samples. PCA was fitted in C2 without condition labels; feature selection was condition-blind. The first two PCs omit remaining variance.

| Feature set | EV_8 nearest distance | Ratio to 16-sample median | Rank, largest first | Next largest sample / distance |
| --- | ---: | ---: | ---: | --- |
| All 13,724 filtered genes | 11.23 | 5.20 | 1/16 | EV_3 / 5.51 |
| Top 5,000 variable genes | 13.30 | 6.32 | 1/16 | EV_3 / 4.72 |
| Top 2,000 variable genes | 14.72 | 8.14 | 1/16 | EV_3 / 3.51 |

EV_8 is also the farthest sample from its leave-one-out batch-peer centroid in all three choices; its nearest neighbor is in its own batch. EV_3 is the next most isolated in the two-PC projection, so the review did not ignore other samples. EV_8 is more extreme than EV_3 under each feature set. The 2× median distance was a **review trigger fixed in C2**, not an exclusion criterion. We did not inspect any DE or treatment-separation outcome to make this decision.

EV_3 has distance ratios **2.55, 2.25, and 1.94** under the same feature sets, crossing the C2 review trigger in the first two. Its ENA read_count is **22,461,058**, its estimated gene total **38,978,692**, and it has **13,253** genes at CPM ≥1. Its mean correlation with the other batch-1 EV samples is **0.9908**. This secondary distance flag is documented; the available technical summaries do not show a critical failure. It was not excluded.

## Technical Exclusion Criteria

The predeclared affirmative reasons were: identity/condition/batch or quantification-file mismatch; confirmed biological duplication; unreadable/corrupt/incomplete quantification; incompatible library metadata; severe quantification failure with independent technical corroboration; or catastrophic expression-distribution abnormality with independent evidence of technical failure. High depth, PCA distance, biological uniqueness, and any future treatment result were explicitly insufficient alone. No affirmative reason was demonstrated.

## EV_8 Decision

**RETAIN.** All identity checks pass, measured depth and quantification totals move together, the cross-sample quantification proxy is ordinary, expression concentration is not catastrophic, and within-batch correlations remain high. Persistent PCA extremeness is retained as a caution, not converted into a technical defect. No sample was removed during C2R.

## Primary C3 Analysis

The frozen future primary analysis includes **all 16 samples** (8 MSC-sEV, 8 DMEM controls), exact-shared Salmon transcript estimates aggregated with tximport and the compatible GENCODE v44 map, pre-DE estimated count ≥10 in at least 4 libraries, and the additive design **`~ batch + condition`**. The contrast is MSC-sEV versus DMEM, with positive log2FC meaning higher after MSC-sEV. A count-based framework with tximport gene-length offsets remains required. No model was fitted here.

## Sensitivity Analysis

A separate future **15-sample** analysis excludes EV_8 only (7 MSC-sEV, 8 controls; batch 2: 3 EV, 4 control). It uses the same count-based framework, filter threshold, design, contrast, and reporting thresholds. It is a robustness analysis only; the 16-sample result stays primary even if the sensitivity result looks stronger. Both fits will report tested-gene coverage differences.

## Frozen Robustness Metrics

1. Pearson correlation of log2FC across shared tested genes.
2. Spearman correlation of log2FC across shared tested genes.
3. Log2FC direction concordance across shared tested genes, with zero and NA exclusions reported.
4. Count and Jaccard overlap of `padj < 0.05` genes.
5. Count and Jaccard overlap of `padj < 0.05 & |log2FC| >= 1` genes.
6. P/M/E/A/I GSEA direction stability under the already frozen program and term-family rules.
7. Pearson/Spearman NES correlation across common eligible GSEA terms.

Null, discordant, and untestable findings must be reported. These metrics compare the two EXP002 fits; they do not change the frozen primary EXP001–EXP002 validation endpoint.

## Batch Model Decision

Keep **`~ batch + condition`** as the primary model. Two batches each contain 4 EV and 4 control samples, so condition is not confounded with batch. The scientific target is the average condition effect across batches. A `batch:condition` interaction is not included in the primary model: two batches alone do not require one, and selecting it from PCA or future significance would change the question after observing data. The 15-sample sensitivity model remains estimable despite its 3/4 EV/control allocation in batch 2.

## Remaining Limitations

- One documented recipient donor lot and unknown EV-preparation independence prevent donor-level and EV-preparation-level generalization. **C1R remains LIMITED_GO.**
- Author Salmon index and mapping-rate logs are unavailable. GENCODE v44 is a compatible mapping, not verified as the authors' index.
- The ENA/Salmon ratio is only a cross-sample proxy because its numerator and denominator may use different units.
- Raw FASTQ read quality, contamination, duplication, and library-complexity metrics were not assessed; absence of a demonstrated defect does not prove absence of all technical problems.
- EV_8 remains an extreme PCA point. Sensitivity analysis is mandatory in C3, and discordance must be reported without replacing the primary analysis.

## C2R Decision

**PASS — EV_8 RETAINED; EXP002-C2 final status: PASS WITH LIMITATIONS.** This resolves the C2 sample-review flag for proceeding to a *future* C3 under the restricted C1R design and preregistered sensitivity analysis. The original C2 JSON remains unchanged as the historical `REVIEW REQUIRED` checkpoint. No differential expression, GSEA, or EXP001–EXP002 biological comparison was performed in C2R.
