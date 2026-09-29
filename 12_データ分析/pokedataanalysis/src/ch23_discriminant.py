"""第23章 判別分析."""
from poke import *

df = load_data()

# %% 23-0
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.metrics import confusion_matrix, roc_auc_score, roc_curve
from sklearn.model_selection import RepeatedStratifiedKFold, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# 2群: タイプ1が「むし」(y=0) と「ドラゴン」(y=1)。ドラゴンを陽性とする
d2 = df[df["タイプ1"].isin(["むし", "ドラゴン"])].reset_index(drop=True)
X2 = d2[STATS].to_numpy(float)
y2 = (d2["タイプ1"] == "ドラゴン").to_numpy(int)
print("件数:", {"むし(0)": int((y2 == 0).sum()), "ドラゴン(1)": int((y2 == 1).sum())})
print("タイプ2にドラゴン/むしを含む行（今回は使わない）:",
      int((types_of(df, "ドラゴン") & (df["タイプ1"] != "ドラゴン")).sum()), "/",
      int((types_of(df, "むし") & (df["タイプ1"] != "むし")).sum()))
d2.groupby("タイプ1", observed=True)[STATS + ["合計種族値"]].agg(["mean", "std"]).T.round(1).unstack()

# %% 23-1
# フィッシャーの線形判別: w = S_W^{-1}(xbar1 - xbar0)
xbar1, xbar0 = X2[y2 == 1].mean(axis=0), X2[y2 == 0].mean(axis=0)
S1, S0 = np.cov(X2[y2 == 1].T), np.cov(X2[y2 == 0].T)
n1, n0 = (y2 == 1).sum(), (y2 == 0).sum()
S_W = ((n1 - 1) * S1 + (n0 - 1) * S0) / (n1 + n0 - 2)      # プールした分散共分散行列
w_fisher = np.linalg.solve(S_W, xbar1 - xbar0)
mid = (xbar1 + xbar0) / 2
f_fisher = (X2 - mid) @ w_fisher                            # f(x) > 0 ならドラゴン

# sklearn は群ごとの（n で割る）分散共分散行列を事前確率で重み付けして平均する。
# 事前確率を既定（標本比率）にすると、それは S_W の定数倍になり、判別係数の方向が一致する
lda_eq = LinearDiscriminantAnalysis(solver="lsqr").fit(X2, y2)
cos = w_fisher @ lda_eq.coef_[0] / np.linalg.norm(w_fisher) / np.linalg.norm(lda_eq.coef_[0])
print("判別係数 w（手計算）:", dict(zip(STATS, w_fisher.round(4))))
print("sklearn coef_ との方向のコサイン類似度:", cos.round(8))
# 群間変動/群内変動の比は w で最大になる（ランダムな方向と比べる）
ratio = lambda v: (v @ (xbar1 - xbar0)) ** 2 / (v @ S_W @ v)
rng = get_rng()
print(f"比 (w'(xbar1-xbar0))^2 / w'S_W w : 判別係数 {ratio(w_fisher):.3f}, "
      f"ランダム方向1000本の最大 {max(ratio(v) for v in rng.normal(size=(1000, 6))):.3f}")

fig, ax = plt.subplots(figsize=(7, 4))
bins = np.linspace(f_fisher.min(), f_fisher.max(), 30)
ax.hist(f_fisher[y2 == 0], bins=bins, alpha=0.7, color=PALETTE[0], label="むし")
ax.hist(f_fisher[y2 == 1], bins=bins, alpha=0.7, color=PALETTE[1], label="ドラゴン")
ax.axvline(0, color=INK["secondary"], ls="--", lw=1)
ax.set(title="フィッシャーの線形判別関数 f(x) の分布", xlabel="f(x)（>0 ならドラゴンと判別）", ylabel="匹数")
ax.legend()
fig.tight_layout()
plt.show()

