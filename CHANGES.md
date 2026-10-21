# Change log and summary for reviewers

**Study:** What Near-Perfect Accuracy Does and Does Not Show on the UCI TCGA Pan-Cancer RNA-Seq Dataset: Leakage,
Equivalence, Conformal Reliability and Data Efficiency

**Author:** Er. Rishabh Aryan, M.Tech (Artificial Intelligence and Data Science), Department of Computer Science and
Engineering, Indian Institute of Information Technology Bhagalpur, Bihar, India. ORCID 0009-0004-7595-9440.

**Version:** revised version, 16 October 2026. It replaces the earlier versions of the manuscript, slides and code.

## 1. What the study is
The UCI "gene expression cancer RNA-Seq" dataset (doi:10.24432/C5R88H; 801 TCGA tumours, 20,531 genes, five cancer
types) is widely used to report near-perfect tumour-type classification. This study asks what such accuracies can and
cannot support. It answers the question empirically, with code that regenerates every number and figure. It does not
propose a new classifier.

* **Protocol.** Gene filtering, ANOVA-F selection and standardisation are fitted inside every training fold.
* **Models.** Seven classifiers and a majority baseline, compared by 10x5 repeated stratified cross-validation
  (50 identical folds).
* **Statistics.**
  * Nadeau-Bengio corrected confidence intervals.
  * All 21 pairwise corrected t-tests with Holm adjustment.
  * Equivalence tests (TOST, +-1 percentage point).
  * Bayesian correlated t-tests (ROPE +-0.5 point).
  * Minimum detectable differences.

## 2. Main findings and contributions
1. **Leakage audit.**
   * With real labels and all 801 samples, fitting gene selection on the full dataset changes accuracy by at most
     0.29 point (for 20 or more genes). For softmax with 100 genes it is 99.50% leaky vs 99.48% in-fold.
   * The bias is clear only with permuted labels and small samples: 68.2% vs 19.9% at n = 60.
   * Near-perfect accuracy on this dataset therefore cannot show that a pipeline is free of leakage.
2. **Protocol audit of prior work.** A table of published protocols on this dataset (Nitta 2021, Wahid & Banday 2023,
   Alanazi 2024, Akter 2025). It is positioned against Sirohi (2026), a stability study on a larger TCGA extract.
3. **Model comparison.**
   * No pair of the seven classifiers differs significantly (smallest Holm-adjusted p = 0.66).
   * Equivalence within +-1 point is shown for 10 of the 15 pairs that do not involve naive Bayes. The remaining pairs
     are inconclusive.
   * Naive Bayes is probably slightly worse, but not significantly.
4. **Selection stability and errors.**
   * The ANOVA top-100 selection is highly stable (Nogueira Phi = 0.93).
   * The few persistent errors are atypical expression profiles by sample-level quality metrics.
5. **Reliability (applied to this dataset for the first time, to our knowledge).** Calibration and split-conformal
   prediction sets (marginal and class-conditional/Mondrian), computed inside each training fold, with abstention on
   non-singleton sets.
   * Calibration: softmax pooled ECE 0.47% (95% CI 0.25-0.83) against 0.14% (0.08-0.22) expected for a perfectly
     calibrated model with the same confidences. This is small and probably real miscalibration, and it lies in the 80
     low-confidence predictions, which hold all 42 errors. The random forest is clearly under-confident (ECE 2.7%).
   * Marginal coverage is valid on average (softmax 89.6 / 94.7 / 99.4% at 90 / 95 / 99%). It varies widely between
     calibration sets of about 160 tumours: fold minimum 78.1% at 90% and 96.9% at 99%.
   * At 99%, abstaining on non-singleton sets lowers the error among accepted predictions from 0.51% (95% CI 0.42-0.60)
     to 0.18% (0.10-0.25). A plain maximum-probability threshold gives 0.26% (0.16-0.35), so conformal prediction
     supplies a calibrated threshold with a coverage guarantee rather than better error selection.
   * Naive Bayes over-covers (98.6% at 90% and 95%) because saturated probabilities tie the scores; randomised p-values
     restore 90.2 / 94.5 / 99.0%.
   * The atypical LUAD samples are flagged in 18 of their 30 appearances (95% CI 41-77%).
   * Mondrian sets are uninformative at 99% because no class has the 99 calibration samples required (about 60 BRCA,
     29 KIRC, 28 LUAD, 27 PRAD, 16 COAD).
6. **Data efficiency (confirmation of known results on this dataset).**
   * Linear models reach 99.4% macro-F1 (95% CI +-0.2) with 10 training tumours per class.
   * Leakage bias on permuted labels falls from 65.1 +- 4.8 points at n = 30 to 14.1 +- 1.7 at n = 390, as earlier
     simulations predict (Vabalas et al. 2019). With real labels it stays near zero, and with 10 genes it is slightly
     negative at n = 390 (-1.6 +- 0.8).

