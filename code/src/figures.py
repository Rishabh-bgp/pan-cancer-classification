import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
CLASSES = ["BRCA", "COAD", "KIRC", "LUAD", "PRAD"]
COL = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
DPI = 300

def fig_data(X, y, fdir):
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
    n = np.bincount(y); ax[0].bar(CLASSES, n, color=COL)
    for i, v in enumerate(n): ax[0].text(i, v + 4, str(v), ha="center", fontsize=8)
    ax[0].set_ylabel("samples"); ax[0].set_title("(a) Class sizes (n = 801)")
    Z = PCA(2, random_state=0).fit(StandardScaler().fit_transform(X[:, X.var(0) > 0]))
    P = Z.transform(StandardScaler().fit_transform(X[:, X.var(0) > 0]))
    for c in range(5): ax[1].scatter(P[y == c, 0], P[y == c, 1], s=5, c=COL[c], label=CLASSES[c], alpha=.7)
    ev = Z.explained_variance_ratio_ * 100
    ax[1].set_xlabel(f"PC1 ({ev[0]:.1f}%)"); ax[1].set_ylabel(f"PC2 ({ev[1]:.1f}%)")
    ax[1].set_title("(b) PCA of all expressed genes"); ax[1].legend(fontsize=7, markerscale=2, frameon=False)
    fig.tight_layout(); fig.savefig(f"{fdir}/fig1_data_pca.png", dpi=DPI); plt.close(fig)

def fig_models(S, fdir):
    S = S.iloc[::-1]
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
    for a, k, lab in [(ax[0], "acc", "Accuracy"), (ax[1], "f1", "Macro-F1")]:
        a.errorbar(S[k] * 100, range(len(S)), xerr=[(S[k] - S[k + "_lo"]) * 100, (S[k + "_hi"] - S[k]) * 100], fmt="o", color="k", ms=4, capsize=2)
        a.set_xlabel(lab + " (%)"); a.set_xlim(95, 100.2); a.axvline(100, color="grey", lw=.5)
    ax[0].set_yticks(range(len(S))); ax[0].set_yticklabels(S.model, fontsize=8)
    maj = S[S.model == "Majority baseline"]
    if len(maj): ax[0].text(95.1, list(S.model).index("Majority baseline"), f"← {maj.acc.iloc[0]*100:.1f}% (off scale)", va="center", fontsize=7)
    if len(maj): ax[1].text(95.1, list(S.model).index("Majority baseline"), f"← {maj.f1.iloc[0]*100:.1f}% (off scale)", va="center", fontsize=7)
    fig.suptitle("10×5 repeated stratified CV, top-100 ANOVA genes; bars = corrected 95% CI", fontsize=8)
    fig.tight_layout(); fig.savefig(f"{fdir}/fig2_model_comparison.png", dpi=DPI); plt.close(fig)

def fig_ablation(G, fdir):
    fig, ax = plt.subplots(figsize=(5.0, 3.0))
    ks = list(G.k.unique()); xs = [int(k) if k != "all" else 20264 for k in ks]
    for m, g in G.groupby("model", sort=False):
        ax.plot(xs, g.f1 * 100, "o-", ms=3, label=m)
    ax.set_xscale("log"); ax.set_xticks(xs); ax.set_xticklabels([k if k != "all" else "all\n(20,264)" for k in ks], fontsize=7)
    ax.set_xlabel("number of ANOVA-selected genes k"); ax.set_ylabel("Macro-F1 (%)"); ax.set_ylim(40, 101)
    ax.legend(fontsize=7, frameon=False, loc="center", bbox_to_anchor=(0.6, 0.35)); ax.set_title("Feature-count ablation (3×5 CV)", fontsize=9)
    fig.tight_layout(); fig.savefig(f"{fdir}/fig3_ablation_k.png", dpi=DPI); plt.close(fig)

