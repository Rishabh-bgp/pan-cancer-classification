"""Revision analyses: leakage audit (R1), all-pairs/equivalence statistics (R3), per-sample QC of errors (R5),
permutation test and chance-corrected stability (R6), main benchmark with all genes (R7)."""
import itertools, json, time
import numpy as np, pandas as pd
from scipy import stats
from joblib import Parallel, delayed
from sklearn.base import clone
from sklearn.feature_selection import f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold
import experiments as E

AUDIT_MODELS = {"Softmax": LogisticRegression(C=1.0, max_iter=5000),
                "Linear SVM": LinearSVC(C=1.0, max_iter=20000),
                "Gaussian NB": GaussianNB()}
KS = [10, 20, 100, 1000]


def _fscore(X, y):
    v = X.var(0) > 0
    F = np.zeros(X.shape[1]); F[v] = np.nan_to_num(f_classif(X[:, v], y)[0])
    F[~v] = -1
    return F


def _top(F, k):
    return np.argsort(-F, kind="stable")[:k]


def _fit_eval(clf, Xtr, ytr, Xte, yte, idx, mu, sd):
    c = clone(clf).fit((Xtr[:, idx] - mu) / sd, ytr)
    p = c.predict((Xte[:, idx] - mu) / sd)
    return accuracy_score(yte, p), f1_score(yte, p, average="macro")


def _cv_both(X, y, splits, ks, models):
    """Leaky (selection + scaling on all samples) vs clean (in-fold) for one label vector; returns rows per fold."""
    Ffull = _fscore(X, y); rows = []
    for f, (tr, te) in enumerate(splits):
        Ftr = _fscore(X[tr], y[tr])
        for k in ks:
            for mode, F, ref in [("leaky", Ffull, X), ("clean", Ftr, X[tr])]:
                idx = _top(F, k); mu = ref[:, idx].mean(0); sd = ref[:, idx].std(0) + 1e-12
                for name, clf in models.items():
                    a, f1 = _fit_eval(clf, X[tr], y[tr], X[te], y[te], idx, mu, sd)
                    rows.append(dict(fold=f, k=k, mode=mode, model=name, acc=a, f1=f1))
    return rows


