# Results

All numbers below are copied from `CHANGES.md` (section 2) and the manuscripts in `paper/`. The code in `code/`
regenerates them into `code/results/` (CSV/JSON) and `code/figures/` (300 dpi PNG).

## 1. Leakage audit
* Real labels, all 801 samples: fitting gene selection on the full dataset changes accuracy by **at most 0.29 point**
  (20 or more genes). Softmax with 100 genes: **99.50%** leaky vs **99.48%** in-fold.
* Bias is clear only with permuted labels and small samples: **68.2% vs 19.9%** at n = 60.
* Conclusion: near-perfect accuracy on this dataset cannot show that a pipeline is free of leakage.

## 2. Model comparison
* No pair of the seven classifiers differs significantly (smallest Holm-adjusted **p = 0.66**).
* Equivalence within ±1 point for **10 of the 15** pairs not involving naive Bayes; the rest are inconclusive.

## 3. Stability and errors
* ANOVA top-100 selection: Nogueira **Φ = 0.93**.
* The few persistent errors are atypical expression profiles by sample-level quality metrics.

## 4. Calibration and conformal prediction
* Softmax pooled ECE **0.47%** (95% CI 0.25–0.83) vs **0.14%** (0.08–0.22) expected for a perfectly calibrated model;
  the 80 low-confidence predictions hold all **42** errors. Random forest ECE **2.7%** (under-confident).
* Marginal coverage (softmax): **89.6 / 94.7 / 99.4%** at 90 / 95 / 99%; fold minimum 78.1% at 90% and 96.9% at 99%.
* Abstention at 99%: error among accepted predictions **0.51%** (0.42–0.60) → **0.18%** (0.10–0.25); plain
  max-probability threshold **0.26%** (0.16–0.35).
* Naive Bayes over-covers (98.6% at 90% and 95%); randomised p-values give **90.2 / 94.5 / 99.0%**.
* Atypical LUAD samples flagged in **18 of 30** appearances (95% CI 41–77%).
* Mondrian sets are uninformative at 99% (no class has the 99 calibration samples required).

## 5. Data efficiency
* Linear models reach **99.4%** macro-F1 (95% CI ±0.2) with **10** training tumours per class.
* Permuted-label leakage bias: **65.1 ± 4.8** points at n = 30 → **14.1 ± 1.7** at n = 390. With real labels it stays
  near zero (10 genes: −1.6 ± 0.8 at n = 390).