def fig_cm(cm, name, fdir):
    fig, ax = plt.subplots(figsize=(3.6, 3.2))
    cmr = cm / cm.sum(1, keepdims=True)
    ax.imshow(cmr, cmap="Blues", vmin=0, vmax=1)
    for i in range(5):
        for j in range(5): ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=8, color="w" if cmr[i, j] > .5 else "k")
    ax.set_xticks(range(5)); ax.set_xticklabels(CLASSES); ax.set_yticks(range(5)); ax.set_yticklabels(CLASSES)
    ax.set_xlabel("predicted"); ax.set_ylabel("true"); ax.set_title(f"{name}\nsummed over 10 repeats (8,010 predictions)", fontsize=8)
    fig.tight_layout(); fig.savefig(f"{fdir}/fig4_confusion_softmax.png", dpi=DPI); plt.close(fig)

def fig_stability(sel_counts, n_folds, fdir):
    fig, ax = plt.subplots(figsize=(5.0, 2.8))
    v = sel_counts[sel_counts > 0]
    ax.hist(v, bins=np.arange(0.5, n_folds + 1.5, 1), color="#4c72b0")
    ax.set_xlabel(f"number of folds (of {n_folds}) in which a gene was in the top 100"); ax.set_ylabel("genes")
    ax.set_title(f"Selection stability: {len(v)} distinct genes ever selected", fontsize=9)
    fig.tight_layout(); fig.savefig(f"{fdir}/fig5_selection_stability.png", dpi=DPI); plt.close(fig)

def fig_footprint(S, F, fdir):
    M = S.merge(F, on="model"); M = M[M.model != "Majority baseline"]
    fig, ax = plt.subplots(figsize=(5.0, 3.0))
    ax.scatter(M.fit_s * 1000, M.f1 * 100, c="k", s=14)
    for _, r in M.iterrows(): ax.annotate(r.model.split(" (")[0], (r.fit_s * 1000, r.f1 * 100), fontsize=7, xytext=(4, 2), textcoords="offset points")
    ax.set_xscale("log"); ax.set_xlabel("mean fit time per fold incl. selection (ms, log)"); ax.set_ylabel("Macro-F1 (%)")
    ax.set_title("Accuracy vs. training cost (single CPU thread)", fontsize=9)
    fig.tight_layout(); fig.savefig(f"{fdir}/fig6_footprint.png", dpi=DPI); plt.close(fig)


def fig_leakage(res, fdir):
    """Leaky vs in-fold selection: real labels (n = 801) and permuted labels (n = 801 and n = 60)."""
    R = pd.read_csv(f"{res}/leak_real_summary.csv"); P = pd.read_csv(f"{res}/leak_perm_fullN.csv"); S = pd.read_csv(f"{res}/leak_small_n.csv")
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.7))
    r = R[(R.metric == "acc") & (R.model == "Softmax")].sort_values("k")
    x = np.arange(len(r)); ax[0].bar(x - 0.2, r.leaky * 100, 0.4, label="leaky", color="#d62728"); ax[0].bar(x + 0.2, r.clean * 100, 0.4, label="in-fold", color="#1f77b4")
    ax[0].set_xticks(x); ax[0].set_xticklabels(r.k); ax[0].set_ylim(90, 100.5); ax[0].set_xlabel("k"); ax[0].set_ylabel("accuracy (%)")
    ax[0].set_title("(a) real labels, n = 801", fontsize=8); h_, l_ = ax[0].get_legend_handles_labels()
    for j, (d, lab) in enumerate([(P, "(b) permuted, n = 801"), (S[S.labels == "permuted"], "(c) permuted, n = 60")]):
        a = ax[j + 1]; data, pos, cols = [], [], []
        for i, k in enumerate([10, 100]):
            for m, (mode, c) in enumerate([("leaky", "#d62728"), ("clean", "#1f77b4")]):
                data.append(d[(d.k == k) & (d["mode"] == mode)].acc.values * 100); pos.append(i * 3 + m); cols.append(c)
        bp = a.boxplot(data, positions=pos, widths=0.8, patch_artist=True, showfliers=False)
        for b, c in zip(bp["boxes"], cols): b.set_facecolor(c); b.set_alpha(.6)
        a.axhline(100 * 0.2435 if j == 0 else 20, color="grey", ls="--", lw=.8)
        if j == 0: a.axhline(100 * 300 / 801, color="grey", ls=":", lw=.8)
        a.set_xticks([0.5, 3.5]); a.set_xticklabels(["k = 10", "k = 100"]); a.set_ylim(0, 100); a.set_title(lab, fontsize=8)
    ax[1].set_ylabel("accuracy (%)"); ax[1].legend(h_, l_, fontsize=7, frameon=False, loc="upper right")
    fig.tight_layout(); fig.savefig(f"{fdir}/fig7_leakage_audit.png", dpi=DPI); plt.close(fig)


