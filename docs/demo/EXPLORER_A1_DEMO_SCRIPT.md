# Explorer A1 demo script — 60–90 seconds

## 0–10 seconds — Frame the problem

Open the Explorer on its default **CTX003** query.

> “SkinExo-AI compares extracellular-vesicle responses in the same recipient cell across different EV sources and experimental settings. The premise is simple: same recipient, different context, different transcriptomic response.”

Point to the context card: human dermal-fibroblast EV, human dermal-fibroblast recipient, 10 ug/mL, 72 h, three treated and three control samples. Briefly show the visible missing donor, preparation, batch, pairing, and control details.

## 10–25 seconds — Read the response profile

Show the P/M/E/A/I overview.

> “CTX003 has observed-null P and E evidence, positive M and A components, and a positive inflammatory response. The Explorer preserves null evidence instead of turning every axis into a favorable signal.”

Open M or I in the Component Explorer to show component names, activity states, NES, FDR, source database, source term, and checkpoint.

## 25–40 seconds — Retrieve contexts

Scroll to **Response Similarity**.

> “The R1 engine compares NES only where both contexts tested the same frozen component. It does not impute missing evidence and it does not use phenotype or reliability to alter the score.”

Show **CTX002 at rank 1** and **CTX001 at rank 2**. Mention the primary and active-union similarities.

## 40–58 seconds — Open WHY THIS MATCH?

Open the CTX002 explanation.

> “CTX002 and CTX003 share exact positive inflammatory components, including I118, I117, I115, and I131. The explanation is generated with a fixed joint-NES ranking rule.”

Switch the explained target to CTX001.

> “CTX001 is less similar. M003, A008, and M025 are directly discordant, which exposes the context-specific response structure.”

Briefly show the axis-aware comparison and its shared-tested and direction counts.

## 58–75 seconds — Separate phenotype and reliability

Show **Phenotype Evidence**.

> “The CCK-8 and scratch anchors are 24-hour functional assays, while the transcriptome is 72 hours. Mouse wound, scar, and collagen evidence is labeled in vivo and different model. None of these anchors changes transcriptomic similarity.”

Show **Reliability & Limitations**.

> “Reliability remains a set of separate dimensions. There is no arbitrary confidence percentage.”

## 75–90 seconds — Close

Open **Evidence Provenance** or the **Response Atlas** tab.

> “Every response traces to its dataset, frozen checkpoint, method, and gene-set release. SkinExo-AI does not assume a universal EV response. It retrieves and explains context-dependent response patterns.”

Stop before discussing prediction, therapeutic efficacy, or unseen-context generalization.
