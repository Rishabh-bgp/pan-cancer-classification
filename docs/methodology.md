# Methodology

*(Summarised from `code/README.md` and `CHANGES.md`.)*

## Pipeline (fitted inside every training fold)
zero-variance filter → ANOVA-F top-k gene selection → z-scoring → classifier. Nothing is fitted on test data.

## Models
Majority-class baseline, softmax (multinomial logistic) regression, ridge classifier, linear SVM, Gaussian naive
Bayes, random forest, LightGBM and a one-hidden-layer MLP. Hyperparameters are fixed in advance (no tuning).

## Evaluation
* 10 × 5 repeated stratified cross-validation (50 identical folds for every model).
* Metrics: accuracy, macro-F1, balanced accuracy, macro one-vs-rest ROC-AUC.
* Nadeau–Bengio corrected 95% confidence intervals.
* All 21 pairwise corrected t-tests with Holm adjustment; TOST equivalence (±1 point); Bayesian correlated t-test
  (ROPE ±0.5 point); minimum detectable differences.
* Feature-count ablation (k = 2 … all), selection stability (Nogueira Φ), label-permutation check, footprint profile.

## Leakage audit (`src/audit.py`)
Leaky vs in-fold selection with real labels (n = 801), 100 permuted-label runs (n = 801) and 50 small subsamples
(n = 60); per-sample quality metrics; all seven classifiers with every expressed gene.

## Reliability and data efficiency (`src/novelty.py`)
Calibration (ECE, Brier, reliability bins); split-conformal prediction sets (marginal and Mondrian, 90/95/99%) nested
inside each outer training fold, with abstention on non-singleton sets; learning curves (3–60 training tumours per
class); leaky vs in-fold selection in balanced subsamples of n = 30–390.

## Robustness (`src/robust.py`)
Fold-level coverage spread and calibration-conditional (Beta) coverage; max-probability threshold baseline;
cross-conformal sets (5 inner folds); randomised conformal p-values; pooled ECE with bootstrap CI, equal-mass ECE and
log-loss; 95% CIs for learning curves and leakage-vs-n results.
