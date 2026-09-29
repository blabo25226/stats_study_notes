"""第30章 モデル選択."""
from poke import *

df = load_data()

# %% 30-0
import itertools
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, LeaveOneOut, cross_val_score

d30 = df.assign(孵化千=df["孵化"] / 1000)
cand30 = [*STATS, "捕獲率", "log高さ", "log重さ", "孵化千"]    # 説明変数の候補（10個）
y30 = d30["経験値"].to_numpy(float)
n30 = len(d30)
print(f"n = {n30}, 候補の説明変数 {len(cand30)} 個 → 部分集合 {2 ** len(cand30)} 通り（切片のみを含む）")
d30[["経験値", *cand30]].describe().T[["mean", "std", "min", "max"]].round(2)

# %% 30-1
# AIC・BIC を定義式から計算する（誤差の正規性を仮定した重回帰）
# 最大対数尤度 logL = -n/2 {log(2π σ̂²) + 1}, σ̂² = RSS/n（最尤推定量）
# パラメータ数 k = 説明変数の数 p + 切片 1 + 誤差分散 1 = p + 2
def aic_bic(rss, n, p):
    ll = -n / 2 * (np.log(2 * np.pi * rss / n) + 1)
    k = p + 2
    return ll, -2 * ll + 2 * k, -2 * ll + np.log(n) * k


ols30 = sm.OLS(y30, sm.add_constant(d30[STATS])).fit()
ll_h, aic_h, bic_h = aic_bic(ols30.ssr, n30, len(STATS))
print(f"最大対数尤度: 手計算 {ll_h:.3f}, statsmodels {ols30.llf:.3f}")
print(f"AIC: 手計算 {aic_h:.3f}, statsmodels {ols30.aic:.3f}（差 {aic_h - ols30.aic:.1f}）")
print(f"BIC: 手計算 {bic_h:.3f}, statsmodels {ols30.bic:.3f}（差 {bic_h - ols30.bic:.3f} = log n = {np.log(n30):.3f}）")
print("→ statsmodels は誤差分散をパラメータ数に数えない（k = p + 1）。モデル間の差は同じなので選択結果は変わらない")

# %% 30-2
# 全部分集合選択: 1024 通りのモデルの AIC・BIC を計算する
Xall30 = d30[cand30].to_numpy(float)
rows30 = []
for r in range(len(cand30) + 1):
    for sub in itertools.combinations(range(len(cand30)), r):
        Xs = np.column_stack([np.ones(n30), Xall30[:, list(sub)]])
        beta = np.linalg.lstsq(Xs, y30, rcond=None)[0]
        rss = ((y30 - Xs @ beta) ** 2).sum()
        _, aic, bic = aic_bic(rss, n30, r)
        rows30.append({"変数": tuple(cand30[j] for j in sub), "p": r, "RSS": rss, "AIC": aic, "BIC": bic,
                       "調整R2": 1 - (rss / (n30 - r - 1)) / (((y30 - y30.mean()) ** 2).sum() / (n30 - 1))})
subsets30 = pd.DataFrame(rows30)
best_aic = subsets30.loc[subsets30["AIC"].idxmin()]
best_bic = subsets30.loc[subsets30["BIC"].idxmin()]
best_adj = subsets30.loc[subsets30["調整R2"].idxmax()]
print(f"AIC 最小（p={best_aic['p']}, AIC={best_aic['AIC']:.1f}）: {best_aic['変数']}")
print(f"BIC 最小（p={best_bic['p']}, BIC={best_bic['BIC']:.1f}）: {best_bic['変数']}")
print(f"調整R^2 最大（p={best_adj['p']}）: {best_adj['変数']}")
print("\nAIC の小さい順（上位5）")
print(subsets30.nsmallest(5, "AIC")[["p", "AIC", "BIC", "変数"]].to_string())