# %% 23-2
# マハラノビス平方距離による判別: D1^2 - D0^2 = -2 f(x) を確認
S_W_inv = np.linalg.inv(S_W)
D2_1 = np.einsum("ij,jk,ik->i", X2 - xbar1, S_W_inv, X2 - xbar1)
D2_0 = np.einsum("ij,jk,ik->i", X2 - xbar0, S_W_inv, X2 - xbar0)
print("max |(D1^2 - D0^2) - (-2 f(x))| =", np.abs((D2_1 - D2_0) + 2 * f_fisher).max().round(10))
print("マハラノビス判別とフィッシャー判別の一致率:", np.mean((D2_1 < D2_0) == (f_fisher > 0)))
print("2群の平均間のマハラノビス距離 D =", np.sqrt((xbar1 - xbar0) @ S_W_inv @ (xbar1 - xbar0)).round(3))
maha_tab = pd.DataFrame({"名前": d2["名前"], "タイプ1": d2["タイプ1"].astype(str),
                         "D^2(むし)": D2_0, "D^2(ドラゴン)": D2_1})
# 誤判別された例
maha_tab[(maha_tab["D^2(ドラゴン)"] < maha_tab["D^2(むし)"]) != (y2 == 1)].round(2)

# %% 23-3
# ベイズ判別: log{P(G1|x)/P(G0|x)} = f(x) + log{P(G1)/P(G0)}（等分散の多変量正規分布を仮定）
for p1 in [0.5, n1 / (n1 + n0), 0.1]:
    post_log_ratio = f_fisher + np.log(p1 / (1 - p1))
    pred = post_log_ratio > 0
    print(f"P(ドラゴン)={p1:.3f}: ドラゴンと判別 {pred.sum():3d}匹（実際 {n1}匹）, 正解率 {np.mean(pred == y2):.3f}, "
          f"感度 {pred[y2 == 1].mean():.3f}, 特異度 {1 - pred[y2 == 0].mean():.3f}")

# sklearn の事後確率と照合（事前確率=標本比率。共分散は n で割る版 S_ML を使う）
S_ML = S_W * (n1 + n0 - 2) / (n1 + n0)
f_ml = (X2 - mid) @ np.linalg.solve(S_ML, xbar1 - xbar0)
post_hand = 1 / (1 + np.exp(-(f_ml + np.log(n1 / n0))))
print("\n事後確率 P(ドラゴン|x) の手計算と sklearn predict_proba の最大差:",
      np.abs(post_hand - lda_eq.predict_proba(X2)[:, 1]).max())

# %% 23-4
# 2次判別: 群ごとの分散共分散行列を使う
def qda_score(X, xbar, S, prior):
    """log π_k - (1/2)log|S_k| - (1/2)(x - xbar_k)' S_k^{-1} (x - xbar_k)."""
    Dk = np.einsum("ij,jk,ik->i", X - xbar, np.linalg.inv(S), X - xbar)
    return np.log(prior) - 0.5 * np.linalg.slogdet(S)[1] - 0.5 * Dk

q_hand = qda_score(X2, xbar1, S1, 0.5) - qda_score(X2, xbar0, S0, 0.5)
qda_eq = QuadraticDiscriminantAnalysis(priors=[0.5, 0.5]).fit(X2, y2)
print("手計算と sklearn QDA の判別結果の一致率:", np.mean((q_hand > 0) == qda_eq.predict(X2)))
print("訓練データでの正解率  LDA:", np.mean((f_fisher > 0) == y2).round(3),
      " QDA:", np.mean((q_hand > 0) == y2).round(3))
# 等分散性の検定（ボックスの M 検定, カイ2乗近似）
p_, g_ = 6, 2
ns = np.array([n0, n1])
M = (ns.sum() - g_) * np.linalg.slogdet(S_W)[1] - sum((nk - 1) * np.linalg.slogdet(Sk)[1] for nk, Sk in [(n0, S0), (n1, S1)])
c_ = (np.sum(1 / (ns - 1)) - 1 / (ns.sum() - g_)) * (2 * p_**2 + 3 * p_ - 1) / (6 * (p_ + 1) * (g_ - 1))
chi_box, df_box = M * (1 - c_), p_ * (p_ + 1) * (g_ - 1) / 2
print(f"ボックスの M 検定: χ² = {chi_box:.1f}, 自由度 = {df_box:.0f}, p値 = {stats.chi2.sf(chi_box, df_box):.2e}")

