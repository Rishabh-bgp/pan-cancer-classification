"""Round-2 robustness analyses for the reliability and data-efficiency results.
(a) conformal: fold-level coverage spread and calibration-conditional (Beta) coverage, a max-probability
    threshold baseline at the same threshold and at matched abstention, cross-conformal (5 inner folds, all
    training data used for calibration), and randomised (smoothed) p-values to break score ties;
(b) calibration: pooled out-of-fold ECE with a sample-cluster bootstrap CI, a consistency-resampling reference
    (labels drawn from the predicted probabilities), equal-mass ECE and log-loss, all-bin reliability data;
(c) uncertainty for the learning curves and the leakage-vs-n results (95% CIs)."""
import time, json
import numpy as np, pandas as pd
from scipy import stats
from joblib import Parallel, delayed
from sklearn.base import clone
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold, train_test_split
import experiments as E
import novelty as NV

SM = "Softmax (multinomial LR, L2)"
B = 2000


def _fold(f, tr, te, X, y):
    rs = E.SEED + 7000 + f
    ptr, cal = train_test_split(tr, test_size=0.25, stratify=y[tr], random_state=rs)   # identical split to novelty.py
    M = E.models(); out = dict(fold=f, te=te, cal=cal, y_cal=y[cal])
    for name in NV.PROB_MODELS:
        out[name] = dict(full=E.pipe(clone(M[name]), E.K_MAIN).fit(X[tr], y[tr]).predict_proba(X[te]))
        p = E.pipe(clone(M[name]), E.K_MAIN).fit(X[ptr], y[ptr])
        out[name]["Pc"] = p.predict_proba(X[cal]); out[name]["Pe"] = p.predict_proba(X[te])
    # cross-conformal for softmax: 5 inner folds over the whole outer training fold
    sc, Pk, own = [], [], []
    for k, (a, b) in enumerate(StratifiedKFold(5, shuffle=True, random_state=rs).split(X[tr], y[tr])):
        p = E.pipe(clone(M[SM]), E.K_MAIN).fit(X[tr[a]], y[tr[a]])
        Pb = p.predict_proba(X[tr[b]]); sc.append(1 - Pb[np.arange(len(b)), y[tr[b]]]); own.append(np.full(len(b), k))
        Pk.append(p.predict_proba(X[te]))
    out["cc"] = dict(scores=np.concatenate(sc), own=np.concatenate(own), Pk=np.stack(Pk))
    return out


def collect(X, y, out, n_jobs=8):
    t0 = time.time()
    cv = list(RepeatedStratifiedKFold(n_splits=5, n_repeats=E.N_REPEATS, random_state=E.SEED).split(X, y))
    R = Parallel(n_jobs=n_jobs)(delayed(_fold)(f, tr, te, X, y) for f, (tr, te) in enumerate(cv))
    print(f"  robustness fits done ({(time.time()-t0)/60:.1f} min)", flush=True)
    return R


def _smooth_sets(sc, Pe, alpha, rng):
    s_te = 1 - Pe                                             # (n_te, 5)
    gt = (sc[None, None, :] > s_te[..., None]).sum(-1); eq = (sc[None, None, :] == s_te[..., None]).sum(-1)
    u = rng.random(s_te.shape)
    p = (gt + u * (eq + 1)) / (len(sc) + 1)
    return p > alpha


def _cc_sets(cc, alpha):
    s = cc["scores"]; own = cc["own"]; Pk = cc["Pk"]           # Pk: (5, n_te, 5)
    s_te = 1 - Pk[own]                                         # (n_cal, n_te, 5): test score under the model that held out i
    p = ((s[:, None, None] >= s_te).sum(0) + 1) / (len(s) + 1)
    return p > alpha, Pk.mean(0)


def _ece_bins(conf, cor, edges):
    out = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any(): out += m.mean() * abs(cor[m].mean() - conf[m].mean())
    return out


def _ece_mass(conf, cor, nb=15):
    o = np.argsort(conf); out = 0.0
    for g in np.array_split(o, nb): out += len(g) / len(conf) * abs(cor[g].mean() - conf[g].mean())
    return out


