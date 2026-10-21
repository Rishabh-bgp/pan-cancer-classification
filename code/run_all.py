"""Reproduce every number and figure in the paper.
Usage: python run_all.py [--data data] [--quick]
Expects data/data.csv and data/labels.csv from the UCI repository (DOI 10.24432/C5R88H).
"""
import argparse, json, os, sys, time, platform
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
import experiments as E, figures as Fg, audit as AU, novelty as NV, robust as RB

ap = argparse.ArgumentParser(); ap.add_argument("--data", default="data"); ap.add_argument("--quick", action="store_true")
ap.add_argument("--revision-only", action="store_true", help="reuse results/ from a previous full run; run only the revision analyses")
ap.add_argument("--jobs", type=int, default=8)
ap.add_argument("--allgenes-jobs", type=int, default=4, help="workers for the memory-heavy all-genes step (capped by available RAM)")
ap.add_argument("--extension-only", action="store_true", help="run only the extension analyses (reliability, data efficiency)")
a = ap.parse_args()
if a.quick: E.N_REPEATS = 2
os.makedirs("results", exist_ok=True); os.makedirs("figures", exist_ok=True)
t0 = time.time()
X, y, genes, ids = E.load(a.data)
print("data", X.shape, np.bincount(y).tolist())
if a.revision_only:
    import pickle, pandas as pd
    df = pd.read_csv("results/fold_scores.csv"); aux = pickle.load(open("results/aux.pkl", "rb"))
    selc, sels = aux["sel_counts"], aux["sel_sets"]
    mis = json.load(open("results/softmax_misclassified.json"))
else:
    df, cms, wrong, selc, sels = E.main_benchmark(X, y, ids, "results")
if not a.revision_only:
    S, T = E.summarise(df, X, y, "results")
    G = E.ablation_k(X, y, "results")
    perm = E.permutation_check(X, y, "results")
    P, stab, chosen = E.full_fit_probes(X, y, genes, selc, "results")
    F = E.footprint(X, y, "results")
    # consistently misclassified samples (softmax)
    sm = "Softmax (multinomial LR, L2)"
    mis = {ids[i]: dict(true=E.CLASSES[y[i]], predicted=[E.CLASSES[p] for p in v], times=len(v)) for i, v in sorted(wrong.get(sm, {}).items())}
    json.dump(mis, open("results/softmax_misclassified.json", "w"), indent=2)
    # Jaccard between fold-wise selected sets
    J = [len(a_ & b_) / len(a_ | b_) for i, a_ in enumerate(sels) for b_ in sels[i + 1:]]
    stab["mean_pairwise_jaccard"] = float(np.mean(J)); stab["min_pairwise_jaccard"] = float(np.min(J))
    json.dump(stab, open("results/selection_stability.json", "w"), indent=2)
    Fg.fig_data(X, y, "figures"); Fg.fig_models(S, "figures"); Fg.fig_ablation(G, "figures")
    Fg.fig_cm(cms[sm], "Softmax (k = 100)", "figures"); Fg.fig_stability(selc, E.N_REPEATS * E.N_SPLITS, "figures"); Fg.fig_footprint(S, F, "figures")
    json.dump(dict(python=platform.python_version(), machine=platform.machine(), cpu_count=os.cpu_count(),
                   runtime_min=(time.time() - t0) / 60, n_repeats=E.N_REPEATS), open("results/run_info.json", "w"), indent=2)
    print(S[["model", "acc", "acc_lo", "acc_hi", "f1", "auc", "errors_per_repeat_mean"]].to_string())
    print(T.to_string()); print(perm); print(stab)
if a.extension_only:
    NV.reliability(X, y, ids, "results", n_jobs=a.jobs); NV.data_efficiency(X, y, "results", n_jobs=a.jobs)
    RB.analyse(RB.collect(X, y, "results", a.jobs), X, y, ids, "results"); RB.data_eff_ci("results")
    Fg.fig_reliability("results", "figures"); Fg.fig_efficiency("results", "figures"); sys.exit(0)
# ---------------- revision analyses (R1, R3, R5, R6, R7)
t1 = time.time()
if not a.revision_only:
    mis = json.load(open("results/softmax_misclassified.json"))
AU.leakage_audit(X, y, "results", n_perm=20 if a.quick else 100, n_sub=10 if a.quick else 50, n_jobs=a.jobs)
AU.pairwise_stats(df, "results")
AU.sample_qc(X, y, ids, mis, "results")
AU.stability_phi(sels, int((X.var(0) > 0).sum()), E.K_MAIN, "results")
AU.benchmark_all_genes(X, y, "results", n_jobs=a.allgenes_jobs)
Fg.fig_leakage("results", "figures")
print(f"revision analyses done in {(time.time()-t1)/60:.1f} min")
# ---------------- extension analyses: reliability (conformal, calibration) and data efficiency
t2 = time.time()
NV.reliability(X, y, ids, "results", n_jobs=a.jobs)
NV.data_efficiency(X, y, "results", n_jobs=a.jobs, n_sub=4 if a.quick else 30)
RB.analyse(RB.collect(X, y, "results", a.jobs), X, y, ids, "results"); RB.data_eff_ci("results")
Fg.fig_reliability("results", "figures"); Fg.fig_efficiency("results", "figures")
print(f"extension analyses done in {(time.time()-t2)/60:.1f} min")
print(f"done in {(time.time()-t0)/60:.1f} min")
