"""第16章 重回帰分析."""
from poke import *

df = load_data()

# %% 16-0
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, lasso_path, enet_path

cols16 = ["経験値", "合計種族値", *STATS, "捕獲率", "log高さ", "log重さ"]
print(f"行数: {len(df)}")
df[cols16].describe().T[["mean", "std", "min", "max"]].round(2)

# %% 16-1
# 正規方程式 (X^T X) beta = X^T y を numpy で解き、statsmodels と照合する
y16 = df["経験値"].to_numpy(float)
X16 = np.column_stack([np.ones(len(df)), df[STATS].to_numpy(float)])
n16, p16 = X16.shape                     # p16 = 切片を含む係数の数 (d+1)

beta_hat = np.linalg.solve(X16.T @ X16, X16.T @ y16)
resid16 = y16 - X16 @ beta_hat
s2_16 = resid16 @ resid16 / (n16 - p16)            # 誤差分散の不偏推定量
se16 = np.sqrt(np.diag(s2_16 * np.linalg.inv(X16.T @ X16)))

ols16 = sm.OLS(df["経験値"], sm.add_constant(df[STATS])).fit()
print(f"n = {n16}, 係数の数 = {p16}, 残差の自由度 = {n16 - p16}")
print("係数の最大差:", np.abs(beta_hat - ols16.params.to_numpy()).max())
print("標準誤差の最大差:", np.abs(se16 - ols16.bse.to_numpy()).max())
pd.DataFrame({"正規方程式": beta_hat, "statsmodels": ols16.params.to_numpy(),
              "標準誤差(手計算)": se16}, index=ols16.params.index).round(4)

# %% 16-2
# 単回帰 log重さ = a + b log高さ。体積則（重さ ∝ 高さ^3）なら b = 3
x_lh = df["log高さ"].to_numpy()
y_lw = df["log重さ"].to_numpy()
n_s = len(x_lh)
Sxx = ((x_lh - x_lh.mean()) ** 2).sum()
Sxy = ((x_lh - x_lh.mean()) * (y_lw - y_lw.mean())).sum()
b_s = Sxy / Sxx
a_s = y_lw.mean() - b_s * x_lh.mean()
e_s = y_lw - (a_s + b_s * x_lh)
s_s = np.sqrt((e_s ** 2).sum() / (n_s - 2))
se_b = s_s / np.sqrt(Sxx)
df_s = n_s - 2
tcrit = stats.t.ppf(0.975, df_s)

ols_s = sm.OLS(y_lw, sm.add_constant(x_lh)).fit()
print(f"傾き b = {b_s:.4f}（statsmodels {ols_s.params[1]:.4f}）, SE = {se_b:.4f}, 切片 a = {a_s:.4f}")
print(f"b の95%信頼区間: [{b_s - tcrit * se_b:.3f}, {b_s + tcrit * se_b:.3f}]")
for b0 in [0, 3]:
    t0 = (b_s - b0) / se_b
    print(f"H0: b = {b0}:  t = {t0:.2f}, 自由度 {df_s}, 両側p値 = {2 * stats.t.sf(abs(t0), df_s):.3g}")
print(f"決定係数 R^2 = {ols_s.rsquared:.3f}")

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.scatter(x_lh, y_lw, s=10, alpha=0.4, color=PALETTE[0], label="ポケモン")
xx = np.linspace(x_lh.min(), x_lh.max(), 50)
ax.plot(xx, a_s + b_s * xx, color=PALETTE[1], label=f"最小二乗直線（傾き {b_s:.2f}）")
ax.plot(xx, a_s + b_s * x_lh.mean() + 3 * (xx - x_lh.mean()), color=PALETTE[2], ls="--",
        label="傾き3（体積則）を平均点に通した線")
ax.set(title="log重さ と log高さ の単回帰", xlabel="log(高さ / m)", ylabel="log(重さ / kg)")
ax.legend()
plt.show()