# %% 23-5
# 正準判別分析（3群: くさ・ほのお・みず）: S_W^{-1} S_B の固有値問題
d3 = df[df["タイプ1"].isin(["くさ", "ほのお", "みず"])].reset_index(drop=True)
grp3 = d3["タイプ1"].astype(str).to_numpy()
X3 = d3[STATS].to_numpy(float)
levels3 = ["くさ", "ほのお", "みず"]
xbar_all = X3.mean(axis=0)
W3 = sum(((X3[grp3 == g] - X3[grp3 == g].mean(0)).T @ (X3[grp3 == g] - X3[grp3 == g].mean(0))) for g in levels3)
B3 = sum((grp3 == g).sum() * np.outer(X3[grp3 == g].mean(0) - xbar_all, X3[grp3 == g].mean(0) - xbar_all)
         for g in levels3)
ev3, V3 = np.linalg.eig(np.linalg.solve(W3, B3))
o3 = np.argsort(ev3.real)[::-1]
ev3, V3 = ev3.real[o3], V3.real[:, o3]
print("S_W^{-1} S_B の固有値:", ev3.round(5), "（非0は 群数-1 = 2 個）")
print("固有値の比:", (ev3[:2] / ev3[:2].sum()).round(4))
lda3 = LinearDiscriminantAnalysis(solver="eigen").fit(X3, grp3)
print("sklearn explained_variance_ratio_:", lda3.explained_variance_ratio_[:2].round(4))
can_hand = (X3 - xbar_all) @ V3[:, :2]
can_sk = lda3.transform(X3)
print("手計算と sklearn の正準変量の相関:",
      [abs(np.corrcoef(can_hand[:, k], can_sk[:, k])[0, 1]).round(6) for k in range(2)])
print("訓練データでの正解率（3群）:", np.mean(lda3.predict(X3) == grp3).round(3))
print(pd.crosstab(pd.Series(grp3, name="実際"), pd.Series(lda3.predict(X3), name="予測")))

fig, ax = plt.subplots(figsize=(6.5, 4.8))
for k, g in enumerate(levels3):
    m = grp3 == g
    ax.scatter(can_sk[m, 0], can_sk[m, 1], s=14, alpha=0.6, color=PALETTE[k], label=f"{g}（{m.sum()}）")
ax.set(title="正準判別分析（くさ・ほのお・みず）", xlabel="第1正準変量", ylabel="第2正準変量")
ax.legend()
fig.tight_layout()
plt.show()
pd.DataFrame(lda3.scalings_[:, :2], index=STATS, columns=["第1正準係数", "第2正準係数"]).round(4)

# %% 23-6
# SVM（標準化したうえで）: C の影響とカーネル
print("6変数・線形 SVM（訓練データ）")
for C in [0.01, 0.1, 1, 10, 1000]:
    svm = make_pipeline(StandardScaler(), SVC(kernel="linear", C=C)).fit(X2, y2)
    print(f"  C={C:>8g}: サポートベクター {svm[-1].n_support_.sum():3d}個, 訓練正解率 {svm.score(X2, y2):.3f}")
print("→ C を大きくしても訓練正解率が1にならない = 線形分離不可能（ハードマージンSVMは解をもたない）")