# 変数の数ごとの最良モデルについて、全体の最小値との差 ΔAIC・ΔBIC（同じ単位なので1つの図に描ける）
by_p = subsets30.groupby("p")[["AIC", "BIC"]].min()
delta_p = by_p - by_p.min()
print("\n変数の数ごとの最良モデルの ΔAIC・ΔBIC")
print(delta_p.round(2).T.to_string())
show_p = delta_p.loc[6:]            # p ≤ 5 は差が100以上あり、図から外す
fig, ax = plt.subplots(figsize=(7, 4.3))
ax.plot(show_p.index, show_p["AIC"], marker="o", color=PALETTE[0], label="ΔAIC")
ax.plot(show_p.index, show_p["BIC"], marker="s", color=PALETTE[1], label="ΔBIC")
ax.axhline(0, color=INK["axis"], lw=0.8)
ax.set(title="変数の数ごとの最良モデルの ΔAIC・ΔBIC（p が6以上）", xlabel="説明変数の数 p",
       ylabel="最小値との差（小さいほど良い）")
ax.set_xticks(show_p.index)
ax.legend()
plt.show()

# %% 30-3
# 交差検証: k 分割 CV と LOO。LOO は PRESS = Σ (e_i / (1 - h_ii))^2 で1回の推定から求まる
def press_loo(X, y):
    """ハット行列の対角成分を使った LOO の予測誤差平方和の平均."""
    Xc = np.column_stack([np.ones(len(y)), X])
    Q, _ = np.linalg.qr(Xc)
    h = (Q ** 2).sum(axis=1)
    e = y - Q @ (Q.T @ y)
    return np.mean((e / (1 - h)) ** 2)


models30 = {
    "切片のみ": [],
    "種族値6項目": STATS,
    f"BIC 最小（{best_bic['p']}変数）": list(best_bic["変数"]),
    f"AIC 最小（{best_aic['p']}変数）": list(best_aic["変数"]),
    "全10変数": cand30,
}
cv_rows = []
for name, cols in models30.items():
    Xm = d30[cols].to_numpy(float) if cols else np.zeros((n30, 0))
    row = {"モデル": name, "p": len(cols)}
    for k in [5, 10]:
        kf = KFold(n_splits=k, shuffle=True, random_state=SEED)
        if cols:
            row[f"{k}分割CV MSE"] = -cross_val_score(LinearRegression(), Xm, y30, cv=kf,
                                                     scoring="neg_mean_squared_error").mean()
        else:  # 切片のみ: 訓練データの平均で予測
            row[f"{k}分割CV MSE"] = np.mean([np.mean((y30[te] - y30[tr].mean()) ** 2) for tr, te in kf.split(y30)])
    row["LOO MSE（PRESS/n）"] = press_loo(Xm, y30)
    cv_rows.append(row)
cv_tab = pd.DataFrame(cv_rows).set_index("モデル")

# 近道式の確認: 実際に n 回あてはめ直した LOO と一致するか（6項目のモデル）
X6 = d30[STATS].to_numpy(float)
loo_brute = -cross_val_score(LinearRegression(), X6, y30, cv=LeaveOneOut(), scoring="neg_mean_squared_error").mean()
print(f"6項目モデルの LOO MSE: 920回あてはめ直し {loo_brute:.4f}, PRESS 近道式 {press_loo(X6, y30):.4f}")
cv_tab.round(1)

# %% 30-4
# 過学習の例: 訓練データ40匹で log重さ ~ log高さ の多項式回帰。次数を上げると？
# 残りの行を「テストデータ」（真の汎化誤差の代わり）として使える
rng30 = get_rng()
idx_tr = rng30.choice(n30, size=40, replace=False)
mask_tr = np.zeros(n30, dtype=bool); mask_tr[idx_tr] = True
x_all = d30["log高さ"].to_numpy(); yw_all = d30["log重さ"].to_numpy()
mu_x, sd_x = x_all[mask_tr].mean(), x_all[mask_tr].std()
z_all = (x_all - mu_x) / sd_x            # 数値的安定のため訓練データで標準化
z_tr, y_tr = z_all[mask_tr], yw_all[mask_tr]
# 多項式は訓練データの範囲外で発散するので、テストは訓練データの x の範囲内の行に限る（内挿のみ評価）
in_range = (~mask_tr) & (z_all >= z_tr.min()) & (z_all <= z_tr.max())
z_te, y_te = z_all[in_range], yw_all[in_range]
print(f"テストに使う行（訓練40匹の log高さ の範囲内）: {in_range.sum()} / {(~mask_tr).sum()}")


