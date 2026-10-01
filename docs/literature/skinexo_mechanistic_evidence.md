# SkinExo mechanistic evidence map (EXP001-C3.5)

Verified 30 September 2026. IDs match `data/metadata/skinexo_evidence_matrix.csv`. `DIRECT` means the paper experimentally measured or directly analyzed the named endpoint in its own model; it does not imply a causal link across every arrow. Reviews are `REVIEW_SYNTHESIS` and contribute no independent experimental axis count. `NA` means the source did not establish the value.

## Provenance ledger

| ID | Verified source | Type and classification | Core use or caveat |
|---|---|---|---|
| P00 | [PubMed PMID 41161638](https://pubmed.ncbi.nlm.nih.gov/41161638/); [GEO GSE293186](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186); [full text PMC13348359](https://pmc.ncbi.nlm.nih.gov/articles/PMC13348359/) | Primary; `SAME_DATASET` | Mandatory EXP001 source; DOI 10.1016/j.jid.2025.10.584. Data statement also cites [INDIGO 10.25417/uic.30592964](https://doi.org/10.25417/uic.30592964). |
| L01 | [PubMed PMID 42798851](https://pubmed.ncbi.nlm.nih.gov/42798851/) | Review; `REVIEW_SYNTHESIS` | EV/macrophage/fibroblast synthesis; DOI 10.3389/fcell.2026.1917543. |
| L02 | [PubMed PMID 42713281](https://pubmed.ncbi.nlm.nih.gov/42713281/) | Review; `REVIEW_SYNTHESIS` | Stem-cell exosome synthesis; DOI 10.3389/fimmu.2026.1846916. |
| L03 | [PubMed PMID 40969665](https://pubmed.ncbi.nlm.nih.gov/40969665/) | Review; `REVIEW_SYNTHESIS` | Skin EV overview; DOI 10.2147/IJN.S548986. |
| L04 | [PubMed PMID 42137193](https://pubmed.ncbi.nlm.nih.gov/42137193/) | Review; `REVIEW_SYNTHESIS` | Barrier/chronic wound overview; DOI 10.2147/IJN.S598256; **2026**, not supplied 2025. |
| L05 | [PubMed PMID 41209696](https://pubmed.ncbi.nlm.nih.gov/41209696/); [Mendeley deposit](https://data.mendeley.com/datasets/gm29wd7b94/1) | Primary; `INDEPENDENT_EXTERNAL_EVIDENCE` | Rat MSC-sEV → rat macrophage; M2/inflammation and wound closure. Full title includes M2/p38 clause. |
| L06 | [PubMed PMID 41869020](https://pubmed.ncbi.nlm.nih.gov/41869020/); [full text PMC13003219](https://pmc.ncbi.nlm.nih.gov/articles/PMC13003219/) | Primary; `INDEPENDENT_EXTERNAL_EVIDENCE` | Human reconstructed skin, EV cargo profiles and phenotypes; no public omics accession found in data statement. |
| L07 | [PubMed PMID 38493383](https://pubmed.ncbi.nlm.nih.gov/38493383/) | Review; `REVIEW_SYNTHESIS` | Skin-on-chip methods; PubMed labels free article. |
| L08 | [PubMed PMID 39593715](https://pubmed.ncbi.nlm.nih.gov/39593715/); [full text PMC11591533](https://pmc.ncbi.nlm.nih.gov/articles/PMC11591533/) | Primary; `RELATED_EXTERNAL_EVIDENCE` | Perfused skin-on-chip and TNF-α/dexamethasone response; no EV intervention; data on request. |
| L09 | [PubMed PMID 41439953](https://pubmed.ncbi.nlm.nih.gov/41439953/) | Systematic review; `REVIEW_SYNTHESIS` | Scratch assay methods, not an independent migration experiment. |
| L10 | [PubMed PMID 35664010](https://pubmed.ncbi.nlm.nih.gov/35664010/); [GEO GSE141814](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE141814) | Primary reanalysis; `INDEPENDENT_EXTERNAL_EVIDENCE` relative to EXP001 | Exact title ends **“Fates.”** Reuses a 2019 mouse dataset with two pooled libraries, no EV treatment. |
| L11 | [PubMed PMID 39687464](https://pubmed.ncbi.nlm.nih.gov/39687464/); [full text PMC11647520](https://pmc.ncbi.nlm.nih.gov/articles/PMC11647520/) | Primary; `INDEPENDENT_EXTERNAL_EVIDENCE` | PMCID belongs to Kang et al.'s **epidermal stem-cell exosome/fibroblast** study, not the supplied scarless-versus-fibrotic title. |
| L12 | [PubMed PMID 39639168](https://pubmed.ncbi.nlm.nih.gov/39639168/); [PMC11810604](https://pmc.ncbi.nlm.nih.gov/articles/PMC11810604/) | Review; `REVIEW_SYNTHESIS` | Main article DOI **10.1038/s41592-024-02528-8**. Separate author correction DOI 10.1038/s41592-024-02578-y must not be substituted. Journal year 2025. |
| L13 | [CVPR 2026 official proceedings](https://openaccess.thecvf.com/content/CVPR2026/html/Chen_Intervention-Aware_Multiscale_Representation_Learning_from_Imaging_Phenomics_and_Perturbation_Transcriptomics_CVPR_2026_paper.html) | Primary computational; `RELATED_EXTERNAL_EVIDENCE` | Imaging/L1000 representation method; no skin EV model. DOI, PMID and PMCID not verified. |
| L14 | [NeurIPS 2025 official proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/ce02df43d66626bb7087ec699e20c7ea-Abstract-Datasets_and_Benchmarks_Track.html); [dataset/code](https://github.com/altoslabs/scGeneScope) | Primary dataset/methods; `RELATED_EXTERNAL_EVIDENCE` | DOI 10.52202/085713-4706; 28 chemicals in U2-OS, scRNA-seq and Cell Painting, no skin EV model. |
| L15 | [ICML 2026 FM4LS accepted papers](https://icml2026fm4ls.github.io/pages/accepted-paper.html); [OpenReview PDF](https://openreview.net/pdf?id=ACHMa1e8J1) | Primary computational; `RELATED_EXTERNAL_EVIDENCE` | **ICML workshop**, not supplied ICLR-related venue. Reuses L14 dataset, no independently verified DOI. |

Metadata not established by these official records is explicitly `NA` in the matrix; no DOI or accession was inferred from title similarity. L13's arXiv identifier is [2604.22832](https://arxiv.org/abs/2604.22832). L14's dataset is [altoslabs/scGeneScope](https://huggingface.co/datasets/altoslabs/scGeneScope), whose official code lists raw and processed downloads. L15 has [author code](https://huggingface.co/Sentinal4D/PhenoSeq), which is a model release rather than a new biological dataset.

## Evidence chain

```text
EV SOURCE
  ↓  P00 endothelial cells; L05 rat bone-marrow MSC; L06 adipose or cord MSC; L11 epidermal stem cells
EV CARGO
  ↓  P00 reports EV-associated FGF2; L06 profiles EV miRNAs/proteins but their causal roles remain candidates
RECIPIENT CELL
  ↓  P00/L11 fibroblasts; L05 macrophages; L06 fibroblasts and keratinocytes in reconstructed skin
MOLECULAR RESPONSE
  ↓  P00 ETV1–FGF2 response in same study; L05 p38 MAPK and macrophage polarization
TRANSCRIPTOMIC STATE
  ↓  P00 bulk RNA-seq; L05 rat macrophage RNA-seq; L06 reconstructed-skin bulk RNA-seq
P / M / E / A / I
  ↓  Direct P: P00,L06,L11. Direct M: P00,L11. Direct E: P00,L06,L11.
     Direct I: L05; L08 measures inflammatory drug response without EVs.
     No directly measured EV-induced angiogenesis among these studies.
REGENERATIVE / FIBROTIC CONTEXT
  ↓  L10 directly contrasts mouse regenerative/fibrotic wound states without EVs.
     P00 shows collagen-rich scar tissue; this does not prove regeneration.
PHENOTYPE
     P00 scratch closure/proliferation/collagen and mouse scar; L05 diabetic-rat closure;
     L06 skin thickness/ECM markers; L11 fibroblast assays and mouse closure.
```

Each line is a set of **observations in the named model**, not proof that one contiguous causal mechanism holds across papers. The cross-study arrow from EV cargo to recipient molecular response is directly supported for P00's FGF2/ETV1 work **within the EXP001 primary study**. L06's miRNA/protein cargo to specific phenotype is a hypothesis pending cargo perturbation. Moving macrophage L05 findings to EXP001 fibroblasts is a hypothesis. Moving L10 mouse regenerative/fibrotic states to human fibroblast EV response is a hypothesis. Reviews L01–L04/L07/L09/L12 provide synthesis or assay design only.

## Interpretation and circularity rules

- `SAME_DATASET`: P00/GSE293186 and its author DEG table; mechanistic experiments in P00 add within-study context but do not independently validate our C3 analysis.
- `RELATED_EXTERNAL_EVIDENCE`: L08 and L13–L15 support assay or method design in different systems, not EV-induced skin repair claims.
- `INDEPENDENT_EXTERNAL_EVIDENCE`: L05/L06/L10/L11 are separate studies or datasets; L10 is itself a **reanalysis** of GSE141814, so do not count the original series twice.
- `REVIEW_SYNTHESIS`: L01–L04/L07/L09/L12 may cite some of these primary studies and cannot be counted as new experiments.
- `HYPOTHESIS`: EV cargo → specific gene → P/M/E/A/I → regenerative fate links unsupported by direct perturbation in the relevant model.

The C4 question list is prespecified in `outputs/exp001/exp001_c3_5_evidence.json`. Freeze the term databases and gene-set construction before running C4, use the C3 raw-count statistical result unchanged, and report both supporting and opposing directions. No enrichment, scoring, or model fitting was performed here.
