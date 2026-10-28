# Secure FHIR-Based Federated Learning Framework for Wearable Healthcare Data

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-6.0+-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C.svg?logo=pytorch&logoColor=white)](https://pytorch.org)
[![Flower](https://img.shields.io/badge/Flower-FL-FF7043.svg)](https://flower.ai)

> **Defense-in-depth federated learning for consumer health wearables utilizing HL7 FHIR R4 semantic normalization, client-side Differential Privacy (DP-SGD), and Secure Multi-Party Aggregation (SecAgg+ / Shamir's Secret Sharing).**

---

## 👥 Authors & Affiliation

- **K. Srigan** ([kakaraparthi.srigan2023@vitstudent.ac.in](mailto:kakaraparthi.srigan2023@vitstudent.ac.in))
- **K. Bala Venkat** ([kancharla.naga2023@vitstudent.ac.in](mailto:kancharla.naga2023@vitstudent.ac.in))
- **K. Sasank** ([kandepalli.bala2023@vitstudent.ac.in](mailto:kandepalli.bala2023@vitstudent.ac.in))
- **Dr. Sangeetha S\*** ([s.sangeetha@vit.ac.in](mailto:s.sangeetha@vit.ac.in)) *(Corresponding Author / Project Guide)*

*School of Computer Science and Engineering, Vellore Institute of Technology (VIT), Vellore 632014, India*

---

## 📖 Overview

Continuous physiological and activity monitoring from consumer wearables (Apple Watch, Fitbit) enables proactive healthcare, but centralized biometric data collection exposes patients to severe privacy, compliance, and gradient leakage risks.

This repository implements a **defense-in-depth privacy-preserving federated learning framework**:
1. **Semantic Interoperability**: Normalizes proprietary device streams into standard **HL7 FHIR Release 4** Observation bundles (`data/fhir_bundles`).
2. **Client-side Differential Privacy (DP-SGD)**: Integrates Opacus with Privacy Loss Distribution (PLD / PRV) accounting to bound privacy leakage against membership inference attacks.
3. **Multi-Party Secure Aggregation (SecAgg+)**: Implements threshold Shamir's Secret Sharing, Diffie-Hellman pairwise masking, and fixed-point quantization on top of Flower to protect against semi-honest server reconstruction and gradient inversion.
4. **Interactive Web Dashboard**: A modern React 18 + Vite + Tailwind CSS dashboard (`frontend/`) running on `http://localhost:5173/` backed by a FastAPI service (`backend/`).

---

## 📁 Repository Structure

```tree
.
├── course_project_paper.pdf      # Compiled Course Project Paper (Typst format)
├── course_project_paper.typ      # Typst source for course project paper
├── journal_paper.pdf             # Compiled Journal Submission Paper
├── journal_paper.tex             # LaTeX source code
├── journal_paper.typ             # Typst source code
├── paper_verification_report.md  # Experimental validation and metric report
├── references.bib                # Bibliography
├── requirements.txt              # Python dependencies
├── data/
│   ├── fhir_bundles/             # HL7 FHIR R4 JSON bundles
│   ├── partitions/               # Non-IID client partitioned datasets
│   ├── processed/                # Normalized tabular data & splits
│   └── raw/                      # Raw Harvard Apple Watch and Fitbit dataset
├── figures/                      # High-resolution architectural and evaluation figures
├── results/                      # Evaluation checkpoints, metrics, and JSON summaries
├── scripts/                      # FL training, simulation, DP accounting, and analysis
│   ├── client.py                 # Federated client implementation (Flower)
│   ├── server.py                 # Federated aggregation server
│   ├── run_phase3_dp_fedavg.py   # DP-FedAvg experiment runner
│   ├── run_phase4_secagg.py      # SecAgg+ experiment runner
│   ├── partition_and_fhir.py     # FHIR transformation & partitioning pipeline
│   └── ...
├── storage/                      # Secure storage (encrypted checkpoints, models, audit logs)
├── backend/                      # Production FastAPI Backend (Runs on http://127.0.0.1:8000)
│   ├── app/
│   │   ├── api/                  # REST API routes (FL, FHIR, Auth, Security, Datasets)
│   │   ├── fhir/                 # HL7 FHIR R4 mapping & validation
│   │   ├── ml/                   # ML models, preprocessing, federated logic
│   │   ├── privacy/              # DP-SGD, Secure Aggregation, Byzantine defense
│   │   └── security/             # AES-256-GCM, TLS/certs, immutable audit logger
│   └── tests/                    # Backend unit & integration test suites
└── frontend/                     # Modern React 18 + Vite + Tailwind CSS Dashboard (Runs on http://localhost:5173)
    ├── src/
    │   ├── api/                  # Typed API client
    │   ├── components/           # Reusable UI components (Header, Sidebar)
    │   ├── pages/                # Interactive dashboard views (FL simulation, FHIR, DP config, etc.)
    │   └── types/                # TypeScript interface definitions
    ├── package.json
    └── vite.config.ts            # Vite config (port 5173 with proxy to backend)
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm
- Git

### 2. Backend Setup
```bash
git clone https://github.com/Srigan17/CourseProject.git
cd CourseProject

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

To start the FastAPI backend:
```bash
uvicorn backend.app.main:app --reload --port 8000
```
Backend will be live at `http://127.0.0.1:8000`.

### 3. Frontend Setup (Interactive Web Dashboard)
Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```
The React + Vite dashboard will launch at **`http://localhost:5173/`**.

### 4. Running Federated Learning Experiments
To run the federated pipeline with DP and Secure Aggregation:
```bash
# Prepare FHIR bundles and partitions
python scripts/partition_and_fhir.py

# Run Phase 3: DP-FedAvg benchmarks
python scripts/run_phase3_dp_fedavg.py

# Run Phase 4: SecAgg+ cryptographic aggregation
python scripts/run_phase4_secagg.py
```

---

## 📊 Key Results

- **Zero-Utility-Loss Secure Aggregation**: Fixed-point quantization in SecAgg+ preserves test accuracy ($67.92\% \pm 1.16\%$ vs. $67.60\% \pm 0.66\%$ baseline; difference within statistical noise, $|\Delta| \le 0.086$ percentage points).
- **Formal Privacy Guarantee**: Under $(\epsilon = 4.29, \delta = 10^{-5})$ differential privacy ($\sigma = 2.0$), model reaches $38.44\% \pm 0.93\%$ on 6-class classification ($+21.77$ percentage points above random chance).

---

## 📄 Citation

If you find this code or research useful, please cite:

```bibtex
@article{srigan2026securefhirfl,
  title={Secure FHIR-Based Federated Learning Framework for Wearable Healthcare Data Using Differential Privacy and Secure Aggregation},
  author={Srigan, K. and Bala Venkat, K. and Sasank, K. and Sangeetha, S.},
  institution={Vellore Institute of Technology},
  year={2026}
}
```

---

## 📜 License

This project is licensed under the MIT License.
