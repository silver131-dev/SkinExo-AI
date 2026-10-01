# Third-party tools and assistance

Version entries are the versions recorded in the current repository environment or C3 run records. `NA` means no stable version was recorded. Listing a tool is disclosure, not a license review.

| Name | Version where known | Source | Purpose in completed work |
|---|---|---|---|
| OpenAI Codex | NA; hosted assistant version not recorded | OpenAI | Coding assistance, workflow construction, documentation support, and literature metadata verification. |
| Python | 3.12.3 in existing `.venv` | [Python Software Foundation](https://www.python.org/) | C1/C2 scripts, C3 artifact builder, C3.5 evidence-file generation, and C4 pathway analysis. |
| R | 4.3.3 | [R Project](https://www.r-project.org/) / Ubuntu package manifest | C3 count-based analysis runtime. |
| Bioconductor | 3.18 | [Bioconductor](https://www.bioconductor.org/) / local manifest | DESeq2 package ecosystem for C3. |
| DESeq2 | 1.42.0 | [Bioconductor DESeq2](https://bioconductor.org/packages/3.18/bioc/html/DESeq2.html) / local manifest | C3 negative-binomial differential expression. |
| pandas | 3.0.6 | [pandas](https://pandas.pydata.org/) / `requirements.txt` | Table input/output and metadata processing. |
| NumPy | 2.5.3 | [NumPy](https://numpy.org/) / `requirements.txt` | Numeric arrays and C2 calculations. |
| SciPy | 1.18.1 | [SciPy](https://scipy.org/) / `requirements.txt` | Scientific/statistical utilities in QC and artifact code. |
| scikit-learn | 1.9.1 | [scikit-learn](https://scikit-learn.org/) / `requirements.txt` | **Unsupervised PCA for C2 QC only**; no predictor trained. |
| Matplotlib | 3.11.2 | [Matplotlib](https://matplotlib.org/) / `requirements.txt` | Team-generated C2/C3/C4 scientific figures. |
| GSEApy | 1.3.1 | [GSEApy project](https://github.com/zqfang/GSEApy) / PyPI; `requirements.txt` | C4 preranked gene-set enrichment with gene-set permutations; no predictive model. |

R's resolved dependencies and archive SHA-256 values are in [exp001_c3_r_packages.tsv](../../configs/exp001_c3_r_packages.tsv); the Python versions are in [requirements.txt](../../requirements.txt). This table does not imply that every listed dependency was called in every checkpoint.

**OpenAI Codex was used for coding assistance, workflow construction, documentation support, and literature metadata verification. All scientific conclusions and submitted materials remain the responsibility of the participant and require independent review. Codex did not perform independent biological validation.**

**TODO before submission:** independently verify AI-assisted prose and metadata; review tool and software licenses against the planned public distribution.