def poly_design(z, deg):
    return np.vander(z, deg + 1, increasing=True)


degs30 = range(1, 13)
kf30 = KFold(n_splits=5, shuffle=True, random_state=SEED)
over_rows = []
for deg in degs30:
    b = np.linalg.lstsq(poly_design(z_tr, deg), y_tr, rcond=None)[0]
    tr_mse = np.mean((y_tr - poly_design(z_tr, deg) @ b) ** 2)
    te_mse = np.mean((y_te - poly_design(z_te, deg) @ b) ** 2)
    cv_mse = np.mean([np.mean((y_tr[te] - poly_design(z_tr[te], deg)
                               @ np.linalg.lstsq(poly_design(z_tr[tr], deg), y_tr[tr], rcond=None)[0]) ** 2)
                      for tr, te in kf30.split(z_tr)])
    _, aic, bic = aic_bic(tr_mse * len(y_tr), len(y_tr), deg)
    over_rows.append({"次数": deg, "訓練MSE": tr_mse, "5分割CV MSE": cv_mse, "テストMSE（残りの行）": te_mse,
                      "AIC": aic, "BIC": bic})
over_tab = pd.DataFrame(over_rows).set_index("次数")
print("CV MSE 最小の次数:", over_tab["5分割CV MSE"].idxmin(), " テストMSE 最小の次数:", over_tab["テストMSE（残りの行）"].idxmin(),
      " AIC 最小:", over_tab["AIC"].idxmin(), " BIC 最小:", over_tab["BIC"].idxmin())

fig, axes = plt.subplots(1, 2, figsize=(12, 4.3))
ax = axes[0]
ax.plot(over_tab.index, over_tab["訓練MSE"], marker="o", color=PALETTE[0], label="訓練MSE")
ax.plot(over_tab.index, over_tab["5分割CV MSE"], marker="s", color=PALETTE[1], label="5分割CV MSE（訓練40匹の中で）")
ax.plot(over_tab.index, over_tab["テストMSE（残りの行）"], marker="^", color=PALETTE[2], label="テストMSE（残りの行）")
ax.set_yscale("log")
ax.set(title="多項式の次数と予測誤差", xlabel="多項式の次数", ylabel="平均二乗誤差（log重さ², 対数目盛）")
ax.set_xticks(list(degs30))
ax.legend(fontsize=8)
ax = axes[1]
zz = np.linspace(z_tr.min(), z_tr.max(), 300)
ax.scatter(x_all[~mask_tr], yw_all[~mask_tr], s=6, alpha=0.2, color=INK["muted"], label="残りの行")
ax.scatter(x_all[mask_tr], y_tr, s=18, color=INK["primary"], label="訓練40匹")
for deg, col in [(1, PALETTE[0]), (3, PALETTE[1]), (12, PALETTE[2])]:
    b = np.linalg.lstsq(poly_design(z_tr, deg), y_tr, rcond=None)[0]
    ax.plot(zz * sd_x + mu_x, poly_design(zz, deg) @ b, color=col, label=f"{deg}次")
ax.set_ylim(yw_all.min() - 1, yw_all.max() + 1)
ax.set(title="訓練40匹にあてはめた多項式", xlabel="log(高さ / m)", ylabel="log(重さ / kg)")
ax.legend(fontsize=8)
fig.tight_layout()
plt.show()
over_tab.round(3)
