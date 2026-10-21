"""Leakage-free benchmark of five-class tumour-type classification on the
UCI 'Gene expression cancer RNA-Seq' (TCGA-PANCAN-HiSeq, 801 x 20,531) data.

All preprocessing (zero-variance filter, ANOVA-F top-k selection, z-scoring)
is fitted inside each training fold through an sklearn Pipeline.
"""
import json, os, pickle, time, warnings
import numpy as np, pandas as pd
from scipy import stats
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, f1_score, balanced_accuracy_score, roc_auc_score, confusion_matrix
from lightgbm import LGBMClassifier

warnings.filterwarnings("ignore")
SEED = 2026
CLASSES = ["BRCA", "COAD", "KIRC", "LUAD", "PRAD"]
N_REPEATS, N_SPLITS, K_MAIN = 10, 5, 100


def load(data_dir):
    lab = pd.read_csv(os.path.join(data_dir, "labels.csv"), index_col=0)
    npy = os.path.join(data_dir, "X.npy")
    cols = pd.read_csv(os.path.join(data_dir, "data.csv"), index_col=0, nrows=0).columns
    if os.path.exists(npy):
        X = np.load(npy)
    else:
        X = pd.read_csv(os.path.join(data_dir, "data.csv"), index_col=0).values.astype(np.float32)
        np.save(npy, X)
    y = lab["Class"].map({c: i for i, c in enumerate(CLASSES)}).values
    return X, y, np.array(cols), lab.index.values


def models():
    return {
        "Majority baseline": DummyClassifier(strategy="most_frequent"),
        "Softmax (multinomial LR, L2)": LogisticRegression(C=1.0, max_iter=5000),
        "Ridge classifier": RidgeClassifier(alpha=10.0),
        "Linear SVM": LinearSVC(C=1.0, max_iter=20000),
        "Gaussian NB": GaussianNB(),
        "Random forest": RandomForestClassifier(n_estimators=500, n_jobs=1, random_state=SEED),
        "LightGBM": LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=15, verbose=-1, n_jobs=1, random_state=SEED),
        "MLP (64 hidden)": MLPClassifier(hidden_layer_sizes=(64,), alpha=1e-3, max_iter=1000, random_state=SEED),
    }


def pipe(clf, k):
    steps = [("var", VarianceThreshold(0.0))]
    if k != "all":
        steps.append(("sel", SelectKBest(f_classif, k=k)))
    steps += [("sc", StandardScaler()), ("clf", clf)]
    return Pipeline(steps)


def scores(p, X):
    if hasattr(p, "predict_proba"):
        try:
            return p.predict_proba(X)
        except Exception:
            pass
    d = p.decision_function(X)
    e = np.exp(d - d.max(1, keepdims=True))
    return e / e.sum(1, keepdims=True)  # monotone per row; used only for ranking-based AUC


def fold_metrics(yt, yp, s):
    try:
        auc = roc_auc_score(yt, s, multi_class="ovr", average="macro")
    except ValueError:
        auc = np.nan
    return dict(acc=accuracy_score(yt, yp), f1=f1_score(yt, yp, average="macro", zero_division=0),
                bacc=balanced_accuracy_score(yt, yp), auc=auc, err=int((yt != yp).sum()))


def corrected_t(diff, n_train, n_test):
    """Nadeau & Bengio (2003) corrected resampled t-test on paired fold differences."""
    d = np.asarray(diff); J = len(d); m = d.mean(); v = d.var(ddof=1)
    if v == 0:
        return m, 0.0, 1.0 if m == 0 else 0.0, (m, m)
    se = np.sqrt((1 / J + n_test / n_train) * v)
    t = m / se; p = 2 * stats.t.sf(abs(t), J - 1)
    h = stats.t.ppf(0.975, J - 1) * se
    return m, t, p, (m - h, m + h)


