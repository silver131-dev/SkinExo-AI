# EXP003-D0 source and discrepancy log

**Scope:** metadata/design audit for CTX003 only. No recipient count matrix or sequencing reads were downloaded. An attempted GSE293957 family-SOFT transfer was stopped when the server reported an 18 MB archive; its incomplete temporary file was deleted without opening or analyzing cargo measurements. Only the brief GSE293957 metadata record was retained. Licensed article text is not reproduced.

## Authoritative sources checked

| Source | D0 use | Local metadata snapshot |
| --- | --- | --- |
| [NCBI GEO GSE293956](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293956), [official family SOFT](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE293nnn/GSE293956/soft/GSE293956_family.soft.gz) | Series title, 12 GSMs, cell types, control/EV labels, platform, three-day design, processed-file names, BioProject, SRX and BioSample links | `data/metadata/exp003_d0_sources/GSE293956_family.soft.gz`; SHA-256 `9e99ad4a77247a02c7c4a97874ed013a5ba94d09aaf54253400ee636bd2e338b` |
| [ENA run file report for PRJNA1247494](https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA1247494&result=read_run&fields=run_accession,experiment_accession,sample_accession,secondary_sample_accession,instrument_platform,instrument_model,library_strategy,fastq_bytes,fastq_ftp&format=tsv) | Cross-check 12 SRX→SRR→BioSample links, instrument and paired FASTQ availability | `data/metadata/exp003_d0_sources/PRJNA1247494_ena_runs.tsv`; SHA-256 `255222cfd2f19b4f85dd4f2f39b940ec22ab2f66729e8221c4c2e4a019543c54` |
| [ENA BioProject PRJNA1247494 XML](https://www.ebi.ac.uk/ena/browser/api/xml/PRJNA1247494) | Confirms secondary SRA accession `SRP576981` and external GEO accession `GSE293956` | `data/metadata/exp003_d0_sources/PRJNA1247494.xml` |
| [ENA BioSample SAMN47817691 XML](https://www.ebi.ac.uk/ena/browser/api/xml/SAMN47817691) | Spot-check primary hDF control attributes; no donor identifier present | `data/metadata/exp003_d0_sources/SAMN47817691.xml` |
| [NCBI GEO GSE293957](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293957), [brief record](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE293957&targ=self&view=brief&form=text) | Same submitters/source, 3 samples, Affymetrix miRNA-4 array `GPL19117`, BioProject `PRJNA1247495` | `data/metadata/exp003_d0_sources/GSE293957_brief.txt`; SHA-256 `41ccb6146e2f098858d96e6ab05b69e46212e9236b81e182693009b7a81fec23` |
| [Liu et al. PubMed record](https://pubmed.ncbi.nlm.nih.gov/40728022/) and [DOI](https://doi.org/10.1002/cbin.70063) | Paper identity and study-method provenance for the 10 µg/mL/72 h exposure, EV preparation metadata, and assay model/time mapping | No publication PDF, copied text, or figure is included |

## Accessions checked

- RNA-seq: `GSE293956`, `PRJNA1247494`, `SRP576981`, `GPL24676`; GSM `GSM8895186`–`GSM8895197`; SRX `SRX28272713`–`SRX28272724`; SRR `SRR33006688`–`SRR33006699`; BioSample `SAMN47817680`–`SAMN47817691`. Exact nonsequential GSM↔SRR mapping is in `data/metadata/GSE293956_samples.csv`.
- Cargo companion: `GSE293957`, `PRJNA1247495`, `GPL19117`, GSM `GSM8895198`–`GSM8895200`. No cargo measurement was opened or analyzed.
- Official GEO supplementary count-file headers returned HTTP 200: hDF 491,697 compressed bytes; HaCaT 467,504 compressed bytes. No count matrix was downloaded. The standard `GSE293956_RAW.tar` path returned 404; ENA/SRA paired FASTQ links remain public.

## Metadata differences and unresolved questions

| Item | GEO / archive | Paper | D0 treatment |
| --- | --- | --- | --- |
| Recipient exposure | Three days; numeric dose absent | 72 h, 10 µg/mL purified hDF-EV | Time agrees; numeric dose attributed to paper only |
| hDF control | `control` label | Results describe untreated controls | Exact RNA-seq medium, vehicle/PBS, and recipient EV-depleted-serum status UNKNOWN; scratch-control recipe not transferred |
| hDF donor | Primary hDF; no donor ID/count in GEO or checked BioSample | Derived from pediatric preputial specimens; no RNA-seq donor allocation | Count, pooling, and donor independence UNKNOWN |
| EV preparation | Source-cell EV production design; no prep IDs | Method described, prep count/assignment absent | Preparation independence and pooling UNKNOWN |
| Replication | Three numbered libraries per arm, each with distinct archive IDs | No donor-to-library or prep-to-library map | Labels and IDs are not independence proof; pairing UNKNOWN |
| Cargo assay label | Affymetrix miRNA-4 **array** | “miRNA sequencing” terminology, but methods name Affymetrix array | Catalog as array; no cargo analysis |
| Publisher supplement | GEO count matrices and run metadata available | No separately archived publisher supplement was verified | No separate publisher supplement assumed |

The exact hDF processed count-matrix structure, gene-ID convention, and integer integrity are left to EXP003-C1. Additional author or repository clarification would be needed for control vehicle and donor/EV-preparation independence.