def analyse(R, X, y, ids, out):
    rng = np.random.default_rng(E.SEED + 13000)
    N = len(y); edges = np.linspace(0, 1, 16)
    rep = np.array([r["fold"] // 5 for r in R])
    rows, base, cov, cal_rows, relbins = [], [], [], [], []
    # ---------------- conformal: per-fold quantities
    for r in R:
        f, te, yc, yt = r["fold"], r["te"], r["y_cal"], y[r["te"]]
        for name in NV.PROB_MODELS:
            Pc, Pe = r[name]["Pc"], r[name]["Pe"]; sc = 1 - Pc[np.arange(len(yc)), yc]; pred = Pe.argmax(1)
            for alpha in NV.ALPHAS:
                q = NV._qhat(sc, alpha); n = len(sc); rk = int(np.ceil((n + 1) * (1 - alpha)))
                variants = {"split": (1 - Pe) <= q, "split_smoothed": _smooth_sets(sc, Pe, alpha, rng)}
                if name == SM:
                    S, Pbar = _cc_sets(r["cc"], alpha); variants["cross"] = S
                for v, S in variants.items():
                    size = S.sum(1); acc = size == 1; c = S[np.arange(len(te)), yt]
                    pv = (S.argmax(1) if v != "cross" else S.argmax(1))
                    rows.append(dict(fold=f, rep=f // 5, model=name, alpha=alpha, variant=v, n_cal=n, rank=rk, tau=float(1 - q) if np.isfinite(q) else -np.inf,
                                     coverage=c.mean(), empty=(size == 0).mean(), singleton=acc.mean(), multi=(size > 1).mean(), mean_size=size.mean(),
                                     n_acc=int(acc.sum()), err_acc=int((pv[acc] != yt[acc]).sum()),
                                     n_te=len(te), err_point=int((pred != yt).sum()),
                                     cov_LUAD=c[yt == 3].mean(), cov_COAD=c[yt == 1].mean()))
                if name == SM and alpha == 0.01:
                    # threshold baselines on the same 75%-trained model
                    mp = Pe.max(1)
                    for lab, tau in [("same_tau", (1 - q) if np.isfinite(q) else -np.inf)]:
                        a_ = mp >= tau
                        base.append(dict(fold=f, rep=f // 5, rule=lab, n_acc=int(a_.sum()), err_acc=int((pred[a_] != yt[a_]).sum())))
                    # matched abstention, threshold from the calibration split: accept the same fraction as conformal accepted on calibration data
                    S_cal = (1 - Pc) <= q; acc_cal = (S_cal.sum(1) == 1).mean()
                    tau_m = np.quantile(Pc.max(1), 1 - acc_cal) if acc_cal < 1 else -np.inf
                    a_ = mp >= tau_m
                    base.append(dict(fold=f, rep=f // 5, rule="matched_cal", n_acc=int(a_.sum()), err_acc=int((pred[a_] != yt[a_]).sum())))
                    S = (1 - Pe) <= q; acc = S.sum(1) == 1
                    base.append(dict(fold=f, rep=f // 5, rule="conformal", n_acc=int(acc.sum()), err_acc=int((pred[acc] != yt[acc]).sum())))
                    base.append(dict(fold=f, rep=f // 5, rule="none", n_acc=len(te), err_acc=int((pred != yt).sum())))
                    Sc, Pbar = _cc_sets(r["cc"], alpha); acc = Sc.sum(1) == 1; pc_ = Pbar.argmax(1)
                    base.append(dict(fold=f, rep=f // 5, rule="cross_conformal", n_acc=int(acc.sum()), err_acc=int((Sc.argmax(1)[acc] != yt[acc]).sum())))
                    base.append(dict(fold=f, rep=f // 5, rule="none_cross", n_acc=len(te), err_acc=int((pc_ != yt).sum())))
    C = pd.DataFrame(rows); C.to_csv(f"{out}/rob_conformal_folds.csv", index=False)
    Bf = pd.DataFrame(base); Bf.to_csv(f"{out}/rob_threshold_folds.csv", index=False)
    # summary with fold spread and Beta calibration-conditional coverage
    summ = []
    for (m, a, v), g in C.groupby(["model", "alpha", "variant"], sort=False):
        n = int(g.n_cal.median()); rk = int(np.ceil((n + 1) * (1 - a)))
        b5 = float(stats.beta.ppf(0.05, rk, n + 1 - rk)) if rk <= n else 1.0
        summ.append(dict(model=m, alpha=a, variant=v, coverage=g.coverage.mean(), cov_min=g.coverage.min(), cov_med=g.coverage.median(),
                         cov_max=g.coverage.max(), cov_sd=g.coverage.std(), beta_p05=b5, n_cal=n,
                         tau_min=g.tau.replace(-np.inf, np.nan).min(), tau_med=g.tau.median(), tau_max=g.tau.max(),
                         empty=g["empty"].mean(), singleton=g.singleton.mean(), multi=g.multi.mean(), mean_size=g.mean_size.mean(),
                         acc_err=g.err_acc.sum() / max(g.n_acc.sum(), 1), cov_LUAD=g.cov_LUAD.mean(), cov_COAD=g.cov_COAD.mean()))
    pd.DataFrame(summ).to_csv(f"{out}/rob_conformal_summary.csv", index=False)
    # CIs for accepted error: bootstrap over the 10 repeats
    reps = sorted(Bf.rep.unique()); bt = []
    agg = Bf.groupby(["rule", "rep"])[["n_acc", "err_acc"]].sum()
    for rule in Bf.rule.unique():
        A = agg.loc[rule].reindex(reps); pt = A.err_acc.sum() / A.n_acc.sum()
        bs = []
        for _ in range(B):
            i = rng.choice(reps, len(reps)); s = A.loc[i].sum(); bs.append(s.err_acc / s.n_acc)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        wl, wh = _wilson(A.err_acc.sum(), A.n_acc.sum())
        bt.append(dict(rule=rule, n_acc=int(A.n_acc.sum()), err=int(A.err_acc.sum()), err_rate=pt, boot_lo=lo, boot_hi=hi, wilson_lo=wl, wilson_hi=wh))
    # paired difference conformal - none
    A1, A0 = agg.loc["conformal"].reindex(reps), agg.loc["none"].reindex(reps); d = []
    for _ in range(B):
        i = rng.choice(reps, len(reps)); d.append(A1.loc[i].err_acc.sum() / A1.loc[i].n_acc.sum() - A0.loc[i].err_acc.sum() / A0.loc[i].n_acc.sum())
    bt.append(dict(rule="diff_conformal_minus_none", err_rate=A1.err_acc.sum() / A1.n_acc.sum() - A0.err_acc.sum() / A0.n_acc.sum(),
                   boot_lo=np.percentile(d, 2.5), boot_hi=np.percentile(d, 97.5)))
    # how often decisions differ: conformal vs same-tau threshold
    pd.DataFrame(bt).to_csv(f"{out}/rob_threshold_summary.csv", index=False)
    # ---------------- calibration: pooled out-of-fold (full-training-fold model)
    for name in NV.PROB_MODELS:
        P = np.concatenate([r[name]["full"] for r in R]); Y = np.concatenate([y[r["te"]] for r in R])
        sid = np.concatenate([r["te"] for r in R]); rp = np.concatenate([np.full(len(r["te"]), r["fold"] // 5) for r in R])
        conf = P.max(1); cor = (P.argmax(1) == Y).astype(float)
        Pcl = np.clip(P, 1e-15, 1); nll = float(-np.log(Pcl[np.arange(len(Y)), Y]).mean())
        ece = _ece_bins(conf, cor, edges); ecem = _ece_mass(conf, cor)
        # cluster bootstrap over the 801 samples (each carries its 10 out-of-fold predictions)
        pos = [np.where(sid == i)[0] for i in range(N)]; bs, bsm, bnll = [], [], []
        for _ in range(B):
            k = np.concatenate([pos[i] for i in rng.integers(0, N, N)])
            bs.append(_ece_bins(conf[k], cor[k], edges)); bsm.append(_ece_mass(conf[k], cor[k]))
            bnll.append(-np.log(Pcl[k, Y[k]]).mean())
        # consistency resampling: labels drawn from the predicted probabilities (perfectly calibrated by construction)
        cs = []; cum = P.cumsum(1)
        for _ in range(B):
            yy = (rng.random(len(Y))[:, None] > cum).sum(1).clip(0, 4)
            cs.append(_ece_bins(conf, (P.argmax(1) == yy).astype(float), edges))
        cs = np.array(cs)
        cal_rows.append(dict(model=name, n=len(Y), acc=cor.mean(), mean_conf=conf.mean(), ece=ece, ece_lo=np.percentile(bs, 2.5), ece_hi=np.percentile(bs, 97.5),
                             ref_mean=cs.mean(), ref_lo=np.percentile(cs, 2.5), ref_hi=np.percentile(cs, 97.5), p_consistency=float((cs >= ece).mean()),
                             ece_mass=ecem, ece_mass_lo=np.percentile(bsm, 2.5), ece_mass_hi=np.percentile(bsm, 97.5),
                             nll=nll, nll_lo=np.percentile(bnll, 2.5), nll_hi=np.percentile(bnll, 97.5),
                             brier=float(((P - np.eye(5)[Y]) ** 2).sum(1).mean()),
                             ece_fold_mean=np.mean([_ece_bins(r[name]["full"].max(1), (r[name]["full"].argmax(1) == y[r["te"]]).astype(float), edges) for r in R])))
        for lo, hi in zip(edges[:-1], edges[1:]):
            m = (conf > lo) & (conf <= hi)
            if m.any(): relbins.append(dict(model=name, lo=lo, hi=hi, n=int(m.sum()), conf=conf[m].mean(), acc=cor[m].mean(), errors=int((1 - cor[m]).sum())))
    pd.DataFrame(cal_rows).to_csv(f"{out}/rob_calibration.csv", index=False)
    pd.DataFrame(relbins).to_csv(f"{out}/rob_reliability_bins.csv", index=False)
    # flagged LUAD samples: interval
    n_fl = None
    print("  robustness analyses done", flush=True)


def _wilson(k, n, z=1.96):
    if n == 0: return np.nan, np.nan
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def data_eff_ci(out):
    """95% CIs: learning curves over the 10 repeats (fold means per repeat, t interval); leakage vs n over the 30 subsamples."""
    L = pd.read_csv(f"{out}/nov_learning_curve_folds.csv"); L["rep"] = L.fold // 5
    r = L.groupby(["model", "m_per_class", "rep"])[["acc", "f1"]].mean().reset_index(); rows = []
    for (m, k), g in r.groupby(["model", "m_per_class"]):
        t = stats.t.ppf(0.975, len(g) - 1)
        rows.append(dict(model=m, m_per_class=k, n_train=5 * k, acc=g.acc.mean(), acc_ci=t * g.acc.std() / np.sqrt(len(g)),
                         f1=g.f1.mean(), f1_ci=t * g.f1.std() / np.sqrt(len(g)), fold_sd_f1=L[(L.model == m) & (L.m_per_class == k)].f1.std()))
    pd.DataFrame(rows).to_csv(f"{out}/rob_learning_curve_ci.csv", index=False)
    Lk = pd.read_csv(f"{out}/nov_leak_vs_n.csv")
    w = Lk.pivot_table(index=["labels", "k", "m_per_class", "n", "sub"], columns="mode", values="acc").reset_index()
    w["delta"] = 100 * (w.leaky - w.clean); rows = []
    for (lab, k, m, n), g in w.groupby(["labels", "k", "m_per_class", "n"]):
        t = stats.t.ppf(0.975, len(g) - 1)
        rows.append(dict(labels=lab, k=k, m_per_class=m, n=n, n_sub=len(g), clean=100 * g.clean.mean(), leaky=100 * g.leaky.mean(),
                         delta=g.delta.mean(), delta_ci=t * g.delta.std() / np.sqrt(len(g)), design="balanced subsample"))
    pd.DataFrame(rows).to_csv(f"{out}/rob_leak_vs_n_ci.csv", index=False)