def main_benchmark(X, y, ids, out):
    cv = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=SEED)
    rows, sel_counts, oof_wrong = [], np.zeros(X.shape[1], int), {}
    cms = {m: np.zeros((5, 5), int) for m in models()}
    sel_sets = []
    for f, (tr, te) in enumerate(cv.split(X, y)):
        rep = f // N_SPLITS
        for name, clf in models().items():
            p = pipe(clf, K_MAIN)
            t0 = time.perf_counter(); p.fit(X[tr], y[tr]); tfit = time.perf_counter() - t0
            t0 = time.perf_counter(); yp = p.predict(X[te]); tpred = time.perf_counter() - t0
            s = scores(p, X[te])
            m = fold_metrics(y[te], yp, s)
            rows.append(dict(model=name, fold=f, repeat=rep, fit_s=tfit, pred_ms_per_sample=1000 * tpred / len(te), **m))
            cms[name] += confusion_matrix(y[te], yp, labels=range(5))
            for i in te[yp != y[te]]:
                oof_wrong.setdefault(name, {}).setdefault(int(i), []).append(int(yp[list(te).index(i)]))
            if name == "Softmax (multinomial LR, L2)":
                keep = np.where(p.named_steps["var"].get_support())[0]
                chosen = keep[p.named_steps["sel"].get_support()]
                sel_counts[chosen] += 1; sel_sets.append(set(chosen.tolist()))
        print(f"fold {f+1}/{N_REPEATS*N_SPLITS} done", flush=True)
    df = pd.DataFrame(rows); df.to_csv(f"{out}/fold_scores.csv", index=False)
    pickle.dump(dict(cms=cms, oof_wrong=oof_wrong, sel_counts=sel_counts, sel_sets=sel_sets), open(f"{out}/aux.pkl", "wb"))
    return df, cms, oof_wrong, sel_counts, sel_sets


def summarise(df, X, y, out):
    n_te = len(y) / N_SPLITS; n_tr = len(y) - n_te
    summ = []
    for name, g in df.groupby("model", sort=False):
        r = dict(model=name)
        for k in ["acc", "f1", "bacc", "auc"]:
            v = g[k].values; m = v.mean(); h = stats.t.ppf(0.975, len(v) - 1) * np.sqrt((1 / len(v) + n_te / n_tr) * v.var(ddof=1))
            r[k] = m; r[k + "_sd"] = v.std(ddof=1); r[k + "_lo"] = max(0, m - h); r[k + "_hi"] = min(1, m + h)
        r["errors_per_repeat_mean"] = g.groupby("repeat")["err"].sum().mean()
        r["errors_per_repeat_min"] = int(g.groupby("repeat")["err"].sum().min())
        r["errors_per_repeat_max"] = int(g.groupby("repeat")["err"].sum().max())
        r["fit_s"] = g["fit_s"].mean(); r["pred_ms_per_sample"] = g["pred_ms_per_sample"].mean()
        summ.append(r)
    S = pd.DataFrame(summ); S.to_csv(f"{out}/summary.csv", index=False)
    # paired corrected t-tests vs softmax (macro-F1 and accuracy)
    ref = "Softmax (multinomial LR, L2)"
    a = df[df.model == ref].sort_values("fold")
    tests = []
    for name in df.model.unique():
        if name == ref: continue
        b = df[df.model == name].sort_values("fold")
        for k in ["acc", "f1"]:
            m, t, p, ci = corrected_t(b[k].values - a[k].values, n_tr, n_te)
            tests.append(dict(model=name, metric=k, mean_diff_vs_softmax=m, t=t, p=p, ci_lo=ci[0], ci_hi=ci[1]))
    T = pd.DataFrame(tests)
    T["p_holm"] = np.nan
    for k in ["acc", "f1"]:
        idx = T[T.metric == k].sort_values("p").index; mm = len(idx); prev = 0
        for j, i in enumerate(idx):
            prev = max(prev, min(1, (mm - j) * T.loc[i, "p"])); T.loc[i, "p_holm"] = prev
    T.to_csv(f"{out}/paired_tests_vs_softmax.csv", index=False)
    return S, T


def ablation_k(X, y, out):
    ks = [2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, "all"]
    abl = {"Softmax (multinomial LR, L2)": LogisticRegression(C=1.0, max_iter=5000),
           "Ridge classifier": RidgeClassifier(alpha=10.0),
           "Linear SVM": LinearSVC(C=1.0, max_iter=20000),
           "Gaussian NB": GaussianNB()}
    cv = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=3, random_state=SEED)
    rows = []
    for f, (tr, te) in enumerate(cv.split(X, y)):
        for k in ks:
            for name, clf in abl.items():
                from sklearn.base import clone
                p = pipe(clone(clf), k); t0 = time.perf_counter(); p.fit(X[tr], y[tr]); tf = time.perf_counter() - t0
                yp = p.predict(X[te])
                rows.append(dict(model=name, k=str(k), fold=f, acc=accuracy_score(y[te], yp),
                                 f1=f1_score(y[te], yp, average="macro"), err=int((yp != y[te]).sum()), fit_s=tf))
        print(f"ablation fold {f+1}/15", flush=True)
    A = pd.DataFrame(rows); A.to_csv(f"{out}/ablation_k_folds.csv", index=False)
    G = A.groupby(["model", "k"], sort=False).agg(acc=("acc", "mean"), acc_sd=("acc", "std"), f1=("f1", "mean"),
                                                  f1_sd=("f1", "std"), err_per_repeat=("err", lambda v: v.sum() / 3), fit_s=("fit_s", "mean")).reset_index()
    G.to_csv(f"{out}/ablation_k_summary.csv", index=False)
    return G