def fig_reliability(res, fdir):
    """(a) reliability diagram, all bins, marker area ~ count; (b) conformal coverage vs nominal with the fold-level range;
    (c) share of singleton / empty / multi-label sets (softmax)."""
    B = pd.read_csv(f"{res}/rob_reliability_bins.csv"); C = pd.read_csv(f"{res}/rob_conformal_summary.csv"); C0 = pd.read_csv(f"{res}/nov_conformal_summary.csv")
    nm = {"Softmax (multinomial LR, L2)": "Softmax", "Gaussian NB": "Naive Bayes", "Random forest": "Random forest", "LightGBM": "LightGBM", "MLP (64 hidden)": "MLP"}
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.7))
    ax[0].plot([0, 1], [0, 1], color="grey", lw=.8, ls="--")
    for i, (m, g) in enumerate(B.groupby("model", sort=False)):
        ax[0].scatter(g.conf, g.acc, s=4 + 3 * np.sqrt(g.n), color=f"C{i}", alpha=.75, lw=0, label=nm[m])
    sm = B[B.model.str.startswith("Softmax")]
    for _, r in sm.iterrows():
        if r.conf < 0.97: ax[0].annotate(str(int(r.n)), (r.conf, r.acc), fontsize=4.5, xytext=(2, 2), textcoords="offset points", color="C0")
    ax[0].set_xlim(0.3, 1.02); ax[0].set_ylim(-0.03, 1.03); ax[0].set_xlabel("mean confidence"); ax[0].set_ylabel("accuracy")
    ax[0].set_title("(a) reliability, all bins (area ~ n)", fontsize=7); ax[0].legend(fontsize=5.5, frameon=False, loc="lower right", markerscale=.6)
    for i, m in enumerate(nm):
        v = "split_smoothed" if m == "Gaussian NB" else "split"
        g = C[(C.model == m) & (C.variant == v)].sort_values("alpha", ascending=False); x = 100 * (1 - g.alpha) + (i - 2) * 0.25
        ax[1].errorbar(x, 100 * g.coverage, yerr=[100 * (g.coverage - g.cov_min), 100 * (g.cov_max - g.coverage)], fmt="o-", ms=2.5, lw=.8, capsize=1.5, color=f"C{i}")
    g = C[(C.model == "Gaussian NB") & (C.variant == "split")].sort_values("alpha", ascending=False)
    ax[1].plot(100 * (1 - g.alpha) - 0.25, 100 * g.coverage, "x:", ms=3, lw=.8, color="C1", label="naive Bayes, ties not broken")
    ax[1].plot([88, 100], [88, 100], color="grey", lw=.8, ls="--"); ax[1].set_xlim(88, 100.5); ax[1].set_ylim(75, 100.5)
    ax[1].set_xlabel("nominal coverage (%)"); ax[1].set_ylabel("empirical coverage (%)"); ax[1].set_title("(b) marginal coverage; bars: fold min–max", fontsize=7)
    ax[1].legend(fontsize=5.5, frameon=False, loc="lower right")
    g = C0[(C0.model == "Softmax (multinomial LR, L2)")].copy(); lab = [f"{'Mond.' if k == 'mondrian' else 'marg.'}\n{int(round(100*(1-a)))}" for k, a in zip(g.kind, g.alpha)]
    sg = 100 * g.singleton.to_numpy(); em = 100 * g["empty"].to_numpy(); mu = np.clip(100 - sg - em, 0, None)
    x = np.arange(len(g)); ax[2].bar(x, sg, color="#4c72b0", label="singleton")
    ax[2].bar(x, em, bottom=sg, color="#dd8452", label="empty (abstain)")
    ax[2].bar(x, mu, bottom=sg + em, color="#8c8c8c", label="≥ 2 labels")
    ax[2].set_xticks(x); ax[2].set_xticklabels(lab, fontsize=5.5); ax[2].set_ylabel("% of test samples"); ax[2].set_ylim(0, 100)
    ax[2].set_title("(c) softmax set types", fontsize=8); ax[2].legend(fontsize=5.5, frameon=True, loc="center right", bbox_to_anchor=(1.0, 0.55))
    fig.tight_layout(); fig.savefig(f"{fdir}/fig8_reliability.png", dpi=DPI); plt.close(fig)


