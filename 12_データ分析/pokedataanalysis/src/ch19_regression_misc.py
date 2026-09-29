"""第19章 回帰分析その他."""
from poke import *

df = load_data()

# %% 19-0
import statsmodels.api as sm
from scipy import optimize
from statsmodels.duration.hazard_regression import PHReg
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold, cross_val_score

print(f"捕獲率 = 255（上限）の行: {(df['捕獲率'] == 255).sum()} / {len(df)}")
print("孵化歩数の値と度数:", df["孵化"].value_counts().sort_index().to_dict())
df[["捕獲率", "合計種族値", "孵化", "log重さ"]].describe().T[["mean", "std", "min", "max"]].round(1)

# %% 19-1
# トービットモデル（人工的な設定）: 捕獲率 = min(y*, 255), y* = b0 + b1 × 合計種族値/100 + ε, ε ~ N(0, σ^2)
y19 = df["捕獲率"].to_numpy(float)
X19 = np.column_stack([np.ones(len(df)), df["合計種族値"].to_numpy(float) / 100])
cens19 = y19 >= 255          # 右打ち切り（上限255に張り付いている）
C_UP = 255.0


def tobit_negll(theta, X, y, cens, c=C_UP):
    """右打ち切りトービットモデルの負の対数尤度. theta = (beta, log σ)."""
    beta, sigma = theta[:-1], np.exp(theta[-1])
    mu = X @ beta
    ll_obs = stats.norm.logpdf((y[~cens] - mu[~cens]) / sigma) - np.log(sigma)   # 観測: 密度
    ll_cen = stats.norm.logsf((c - mu[cens]) / sigma)                           # 打ち切り: P(y* ≥ c)
    return -(ll_obs.sum() + ll_cen.sum())


ols19 = sm.OLS(y19, X19).fit()
ols19_unc = sm.OLS(y19[~cens19], X19[~cens19]).fit()
theta0 = np.r_[ols19.params, np.log(np.sqrt(ols19.mse_resid))]
res_tb = optimize.minimize(tobit_negll, theta0, args=(X19, y19, cens19), method="Nelder-Mead",
                          options={"xatol": 1e-8, "fatol": 1e-10, "maxiter": 20000})
beta_tb, sigma_tb = res_tb.x[:-1], np.exp(res_tb.x[-1])
# 標準誤差: 負の対数尤度の数値ヘッセ行列（中心差分）の逆行列


def num_hess(f, x, eps=1e-4):
    k = len(x); H = np.zeros((k, k))
    for i in range(k):
        for j in range(k):
            e_i, e_j = np.eye(k)[i] * eps, np.eye(k)[j] * eps
            H[i, j] = (f(x + e_i + e_j) - f(x + e_i - e_j) - f(x - e_i + e_j) + f(x - e_i - e_j)) / (4 * eps ** 2)
    return H


H_tb = num_hess(lambda t: tobit_negll(t, X19, y19, cens19), res_tb.x)
se_tb = np.sqrt(np.diag(np.linalg.inv(H_tb)))
se_sigma = sigma_tb * se_tb[-1]          # デルタ法: SE(σ) ≈ σ × SE(log σ)
grad_tb = optimize.approx_fprime(res_tb.x, tobit_negll, 1e-6, X19, y19, cens19)
print(f"収束: {res_tb.success}, 最大対数尤度 {-res_tb.fun:.2f}, 解での勾配の最大絶対値 {np.abs(grad_tb).max():.1e}")
tobit_tab = pd.DataFrame({
    "OLS（全データ）": [*ols19.params, np.sqrt(ols19.mse_resid)],
    "OLS（255を除く）": [*ols19_unc.params, np.sqrt(ols19_unc.mse_resid)],
    "トービット": [*beta_tb, sigma_tb],
    "トービットSE": [*se_tb[:2], se_sigma],
}, index=["切片", "合計種族値/100", "σ"])

# トービットでの「観測値の期待値」E[y|x] = E[min(y*, c)] と、潜在変数の期待値 x'β
xs19 = np.linspace(1.5, 8, 100)
mu_s = beta_tb[0] + beta_tb[1] * xs19
z_s = (C_UP - mu_s) / sigma_tb
Ey_obs = mu_s * stats.norm.cdf(z_s) - sigma_tb * stats.norm.pdf(z_s) + C_UP * stats.norm.sf(z_s)

