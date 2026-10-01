"""Regenerate the EXP001-C3.5 metadata artifacts from audited source records.

This script reads C3 outputs; it does not rerun or modify C1-C3 or perform C4 analysis.
Source URLs and interpretation notes are in docs/literature/skinexo_mechanistic_evidence.md.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/exp001"
META = ROOT / "data/metadata"
NA = "NA"
N = "NOT_ASSESSED"
D = "DIRECT"
I = "INDIRECT"
E = "INDEPENDENT_EXTERNAL_EVIDENCE"
R = "RELATED_EXTERNAL_EVIDENCE"
V = "REVIEW_SYNTHESIS"


def paper(id, title, authors, year, journal, doi=NA, pmid=NA, pmcid=NA,
          article_type="Primary research", status="VERIFIED", correction=NA,
          oa="OPEN_ACCESS", species=NA, model=NA, ev_source=NA, ev_type=NA,
          ev_cargo=NA, recipient=NA, omics=NA, axes=None, regen=N, fibrotic=N,
          regen_actual=NA, fibrotic_actual=NA, settings=NA, dataset=NA,
          repository=NA, accession=NA, data_type=NA, sample_count=NA,
          raw=NA, processed=NA, role=NA, candidate=NA, evidence_class=None,
          notes=NA, url=NA):
    primary = article_type not in ("Narrative review", "Systematic review")
    row = dict(paper_id=id, title=title, authors=authors, year=year,
               journal=journal, doi=doi, pmid=pmid, pmcid=pmcid,
               article_type=article_type, verification_status=status,
               correction_note=correction, open_access=oa,
               primary_research=primary, review=not primary,
               evidence_source_type="PRIMARY_EXPERIMENT" if primary else V,
               evidence_class=evidence_class or (R if primary else V),
               species=species, model_type=model, EV_source=ev_source,
               EV_type=ev_type, EV_cargo=ev_cargo, recipient_cell=recipient,
               omics_type=omics, regenerative_evidence=regen,
               fibrotic_evidence=fibrotic,
               regenerative_actual_evidence=regen_actual,
               fibrotic_actual_evidence=fibrotic_actual,
               dataset_available=dataset, dataset_repository=repository,
               dataset_accession=accession, dataset_data_type=data_type,
               dataset_sample_count=sample_count, raw_available=raw,
               processed_available=processed, role_in_skinexo=role,
               candidate_EXP=candidate, notes=notes, verification_url=url)
    for col in ("P_proliferation", "M_migration", "E_ecm",
                "A_angiogenesis", "I_inflammation"):
        row[col] = (axes or {}).get(col[0], N)
    for cell, pattern in (("fibroblast", "fibroblast"),
                          ("keratinocyte", "keratinocyte"),
                          ("endothelial", "endothelial"),
                          ("macrophage", "macrophage")):
        row[cell] = pattern in recipient.lower() if recipient != NA else False
    row["other_cell"] = recipient if recipient != NA and not any(
        row[c] for c in ("fibroblast", "keratinocyte", "endothelial", "macrophage")) else NA
    omics_lower = omics.lower() if omics != NA else ""
    for field, token in (("bulk_rna_seq", "bulk RNA-seq"),
                         ("scrna_seq", "scRNA-seq"),
                         ("spatial_transcriptomics", "spatial transcriptomics"),
                         ("mirna_seq", "miRNA-seq"),
                         ("proteomics", "proteomics"),
                         ("metabolomics", "metabolomics"),
                         ("imaging", "imaging")):
        row[field] = token.lower() in omics_lower
    for field, token in (("in_vitro", "in_vitro"), ("ex_vivo", "ex_vivo"),
                         ("in_vivo", "in_vivo"), ("skin_on_chip", "skin_on_chip"),
                         ("3d_skin_model", "3d_skin_model")):
        row[field] = token in settings.split(";")
    for exp in range(1, 7):
        row[f"EXP{exp:03d}"] = f"EXP{exp:03d}" in candidate.split(";")
    return row


PAPERS = [
    paper("L01", "Extracellular vesicles in wound healing and scar formation: molecular regulation of macrophages, fibroblasts, and their crosstalk.", "Liu T; Liu Y; Liu Y; Wen D; Sun J; Zhang Y; Gao Y; Zheng D", 2026, "Frontiers in Cell and Developmental Biology", "10.3389/fcell.2026.1917543", "42798851", "PMC13613145", article_type="Narrative review", role="EV wound-repair synthesis", candidate="EXP004;EXP006", url="https://pubmed.ncbi.nlm.nih.gov/42798851/"),
    paper("L02", "Application of stem cell-derived exosomes in skin wound healing: mechanisms, prospects, and challenges.", "Li Y; Zheng F; Bai Y; Yu Y; Zhang R; Feng Q; Yu Y; Zhu L; Wang D; Liu H", 2026, "Frontiers in Immunology", "10.3389/fimmu.2026.1846916", "42713281", "PMC13551746", article_type="Narrative review", role="EV wound-repair synthesis", candidate="EXP004;EXP006", url="https://pubmed.ncbi.nlm.nih.gov/42713281/"),
    paper("L03", "Extracellular Vesicles in Skin: Biological Function and Therapeutic Potential.", "Yuan S; Jin M; Zhang Y; Zhang M; Yuan M; Ding X; Wang J", 2025, "International Journal of Nanomedicine", "10.2147/IJN.S548986", "40969665", "PMC12442902", article_type="Narrative review", role="Skin EV overview", candidate="EXP004;EXP006", url="https://pubmed.ncbi.nlm.nih.gov/40969665/"),
    paper("L04", "Role of Extracellular Vesicles in Skin Barrier Repair: Applications in Atopic Dermatitis and Chronic Wounds.", "Khoo L; Chin YZ; Law JX", 2026, "International Journal of Nanomedicine", "10.2147/IJN.S598256", "42137193", "PMC13168907", article_type="Narrative review", status="CORRECTED", correction="Supplied year 2025; journal record is 2026.", role="Barrier/immune synthesis", candidate="EXP004;EXP006", url="https://pubmed.ncbi.nlm.nih.gov/42137193/"),
    paper("L05", "Mesenchymal stem cell-derived small extracellular vesicles-loaded GelMA microspheres enhance diabetic wound healing by promoting M2 macrophage polarization through p38 MAPK inhibition.", "Li W; Chen J; Yu L; Ding L; Zhang X; Yan L; Shi M", 2025, "Materials Today Bio", "10.1016/j.mtbio.2025.102423", "41209696", "PMC12590144", status="CORRECTED", correction="Supplied title omitted the M2 macrophage/p38 MAPK clause.", species="Rat", model="Rat bone-marrow-derived macrophages; diabetic rat wound", ev_source="Rat bone-marrow mesenchymal stem cells", ev_type="Small EV", recipient="Macrophage", omics="bulk RNA-seq", axes={"I": D}, regen=I, regen_actual="Improved diabetic wound closure in rats; scarless repair not measured", settings="in_vitro;in_vivo", dataset="YES", repository="Mendeley Data", accession="10.17632/gm29wd7b94.1", data_type="RNA-seq", sample_count="9", raw=NA, processed=NA, role="External EV macrophage/immune mechanism", candidate="EXP002;EXP004;EXP006", evidence_class=E, notes="n=3/group in deposited rat BMDM RNA-seq; LPS and EV-LPS design differs from EXP001. GelMA co-intervention in vivo.", url="https://pubmed.ncbi.nlm.nih.gov/41209696/"),
    paper("L06", "Extracellular vesicles modulate skin aging biomarkers in a 3D reconstructed full-thickness skin model.", "Teng Y; Bou Samra E; Girardeau-Hubert S; Betts RJ; Juchaux F; Marat X; Fallou B; Zhong L; De Vecchi R; Huang N; Zheng Q; Gao Y; Roy DC; Wang P", 2026, "Frontiers in Cell and Developmental Biology", "10.3389/fcell.2026.1784998", "41869020", "PMC13003219", species="Human", model="Primary skin cells and 3D reconstructed full-thickness skin", ev_source="Adipose-derived stem cells; umbilical-cord mesenchymal stem cells", ev_type="EV", ev_cargo="miRNA and protein cargo profiled; candidate mediators, not proven causal", recipient="Fibroblast; keratinocyte", omics="bulk RNA-seq; miRNA-seq; proteomics; imaging", axes={"P": D, "E": D}, regen=I, regen_actual="Proliferation, epidermal thickness, collagen IV and fibrillin-1 measured; scarless regeneration not tested", settings="in_vitro;3d_skin_model", dataset="SUPPLEMENT_ONLY", repository="Article supplementary material", data_type="bulk RNA-seq; miRNA-seq; proteomics", raw=NA, processed="PARTIAL", role="External EV skin model and cargo response", candidate="EXP002;EXP003;EXP004;EXP006", evidence_class=E, notes="No public omics repository accession in data availability statement; source/model differ from EXP001.", url="https://pubmed.ncbi.nlm.nih.gov/41869020/"),
    paper("L07", "Advances in Skin-on-a-Chip Technologies for Dermatological Disease Modeling.", "Cho SW; Malick H; Kim SJ; Grattoni A", 2024, "Journal of Investigative Dermatology", "10.1016/j.jid.2024.01.031", "38493383", article_type="Narrative review", oa="FREE_TO_READ", role="Skin-on-chip design review", candidate="EXP003;EXP004", url="https://pubmed.ncbi.nlm.nih.gov/38493383/"),
    paper("L08", "Full-Thickness Perfused Skin-on-a-Chip with In Vivo-Like Drug Response for Drug and Cosmetics Testing.", "Rhee S; Xia C; Chandra A; Hamon M; Lee G; Yang C; Guo Z; Sun B", 2024, "Bioengineering", "10.3390/bioengineering11111055", "39593715", "PMC11591533", species="Human", model="Perfused full-thickness skin-on-chip", recipient="Fibroblast; keratinocyte", omics="imaging", axes={"I": D}, settings="in_vitro;skin_on_chip;3d_skin_model", dataset="ON_REQUEST", role="Skin-chip assay design; no EV intervention", candidate="EXP003;EXP004", evidence_class=R, notes="TNF-alpha/dexamethasone inflammatory drug response measured. Data available on reasonable request, no public accession.", url="https://pubmed.ncbi.nlm.nih.gov/39593715/"),
    paper("L09", "Microfluidic-Based Scratch Assays for Wound Healing Studies: A Systematic Review.", "Oliveira FA; Valle NME; Silva KFD; Alves AH; Galanciak MCS; Rosário GM; Mamani JB; Nucci MP; Gamarra LF", 2025, "Cells", "10.3390/cells14241931", "41439953", "PMC12731330", article_type="Systematic review", role="Migration assay design synthesis", candidate="EXP004", url="https://pubmed.ncbi.nlm.nih.gov/41439953/"),
    paper("L10", "Single-Cell RNA-seq Analysis Reveals Cellular Functional Heterogeneity in Dermis Between Fibrotic and Regenerative Wound Healing Fates.", "Chen CJ; Kajita H; Takaya K; Aramaki-Hattori N; Sakai S; Asou T; Kishi K", 2022, "Frontiers in Immunology", "10.3389/fimmu.2022.875407", "35664010", "PMC9156976", status="CORRECTED", correction="Supplied title omitted the final word 'Fates'.", species="Mouse", model="Day-18 murine large skin wounds; reanalysis of GSE141814", recipient="Fibroblast; macrophage; endothelial cell; pericyte", omics="scRNA-seq", axes={"P": I, "M": I, "E": I, "A": I, "I": I}, regen=D, fibrotic=D, regen_actual="Regenerative wound dermis and EN1-negative/positive myofibroblast states compared", fibrotic_actual="Fibrotic wound dermis and myofibroblast/macrophage states compared", settings="in_vivo", dataset="YES_REUSED", repository="GEO", accession="GSE141814", data_type="scRNA-seq", sample_count="2 pooled libraries", raw="YES", processed="YES", role="External regenerative/fibrotic context; secondary reanalysis", candidate="EXP004", evidence_class=E, notes="GSE141814 predates this paper; two pooled libraries, each from 6-8 wounds, are not independent biological replicate libraries. No EV exposure.", url="https://pubmed.ncbi.nlm.nih.gov/35664010/"),
    paper("L11", "Epidermal stem cell-derived exosomes improve wound healing by promoting the proliferation and migration of human skin fibroblasts.", "Kang D; Wang X; Chen W; Mao L; Zhang W; Shi Y; Xie J; Yang R", 2024, "Burns & Trauma", "10.1093/burnst/tkae047", "39687464", "PMC11647520", status="CORRECTED", correction="Supplied PMCID points to this EV-fibroblast paper, not the supplied scarless-versus-fibrotic landscape title; that title was not verified.", species="Human; mouse", model="Human skin fibroblast culture; mouse wound", ev_source="Epidermal stem cells", ev_type="Exosome", recipient="Fibroblast", omics="bulk RNA-seq; imaging", axes={"P": D, "M": D, "E": D}, regen=I, regen_actual="Proliferation, migration, collagen synthesis and wound closure measured; scarless outcome not demonstrated", settings="in_vitro;in_vivo", dataset="ON_REQUEST", role="External fibroblast EV phenotypes", candidate="EXP002;EXP004;EXP006", evidence_class=E, notes="Data available from corresponding author on request; collagen synthesis alone does not identify regenerative fate.", url="https://pubmed.ncbi.nlm.nih.gov/39687464/"),
    paper("L12", "Cell Painting: a decade of discovery and innovation in cellular imaging.", "Seal S; Trapotsi MA; Spjuth O; Singh S; Carreras-Puigvert J; Greene N; Bender A; Carpenter AE", 2025, "Nature Methods", "10.1038/s41592-024-02528-8", "39639168", "PMC11810604", article_type="Narrative review", oa="FREE_PMC_MANUSCRIPT", role="Imaging phenomics design synthesis", candidate="EXP003;EXP005", notes="Main article DOI verified; separate author correction has DOI 10.1038/s41592-024-02578-y. Journal year 2025; online first 2024.", url="https://pubmed.ncbi.nlm.nih.gov/39639168/"),
    paper("L13", "Intervention-Aware Multiscale Representation Learning from Imaging Phenomics and Perturbation Transcriptomics.", "Chen J; Liu R; Gu Z; Zhang P", 2026, "Proceedings of CVPR", article_type="Primary computational methods", species="Human cell lines", model="Cell Painting and RxRx perturbation benchmark", recipient="Other cell lines", omics="bulk RNA-seq; imaging", dataset="YES_REUSED", repository="Public Cell Painting/RxRx/L1000 sources", accession=NA, data_type="Perturbation imaging; L1000 expression", raw=NA, processed=NA, role="Future multimodal method reference; no skin EV evidence", candidate="EXP003;EXP005", evidence_class=R, notes="Reuses public benchmark data; no single paper-specific omics accession verified. arXiv:2604.22832.", url="https://openaccess.thecvf.com/content/CVPR2026/html/Chen_Intervention-Aware_Multiscale_Representation_Learning_from_Imaging_Phenomics_and_Perturbation_Transcriptomics_CVPR_2026_paper.html"),
    paper("L14", "scGeneScope: A Treatment-Matched Single Cell Imaging and Transcriptomics Dataset and Benchmark for Treatment Response Modeling.", "Dapello J; Nassar M; Eksi R; Wang B; Gagnon-Marchand J; Gao K; Baharlouei A; Thrush K; Riehs N; Peterson A; Tolpadi A; Rajagopal A; Miller H; Conard A; Alvarez-Melis D; Stark R; Bianco S; Levine M; Amini A; Lu AX; Fusi N; Pandya R; Pedoia V; El-Samad H", 2025, "NeurIPS Datasets and Benchmarks Track", "10.52202/085713-4706", article_type="Primary dataset/methods", species="Human cell line", model="U2-OS chemical perturbations", recipient="U2-OS osteosarcoma cell", omics="scRNA-seq; imaging", dataset="YES", repository="Hugging Face", accession="altoslabs/scGeneScope", data_type="scRNA-seq; Cell Painting", raw="YES", processed="YES", role="Future multimodal benchmark; non-skin, non-EV", candidate="EXP003;EXP005", evidence_class=R, notes="28 chemicals, five replicates in two rounds; imaging and scRNA-seq are treatment-matched, not cell-paired. Noncommercial dataset license.", url="https://proceedings.neurips.cc/paper_files/paper/2025/hash/ce02df43d66626bb7087ec699e20c7ea-Abstract-Datasets_and_Benchmarks_Track.html"),
    paper("L15", "Cell Painting Generates Single-Cell Transcriptomics via Conditional Diffusion.", "Naidoo R; Hu J; Tripodi G; Bakal C; Chakraborti T", 2026, "ICML FM4LS workshop / OpenReview", article_type="Primary computational methods", status="CORRECTED", correction="Supplied ICLR-related venue; official accepted-paper list identifies ICML 2026 FM4LS workshop.", species="Human cell line", model="U2-OS scGeneScope benchmark", recipient="U2-OS osteosarcoma cell", omics="scRNA-seq; imaging", dataset="YES_REUSED", repository="Hugging Face", accession="altoslabs/scGeneScope", data_type="scRNA-seq; Cell Painting", raw="YES", processed="YES", role="Future image-to-expression method reference; no skin EV evidence", candidate="EXP003;EXP005", evidence_class=R, notes="Reuses L14 dataset, not independent biological validation; model outputs synthetic embeddings. DOI/PMID/PMCID unverified.", url="https://icml2026fm4ls.github.io/pages/accepted-paper.html"),
    paper("P00", "The Role of Endothelial Cell-Derived Extracellular Vesicles in Modulating Fibroblast Function in Skin Wound Healing.", "Yuan H; Salapatas AM; Leonardo TR; Han C; Vegesna B; Debnath K; Chen L; Ravindran S; DiPietro LA", 2026, "Journal of Investigative Dermatology", "10.1016/j.jid.2025.10.584", "41161638", "PMC13348359", species="Human; mouse", model="Primary human dermal fibroblasts at 72 h; mouse skin wound", ev_source="Endothelial cells", ev_type="EV", ev_cargo="FGF2 on EVs; ETV1 response", recipient="Fibroblast", omics="bulk RNA-seq; imaging", axes={"P": D, "M": D, "E": D}, regen=N, fibrotic=I, fibrotic_actual="Mouse wounds showed increased collagen density and fibroblast quantity in scar tissue; not proof of anti-fibrotic repair", settings="in_vitro;in_vivo", dataset="YES", repository="GEO; INDIGO", accession="GSE293186; 10.25417/uic.30592964", data_type="bulk RNA-seq; primary study data", sample_count="6 for EXP001 72-h comparison", raw="YES", processed="YES", role="EXP001_PRIMARY_DATA_SOURCE", candidate="EXP001;EXP004;EXP006", evidence_class="SAME_DATASET", notes="Includes scratch migration, mechanistic and mouse experiments beyond EXP001; any concordance with C3 is same-study evidence. ETV1 functional/FGF2 analysis reported.", url="https://pubmed.ncbi.nlm.nih.gov/41161638/"),
]


DATASETS = [
    dict(dataset_id="GSE293186", study_id="P00", repository="GEO", species="Human", model="Primary dermal fibroblasts; 72 h ECEV vs CTRL", EV_source="Endothelial cells", recipient_cell="Fibroblast", omics_type="bulk RNA-seq", sample_count=6, control_available="YES", raw_available="YES", processed_available="YES", P=D, M=N, E=D, A=N, I=N, regenerative_context=N, fibrotic_context=I, candidate_EXP="EXP001;EXP004;EXP006", access_url="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293186", notes="SAME_DATASET; not independent validation"),
    dict(dataset_id="10.17632/gm29wd7b94.1", study_id="L05", repository="Mendeley Data", species="Rat", model="LPS-treated bone-marrow-derived macrophages; 3 conditions", EV_source="Bone-marrow MSC", recipient_cell="Macrophage", omics_type="bulk RNA-seq", sample_count=9, control_available="YES", raw_available=NA, processed_available=NA, P=N, M=N, E=N, A=N, I=D, regenerative_context=I, fibrotic_context=N, candidate_EXP="EXP002;EXP004;EXP006", access_url="https://data.mendeley.com/datasets/gm29wd7b94/1", notes="n=3/group per official deposit; sample/file formats not inspected; species/model mismatch with EXP001"),
    dict(dataset_id="GSE141814", study_id="L10", repository="GEO", species="Mouse", model="Day-18 fibrotic vs regenerative large wounds", EV_source=NA, recipient_cell="Dermal multicellular", omics_type="scRNA-seq", sample_count="2 pooled libraries", control_available="NO_EV_CONTROL", raw_available="YES", processed_available="YES", P=I, M=I, E=I, A=I, I=I, regenerative_context=D, fibrotic_context=D, candidate_EXP="EXP004", access_url="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE141814", notes="Original GEO series predates L10 reanalysis; each library pooled from 6-8 wounds; not independent replicate libraries"),
    dict(dataset_id="altoslabs/scGeneScope", study_id="L14;L15", repository="Hugging Face", species="Human cell line", model="U2-OS; 28 chemical interventions", EV_source=NA, recipient_cell="U2-OS osteosarcoma cell", omics_type="scRNA-seq; Cell Painting", sample_count=NA, control_available="YES", raw_available="YES", processed_available="YES", P=N, M=N, E=N, A=N, I=N, regenerative_context=N, fibrotic_context=N, candidate_EXP="EXP003;EXP005", access_url="https://huggingface.co/datasets/altoslabs/scGeneScope", notes="Treatment-matched modalities, non-skin, no EV; ~80 GB scRNA and ~186 GB imaging per official code; noncommercial license"),
]


GENES = "HGF ETV1 TOP2A NBL1 HMGA2 PHLDA1 SLC14A1 CENPF ANPEP PSAT1 CCDC80 TAGLN OXTR GFRA1 IGFBP5 GRIA1 ADM2 SLC7A11 SEMA3D".split()
QUESTIONS = [
    dict(id="Q1", question="Are cell-cycle and proliferation programs represented in the ECEV response?", methods="ORA;GSEA", databases="GO Biological Process;Reactome;MSigDB Hallmark", rationale="Direct proliferation measurements in P00, L06, L11; P00 is same study."),
    dict(id="Q2", question="Are migration and motility programs represented?", methods="ORA;GSEA", databases="GO Biological Process;Reactome", rationale="L11 directly measured fibroblast migration; this is external EV evidence."),
    dict(id="Q3", question="Are ECM organization/remodeling programs altered, and in which direction?", methods="ORA;GSEA", databases="GO Biological Process;Reactome", rationale="P00, L06, L11 measured ECM-related outcomes; more collagen does not imply regeneration."),
    dict(id="Q4", question="Are angiogenesis or endothelial-interaction programs represented?", methods="ORA;GSEA", databases="GO Biological Process;Reactome", rationale="Endothelial EV source in P00 motivates the question but angiogenesis was not directly measured in EXP001."),
    dict(id="Q5", question="Are inflammatory/immune programs altered in fibroblasts?", methods="ORA;GSEA", databases="GO Biological Process;Reactome;MSigDB Hallmark", rationale="L05 directly measured macrophage inflammatory response in a different model; applicability to fibroblasts is unresolved."),
    dict(id="Q6", question="Does the ranked response overlap externally defined regenerative or fibrotic skin-repair programs?", methods="GSEA;ORA", databases="Externally defined skin-repair signatures; GO Biological Process;Reactome", rationale="Use independent signatures with species and cell-type mapping and non-overlapping training data; GSE141814 has pooled mouse libraries."),
]


def main():
    c3 = json.loads((OUT / "exp001_c3_de.json").read_text())
    if not c3.get("overall_pass") or not c3.get("c1_overall_pass") or not c3.get("c2_overall_pass"):
        raise RuntimeError("C1/C2/C3 pass required")
    all_de = pd.read_csv(OUT / "differential_expression_all.csv")
    sig = pd.read_csv(OUT / "differential_expression_significant.csv")
    if len(all_de) != c3["genes_tested"] or len(sig) != c3["threshold_b_total"]:
        raise RuntimeError("C3 artifacts are inconsistent")
    if len(PAPERS) != 16 or len({p['paper_id'] for p in PAPERS}) != 16:
        raise RuntimeError("Expected 15 candidates plus primary study")
    codes = {N, I, D, "CONFLICTING"}
    for p in PAPERS:
        for key in ("P_proliferation", "M_migration", "E_ecm", "A_angiogenesis", "I_inflammation", "regenerative_evidence", "fibrotic_evidence"):
            if p[key] not in codes:
                raise RuntimeError(f"Invalid code: {p['paper_id']} {key}")
        if p['review'] and any(p[k] != N for k in ("P_proliferation", "M_migration", "E_ecm", "A_angiogenesis", "I_inflammation")):
            raise RuntimeError("Review synthesis cannot be coded as measured axis evidence")
    META.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(PAPERS).to_csv(META / "skinexo_evidence_matrix.csv", index=False, na_rep=NA)
    pd.DataFrame(DATASETS).to_csv(META / "skinexo_dataset_catalog.csv", index=False, na_rep=NA)

    bridge = []
    for gene in GENES:
        hit = all_de.loc[all_de.gene_symbol == gene]
        if len(hit) != 1:
            raise RuntimeError(f"Ambiguous C3 symbol {gene}: {len(hit)} rows")
        de = hit.iloc[0]
        row = dict(gene=gene, gene_id=de.gene_id, C3_log2FC=de.log2FoldChange,
                   C3_padj=de.padj, literature_P=N, literature_M=N,
                   literature_E=N, literature_A=N, literature_I=N,
                   regenerative_context=N, fibrotic_context=N,
                   evidence_level="INSUFFICIENT", evidence_class="HYPOTHESIS",
                   supporting_study_ids=NA,
                   notes="No gene-specific functional evidence in screened external primary studies; C3 differential expression alone does not establish function.")
        if gene == "ETV1":
            row.update(literature_P=D, literature_E=I, fibrotic_context=I,
                       evidence_level=D, evidence_class="SAME_DATASET",
                       supporting_study_ids="P00",
                       notes="P00 reports ETV1 perturbation/FGF2-linked fibroblast response in the same primary study; not independent validation of C3. ECM/scar link is indirect.")
        elif gene == "TAGLN":
            row.update(evidence_level=I, evidence_class="INDEPENDENT_EXTERNAL_EVIDENCE",
                       supporting_study_ids="L10",
                       notes="L10 lists Tagln as a pericyte cluster marker in mouse wound scRNA-seq; cell-type context differs from EXP001 fibroblasts and does not establish wound-repair direction.")
        bridge.append(row)
    pd.DataFrame(bridge).to_csv(OUT / "c3_literature_bridge.csv", index=False, na_rep=NA)

    up = sig.loc[sig.log2FoldChange > 0].sort_values("padj").head(10)
    down = sig.loc[sig.log2FoldChange < 0].sort_values("padj").head(10)
    evidence_summary = dict(contrast=c3["contrast"], genes_tested=c3["genes_tested"],
                            padj_lt_0_05=c3["padj_lt_0_05"],
                            threshold_b_total=c3["threshold_b_total"],
                            upregulated=c3["threshold_b_up"],
                            downregulated=c3["threshold_b_down"],
                            strongest_up=up[["gene_symbol", "log2FoldChange", "padj"]].to_dict("records"),
                            strongest_down=down[["gene_symbol", "log2FoldChange", "padj"]].to_dict("records"),
                            author_concordance=c3["author_deg_concordance"],
                            interpretation="Computational C3 evidence only; no phenotype inferred")
    (OUT / "c3_evidence_summary.json").write_text(json.dumps(evidence_summary, indent=2) + "\n")

    corrected = [p for p in PAPERS if p["verification_status"] == "CORRECTED"]
    direct_counts = {x: sum(p[f"{x}_{name}"] == D and p["primary_research"] for p in PAPERS)
                     for x, name in (("P", "proliferation"), ("M", "migration"),
                                     ("E", "ecm"), ("A", "angiogenesis"),
                                     ("I", "inflammation"))}
    risks = ["P00 and GSE293186 are the same study/dataset; no independent validation.",
             "Reviews may cite P00 or overlapping primary papers; do not count them as independent experiments.",
             "C4 terms or gene sets chosen after inspecting DEGs could bias interpretation.",
             "Gene examples chosen for narrative fit could bias biological interpretation.",
             "L10 reuses GSE141814; L15 reuses scGeneScope, so each shared dataset counts once."]
    checkpoint = dict(dataset="GSE293186", experiment="EXP001", checkpoint="EXP001-C3.5 SkinExo Evidence Framework",
                      papers_screened=16, papers_verified=16, papers_corrected=len(corrected),
                      papers_unverified=0,
                      primary_research_count=sum(p["primary_research"] for p in PAPERS),
                      review_count=sum(p["review"] for p in PAPERS),
                      public_datasets_found=len(DATASETS),
                      EXP002_dataset_candidates=["10.17632/gm29wd7b94.1"],
                      EXP003_dataset_candidates=["altoslabs/scGeneScope"],
                      EXP004_dataset_candidates=["GSE141814", "10.17632/gm29wd7b94.1"],
                      EXP005_dataset_candidates=["altoslabs/scGeneScope"],
                      EXP006_dataset_candidates=["10.17632/gm29wd7b94.1", "GSE293186"],
                      direct_P_evidence_count=direct_counts["P"], direct_M_evidence_count=direct_counts["M"],
                      direct_E_evidence_count=direct_counts["E"], direct_A_evidence_count=direct_counts["A"],
                      direct_I_evidence_count=direct_counts["I"],
                      circularity_risks=risks, C4_questions=QUESTIONS,
                      bridge_gene_count=len(bridge),
                      bridge_evidence_counts={label: sum(r["evidence_level"] == label for r in bridge)
                                              for label in (D, I, "CONFLICTING", "INSUFFICIENT")},
                      important_corrections={p["paper_id"]: p["correction_note"] for p in corrected},
                      overall_pass=True)
    (OUT / "exp001_c3_5_evidence.json").write_text(json.dumps(checkpoint, indent=2) + "\n")
    print(json.dumps({k: checkpoint[k] for k in ("papers_screened", "papers_corrected", "primary_research_count", "review_count", "public_datasets_found", "bridge_evidence_counts", "overall_pass")}, indent=2))


if __name__ == "__main__":
    main()
