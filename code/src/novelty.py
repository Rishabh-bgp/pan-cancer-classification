"""Extension analyses: (1) reliability - split-conformal and Mondrian (class-conditional) prediction sets with
selective abstention, nested inside the outer CV, plus calibration (ECE, Brier, reliability data);
(3) data efficiency - learning curves by training samples per class, and leakage bias as n shrinks."""
import time, json
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from sklearn.base import clone
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold, train_test_split
from sklearn.metrics import accuracy_score, f1_score
import experiments as E
import audit as AU

PROB_MODELS = ["Softmax (multinomial LR, L2)", "Gaussian NB", "Random forest", "LightGBM", "MLP (64 hidden)"]
ALPHAS = [0.10, 0.05, 0.01]
FLAG = ["sample_129", "sample_507", "sample_599"]


def _qhat(s, alpha):
    n = len(s); r = int(np.ceil((n + 1) * (1 - alpha)))
    return np.inf if r > n else np.sort(s)[r - 1]


def _ece(P, y, bins=15):
    conf = P.max(1); pred = P.argmax(1); acc = (pred == y).astype(float)
    e = np.linspace(0, 1, bins + 1); out = 0.0
    for lo, hi in zip(e[:-1], e[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any(): out += m.mean() * abs(acc[m].mean() - conf[m].mean())
    return out


def _cw_ece(P, y, bins=15):
    e = np.linspace(0, 1, bins + 1); tot = 0.0
    for c in range(P.shape[1]):
        p = P[:, c]; t = (y == c).astype(float)
        for lo, hi in zip(e[:-1], e[1:]):
            m = (p > lo) & (p <= hi) if lo > 0 else (p >= lo) & (p <= hi)
            if m.any(): tot += m.mean() * abs(t[m].mean() - p[m].mean())
    return tot / P.shape[1]


def _conf_fold(f, tr, te, X, y, ids):
    rows, samp, calrows = [], [], []
    rs = E.SEED + 7000 + f
    ptr, cal = train_test_split(tr, test_size=0.25, stratify=y[tr], random_state=rs)
    M = E.models()
    for name in PROB_MODELS:
        # (a) calibration of the model fitted on the whole training fold
        p_full = E.pipe(clone(M[name]), E.K_MAIN).fit(X[tr], y[tr]); Pt = p_full.predict_proba(X[te])
        oh = np.eye(5)[y[te]]
        calrows.append(dict(fold=f, model=name, ece=_ece(Pt, y[te]), cw_ece=_cw_ece(Pt, y[te]),
                            brier=float(((Pt - oh) ** 2).sum(1).mean()), acc=accuracy_score(y[te], Pt.argmax(1)),
                            conf=Pt.max(1).tolist(), correct=(Pt.argmax(1) == y[te]).astype(int).tolist()))
        # (b) split conformal: fit on proper-training part, calibrate on held-out part of the training fold
        p = E.pipe(clone(M[name]), E.K_MAIN).fit(X[ptr], y[ptr])
        Pc = p.predict_proba(X[cal]); Pe = p.predict_proba(X[te])
        sc = 1 - Pc[np.arange(len(cal)), y[cal]]
        for alpha in ALPHAS:
            for kind in ["marginal", "mondrian"]:
                if kind == "marginal":
                    q = np.full(5, _qhat(sc, alpha))
                else:
                    q = np.array([_qhat(sc[y[cal] == c], alpha) for c in range(5)])
                S = (1 - Pe) <= q[None, :]
                size = S.sum(1); cover = S[np.arange(len(te)), y[te]]
                single = size == 1; pred = Pe.argmax(1)
                acc_acc = float((S[single].argmax(1) == y[te][single]).mean()) if single.any() else np.nan
                pc_cov = [float(cover[y[te] == c].mean()) for c in range(5)]
                rows.append(dict(fold=f, model=name, alpha=alpha, kind=kind, coverage=float(cover.mean()),
                                 mean_size=float(size.mean()), empty=float((size == 0).mean()), singleton=float(single.mean()),
                                 full=float((size == 5).mean()), acc_on_singletons=acc_acc,
                                 point_acc=float((pred == y[te]).mean()), **{f"cov_{E.CLASSES[c]}": pc_cov[c] for c in range(5)},
                                 n_cal_min=int(min((y[cal] == c).sum() for c in range(5)))))
                for j, i in enumerate(te):
                    if size[j] != 1 or pred[j] != y[i] or ids[i] in FLAG:
                        samp.append(dict(fold=f, model=name, alpha=alpha, kind=kind, sample=ids[i], true=E.CLASSES[y[i]],
                                         pred=E.CLASSES[pred[j]], size=int(size[j]), covered=bool(cover[j]),
                                         set="+".join(E.CLASSES[c] for c in range(5) if S[j, c])))
    return rows, samp, calrows


def reliability(X, y, ids, out, n_jobs=8):
    t0 = time.time()
    cv = list(RepeatedStratifiedKFold(n_splits=5, n_repeats=E.N_REPEATS, random_state=E.SEED).split(X, y))
    res = Parallel(n_jobs=n_jobs)(delayed(_conf_fold)(f, tr, te, X, y, ids) for f, (tr, te) in enumerate(cv))
    R = pd.DataFrame([r for a in res for r in a[0]]); R.to_csv(f"{out}/nov_conformal_folds.csv", index=False)
    Sm = pd.DataFrame([r for a in res for r in a[1]]); Sm.to_csv(f"{out}/nov_conformal_samples.csv", index=False)
    C = pd.DataFrame([r for a in res for r in a[2]])
    rel = []
    for m, g in C.groupby("model", sort=False):
        conf = np.concatenate(g.conf.values); cor = np.concatenate(g.correct.values)
        e = np.linspace(0, 1, 16)
        for lo, hi in zip(e[:-1], e[1:]):
            k = (conf > lo) & (conf <= hi)
            if k.any(): rel.append(dict(model=m, lo=lo, hi=hi, n=int(k.sum()), conf=float(conf[k].mean()), acc=float(cor[k].mean())))
    pd.DataFrame(rel).to_csv(f"{out}/nov_reliability_bins.csv", index=False)
    C.drop(columns=["conf", "correct"]).to_csv(f"{out}/nov_calibration_folds.csv", index=False)
    agg = R.groupby(["model", "kind", "alpha"]).mean(numeric_only=True).drop(columns="fold").reset_index()
    agg.to_csv(f"{out}/nov_conformal_summary.csv", index=False)
    C.drop(columns=["conf", "correct"]).groupby("model", sort=False).mean(numeric_only=True).drop(columns="fold").reset_index().to_csv(f"{out}/nov_calibration_summary.csv", index=False)
    print(f"  reliability done ({(time.time()-t0)/60:.1f} min)", flush=True)


def _lc_fold(f, tr, te, X, y, ms):
    rng = np.random.default_rng(E.SEED + 9000 + f); rows = []
    mods = {"Softmax": AU.AUDIT_MODELS["Softmax"], "Linear SVM": AU.AUDIT_MODELS["Linear SVM"], "Gaussian NB": AU.AUDIT_MODELS["Gaussian NB"]}
    for m in ms:
        sub = np.concatenate([rng.choice(tr[y[tr] == c], min(m, (y[tr] == c).sum()), replace=False) for c in range(5)])
        for name, clf in mods.items():
            p = E.pipe(clone(clf), E.K_MAIN).fit(X[sub], y[sub]); yp = p.predict(X[te])
            rows.append(dict(fold=f, m_per_class=m, n_train=len(sub), model=name, acc=accuracy_score(y[te], yp),
                             f1=f1_score(y[te], yp, average="macro")))
    return rows


def _leak_sub(i, m, X, y):
    rng = np.random.default_rng(E.SEED + 11000 + 100 * m + i)
    idx = np.concatenate([rng.choice(np.where(y == c)[0], m, replace=False) for c in range(5)])
    Xs, ys = X[idx], y[idx]; res = []
    for lab, yy in [("real", ys), ("permuted", rng.permutation(ys))]:
        sp = list(StratifiedKFold(5, shuffle=True, random_state=E.SEED + i).split(Xs, yy))
        r = pd.DataFrame(AU._cv_both(Xs, yy, sp, [10, 100], {"Softmax": AU.AUDIT_MODELS["Softmax"]}))
        res.append(r.groupby(["k", "mode"]).acc.mean().reset_index().assign(sub=i, labels=lab, m_per_class=m, n=5 * m))
    return pd.concat(res)


def data_efficiency(X, y, out, n_jobs=8, n_sub=30, ms=(3, 5, 10, 20, 40, 60), leak_ms=(6, 12, 24, 48, 78)):
    t0 = time.time()
    cv = list(RepeatedStratifiedKFold(n_splits=5, n_repeats=E.N_REPEATS, random_state=E.SEED).split(X, y))
    L = pd.DataFrame([r for a in Parallel(n_jobs=n_jobs)(delayed(_lc_fold)(f, tr, te, X, y, ms) for f, (tr, te) in enumerate(cv)) for r in a])
    L.to_csv(f"{out}/nov_learning_curve_folds.csv", index=False)
    L.groupby(["model", "m_per_class"]).agg(n_train=("n_train", "mean"), acc=("acc", "mean"), acc_sd=("acc", "std"),
                                            f1=("f1", "mean"), f1_sd=("f1", "std")).reset_index().to_csv(f"{out}/nov_learning_curve.csv", index=False)
    print(f"  learning curves done ({(time.time()-t0)/60:.1f} min)", flush=True)
    jobs = [(i, m) for m in leak_ms for i in range(n_sub)]
    B = pd.concat(Parallel(n_jobs=n_jobs)(delayed(_leak_sub)(i, m, X, y) for i, m in jobs))
    B.to_csv(f"{out}/nov_leak_vs_n.csv", index=False)
    print(f"  leakage vs n done ({(time.time()-t0)/60:.1f} min)", flush=True)