**Novelty check (October 2026).**
* Conformal prediction has been applied to other expression-based classifiers:
  * leukaemia RNA-Seq (JCO Clinical Cancer Informatics 2025);
  * TCGA breast-cancer PAM50 (Frontiers in AI 2026);
  * lymphoma (Frontiers in Bioinformatics 2025).
* Leakage bias versus sample size was characterised by Vabalas et al. (PLOS ONE 2019). Learning curves for expression
  classifiers go back to Mukherjee et al. (2003), Figueroa et al. (2012) and Qi et al. (2025, bulk RNA-Seq). These are
  now cited, and the data-efficiency results are presented as confirmations on this dataset.
* We found no study reporting calibration, conformal sets or abstention on this dataset.
* Small gene panels for this dataset have been reported before (for example 17 genes; models with 4, 31 and 74 genes).
  A "minimal panel" is therefore not claimed as a contribution.

## 3. What changed from earlier versions, and why
| Area | Earlier version | Now | Reason |
|---|---|---|---|
| Gene names | Gene symbols (e.g. ESR1, KLK3) attached to anonymised columns, with hand-set weights and claimed KEGG/COSMIC checks | No gene symbols; genes reported only by their anonymised UCI index, with selection frequency and coefficients | The UCI release uses dummy names (gene_0 ... gene_20530); the symbols could not have come from the data |
| Document files | DOCX with corrupted text (unescaped characters) | Rebuilt DOCX and PDF, checked page by page | File integrity |
| Affiliation and metadata | Wrong affiliation; publication-target and "proposed publication" lines | Correct IIIT Bhagalpur affiliation and ORCID; anonymised review copy and camera-ready copy | Accuracy; double-blind review |
| Evaluation | Single 5-fold CV; softmax presented as the proposed best model | 10x5 repeated CV, seven classifiers plus baseline, corrected CIs; softmax ranks 4th of 7 and is not called best | Single splits cannot separate models differing by a few samples |
| Framing | "Leakage-free benchmark"; dataset presented as a leakage check | Leakage quantified: it barely changes accuracy here at full size; dataset cannot reveal leakage | The audit showed the original premise was weak; reported honestly |
| Statistics | Paired tests only against softmax; "no model is better" | All 21 pairs with Holm, TOST equivalence, Bayesian test, minimum detectable difference; claim scoped to what is shown | A non-significant result is not equivalence |
| Errors | "Possibly mislabelled" | Sample-level quality metrics; atypical profiles documented; whole-profile statistics predict class at 52.7% balanced accuracy (stated as a limitation) | Evidence instead of speculation |
| All-gene setting | Partial | All seven classifiers with every expressed gene (ridge and linear SVM: no errors; naive Bayes 56.5%) | Completeness |
| Reliability, data efficiency | Absent | Sections 4.6-4.7, Figs. 2-3, Table 4, Supplement S11-S12 | Contributions supported by the anonymised data |
| Claims removed | log2 transform, BH-FDR, "Nesterov" momentum, "airtight", page-count claims | Removed | Not performed by the code, or not accurate |
| References | Padding citations (e.g. AlphaFold) | 46 references, all relevant; every DOI resolved via Crossref, other items opened online | Accuracy and relevance |
| Figures | Low-resolution PNGs (400x400 px) | All figures regenerated by the code at 300 dpi | Quality |
| Slides | Earlier deck | 16 slides in the NIELIT Bio-AI Conclave 2026 template (Track 2), with speaker notes, matching the paper | Consistency |