# 2変数（HP・攻撃）で境界を描く
X2d = d2[["HP", "攻撃"]].to_numpy(float)
xx, yy = np.meshgrid(np.linspace(0, 200, 200), np.linspace(0, 200, 200))
fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True)
for ax, (kernel, C) in zip(axes, [("linear", 0.1), ("rbf", 1), ("rbf", 100)]):
    svm2 = make_pipeline(StandardScaler(), SVC(kernel=kernel, C=C, gamma="scale")).fit(X2d, y2)
    zz = svm2.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    ax.contourf(xx, yy, zz > 0, levels=[-0.5, 0.5, 1.5], colors=["#dbe8f8", "#fbe1d6"], alpha=0.8)
    ax.contour(xx, yy, zz, levels=[-1, 0, 1], colors=INK["secondary"], linestyles=["--", "-", "--"], linewidths=1)
    for k, nm in enumerate(["むし", "ドラゴン"]):
        ax.scatter(X2d[y2 == k, 0], X2d[y2 == k, 1], s=12, color=PALETTE[k], label=nm)
    ax.set(title=f"{kernel}, C={C}（訓練正解率 {svm2.score(X2d, y2):.2f}）", xlabel="HP", xlim=(0, 200), ylim=(0, 200))
axes[0].set_ylabel("攻撃")
axes[0].legend(loc="upper left")
fig.suptitle("SVM の判別境界（実線）とマージン（破線, 決定関数=±1）", fontsize=12)
fig.tight_layout()
plt.show()

# %% 23-7
# 混同行列・感度・特異度・ROC/AUC（訓練データで評価。陽性=ドラゴン）
def binary_report(y_true, score, thr=0.0):
    pred = (score > thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
    return {"TP": tp, "FN": fn, "FP": fp, "TN": tn, "正解率": (tp + tn) / len(y_true),
            "感度(TPR)": tp / (tp + fn), "特異度(1-FPR)": tn / (tn + fp), "AUC": roc_auc_score(y_true, score)}

rep = pd.DataFrame({"LDA": binary_report(y2, f_fisher), "QDA": binary_report(y2, q_hand)}).T
print(rep.round(3).to_string())
# AUC = P(ドラゴンの得点 > むしの得点)（マン・ホイットニーの U / (n1 n0)）で確認
U = stats.mannwhitneyu(f_fisher[y2 == 1], f_fisher[y2 == 0]).statistic
print("\nLDA の AUC: U/(n1 n0) =", round(U / (n1 * n0), 4), " roc_auc_score =", round(roc_auc_score(y2, f_fisher), 4))

fig, ax = plt.subplots(figsize=(5, 4.5))
for k, (nm, sc) in enumerate([("LDA", f_fisher), ("QDA", q_hand)]):
    fpr, tpr, _ = roc_curve(y2, sc)
    ax.plot(fpr, tpr, color=PALETTE[k], label=f"{nm}（AUC {roc_auc_score(y2, sc):.3f}）")
ax.plot([0, 1], [0, 1], color=INK["muted"], ls="--", lw=1)
ax.set(title="ROC 曲線（訓練データ）", xlabel="偽陽性率 FPR", ylabel="真陽性率 TPR（感度）")
ax.legend(loc="lower right")
fig.tight_layout()
plt.show()

# %% 23-8
# 訓練データでの評価は楽観的: 5分割交差検証（10回くり返し）と比較
models = {
    "LDA": LinearDiscriminantAnalysis(),
    "QDA": QuadraticDiscriminantAnalysis(),
    "線形SVM C=1": make_pipeline(StandardScaler(), SVC(kernel="linear", C=1)),
    "RBF-SVM C=1": make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1)),
    "RBF-SVM C=1000": make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1000)),
}
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=SEED)
rows = []
for nm, mdl in models.items():
    r = cross_validate(mdl, X2, y2, cv=cv, scoring=["accuracy", "roc_auc"], return_train_score=True)
    rows.append({"モデル": nm, "訓練 正解率": r["train_accuracy"].mean(), "CV 正解率": r["test_accuracy"].mean(),
                 "訓練 AUC": r["train_roc_auc"].mean(), "CV AUC": r["test_roc_auc"].mean()})
print("多数派（むし）と常に答えたときの正解率:", round(n0 / (n0 + n1), 3))
pd.DataFrame(rows).set_index("モデル").round(3)