fig, ax = plt.subplots(figsize=(7.5, 4.8))
ax.scatter(X19[~cens19, 1] * 100, y19[~cens19], s=8, alpha=0.35, color=INK["muted"], label="観測（255未満）")
ax.scatter(X19[cens19, 1] * 100, y19[cens19], s=10, alpha=0.6, color=PALETTE[2], label="打ち切り（255）")
ax.plot(xs19 * 100, ols19.params[0] + ols19.params[1] * xs19, color=PALETTE[1], label="OLS（全データ）")
ax.plot(xs19 * 100, mu_s, color=PALETTE[0], label="トービット: 潜在変数 E[y*|x]")
ax.plot(xs19 * 100, Ey_obs, color=PALETTE[0], ls="--", label="トービット: 観測値 E[min(y*,255)|x]")
ax.axhline(C_UP, color=INK["axis"], lw=1)
ax.set(title="捕獲率の上限255を右打ち切りとみなしたトービットモデル", xlabel="合計種族値", ylabel="捕獲率")
ax.legend(fontsize=8)
plt.show()
tobit_tab.round(3)

# %% 19-2
# 生存時間解析（人工的な設定）: 孵化歩数を「孵化までの時間」とみなす。打ち切りはない
T19 = df["孵化"].to_numpy(float)
E19 = np.ones(len(df), dtype=int)       # イベント発生（1 = 孵化した）。全員1


def kaplan_meier(t, e):
    """カプラン・マイヤー推定. 各イベント時刻 t_j の n_j, d_j, S(t_j), ハザード d_j/n_j, 累積ハザードを返す."""
    times = np.unique(t[e == 1])
    n_risk = np.array([(t >= s).sum() for s in times])
    d = np.array([((t == s) & (e == 1)).sum() for s in times])
    S = np.cumprod(1 - d / n_risk)
    return pd.DataFrame({"時刻": times, "n_j（リスク集合）": n_risk, "d_j（イベント数）": d,
                         "S(t)": S, "h_j = d_j/n_j": d / n_risk,
                         "H(t)（ネルソン・アーレン）": np.cumsum(d / n_risk), "-log S(t)": -np.log(np.where(S > 0, S, np.nan))})


km19 = kaplan_meier(T19, E19)
# 打ち切りがなければ、KM は経験生存関数 S_n(t) = #{T_i > t} / n と一致する
S_emp = np.array([(T19 > s).mean() for s in km19["時刻"]])
print("KM と経験生存関数の最大差:", np.abs(km19["S(t)"].to_numpy() - S_emp).max())
print(f"孵化歩数の中央値（S(t) ≤ 0.5 となる最小の t）: {km19.loc[km19['S(t)'] <= 0.5, '時刻'].iloc[0]:.0f}")
km19.round(4)

# %% 19-3
# タマゴグループ（タマゴ1）別の KM 曲線と、ログランク検定（numpy で実装）
groups19 = ["陸上", "虫", "ドラゴン"]
g19 = df["タマゴ1"].astype(str)
sel19 = g19.isin(groups19).to_numpy()
Tg, Gg = T19[sel19], g19[sel19].to_numpy()


def logrank(t, g, levels):
    """k 群のログランク検定（打ち切りなし・同順位あり）. 統計量 ~ χ²(k-1)."""
    times = np.unique(t)
    k = len(levels)
    O_E = np.zeros(k); V = np.zeros((k, k))
    for s in times:
        at_risk = np.array([((t >= s) & (g == lv)).sum() for lv in levels])
        d_g = np.array([((t == s) & (g == lv)).sum() for lv in levels])
        n, dd = at_risk.sum(), d_g.sum()
        if n < 2:
            continue
        O_E += d_g - dd * at_risk / n
        V += dd * (n - dd) / (n - 1) * (np.diag(at_risk / n) - np.outer(at_risk, at_risk) / n ** 2)
    stat = O_E[:-1] @ np.linalg.solve(V[:-1, :-1], O_E[:-1])
    return stat, k - 1, stats.chi2.sf(stat, k - 1)


lr_stat, lr_df, lr_p = logrank(Tg, Gg, groups19)
print(f"ログランク検定（{'・'.join(groups19)}）: χ² = {lr_stat:.2f}, 自由度 {lr_df}, p = {lr_p:.3g}")
print(df[sel19].groupby(g19[sel19], observed=True)["孵化"].agg(["size", "median", "mean"]).to_string())

fig, axes = plt.subplots(1, 2, figsize=(12, 4.3))
for lv, col in zip(groups19, PALETTE):
    km_g = kaplan_meier(Tg[Gg == lv], np.ones((Gg == lv).sum(), dtype=int))
    tt = np.r_[0, km_g["時刻"]]
    axes[0].step(tt, np.r_[1, km_g["S(t)"]], where="post", color=col, label=f"{lv}（{(Gg == lv).sum()}匹）")
    axes[1].step(tt, np.r_[0, km_g["H(t)（ネルソン・アーレン）"]], where="post", color=col, label=lv)
