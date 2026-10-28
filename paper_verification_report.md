# Journal Paper Verification & Compliance Report

**Manuscript Title:** Secure FHIR-Based Federated Learning Framework for Wearable Healthcare Data Using Differential Privacy and Secure Aggregation  
**Target Venue:** IEEE Transactions on Information Forensics and Security / IEEE Journal of Biomedical and Health Informatics (Standard IEEE Two-Column Format)  
**Verification Date:** October 27, 2026  
**Verification Status:** PASSED (All Verification Gates Satisfied)

---

## 1. Executive Summary & Page Count Verification

The manuscript was formatted, calibrated, and compiled to mirror the typography, density, and structure of the reference publication (`VisionRAG_Researchpaper (1).pdf`).

- **Target Page Count:** Exactly 8 Pages
- **Compiled Page Count:** **8 Pages** (Verified via `pypdf` reader)
- **Primary Deliverables:**
  1. [`journal_paper.pdf`](file:///c:/Users/Srigan/OneDrive/Desktop/ProjectIReview/journal_paper.pdf): Final, compiled 8-page publication PDF in two-column IEEE format.
  2. [`journal_paper.tex`](file:///c:/Users/Srigan/OneDrive/Desktop/ProjectIReview/journal_paper.tex): Complete, self-contained LaTeX source using standard `\documentclass[journal,twocolumn,10pt]{IEEEtran}`.
  3. [`journal_paper.typ`](file:///c:/Users/Srigan/OneDrive/Desktop/ProjectIReview/journal_paper.typ): Typst typesetting source code producing the pixel-perfect 8-page PDF.
  4. [`references.bib`](file:///c:/Users/Srigan/OneDrive/Desktop/ProjectIReview/references.bib): 30 verified academic citations with complete DOIs, volumes, and years.
  5. [`figures/`](file:///c:/Users/Srigan/OneDrive/Desktop/ProjectIReview/figures): High-resolution vector PDF and 300 DPI PNG figures for architecture, SecAgg+ protocol state machine, and privacy-utility Pareto frontiers.

### Page-by-Page Density Breakdown

| Page | Section(s) / Content | Word Count | Char Count | Status |
|:---:|:---|:---:|:---:|:---:|
| **1** | Title, Author Block, Abstract, Index Terms, Section I (Introduction) | 777 | 6,210 | Perfectly filled |
| **2** | Section II (Related Work), Section III (Problem Formulation & System Architecture) | 830 | 6,212 | Full two-column |
| **3** | Figure 1 (Architecture), Section IV (FHIR Wearable Pipeline & Normalization) | 597 | 4,195 | Full two-column |
| **4** | Section V (Privacy-Preserving Federated Protocol: DP-SGD & SecAgg+ Formulations) | 743 | 4,404 | Full two-column |
| **5** | Algorithm 1, Figure 2 (SecAgg State Machine), Section VI (Experimental Setup) | 840 | 5,227 | Full two-column |
| **6** | Table I, Table II, Figure 3 (Privacy-Utility Tradeoff), Section VII (Empirical Results) | 734 | 4,200 | Full two-column |
| **7** | Table III, Table IV, Section VIII (Security & Threat Model Analysis), Section IX (Discussion & Limitations) | 864 | 6,120 | Full two-column |
| **8** | Section X (Conclusion), Acknowledgments, References [1]–[30] | 485 | 3,427 | Perfectly balanced across both columns; finishes cleanly on Page 8 |

---

## 2. Author Block & Affiliation Verification

The author block strictly follows the mandatory order, naming, institutional affiliation, and corresponding author guidance requested by the authors:

1. **First Author:** `K.Srigan` (`kakaraparthi.srigan2023@vitstudent.ac.in`)
2. **Second Author:** `K.Bala Venkat` (`kancharla.naga2023@vitstudent.ac.in`)
3. **Third Author:** `K.Sasank` (`kandepalli.bala2023@vitstudent.ac.in`)
4. **Project Guide & Corresponding Author:** `Sangeetha S*` (`s.sangeetha@vit.ac.in`)

- **Institutional Affiliation:** School of Computer Science and Engineering, Vellore Institute of Technology, Vellore 632014, India
- **Footnote / Correspondence Notice:** `*Corresponding author (Project Guide): s.sangeetha@vit.ac.in`

---

## 3. Empirical Results & Mathematical Audit Consistency

All numerical values, standard deviations, and privacy parameters reported in the manuscript match the verified benchmark results in [`results/secagg_track2/final_results_integrity_verification.json`](file:///c:/Users/Srigan/OneDrive/Desktop/ProjectIReview/results/secagg_track2/final_results_integrity_verification.json).

### 3.1 Four Benchmark Configurations (5 Seeds: 42, 123, 456, 789, 2026)

- **Configuration A (Plaintext FedAvg Reference):**
  - Accuracy: $67.60\% \pm 0.66\%$ (sample standard deviation, $s$ with $N-1=4$); $[0.59\%]$ (population standard deviation, $\sigma_p$ with $N=5$)
  - Macro $F_1$: $67.89\% \pm 0.62\%$ (sample $s$); $[0.55\%]$ (population $\sigma_p$)
  - Balanced Accuracy: $67.57\% \pm 0.66\%$
  - Mean Client Wall-Clock Time: $0.183 \pm 0.007\text{ s/round}$
- **Configuration C (SecAgg-Only FedAvg, Zero Noise):**
  - Accuracy: $67.92\% \pm 1.16\%$ (sample $s$); $[1.04\%]$ (population $\sigma_p$)
  - Macro $F_1$: $68.21\% \pm 1.17\%$ (sample $s$); $[1.04\%]$ (population $\sigma_p$)
  - Balanced Accuracy: $67.90\% \pm 1.15\%$
  - Accuracy delta vs Config A: $+0.32\text{ percentage points}$ (empirically within $1\times$ inter-seed standard deviation)
  - Mean Client Wall-Clock Time: $0.218 \pm 0.008\text{ s/round}$ ($+19.1\%$ cryptographic overhead)
- **Configuration B (DP-Only FedAvg, $C=1.0, \delta=10^{-5}$):**
  - $\sigma = 0.5 \implies \epsilon_{\text{PRV}} = 14.86$, Accuracy: $45.98\% \pm 1.48\%$, Macro $F_1$: $43.95\% \pm 1.77\%$
  - $\sigma = 1.0 \implies \epsilon_{\text{PRV}} = 4.29$, Accuracy: $41.56\% \pm 1.42\%$, Macro $F_1$: $39.52\% \pm 1.76\%$
  - $\sigma = 1.5 \implies \epsilon_{\text{PRV}} = 2.45$, Accuracy: $39.54\% \pm 1.11\%$, Macro $F_1$: $36.85\% \pm 1.34\%$
  - $\sigma = 2.0 \implies \epsilon_{\text{PRV}} = 1.71$, Accuracy: $38.47\% \pm 0.89\%$, Macro $F_1$: $35.40\% \pm 1.10\%$
  - Mean Client Wall-Clock Time: $0.462 \pm 0.012\text{ s/round}$
- **Configuration D (DP + SecAgg Combined Framework):**
  - $\sigma = 0.5 \implies$ Accuracy: $46.07\% \pm 1.50\%$ ($\Delta = +0.086\text{ pp}$ vs B)
  - $\sigma = 1.0 \implies$ Accuracy: $41.56\% \pm 1.42\%$ ($\Delta = +0.000\text{ pp}$ vs B)
  - $\sigma = 1.5 \implies$ Accuracy: $39.54\% \pm 1.11\%$ ($\Delta = +0.000\text{ pp}$ vs B)
  - $\sigma = 2.0 \implies$ Accuracy: $38.44\% \pm 0.90\%$ ($\Delta = -0.027\text{ pp}$ vs B)
  - Mean Client Wall-Clock Time: $0.498 \pm 0.015\text{ s/round}$

### 3.2 Quantization & Protocol Precision

- Quantization clip threshold: $\gamma = 0.5$
- Scaling factor: $S = 2^{16} = 65,536$
- Modulus: $M = 2^{31} - 1 = 2,147,483,647$ (31-bit Mersenne prime)
- Empirical isolated test error:
  - Max absolute parameter error: $1.396 \times 10^{-5} < 1.526 \times 10^{-5}$ (theoretical bound $\frac{1}{2S}$)
  - Mean squared error (MSE): $1.95 \times 10^{-11}$
- Network transmission per client per round:
  - Model weights ($d = 10,886$ float32): $43.54\text{ KB}$
  - Quantized integer vector ($d$ int32): $43.54\text{ KB}$
  - Public keys ($2 \times 32\text{ B}$ X25519) + Shamir shares ($3 \times 48\text{ B}$): $\approx 208\text{ B}$
  - Combined communication footprint: $43.75\text{ KB/client/round}$

---

## 4. Scientific Boundaries & Negative Claims Explicitly Enforced

To adhere to rigorous academic peer-review standards, the manuscript explicitly enforces the following limitations:

1. **Scope of Differential Privacy:**
   - The $(\epsilon, \delta)$-DP guarantee is defined strictly at the **record-level** (adding or removing a single 15-minute sensor observation window $\mathbf{x} \in \mathcal{D}_k$) using Rényi Differential Privacy (RDP) converted via the PRV accountant.
   - **No Patient-Level Privacy Claim:** Because individual patients contribute multiple temporal windows across monitoring sessions, record-level DP does *not* provide formal $(\epsilon, \delta)$ patient-level bounding without group-privacy scaling (which would scale $\epsilon$ linearly by the number of patient records $k$).
   - **Held-Out Test Set:** Held-out test evaluation on the 732 records is conducted using standard empirical evaluation; test metrics are *not* post-processed with differential privacy.
2. **Zero Utility Loss Boundary:**
   - The paper avoids claiming that SecAgg provides "provable asymptotic zero loss" across arbitrary models. The small empirical divergence ($|\Delta| \le 0.086\text{ percentage points}$) is attributed to fixed-point quantization truncation with $S = 65,536$, well within standard SGD stochastic variance.
3. **Dropout Robustness & Adversarial Threshold:**
   - Dropout recovery is proved under the honest-but-curious server model with a minimum threshold $U_3 \ge t = 3$ surviving clients. Collusion with $\ge t$ clients or active Byzantine message corruption falls outside the SecAgg+ security proof and is documented in Section IX.
4. **Regulatory Disclaimers:**
   - The framework implements technical safeguards aligned with the principle of data minimization (HIPAA Security Rule 45 CFR § 164.312, GDPR Article 25/32). The paper explicitly disclaims legal or statutory compliance certification.

---

## 5. Summary of Deliverable Files

| File | Type | Description |
|:---|:---:|:---|
| [`journal_paper.pdf`](file:///c:/Users/Srigan/OneDrive/Desktop/ProjectIReview/journal_paper.pdf) | PDF (8 Pages) | Complete, publication-ready two-column manuscript matching reference PDF format |
| [`journal_paper.tex`](file:///c:/Users/Srigan/OneDrive/Desktop/ProjectIReview/journal_paper.tex) | LaTeX Source | Standard IEEEtran source code, fully formatted with math, tables, algorithms, and references |
| [`journal_paper.typ`](file:///c:/Users/Srigan/OneDrive/Desktop/ProjectIReview/journal_paper.typ) | Typst Source | High-precision Typst source file calibrated to exactly 8.00 pages |
| [`references.bib`](file:///c:/Users/Srigan/OneDrive/Desktop/ProjectIReview/references.bib) | BibTeX | 30 complete, verified academic citations |
| [`figures/fig1_system_architecture.pdf`](file:///c:/Users/Srigan/OneDrive/Desktop/ProjectIReview/figures/fig1_system_architecture.pdf) | Vector Graphic | System Architecture: Wearable $\to$ FHIR $\to$ Local DP-SGD $\to$ SecAgg+ |
| [`figures/fig2_secagg_workflow.pdf`](file:///c:/Users/Srigan/OneDrive/Desktop/ProjectIReview/figures/fig2_secagg_workflow.pdf) | Vector Graphic | Four-stage SecAgg+ cryptographic protocol state machine and dropout recovery |
| [`figures/fig3_privacy_utility_tradeoff.pdf`](file:///c:/Users/Srigan/OneDrive/Desktop/ProjectIReview/figures/fig3_privacy_utility_tradeoff.pdf) | Vector Graphic | Privacy ($\epsilon$) vs Utility (Accuracy/F1) Pareto frontier across noise scales |

All files have been verified and are ready for submission or camera-ready generation.
