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

## 🔗 Other repositories by Rishabh Aryan

| Repository | Description | Live |
|---|---|---|
| [100-days-of-python](https://github.com/Rishabh-bgp/100-days-of-python) | My original, offline, no-API-key solutions to all 100 projects of the 100 Days of Code Python bootcamp curriculum… | — |
| [Agentic-Engineering-Ebook](https://github.com/Rishabh-bgp/Agentic-Engineering-Ebook) | Agentic Engineering is a practical notebook-book on specifying, generating, verifying, and refining multi-tenant… | — |
| [beed-ml-study](https://github.com/Rishabh-bgp/beed-ml-study) | Provenance audit and leakage-aware benchmark of seizure-type classifiers on the Bangalore EEG Epilepsy Dataset — IIT… | — |
| [boston-house-price-prediction](https://github.com/Rishabh-bgp/boston-house-price-prediction) | Boston house price prediction with machine learning: scikit-learn gradient boosting, repeated K-fold CV, race… | [open](https://rishabh-bgp.github.io/boston-house-price-prediction/) |
| [Brain-Computer-Interfaces-and-Cognitive-Computing-An-Introduction](https://github.com/Rishabh-bgp/Brain-Computer-Interfaces-and-Cognitive-Computing-An-Introduction) | Brain–computer interfaces (BCIs) link neural activity to external devices, translating brain signals via algorithms… | — |
| [building-a-virtual-cell-in-python](https://github.com/Rishabh-bgp/building-a-virtual-cell-in-python) | A cell has a normal gene-activity pattern. Knock out one gene and that pattern changes. This project trains a small… | — |
| [Chronic-Kidney-Disease-Stage-Identification-in-HIV-Infected-Patients-Using-Supervised-ML](https://github.com/Rishabh-bgp/Chronic-Kidney-Disease-Stage-Identification-in-HIV-Infected-Patients-Using-Supervised-ML) | ML is transforming Chronic Kidney Disease (CKD) detection in HIV patients, catching early asymptomatic stages to… | — |
| [cobratate](https://github.com/Rishabh-bgp/cobratate) | Cobratate, an esoteric imperative programming language. Tate-flavored syntax, ordinary semantics, and a Python… | [open](https://rishabh-bgp.github.io/cobratate/) |
| [coda-synth](https://github.com/Rishabh-bgp/coda-synth) | CoDA-Synth: stylometric detection of LLM-rewritten dark-web documents with sparse TF-IDF + LinearSVC. Research lab,… | [open](https://shale-ember-delta-kite.grok.me/) |
| [IIT-ROPAR-GENAI-FOUNDATIONS](https://github.com/Rishabh-bgp/IIT-ROPAR-GENAI-FOUNDATIONS) | Free open-source Generative AI foundations ebooks (2026) covering Claude, Grok, Gemini, Cursor, OpenAI and more —… | — |
| [iris-classification](https://github.com/Rishabh-bgp/iris-classification) | Iris flower classification in Python: scikit-learn model comparison, tuning and evaluation, FastAPI /predict API,… | [open](https://rishabh-bgp.github.io/iris-classification/) |
| [kbc-game](https://github.com/Rishabh-bgp/kbc-game) | Kaun Banega Crorepati (KBC) quiz game for the terminal in Python: 16-question prize ladder, safe levels and 4… | — |
| [knn-classifier](https://github.com/Rishabh-bgp/knn-classifier) | Simple K-Nearest Neighbors classifier on the classic Iris dataset using scikit-learn. Loads data, trains the model,… | — |
| [linear-regression-model-](https://github.com/Rishabh-bgp/linear-regression-model-) | Supervised linear regression on the scikit-learn diabetes dataset. A single feature (BMI) is used to predict… | — |
| [logistic-regression](https://github.com/Rishabh-bgp/logistic-regression) | This graduate capstone applies multi-class logistic regression to the Iris dataset. It includes EDA, stratified… | — |
| [logistics-website-capstone](https://github.com/Rishabh-bgp/logistics-website-capstone) | Logistics website capstone: Kargonaut Logistics, a premium freight site mixing claymorphism, glassmorphism and… | [open](https://rishabh-bgp.github.io/logistics-website-capstone/) |
| [lovelight-leap](https://github.com/Rishabh-bgp/lovelight-leap) | 💖 Lovelight Leap: a love-themed 2D platformer in vanilla JS canvas. 4 worlds, a boss you cheer up, original… | [open](https://rishabh-bgp.github.io/lovelight-leap/) |
| [machine-learning-part-1](https://github.com/Rishabh-bgp/machine-learning-part-1) | Machine learning in Python with scikit-learn: heart disease classification and medical insurance cost regression… | — |
| [Meeting-of-Machines-Consumer-Agents-Seller-Agents-and-Hidden-Fulfilment-Risk-in-Online-Retail](https://github.com/Rishabh-bgp/Meeting-of-Machines-Consumer-Agents-Seller-Agents-and-Hidden-Fulfilment-Risk-in-Online-Retail) | Agentic commerce lets shopping and seller agents place orders without showing operational truth. This IS case argues… | — |
| [morocco-city-aware-load-forecasting](https://github.com/Rishabh-bgp/morocco-city-aware-load-forecasting) | City-aware short-term load forecasting and peak detection on high-resolution Moroccan smart-meter data (5 zones).… | — |
| [NIELIT-DATA-SCIENCE](https://github.com/Rishabh-bgp/NIELIT-DATA-SCIENCE) | Hands-on NumPy, Pandas, and Matplotlib Jupyter notebooks for the NIELIT Data Science curriculum — practical,… | — |
| [NIELIT-MACHINE-LEARNING-PROJECTS](https://github.com/Rishabh-bgp/NIELIT-MACHINE-LEARNING-PROJECTS) | Nineteen end-to-end machine learning projects: classification, regression, clustering, and recommendation, with… | — |
| [NIELIT-PYTHON-](https://github.com/Rishabh-bgp/NIELIT-PYTHON-) | Open-source Python teaching notebooks: a language reference and five capstone programs, with detailed documentation.… | — |
| [Predicting-Hot-Events-in-the-Early-Period-through-Bayesian-Model-for-Social-Networks](https://github.com/Rishabh-bgp/Predicting-Hot-Events-in-the-Early-Period-through-Bayesian-Model-for-Social-Networks) | This notebook details the implementation and evaluation of a Bayesian perspective Early stage Event Prediction… | — |
| [prediction-as-power](https://github.com/Rishabh-bgp/prediction-as-power) | Laboratory and working paper on prediction as power in European electricity markets. A DE-like hourly simulator… | — |
| [real-estate-valuation-taiwan](https://github.com/Rishabh-bgp/real-estate-valuation-taiwan) | Taiwan real estate valuation (Xindian, New Taipei): house price per ping prediction with scikit-learn gradient… | [open](https://rishabh-bgp.github.io/real-estate-valuation-taiwan/) |
| [snakes-and-ladders](https://github.com/Rishabh-bgp/snakes-and-ladders) | 🐍🪜 Original Snakes & Ladders browser game: hand-drawn SVG snakes and ladders, 3D dice, 2-4 humans or bots, sound,… | [open](https://rishabh-bgp.github.io/snakes-and-ladders/) |
| [spam-scan](https://github.com/Rishabh-bgp/spam-scan) | Explainable spam, phishing & Indian-scam detector for SMS/email (English, Hindi, Hinglish): TF-IDF + Logistic… | [open](https://spam-scan.onrender.com) |
| [vedic-math-hybrid-kt](https://github.com/Rishabh-bgp/vedic-math-hybrid-kt) | Hybrid Vedic Math AI: rule-based sutras (Urdhva-Tiryagbhyam, Nikhilam, Yavadunam) plus RF classifier that cleans… | — |
| [wind-turbine-power-model](https://github.com/Rishabh-bgp/wind-turbine-power-model) | Single-turbine power curves + wind-farm simulation. Weibull wind stats, hourly NASA-style speed data, and… | — |
| [zoo-website-capstone](https://github.com/Rishabh-bgp/zoo-website-capstone) | Capstone project: a fictional zoo website built twice — a beginner-style simple version and a cinematic advanced… | [open](https://rishabh-bgp.github.io/zoo-website-capstone/) |