axes[0].set(title="カプラン・マイヤー曲線（タマゴグループ別）", xlabel="孵化歩数（歩）", ylabel="生存関数 S(t) = P(T > t)")
axes[1].set(title="累積ハザード（ネルソン・アーレン推定）", xlabel="孵化歩数（歩）", ylabel="累積ハザード H(t)")
axes[0].legend(); axes[1].legend()
fig.tight_layout()
plt.show()

# %% 19-4
# Cox 比例ハザードモデル: h(t|x) = h0(t) exp(x'β)。同順位が多いので Efron 法
cox_cols = ["合計100", "log重さ", "性別不明"]
dcox = df.assign(合計100=df["合計種族値"] / 100, 性別不明=df["雄率"].isna().astype(int))
cox19 = PHReg(dcox["孵化"].to_numpy(float), dcox[cox_cols].to_numpy(float),
              status=np.ones(len(dcox)), ties="efron").fit()
cox_tab = pd.DataFrame({"係数": cox19.params, "標準誤差": cox19.bse, "z": cox19.params / cox19.bse,
                        "p値": cox19.pvalues, "ハザード比": np.exp(cox19.params),
                        "95%CI下限": np.exp(cox19.params - 1.96 * cox19.bse),
                        "95%CI上限": np.exp(cox19.params + 1.96 * cox19.bse)}, index=cox_cols)
print(f"部分対数尤度 {cox19.llf:.2f}")

# 比例ハザード性の簡易チェック: 孵化歩数の短い半分と長い半分で、合計種族値のハザード比を比べる
# （時点 t0 で分割し、t0 以降は t0 まで生き残った行だけで再推定する）
t0 = 5355
early = PHReg(np.minimum(dcox["孵化"], t0).to_numpy(float), dcox[cox_cols].to_numpy(float),
              status=(dcox["孵化"] < t0).astype(int).to_numpy(), ties="efron").fit()
late_mask = (dcox["孵化"] >= t0).to_numpy()
late = PHReg(dcox.loc[late_mask, "孵化"].to_numpy(float), dcox.loc[late_mask, cox_cols].to_numpy(float),
             status=np.ones(late_mask.sum()), ties="efron").fit()
print(f"合計100 のハザード比: 全期間 {np.exp(cox19.params[0]):.3f}, t < {t0} {np.exp(early.params[0]):.3f}, "
      f"t ≥ {t0}（{late_mask.sum()}匹） {np.exp(late.params[0]):.3f}")
cox_tab.round(4)

# %% 19-5
# ニューラルネットワーク（MLP）と線形回帰の比較: 5分割交差検証の RMSE
kf19 = KFold(n_splits=5, shuffle=True, random_state=SEED)
models19 = {
    "線形回帰": make_pipeline(StandardScaler(), LinearRegression()),
    "MLP（隠れ層16, ReLU）": make_pipeline(StandardScaler(), MLPRegressor(
        hidden_layer_sizes=(16,), activation="relu", solver="lbfgs", alpha=1e-2, max_iter=5000,
        random_state=SEED)),
}
rows19 = []
for target in ["経験値", "捕獲率"]:
    for name, mdl in models19.items():
        sc = -cross_val_score(mdl, df[STATS], df[target], cv=kf19, scoring="neg_root_mean_squared_error")
        rows19.append({"目的変数": target, "モデル": name, "CV RMSE": sc.mean(), "fold間の標準偏差": sc.std()})
nn_tab = pd.DataFrame(rows19).set_index(["目的変数", "モデル"])

# 合計種族値に対する予測（他の配分は平均的な形で比例させる）: 捕獲率
mlp_c = models19["MLP（隠れ層16, ReLU）"].fit(df[STATS], df["捕獲率"])
lin_c = make_pipeline(StandardScaler(), LinearRegression()).fit(df[STATS], df["捕獲率"])
share = df[STATS].mean() / df[STATS].mean().sum()
tot_grid = np.linspace(180, 780, 100)
grid_X = pd.DataFrame(np.outer(tot_grid, share), columns=STATS)
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.scatter(df["合計種族値"], df["捕獲率"], s=8, alpha=0.3, color=INK["muted"], label="ポケモン")
ax.plot(tot_grid, lin_c.predict(grid_X), color=PALETTE[1], label="線形回帰")
ax.plot(tot_grid, mlp_c.predict(grid_X), color=PALETTE[0], label="MLP")
ax.set(title="捕獲率の予測（6項目を平均的な比率で配分したとき）", xlabel="合計種族値", ylabel="捕獲率")
ax.legend()
plt.show()
nn_tab.round(2)