### Second review round (16 October 2026)
| Area | Before | Now | Reason |
|---|---|---|---|
| Novelty claims | Contributions, abstract and slides called the reliability and data-efficiency angles "new" | Prior work cited (Vabalas 2019; Mukherjee 2003; Figueroa 2012; Qi 2025); reliability is "applied to this dataset for the first time, to our knowledge"; data efficiency is presented as a confirmation | Leakage-versus-n and learning curves are known results |
| Conformal analysis | Coverage reported as means only; "conformal" abstention not compared with a simpler rule | Fold coverage range and calibration-conditional (Beta) coverage; threshold varies 0.05-0.97 across folds; maximum-probability baseline at the same threshold and at matched abstention; cross-conformal variant; bootstrap CIs on accepted error; point predictions stated to come from the 75% model | At 99% with about 160 calibration samples, the quantile is a single score; conformal adds a calibrated threshold, not better selection |
| Naive Bayes coverage | "Close to nominal for every model" | Over-coverage from tied scores reported and fixed with randomised p-values | Saturated probabilities produce ties |
| Mondrian explanation | Failure attributed to about 16 COAD calibration samples | Every class has fewer than the 99 samples needed at 99% (about 60 BRCA ... 16 COAD); COAD alone explains the 95% case | Correct finite-sample condition |
| Calibration | "Well calibrated" (per-fold ECE 0.59%) | Pooled ECE with bootstrap CI, perfectly calibrated reference by consistency resampling, equal-mass ECE, log-loss; reliability diagram shows all bins with counts; wording "small and probably real miscalibration" | Per-fold ECE sits near its sampling-noise floor |
| Learning curves, leakage vs n | Point means or +-SD | 95% CIs (repeats or subsamples); n = 801 point drawn separately as a different design; negative real-label difference at k = 10 and subsample overlap at n = 390 stated | Uncertainty and design caveats |
| Length and consistency | 29-page review copy, 366-word abstract | 23 pages, 295-word abstract; pairwise table, coefficient table, footprint section, PCA, model-comparison, confusion, ablation and stability figures moved to the supplement (now 11 pages); Sections 2.3 and 2.4 merged; declarations worded independently of author count; slide labels and notes aligned with the paper | Readability; consistency |
| Code | All-gene step used 8 workers | Memory-aware worker count for the all-gene step (default 4, capped by available RAM); peak RAM stated in the code README | Out-of-memory failure at 8 workers |

### Third review round (16 October 2026)
Accepted with minor edits. Wording polished: fold coverage is described as wider than the calibration-conditional
5th percentiles (each test fold adds binomial noise; 9 of 50 folds fall below them); the cross-conformal accepted
error is given next to its 0.62% no-abstention error; miscalibration is called "small and probably real" (no
tumour-level clustered reference); linear SVM learning-curve interval shown as ±0.04. No analyses were rerun.
A 4-page plain-language explainer (explainer/PanCancer_Simple_Explainer) was added; its numbers match the paper.
The calibration summary above now matches the paper: the 80 predictions below 0.93 confidence hold all 42 errors.

## 4. Reproducibility
* `supplementary/PanCancer_code_S1.zip` contains `run_all.py`, `src/` and pinned `requirements.txt`; `data/` holds the
  dataset.
* SHA-256 checksums:
  * data.csv: e3e7eff51f4a5fe5f121fb183c09786c767c755ef10d1c7b3ce3c193a7082ca9
  * labels.csv: e1653ccf5a630deb3b953ccac5a8b331b89adc5433e5d2d3444c1fc01d79e7aa
* Verification: the code was unpacked into a fresh directory with a fresh virtual environment and run from the CSV
  files. Every result file (main benchmark, ablation, leakage audit, pairwise statistics, quality metrics, stability and
  all-gene benchmark) matched the results used in the paper. Maximum absolute difference: 0, or about 1e-14 from
  floating-point summation; timings excluded.
* The new analyses (calibration, conformal prediction, learning curves, leakage vs sample size) were rerun from the released code archive in a fresh environment; all nine result tables matched exactly (maximum absolute difference 0).
* Second-round analyses (src/robust.py: calibration references, conformal robustness checks and confidence
  intervals) were rerun from the updated code archive in a fresh environment, together with the
  extension analyses; all 17 result tables matched exactly (maximum absolute difference 0).
* Run time on an 8-vCPU machine:
  * main benchmark: about 18 min on one thread;
  * revision analyses: about 1 h, mostly LightGBM on all genes (4 workers by default, see the memory note in the code README);
  * extension and robustness analyses: about 5 min.

## 5. Known limitations and open items
* Single source (TCGA), five well-separated tissue types, no clinical metadata, no external cohort.
* Genes are anonymised. Mapping indices to symbols requires the original Synapse annotation (syn4301332) and is left
  for future work.
* Conformal guarantees assume exchangeability and apply only within TCGA-like data; with about 160 calibration
  tumours, coverage varies widely between calibration sets.
* Calibration references treat the ten predictions per tumour as independent, so their ranges are somewhat too narrow.
* The author still has to finalise the funding, licence and repository-link placeholders and the AI-use and
  conflict-of-interest declarations, and confirm the venue, track and any length limit with the organisers.
* A separate upload package for a double-blind portal (anonymised paper and supplement only, without this file, the
  README or the data) will be prepared once the venue is confirmed.

## Submission-guideline audit (16 Oct 2026)
* Checked against every section of the NIELIT Bio-AI Conclave 2026 full-paper guidelines; see submission_checklist.md.
* Added Section 3.8 "Software and computational environment" (Python and library versions, hardware, single-script rerun).
* Data Availability Statement now gives the software details asked for in guideline section 15 (name, version, language,
  platform, dependencies, licence placeholder).
* Added separate Funding and Author Contributions sections (placeholders to confirm; removed in the anonymised copy).
* Table notes are now double-spaced like the rest of the text.
* Added a cover letter / author declaration (guideline section 22). No scientific number changed.
