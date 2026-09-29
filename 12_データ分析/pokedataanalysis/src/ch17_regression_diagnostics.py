"""第17章 回帰診断法."""
from poke import *

df = load_data()

# %% 17-0
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import OLSInfluence
from statsmodels.stats.diagnostic import het_breuschpagan

# 第16章と同じモデル: 経験値 ~ 種族値6項目
X17 = sm.add_constant(df[STATS])
y17 = df["経験値"]
ols17 = sm.OLS(y17, X17).fit()
n17, p17 = X17.shape
print(f"n = {n17}, 係数の数 p = {p17}, R^2 = {ols17.rsquared:.3f}")
df[["経験値", *STATS, "高さ", "重さ"]].describe().T[["mean", "std", "min", "max"]].round(1)

# %% 17-1
# 残差プロットと正規 Q-Q プロット
fit17 = ols17.fittedvalues
res17 = ols17.resid
s17 = np.sqrt(ols17.mse_resid)
print(f"残差の歪度 {stats.skew(res17):.2f}, 尖度(-3) {stats.kurtosis(res17):.2f}")
jb17 = stats.jarque_bera(res17)
print(f"Jarque-Bera: 統計量 {jb17.statistic:.0f}, 自由度 2, p = {jb17.pvalue:.3g}")

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
axes[0].scatter(fit17, res17, s=10, alpha=0.5, color=PALETTE[0])
axes[0].axhline(0, color=INK["axis"], lw=1)
for i in res17.abs().nlargest(4).index:
    axes[0].annotate(df.loc[i, "名前"], (fit17[i], res17[i]), xytext=(4, 0), textcoords="offset points",
                     fontsize=8, color=INK["secondary"], va="center")
axes[0].set(title="残差プロット", xlabel="予測値（経験値）", ylabel="残差（経験値）")
osm, osr = stats.probplot(res17 / s17, dist="norm", fit=False)
axes[1].scatter(osm, osr, s=10, alpha=0.5, color=PALETTE[0])
lim = [osm.min(), osm.max()]
axes[1].plot(lim, lim, color=PALETTE[1], lw=1.5, label="傾き1の直線")
axes[1].set(title="正規 Q-Q プロット（残差 / s）", xlabel="標準正規分布の分位点", ylabel="標準化した残差の分位点")
axes[1].legend()
fig.tight_layout()
plt.show()

# %% 17-2
# てこ比: ハット行列 H = X (X^T X)^{-1} X^T の対角成分。QR 分解 X = QR なら H = Q Q^T
Xm17 = X17.to_numpy(float)
Q17, _ = np.linalg.qr(Xm17)
h17 = (Q17 ** 2).sum(axis=1)
infl17 = OLSInfluence(ols17)
print(f"sum h_ii = {h17.sum():.6f}（= p = {p17}）")
print("statsmodels との最大差:", np.abs(h17 - infl17.hat_matrix_diag).max())
print(f"平均 p/n = {p17 / n17:.4f}, 目安 2p/n = {2 * p17 / n17:.4f} を超える行: {(h17 > 2 * p17 / n17).sum()}")
lev_top = df.assign(てこ比=h17).nlargest(8, "てこ比")[["名前", *STATS, "経験値", "てこ比"]]
lev_top.round(3)

# %% 17-3
# スチューデント化残差
# 内部: r_i = e_i / (s sqrt(1 - h_ii))
# 外部: t_i = e_i / (s_(i) sqrt(1 - h_ii))。s_(i) は i を除いた推定。H0 のもと t_i ~ t(n - p - 1)
e17 = res17.to_numpy()
r_int = e17 / (s17 * np.sqrt(1 - h17))
s2_del = ((n17 - p17) * s17 ** 2 - e17 ** 2 / (1 - h17)) / (n17 - p17 - 1)
r_ext = e17 / np.sqrt(s2_del * (1 - h17))
print("内部スチューデント化残差 最大差:", np.abs(r_int - infl17.resid_studentized_internal).max())
print("外部スチューデント化残差 最大差:", np.abs(r_ext - infl17.resid_studentized_external).max())

# ボンフェローニ補正した外れ値検定（有意水準5%, n 回の検定）
crit17 = stats.t.ppf(1 - 0.05 / (2 * n17), n17 - p17 - 1)
print(f"|t_i| > 2 の行: {(np.abs(r_ext) > 2).sum()}（正規なら約 {0.0455 * n17:.0f} 行）")
print(f"ボンフェローニ補正の臨界値 {crit17:.2f} を超える行: {(np.abs(r_ext) > crit17).sum()}")
df.assign(外部スチューデント化残差=r_ext, てこ比=h17).loc[
    np.argsort(-np.abs(r_ext))[:8], ["名前", "合計種族値", "経験値", "外部スチューデント化残差", "てこ比"]].round(3)

# %% 17-4
# Cook の距離 D_i = sum_j (yhat_j - yhat_j(-i))^2 / (p s^2) = r_i^2 h_ii / (p (1 - h_ii))
cook17 = r_int ** 2 * h17 / (p17 * (1 - h17))
print("Cook の距離 最大差（公式 vs statsmodels）:", np.abs(cook17 - infl17.cooks_distance[0]).max())