# %% 16-3
# 決定係数・自由度調整済み決定係数・F 検定を定義式から計算
y_bar = y16.mean()
ST = ((y16 - y_bar) ** 2).sum()                    # 総変動
SE_ = (resid16 ** 2).sum()                         # 残差平方和
SR = ST - SE_                                      # 回帰変動
d16 = p16 - 1                                      # 説明変数の数
R2 = SR / ST
R2_adj = 1 - (SE_ / (n16 - d16 - 1)) / (ST / (n16 - 1))
F16 = (SR / d16) / (SE_ / (n16 - d16 - 1))
print(f"R^2 = {R2:.4f}（sm {ols16.rsquared:.4f}）, 調整済み R^2 = {R2_adj:.4f}（sm {ols16.rsquared_adj:.4f}）")
print(f"F = {F16:.1f}（sm {ols16.fvalue:.1f}）, 自由度 ({d16}, {n16 - d16 - 1}), p = {stats.f.sf(F16, d16, n16 - d16 - 1):.3g}")

# 係数ごとの t 検定（H0: beta_j = 0）
t16 = beta_hat / se16
coef_tab16 = pd.DataFrame({"係数": beta_hat, "標準誤差": se16, "t": t16,
                           "p値": 2 * stats.t.sf(np.abs(t16), n16 - p16)}, index=ols16.params.index)
print(coef_tab16.round(4).to_string())

# 入れ子モデルの F 検定: H0「6項目の係数がすべて等しい」（= 合計種族値だけのモデル）
ols16_tot = sm.OLS(df["経験値"], sm.add_constant(df["合計種族値"])).fit()
q16 = d16 - 1                                      # 制約の数
F_nest = ((ols16_tot.ssr - ols16.ssr) / q16) / (ols16.ssr / (n16 - p16))
print(f"\n合計種族値だけのモデル R^2 = {ols16_tot.rsquared:.4f}")
print(f"係数が等しいかの F = {F_nest:.2f}, 自由度 ({q16}, {n16 - p16}), p = {stats.f.sf(F_nest, q16, n16 - p16):.3g}")
print("statsmodels compare_f_test:", np.round(ols16.compare_f_test(ols16_tot), 4))

# %% 16-4
# 多重共線性: VIF_j = 1 / (1 - R_j^2)（R_j^2 は x_j を他の説明変数で回帰した決定係数）
vif_cols = [*STATS, "捕獲率", "log高さ", "log重さ"]
Xv = df[vif_cols]
vif_hand = []
for c in vif_cols:
    r2j = sm.OLS(Xv[c], sm.add_constant(Xv.drop(columns=c))).fit().rsquared
    vif_hand.append(1 / (1 - r2j))
Xv_c = sm.add_constant(Xv).to_numpy(float)
vif_sm = [variance_inflation_factor(Xv_c, i + 1) for i in range(len(vif_cols))]
print(pd.DataFrame({"VIF(手計算)": vif_hand, "VIF(statsmodels)": vif_sm}, index=vif_cols).round(2).to_string())

# 完全な共線性: 合計種族値 = 6項目の和 なので、全部入れると X^T X が特異になる
X_sing = np.column_stack([np.ones(len(df)), df[STATS + ["合計種族値"]].to_numpy(float)])
print(f"\n6項目+合計種族値: 列数 {X_sing.shape[1]}, 階数 {np.linalg.matrix_rank(X_sing)}, "
      f"X^T X の条件数 {np.linalg.cond(X_sing.T @ X_sing):.2e}")

# %% 16-5
# 不均一分散の確認（Breusch-Pagan）と実行可能な一般化最小二乗法（FGLS = 推定した重みの WLS）
X16_df = sm.add_constant(df[STATS])
lm, lm_p, _, _ = het_breuschpagan(ols16.resid, X16_df)
print(f"Breusch-Pagan: LM = {lm:.1f}, 自由度 {d16}, p = {lm_p:.3g}")

