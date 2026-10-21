# Leakage audit and benchmark: five-class tumour-type classification on the UCI TCGA pan-cancer RNA-Seq data

Code for the paper "What Near-Perfect Accuracy Does and Does Not Show on the UCI TCGA Pan-Cancer RNA-Seq Dataset:
Leakage, Equivalence, Conformal Reliability and Data Efficiency" (Supplementary File S1).

## What it does
* Loads the UCI "gene expression cancer RNA-Seq" data (801 samples x 20,531 genes; BRCA, COAD, KIRC, LUAD, PRAD).
* For every training fold, fits: zero-variance filter -> ANOVA-F top-k gene selection -> z-scoring -> classifier.
  Nothing is fitted on test data.
* Compares a majority-class baseline, softmax (multinomial logistic) regression, ridge classifier, linear SVM,
  Gaussian naive Bayes, random forest, LightGBM and a one-hidden-layer MLP with 10 x 5 repeated stratified CV.
  Hyperparameters are fixed in advance (no tuning).
* Reports accuracy, macro-F1, balanced accuracy and macro one-vs-rest ROC-AUC with Nadeau-Bengio corrected 95% CIs,
  corrected paired t-tests against softmax regression (Holm-adjusted), a feature-count ablation (k = 2 ... all),
  selection stability across folds, a label-permutation check and a footprint profile.
* Revision analyses (`src/audit.py`): leaky vs in-fold selection with real labels (n = 801), 100 permuted-label runs
  (n = 801) and 50 small subsamples (n = 60); all 21 pairwise tests with Holm adjustment, TOST equivalence (+-1 point),
  Bayesian correlated t-test (ROPE +-0.5 point) and minimum detectable differences; Nogueira stability; per-sample
  quality metrics; and all seven classifiers with every expressed gene.
* Extension analyses (`src/novelty.py`): calibration (ECE, Brier, reliability bins) and split-conformal prediction sets
  (marginal and Mondrian, 90/95/99%) nested inside each outer training fold, with abstention on non-singleton sets;
  learning curves (3-60 training tumours per class); leaky vs in-fold selection in balanced subsamples of n = 30-390.
* Robustness checks (`src/robust.py`): fold-level coverage spread and calibration-conditional (Beta) coverage; a
  max-probability threshold baseline (same threshold, and matched abstention); cross-conformal sets (5 inner folds);
  randomised (smoothed) conformal p-values to break score ties; pooled ECE with a bootstrap CI, a consistency-resampling
  reference, equal-mass ECE and log-loss; 95% CIs for the learning curves and the leakage-vs-n results.

## What it does not do
* It does not identify genes. The UCI release names genes `gene_0` ... `gene_20530` (dummy names); no gene symbols
  are included, so the top-ranked genes are reported only as these indices.
* It does not test generalisation beyond this TCGA subset (no external cohort).
* Timings are from one shared virtual machine and are indicative only.

## Data
Download `TCGA-PANCAN-HiSeq-801x20531.tar.gz` from https://archive.ics.uci.edu/dataset/401 (doi:10.24432/C5R88H),
extract it and place `data.csv` and `labels.csv` in `data/`. Expected SHA-256:

    data.csv    e3e7eff51f4a5fe5f121fb183c09786c767c755ef10d1c7b3ce3c193a7082ca9
    labels.csv  e1653ccf5a630deb3b953ccac5a8b331b89adc5433e5d2d3444c1fc01d79e7aa

## Run
    python -m venv .venv && . .venv/bin/activate
    pip install -r requirements.txt
    python run_all.py                    # full run: main benchmark about 18 min on one thread, then the
                                         # revision analyses (about 1 h with --jobs 8 on 8 vCPUs, mostly LightGBM on all genes)
    python run_all.py --quick            # 2-repeat smoke test
    python run_all.py --revision-only    # rerun only the revision analyses, reusing results/
    python run_all.py --revision-only --extension-only   # only the extension analyses (about 5 min)
    python run_all.py --jobs 4           # number of parallel workers for the revision analyses (default 8)
    python run_all.py --allgenes-jobs 2  # workers for the all-genes benchmark (default 4, capped by available RAM)

## Memory
Peak RAM is set by the all-genes benchmark (every classifier on about 20,264 genes). One worker peaks at about
1.4 GB resident (measured: LightGBM and the MLP on one fold; the linear models stay below 0.7 GB), so the code budgets
2 GB per worker and never starts more workers than fit in 80% of the currently available RAM, whatever
`--allgenes-jobs` says. With the default 4 workers the full run needs about 8 GB of RAM; 8 workers need about 16 GB
and can run out of memory on a 16 GB machine. The other steps fit at most 1,000 genes and use much less memory per worker.

Outputs: `results/` (CSV/JSON: fold scores, summary, paired tests, ablation, stability, top genes, footprint,
misclassified samples, permutation check, leak_*.csv, pairwise_all.csv, ceiling_stats.json, stability_phi.json,
sample_qc.csv, global_qc_predictability.json, allgenes_*.csv, nov_*.csv, rob_*.csv) and `figures/` (PNG, 300 dpi). The first run caches the matrix as
`data/X.npy`.

## Files
* `run_all.py` - entry point.
* `src/experiments.py` - data loading, pipeline, models, CV, statistics, ablation, stability, footprint.
* `src/audit.py` - leakage audit, all-pairs/equivalence statistics, sample QC, Nogueira stability, all-gene benchmark.
* `src/novelty.py` - calibration, conformal prediction and abstention, learning curves, leakage vs n.
* `src/robust.py` - robustness checks and confidence intervals for the reliability and data-efficiency results.
* `src/figures.py` - figures.
* `requirements.txt` - pinned versions used for the paper.

Results were produced with Python 3.13 on Linux x86-64. Small numerical differences are possible on other
platforms or library versions (for example in the MLP and LightGBM).