# 最大の行について、実際に1行除いて再推定し、定義式で確認する
i_max = int(np.argmax(cook17))
keep = np.arange(n17) != i_max
b_del = np.linalg.lstsq(Xm17[keep], y17.to_numpy()[keep], rcond=None)[0]
D_def = ((fit17.to_numpy() - Xm17 @ b_del) ** 2).sum() / (p17 * s17 ** 2)
print(f"{df.loc[i_max, '名前']}: 定義式 {D_def:.4f}, 公式 {cook17[i_max]:.4f}")
print(f"目安 4/n = {4 / n17:.4f} を超える行: {(cook17 > 4 / n17).sum()}, D > 0.5 の行: {(cook17 > 0.5).sum()}")

cook_tab = df.assign(Cook=cook17, てこ比=h17, 外部スチューデント化残差=r_ext)
cook_top = cook_tab.nlargest(10, "Cook")[["名前", "HP", "防御", "合計種族値", "経験値", "てこ比", "外部スチューデント化残差", "Cook"]]

# 影響度プロット: てこ比 × スチューデント化残差、点の大きさ = Cook の距離
fig, ax = plt.subplots(figsize=(7.5, 4.8))
ax.scatter(h17, r_ext, s=10 + 400 * cook17 / cook17.max(), alpha=0.5, color=PALETTE[0],
           edgecolor=INK["surface"], linewidth=0.5)
ax.axvline(2 * p17 / n17, color=INK["muted"], lw=1, ls="--", label="てこ比の目安 2p/n")
ax.axhline(crit17, color=PALETTE[1], lw=1, ls=":", label="ボンフェローニ臨界値（±）")
ax.axhline(-crit17, color=PALETTE[1], lw=1, ls=":")
for i in cook_tab.nlargest(6, "Cook").index.union(cook_tab.nlargest(3, "てこ比").index):
    ax.annotate(df.loc[i, "名前"], (h17[i], r_ext[i]), xytext=(5, 3), textcoords="offset points",
                fontsize=8, color=INK["secondary"])
ax.set(title="影響度プロット（点の大きさ = Cook の距離）", xlabel="てこ比 h_ii", ylabel="外部スチューデント化残差")
ax.legend(loc="lower right")
plt.show()
cook_top.round(3)

# %% 17-5
# 変換前後の比較: 重さ ~ 高さ と log重さ ~ log高さ
fits_tr = {
    "重さ ~ 高さ": sm.OLS(df["重さ"], sm.add_constant(df["高さ"])).fit(),
    "log重さ ~ log高さ": sm.OLS(df["log重さ"], sm.add_constant(df["log高さ"])).fit(),
}
rows_tr = []
for name, m in fits_tr.items():
    im = OLSInfluence(m)
    lm, lm_p, _, _ = het_breuschpagan(m.resid, m.model.exog)
    rows_tr.append({"モデル": name, "R^2": m.rsquared, "残差の歪度": stats.skew(m.resid),
                    "残差の尖度(-3)": stats.kurtosis(m.resid), "BP統計量": lm, "BP p値": lm_p,
                    "Cook > 4/n の行": (im.cooks_distance[0] > 4 / n17).sum(),
                    "最大Cook": im.cooks_distance[0].max(),
                    "最大Cookの名前": df.loc[np.argmax(im.cooks_distance[0]), "名前"]})
print(pd.DataFrame(rows_tr).set_index("モデル").round(3).T.to_string())

fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
for row, (name, m) in enumerate(fits_tr.items()):
    ax = axes[row, 0]
    ax.scatter(m.fittedvalues, m.resid, s=8, alpha=0.4, color=PALETTE[0])
    ax.axhline(0, color=INK["axis"], lw=1)
    unit = "kg" if row == 0 else "log kg"
    ax.set(title=f"{name}：残差プロット", xlabel=f"予測値（{unit}）", ylabel=f"残差（{unit}）")
    ax = axes[row, 1]
    osm, osr = stats.probplot(m.resid / np.sqrt(m.mse_resid), dist="norm", fit=False)
    ax.scatter(osm, osr, s=8, alpha=0.4, color=PALETTE[0])
    ax.plot([osm.min(), osm.max()], [osm.min(), osm.max()], color=PALETTE[1], lw=1.5)
    ax.set(title=f"{name}：正規 Q-Q", xlabel="標準正規分布の分位点", ylabel="標準化した残差の分位点")
fig.tight_layout()
plt.show()

# %% 17-6
# 影響の大きい行（Cook > 4/n）を除いて再推定し、係数の変化を見る
out17 = cook17 > 4 / n17
print(f"除いた行: {out17.sum()}")
print("除いた行（Cook の大きい順）:", ", ".join(cook_tab.loc[out17].sort_values("Cook", ascending=False)["名前"]))
ols17_drop = sm.OLS(y17[~out17], X17[~out17]).fit()
ols17_nohappy = sm.OLS(y17[df["名前"] != "ハピナス"], X17[df["名前"] != "ハピナス"]).fit()
print(f"R^2: 全データ {ols17.rsquared:.3f} → ハピナス除外 {ols17_nohappy.rsquared:.3f} → Cook>4/n 除外 {ols17_drop.rsquared:.3f}")
pd.DataFrame({"全データ": ols17.params, "標準誤差": ols17.bse,
              "ハピナス除外": ols17_nohappy.params,
              "Cook>4/n 除外": ols17_drop.params, "標準誤差(除外後)": ols17_drop.bse}).round(3)