# 分散関数を log(e^2) = X gamma で推定し、重み w_i = 1 / sigma_i^2 とする
aux = sm.OLS(np.log(ols16.resid ** 2), X16_df).fit()
sigma2_hat = np.exp(aux.fittedvalues)
wls16 = sm.WLS(df["経験値"], X16_df, weights=1 / sigma2_hat).fit()

# WLS = 各行を sigma_i で割ったデータの OLS（手計算で照合）
w_sqrt = 1 / np.sqrt(sigma2_hat.to_numpy())
beta_wls = np.linalg.lstsq(X16 * w_sqrt[:, None], y16 * w_sqrt, rcond=None)[0]
print("WLS 係数の最大差（手計算 vs sm）:", np.abs(beta_wls - wls16.params.to_numpy()).max())

hc3 = ols16.get_robustcov_results("HC3")
pd.DataFrame({"OLS係数": ols16.params, "OLS標準誤差": ols16.bse,
              "OLS頑健SE(HC3)": hc3.bse, "FGLS係数": wls16.params, "FGLS標準誤差": wls16.bse}).round(3)

# %% 16-6
# 正則化（Ridge / Lasso / Elastic Net）。説明変数と目的変数を標準化してから推定する
reg_cols = [*STATS, "捕獲率", "log重さ"]
Z16 = StandardScaler().fit_transform(df[reg_cols])
yz16 = (y16 - y16.mean()) / y16.std()
alphas_l, coefs_l, _ = lasso_path(Z16, yz16, n_alphas=100, eps=1e-4)
alphas_e, coefs_e, _ = enet_path(Z16, yz16, l1_ratio=0.5, n_alphas=100, eps=1e-4)
alphas_r = np.logspace(-2, 5, 100)
coefs_r = np.array([Ridge(alpha=a).fit(Z16, yz16).coef_ for a in alphas_r]).T

# Lasso で各変数が初めて 0 でなくなる λ（大きい順 = モデルに入る順）
enter16 = {c: alphas_l[np.argmax(b != 0)] if (b != 0).any() else 0 for c, b in zip(reg_cols, coefs_l)}
print("Lasso で係数が 0 でなくなる λ:", {c: round(a, 4) for c, a in sorted(enter16.items(), key=lambda t: -t[1])})
print("標準化 OLS 係数:", dict(zip(reg_cols, np.linalg.lstsq(Z16, yz16, rcond=None)[0].round(3))))

# 注目する3変数だけ色を付け、残り（攻撃・防御・特攻・特防・素早）は灰色の「その他」にまとめる
hl16 = {"HP": PALETTE[0], "捕獲率": PALETTE[1], "log重さ": PALETTE[2]}
fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
for ax, (name, al, co, lab) in zip(axes, [
        ("Ridge", alphas_r, coefs_r, "Ridge の λ"),
        ("Lasso", alphas_l, coefs_l, "Lasso の λ"),
        ("Elastic Net（L1比 0.5）", alphas_e, coefs_e, "Elastic Net の λ")]):
    first_other = True
    for c, b in zip(reg_cols, co):
        if c in hl16:
            ax.plot(np.log10(al), b, color=hl16[c], lw=2, label=c)
        else:
            ax.plot(np.log10(al), b, color=INK["muted"], lw=1,
                    label="その他（攻撃・防御・特攻・特防・素早）" if first_other else None)
            first_other = False
    ax.axhline(0, color=INK["axis"], lw=0.8)
    ax.set(title=f"{name} の係数パス", xlabel=f"log10({lab})")
axes[0].set_ylabel("標準化係数")
h16, l16 = axes[0].get_legend_handles_labels()
fig.legend(h16, l16, loc="lower center", ncol=4)
fig.tight_layout(rect=(0, 0.08, 1, 1))
plt.show()