def fig_efficiency(res, fdir):
    """(a) learning curves with 95% CI over repeats; (b) leakage inflation vs n with 95% CI; n = 801 (different design) drawn separately."""
    L = pd.read_csv(f"{res}/rob_learning_curve_ci.csv"); B = pd.read_csv(f"{res}/rob_leak_vs_n_ci.csv"); P = pd.read_csv(f"{res}/leak_perm_fullN.csv")
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
    for m in ["Softmax", "Linear SVM", "Gaussian NB"]:
        g = L[L.model == m].sort_values("m_per_class")
        ax[0].errorbar(g.m_per_class, 100 * g.f1, yerr=100 * g.f1_ci, fmt="o-", ms=3, lw=1, capsize=2, label=m)
    ax[0].set_xscale("log"); ax[0].xaxis.set_minor_locator(plt.NullLocator()); ax[0].set_xticks([3, 5, 10, 20, 40, 60]); ax[0].set_xticklabels(["3", "5", "10", "20", "40", "60"])
    ax[0].set_xlabel("training samples per class"); ax[0].set_ylabel("macro-F1 on held-out fold (%)"); ax[0].set_ylim(50, 101)
    ax[0].set_title("(a) learning curves (k = 100, in-fold; 95% CI)", fontsize=8); ax[0].legend(fontsize=7, frameon=False, loc="lower right")
    for i, ((lab, k), g) in enumerate(B.groupby(["labels", "k"])):
        g = g.sort_values("n")
        ax[1].errorbar(g.n, g.delta, yerr=g.delta_ci, fmt=("o-" if lab == "permuted" else "s--"), ms=3, lw=1, capsize=2, color=f"C{i}", label=f"{lab}, k = {k}")
        if lab == "permuted":
            w = P.pivot_table(index="perm", columns=["k", "mode"], values="acc"); d = 100 * (w[(k, "leaky")] - w[(k, "clean")])
            ax[1].errorbar([801], [d.mean()], yerr=[1.96 * d.std() / np.sqrt(len(d))], fmt="D", mfc="none", ms=4, capsize=2, color=f"C{i}")
    ax[1].axhline(0, color="grey", lw=.8); ax[1].set_xscale("log"); ax[1].xaxis.set_minor_locator(plt.NullLocator())
    ax[1].set_xticks([30, 60, 120, 240, 390, 801]); ax[1].set_xticklabels(["30", "60", "120", "240", "390", "801*"])
    ax[1].set_xlabel("dataset size n (balanced; *801: all samples, unbalanced)", fontsize=7); ax[1].set_ylabel("leaky − in-fold accuracy (points)")
    ax[1].set_title("(b) leakage bias vs n (softmax; 95% CI)", fontsize=8); ax[1].legend(fontsize=6.5, frameon=False)
    fig.tight_layout(); fig.savefig(f"{fdir}/fig9_data_efficiency.png", dpi=DPI); plt.close(fig)
