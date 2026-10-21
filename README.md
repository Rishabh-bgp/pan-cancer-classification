<div align="center">

# 🧬 Pan-Cancer Tumour-Type Classification

### What Near-Perfect Accuracy Does and Does Not Show on the UCI TCGA Pan-Cancer RNA-Seq Dataset: Leakage, Equivalence, Conformal Reliability and Data Efficiency

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.9.1-F7931E?logo=scikitlearn&logoColor=white)
![LightGBM](https://img.shields.io/badge/LightGBM-4.7.0-02569B)
![Dataset](https://img.shields.io/badge/data-UCI%20%23401%20(included)-success)
![Git LFS](https://img.shields.io/badge/Git%20LFS-data.csv-F64935?logo=git&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue)

</div>

> Research work carried out as part of the **6-Month Industrial Training & Certification Program in Artificial Intelligence and Machine Learning**, jointly offered by [IIT Ropar](https://www.iitrpr.ac.in/) and [NIELIT Ropar](https://www.nielit.gov.in/ropar/), under MeitY, Govt. of India.

---

## 📌 Overview
The UCI *gene expression cancer RNA-Seq* dataset (801 TCGA tumours × 20,531 genes, five cancer types: BRCA, COAD,
KIRC, LUAD, PRAD) is widely used to report near-perfect tumour-type classification. This study asks **what such
accuracies can and cannot support**. It does not propose a new classifier. Instead it audits leakage, compares models
with equivalence statistics, measures calibration and conformal reliability, and studies data efficiency, with code
that regenerates every number and figure.

## 🔑 Key findings
*(all numbers are taken from `CHANGES.md` and the paper in this repository)*

| Question | Finding |
|---|---|
| Does leaky gene selection inflate accuracy on real labels? | Barely: at most **0.29 point** (≥ 20 genes). Softmax, 100 genes: **99.50%** leaky vs **99.48%** in-fold. |
| When is the leak visible? | With permuted labels and small samples: **68.2% vs 19.9%** at n = 60. |
| Do the seven classifiers differ? | No pair differs significantly (smallest Holm-adjusted p = **0.66**); equivalence within ±1 point for **10 of 15** non-naive-Bayes pairs. |
| Is gene selection stable? | ANOVA top-100 selection: Nogueira **Φ = 0.93**. |
| Calibration | Softmax pooled ECE **0.47%** (95% CI 0.25–0.83); random forest under-confident (ECE **2.7%**). |
| Conformal coverage (softmax) | **89.6 / 94.7 / 99.4%** at 90 / 95 / 99% nominal. |
| Abstention at 99% | Error among accepted predictions falls from **0.51%** to **0.18%**; a max-probability threshold gives **0.26%**. |
| Data efficiency | Linear models reach **99.4%** macro-F1 (±0.2) with **10** training tumours per class. |

See [`docs/results.md`](docs/results.md) for the full list.

## 📂 Repository structure
```
README.md                 this file
CHANGES.md                reviewer summary: findings, contributions, changes, reproducibility
submission_checklist.md   check against the NIELIT Bio-AI Conclave 2026 guidelines
code/                     analysis pipeline (run_all.py, src/, requirements.txt)
data/                     data.csv (Git LFS, 206 MB) and labels.csv — INCLUDED
paper/                    review (anonymised) and camera-ready manuscripts; paper/IJCRT/ journal-format version
supplementary/            Supplementary Sections S1–S12 and code archive S1
presentation/             conference deck and speaker notes
cover_letter/             cover letter
explainer/                plain-language summary
docs/                     extended documentation (this repository)
```

## 🚀 Quick start
```bash
git lfs install
git clone https://github.com/Rishabh-bgp/pan-cancer-classification.git
cd pan-cancer-classification/code
cp ../data/data.csv ../data/labels.csv data/
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python run_all.py --quick     # smoke test
python run_all.py             # full run (~1.5–2 h on 8 vCPUs, ~8 GB RAM)
```
Full details: [`docs/reproducing.md`](docs/reproducing.md).

## 📚 Documentation
| Page | Contents |
|---|---|
| [docs/data.md](docs/data.md) | Dataset source, format, checksums, licence |
| [docs/methodology.md](docs/methodology.md) | Pipeline, models, statistics, reliability analyses |
| [docs/results.md](docs/results.md) | All headline results with pointers to result files |
| [docs/reproducing.md](docs/reproducing.md) | Environment, commands, runtime, memory |
| [docs/faq.md](docs/faq.md) | FAQ and limitations |
| [docs/materials-overview.md](docs/materials-overview.md) | Original overview of the manuscript materials |

## 📝 Citation
See [`CITATION.cff`](CITATION.cff) (GitHub shows a "Cite this repository" button).

## ⚖️ Licence
Code and documentation: MIT © 2026 Rishabh Aryan. The dataset in `data/` remains under its original UCI licence
(see `docs/data.md`).

## 🔗 Related work / Portfolio

Other repositories from my IIT Ropar & NIELIT Ropar AI/ML training:

| Repository | Description | Live |
|---|---|---|
| [beed-ml-study](https://github.com/Rishabh-bgp/beed-ml-study) | Provenance audit and leakage-aware benchmark of seizure-type classifiers on the Bangalore EEG Epilepsy Dataset | — |
| [NIELIT-MACHINE-LEARNING-PROJECTS](https://github.com/Rishabh-bgp/NIELIT-MACHINE-LEARNING-PROJECTS) | Nineteen end-to-end machine learning projects | — |
| [NIELIT-DATA-SCIENCE](https://github.com/Rishabh-bgp/NIELIT-DATA-SCIENCE) | NumPy, Pandas and Matplotlib notebooks for the NIELIT Data Science curriculum | — |
| [NIELIT-PYTHON-](https://github.com/Rishabh-bgp/NIELIT-PYTHON-) | Python teaching notebooks and five capstone programs | — |
| [IIT-ROPAR-GENAI-FOUNDATIONS](https://github.com/Rishabh-bgp/IIT-ROPAR-GENAI-FOUNDATIONS) | Generative AI foundations ebooks from an IIT Ropar AI tools workshop | — |
| [zoo-website-capstone](https://github.com/Rishabh-bgp/zoo-website-capstone) | Zoo website capstone (simple and advanced versions) | [demo](https://rishabh-bgp.github.io/zoo-website-capstone/) |
| [logistics-website-capstone](https://github.com/Rishabh-bgp/logistics-website-capstone) | Kargonaut Logistics website capstone (claymorphism, glassmorphism, neumorphism) | [demo](https://rishabh-bgp.github.io/logistics-website-capstone/) |