def leakage_audit(X, y, out, n_perm=100, n_sub=50, sub_n=60, n_jobs=8):
    t0 = time.time()
    # (a) real labels, 10x5 repeated CV, three classifiers, four k
    cv = list(RepeatedStratifiedKFold(n_splits=5, n_repeats=E.N_REPEATS, random_state=E.SEED).split(X, y))
    real = pd.DataFrame(_cv_both(X, y, cv, KS, AUDIT_MODELS))
    real.to_csv(f"{out}/leak_real_folds.csv", index=False)
    n_te = len(y) / 5; n_tr = len(y) - n_te
    summ = []
    for (k, m), g in real.groupby(["k", "model"]):
        a = g[g["mode"] == "leaky"].sort_values("fold"); b = g[g["mode"] == "clean"].sort_values("fold")
        for met in ["acc", "f1"]:
            d = a[met].values - b[met].values
            mm, t, p, ci = E.corrected_t(d, n_tr, n_te)
            summ.append(dict(k=k, model=m, metric=met, leaky=a[met].mean(), clean=b[met].mean(), diff=mm, ci_lo=ci[0], ci_hi=ci[1], p=p))
    pd.DataFrame(summ).to_csv(f"{out}/leak_real_summary.csv", index=False)
    print(f"  leakage audit real labels done ({(time.time()-t0)/60:.1f} min)", flush=True)

    # (b) permuted labels, full n: softmax, k in {10, 100}; one 5-fold split per permutation
    def one_perm(i):
        rng = np.random.default_rng(E.SEED + 1000 + i); yp = rng.permutation(y)
        sp = list(StratifiedKFold(5, shuffle=True, random_state=E.SEED + i).split(X, yp))
        r = pd.DataFrame(_cv_both(X, yp, sp, [10, 100], {"Softmax": AUDIT_MODELS["Softmax"]}))
        return r.groupby(["k", "mode"]).acc.mean().reset_index().assign(perm=i)
    perm = pd.concat(Parallel(n_jobs=n_jobs)(delayed(one_perm)(i) for i in range(n_perm)))
    perm.to_csv(f"{out}/leak_perm_fullN.csv", index=False)
    print(f"  permutations full n done ({(time.time()-t0)/60:.1f} min)", flush=True)

    # (c) small-n setting (n = 60, 12 per class), as in Ambroise & McLachlan: real and permuted labels
    def one_sub(i):
        rng = np.random.default_rng(E.SEED + 5000 + i)
        idx = np.concatenate([rng.choice(np.where(y == c)[0], sub_n // 5, replace=False) for c in range(5)])
        Xs, ys = X[idx], y[idx]; res = []
        for lab, yy in [("real", ys), ("permuted", rng.permutation(ys))]:
            sp = list(StratifiedKFold(5, shuffle=True, random_state=E.SEED + i).split(Xs, yy))
            r = pd.DataFrame(_cv_both(Xs, yy, sp, [10, 100], {"Softmax": AUDIT_MODELS["Softmax"]}))
            res.append(r.groupby(["k", "mode"]).acc.mean().reset_index().assign(sub=i, labels=lab))
        return pd.concat(res)
    sub = pd.concat(Parallel(n_jobs=n_jobs)(delayed(one_sub)(i) for i in range(n_sub)))
    sub.to_csv(f"{out}/leak_small_n.csv", index=False)
    print(f"  small-n audit done ({(time.time()-t0)/60:.1f} min)", flush=True)
    return real, perm, sub


def pairwise_stats(df, out, rope=0.005, margin=0.01):
    n = 801; n_te = n / 5; n_tr = n - n_te; rho = n_te / n
    ms = [m for m in df.model.unique() if m != "Majority baseline"]
    rows = []
    for a, b in itertools.combinations(ms, 2):
        A = df[df.model == a].sort_values("fold"); B = df[df.model == b].sort_values("fold")
        for met in ["f1", "acc"]:
            d = B[met].values - A[met].values; J = len(d); m = d.mean(); v = d.var(ddof=1)
            se = np.sqrt((1 / J + n_te / n_tr) * v); t = m / se if se > 0 else 0; p = 2 * stats.t.sf(abs(t), J - 1) if se > 0 else 1
            pt = max(stats.t.sf((m + margin) / se, J - 1), stats.t.cdf((m - margin) / se, J - 1)) if se > 0 else 0
            post = stats.t(J - 1, loc=m, scale=np.sqrt((1 / J + rho / (1 - rho)) * v))
            pa = post.cdf(-rope); pr = post.cdf(rope) - pa; pb = 1 - post.cdf(rope)
            mdd = (stats.t.ppf(0.975, J - 1) + stats.t.ppf(0.8, J - 1)) * se
            rows.append(dict(a=a, b=b, metric=met, diff_b_minus_a=m, t=t, p=p, tost_p=pt, P_a_better=pa, P_rope=pr,
                             P_b_better=pb, mdd80=mdd))
    T = pd.DataFrame(rows)
    for met in ["f1", "acc"]:
        idx = T[T.metric == met].sort_values("p").index; mm = len(idx); prev = 0
        for j, i in enumerate(idx):
            prev = max(prev, min(1, (mm - j) * T.loc[i, "p"])); T.loc[i, "p_holm21"] = prev
        idx = T[T.metric == met].sort_values("tost_p").index; prev = 0
        for j, i in enumerate(idx):
            prev = max(prev, min(1, (mm - j) * T.loc[i, "tost_p"])); T.loc[i, "tost_p_holm21"] = prev
    T.to_csv(f"{out}/pairwise_all.csv", index=False)
    perfect = df.groupby("model").f1.apply(lambda v: float((v == 1).mean())).to_dict()
    errs = {}
    for m, g in df.groupby("model"):
        e = int(g.err.sum()); N = 801 * E.N_REPEATS
        lo, hi = stats.binomtest(e, N).proportion_ci(method="wilson") if e < N else (1, 1)
        errs[m] = dict(errors=e, predictions=N, rate=e / N, wilson_lo=lo, wilson_hi=hi)
    json.dump(dict(perfect_fold_fraction=perfect, pooled_errors=errs), open(f"{out}/ceiling_stats.json", "w"), indent=2)
    return T


def sample_qc(X, y, ids, mis, out):
    v = X.var(0) > 0; Xv = X[:, v]
    mean = Xv.mean(1); zero = (Xv == 0).mean(1)
    corr = np.zeros(len(y))
    for c in range(5):
        m = np.where(y == c)[0]; S = Xv[m].sum(0)
        for i in m:
            cen = (S - Xv[i]) / (len(m) - 1); corr[i] = np.corrcoef(Xv[i], cen)[0, 1]
    rows = []
    for i in range(len(y)):
        rows.append(dict(sample=ids[i], cls=E.CLASSES[y[i]], mean_expr=mean[i], zero_frac=zero[i], corr_to_centroid=corr[i]))
    Q = pd.DataFrame(rows)
    for col in ["mean_expr", "zero_frac", "corr_to_centroid"]:
        g = Q.groupby("cls")[col]; Q[col + "_z"] = (Q[col] - g.transform("mean")) / g.transform("std")
        Q[col + "_rank"] = g.rank(method="min").astype(int) - 1
    Q["n_in_class"] = Q.groupby("cls")["sample"].transform("count")
    Q["misclassified_times"] = Q["sample"].map(lambda s: mis.get(s, {}).get("times", 0))
    Q.to_csv(f"{out}/sample_qc.csv", index=False)
    # can global QC statistics alone predict class? (5-fold LR on 3 features + 6 percentiles)
    from sklearn.model_selection import cross_val_predict
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    from sklearn.metrics import balanced_accuracy_score
    G = np.column_stack([mean, Xv.std(1), zero] + [np.percentile(Xv, q, axis=1) for q in (5, 25, 50, 75, 95, 99)])
    pr = cross_val_predict(make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000)), G, y,
                           cv=StratifiedKFold(5, shuffle=True, random_state=E.SEED))
    r = dict(global_qc_balanced_accuracy=float(balanced_accuracy_score(y, pr)))
    json.dump(r, open(f"{out}/global_qc_predictability.json", "w"), indent=2)
    return Q, r


def stability_phi(sets, p, k, out, n_boot=1000):
    M = len(sets); Z = np.zeros((M, p), bool)
    for i, s in enumerate(sets): Z[i, list(s)] = True
    def phi(Z):
        M = Z.shape[0]; pf = Z.mean(0); s2 = M / (M - 1) * pf * (1 - pf); kb = Z.sum(1).mean()
        return 1 - s2.mean() / ((kb / p) * (1 - kb / p))
    def kuncheva(Z):
        vals = []
        for i in range(len(Z)):
            for j in range(i + 1, len(Z)):
                r = (Z[i] & Z[j]).sum(); vals.append((r * p - k * k) / (k * (p - k)))
        return float(np.mean(vals))
    rng = np.random.default_rng(E.SEED); bs = [phi(Z[rng.integers(0, M, M)]) for _ in range(n_boot)]
    r = dict(nogueira_phi=float(phi(Z)), phi_boot_lo=float(np.percentile(bs, 2.5)), phi_boot_hi=float(np.percentile(bs, 97.5)),
             kuncheva=kuncheva(Z), n_selections=M, p=int(p), k=int(k))
    json.dump(r, open(f"{out}/stability_phi.json", "w"), indent=2); return r


ALLGENES_GB_PER_WORKER = 2.0   # one worker peaks at about 1.4 GB (LightGBM/MLP on ~20,264 genes); 2 GB budget, see README


def _mem_available_gb():
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable:"): return int(line.split()[1]) / 2 ** 20
    except OSError:
        pass
    try:
        import psutil; return psutil.virtual_memory().available / 2 ** 30
    except Exception:
        return None


def allgenes_jobs(requested):
    """Memory-aware worker count for the all-genes benchmark: at most what fits in 80% of available RAM."""
    avail = _mem_available_gb()
    if avail is None: return min(requested, 2)
    fit = max(1, int(0.8 * avail // ALLGENES_GB_PER_WORKER))
    return max(1, min(requested, fit))


def benchmark_all_genes(X, y, out, n_jobs=4):
    n_jobs = allgenes_jobs(n_jobs)
    print(f"  all-genes benchmark: {n_jobs} parallel workers (about {ALLGENES_GB_PER_WORKER:.0f} GB each)", flush=True)
    cv = list(RepeatedStratifiedKFold(n_splits=5, n_repeats=E.N_REPEATS, random_state=E.SEED).split(X, y))
    def run(f, tr, te):
        rows = []
        for name, clf in E.models().items():
            if name == "Majority baseline": continue
            p = E.pipe(clf, "all"); t0 = time.perf_counter(); p.fit(X[tr], y[tr]); tf = time.perf_counter() - t0
            yp = p.predict(X[te]); m = E.fold_metrics(y[te], yp, E.scores(p, X[te]))
            rows.append(dict(model=name, fold=f, fit_s=tf, **m))
        return rows
    res = Parallel(n_jobs=n_jobs)(delayed(run)(f, tr, te) for f, (tr, te) in enumerate(cv))
    D = pd.DataFrame([r for rr in res for r in rr]); D.to_csv(f"{out}/allgenes_fold_scores.csv", index=False)
    n_te = len(y) / 5; n_tr = len(y) - n_te; rows = []
    for name, g in D.groupby("model", sort=False):
        r = dict(model=name)
        for k in ["acc", "f1", "auc"]:
            v = g[k].values; m = v.mean(); h = stats.t.ppf(0.975, len(v) - 1) * np.sqrt((1 / len(v) + n_te / n_tr) * v.var(ddof=1))
            r[k] = m; r[k + "_lo"] = max(0, m - h); r[k + "_hi"] = min(1, m + h)
        r["errors_per_repeat_mean"] = g.err.sum() / E.N_REPEATS; r["fit_s"] = g.fit_s.mean()
        rows.append(r)
    S = pd.DataFrame(rows); S.to_csv(f"{out}/allgenes_summary.csv", index=False); return S
