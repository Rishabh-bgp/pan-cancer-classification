# Pan-Cancer tumour-type classification: leakage, equivalence, conformal reliability and data efficiency

Materials for the manuscript "What Near-Perfect Accuracy Does and Does Not Show on the UCI TCGA Pan-Cancer RNA-Seq
Dataset: Leakage, Equivalence, Conformal Reliability and Data Efficiency" (Er. Rishabh Aryan, IIIT Bhagalpur).
`CHANGES.md` covers the study summary, the contributions and the changes from earlier versions.

## Folder layout
```
README.md                 this file
CHANGES.md                summary for reviewers: findings, contributions, changes and reasons, reproducibility
submission_checklist.md   item-by-item check against the NIELIT Bio-AI Conclave 2026 submission guidelines
data/
  data.csv                UCI dataset 401, TCGA-PANCAN-HiSeq-801x20531: 801 samples x 20,531 genes (dummy gene names)
  labels.csv              cancer type per sample (BRCA, COAD, KIRC, LUAD, PRAD)
paper/
  PanCancer_paper_review_anonymised.docx / .pdf   double-blind review copy (author details removed)
  PanCancer_paper_camera_ready.docx / .pdf        camera-ready copy
supplementary/
  PanCancer_supplementary.docx / .pdf             Supplementary Sections S1-S12
  PanCancer_code_S1.zip                           code (Supplementary File S1)
presentation/
  PanCancer_Conclave_Presentation.pptx / .pdf     16-slide conference deck (NIELIT Bio-AI Conclave 2026, Track 2)
  PanCancer_Conclave_Speaker_Notes.docx / .pdf    speaker notes, slide by slide
cover_letter/
  PanCancer_cover_letter.docx / .pdf              cover letter and author declaration (guideline section 22; placeholders to confirm)
explainer/
  PanCancer_Simple_Explainer.docx / .pdf          4-page plain-language summary of the study for non-specialists
```

## Data
Source: Fiorini S. *Gene expression cancer RNA-Seq* [dataset]. UCI Machine Learning Repository, 2016,
doi:10.24432/C5R88H (https://archive.ics.uci.edu/dataset/401). The data derive from the TCGA Pan-Cancer project
(https://www.cancer.gov/tcga). Values are already log-scaled. Gene columns are dummy names (gene_0 ... gene_20530), and
no gene symbols are included.

SHA-256 checksums:
* data.csv: e3e7eff51f4a5fe5f121fb183c09786c767c755ef10d1c7b3ce3c193a7082ca9
* labels.csv: e1653ccf5a630deb3b953ccac5a8b331b89adc5433e5d2d3444c1fc01d79e7aa

## Reproducing the results
```
unzip supplementary/PanCancer_code_S1.zip && cd PanCancer_code_S1
cp ../data/data.csv ../data/labels.csv data/
python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python run_all.py          # all analyses; writes results/ (CSV/JSON) and figures/ (300 dpi PNG)
python run_all.py --quick  # short smoke test
```
The full run takes about 1.5-2 h on an 8-vCPU machine and needs about 8 GB of RAM with the default settings (the
all-genes step is memory-aware; see the README inside the zip for options, memory use and file descriptions).