def permutation_check(X, y, out, n_perm=5):
    rng = np.random.default_rng(SEED); accs = []
    for i in range(n_perm):
        yp_ = rng.permutation(y)
        cv = StratifiedKFold(5, shuffle=True, random_state=SEED + i)
        for tr, te in cv.split(X, yp_):
            p = pipe(LogisticRegression(C=1.0, max_iter=5000), K_MAIN).fit(X[tr], yp_[tr])
            accs.append(accuracy_score(yp_[te], p.predict(X[te])))
    r = dict(n_permutations=n_perm, mean_acc=float(np.mean(accs)), sd=float(np.std(accs, ddof=1)),
             max_acc=float(np.max(accs)), majority_rate=float(np.bincount(y).max() / len(y)))
    json.dump(r, open(f"{out}/permutation_check.json", "w"), indent=2); return r


def full_fit_probes(X, y, genes, sel_counts, out):
    """Descriptive only: fit the k=100 softmax pipeline on all 801 samples and
    report the anonymised probes (gene_<index>) with largest class coefficients."""
    p = pipe(LogisticRegression(C=1.0, max_iter=5000), K_MAIN).fit(X, y)
    keep = np.where(p.named_steps["var"].get_support())[0]
    chosen = keep[p.named_steps["sel"].get_support()]
    F = f_classif(X[:, keep], y)[0]
    W = p.named_steps["clf"].coef_  # 5 x 100
    rows = []
    for ci, c in enumerate(CLASSES):
        order = np.argsort(W[ci])[::-1][:5]
        for r, j in enumerate(order):
            g = chosen[j]
            mu = [X[y == q, g].mean() for q in range(5)]
            rows.append(dict(cls=c, rank=r + 1, probe=genes[g], coef=W[ci, j], sel_freq=int(sel_counts[g]),
                             mean_in_class=mu[ci], mean_other=float(np.mean(X[y != ci, g]))))
    P = pd.DataFrame(rows); P.to_csv(f"{out}/top_probes_by_class.csv", index=False)
    # stability
    n_folds = N_REPEATS * N_SPLITS
    stab = dict(n_folds=n_folds, n_probes_ever_selected=int((sel_counts > 0).sum()),
                n_probes_selected_every_fold=int((sel_counts == n_folds).sum()),
                n_probes_selected_ge_90pct=int((sel_counts >= 0.9 * n_folds).sum()),
                full_fit_overlap_with_always=int(np.isin(chosen, np.where(sel_counts == n_folds)[0]).sum()))
    return P, stab, chosen


def footprint(X, y, out):
    from sklearn.base import clone
    rows = []
    for name, clf in models().items():
        p = pipe(clone(clf), K_MAIN).fit(X, y)
        c = p.named_steps["clf"]
        if hasattr(c, "coef_"): npar = c.coef_.size + np.size(getattr(c, "intercept_", 0))
        elif hasattr(c, "coefs_"): npar = sum(w.size for w in c.coefs_) + sum(b.size for b in c.intercepts_)
        elif hasattr(c, "theta_"): npar = c.theta_.size + c.var_.size + c.class_prior_.size
        elif hasattr(c, "estimators_"): npar = int(sum(e.tree_.node_count for e in c.estimators_))
        elif hasattr(c, "booster_"): npar = int(c.booster_.trees_to_dataframe().shape[0])
        else: npar = 5
        size_kb = len(pickle.dumps(c)) / 1024
        rows.append(dict(model=name, input_features=K_MAIN, params_or_nodes=int(npar), model_kb=size_kb))
    F = pd.DataFrame(rows); F.to_csv(f"{out}/footprint.csv", index=False); return F
