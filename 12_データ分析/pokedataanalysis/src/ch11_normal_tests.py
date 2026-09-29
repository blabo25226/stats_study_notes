"""第11章 正規分布に関する検定."""
from poke import *

df = load_data()

# %% 11-0
# 使う群（タイプ1で分類）と列の要約
fire11 = df.loc[df["タイプ1"] == "ほのお", "合計種族値"].to_numpy(dtype=float)
water11 = df.loc[df["タイプ1"] == "みず", "合計種族値"].to_numpy(dtype=float)
elec_speed = df.loc[df["タイプ1"] == "でんき", "素早"].to_numpy(dtype=float)
diff_as = (df["攻撃"] - df["特攻"]).to_numpy(dtype=float)
summary11 = pd.DataFrame({
    "n": [len(fire11), len(water11), len(elec_speed), len(diff_as)],
    "平均": [fire11.mean(), water11.mean(), elec_speed.mean(), diff_as.mean()],
    "標準偏差(不偏)": [fire11.std(ddof=1), water11.std(ddof=1), elec_speed.std(ddof=1), diff_as.std(ddof=1)],
}, index=["ほのお 合計種族値", "みず 合計種族値", "でんき 素早", "全体 攻撃−特攻"])
print(f"全920行の素早の平均: {df['素早'].mean():.2f}")
summary11.round(2)

# %% 11-1
# 1標本 t 検定: でんき（タイプ1）の素早の平均は、全体平均 μ0 と等しいか
mu0_speed = df["素早"].mean()   # 基準値として固定する
n_e = len(elec_speed)
t_e = (elec_speed.mean() - mu0_speed) / (elec_speed.std(ddof=1) / np.sqrt(n_e))
p_e = 2 * stats.t.sf(abs(t_e), n_e - 1)
lib_e = stats.ttest_1samp(elec_speed, mu0_speed)
print(f"H0: μ = {mu0_speed:.2f}, n = {n_e}")
print(f"手計算: t = {t_e:.4f}, 自由度 {n_e - 1}, p値 = {p_e:.3g}")
print(f"scipy : t = {lib_e.statistic:.4f}, p値 = {lib_e.pvalue:.3g}")
print(f"棄却限界 t(0.025; {n_e - 1}) = {stats.t.ppf(0.975, n_e - 1):.3f} → 有意水準5%で",
      "H0 を棄却" if p_e < 0.05 else "H0 を棄却しない")

# %% 11-2
# 2標本 t 検定（等分散）と Welch の t 検定: ほのお vs みず の合計種族値
n1, n2 = len(fire11), len(water11)
v1, v2 = fire11.var(ddof=1), water11.var(ddof=1)
d12 = fire11.mean() - water11.mean()
# 等分散: プールした分散, 自由度 n1+n2-2
sp2 = ((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2)
t_pool = d12 / np.sqrt(sp2 * (1 / n1 + 1 / n2))
p_pool = 2 * stats.t.sf(abs(t_pool), n1 + n2 - 2)
# Welch: 自由度はサタスウェイトの近似
se_w = np.sqrt(v1 / n1 + v2 / n2)
nu_w = se_w**4 / ((v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1))
t_welch = d12 / se_w
p_welch = 2 * stats.t.sf(abs(t_welch), nu_w)
lib_pool = stats.ttest_ind(fire11, water11, equal_var=True)
lib_welch = stats.ttest_ind(fire11, water11, equal_var=False)
pd.DataFrame({
    "t（手計算）": [t_pool, t_welch], "自由度": [n1 + n2 - 2, nu_w], "p値（手計算）": [p_pool, p_welch],
    "t（scipy）": [lib_pool.statistic, lib_welch.statistic], "p値（scipy）": [lib_pool.pvalue, lib_welch.pvalue],
}, index=["等分散 t 検定", "Welch の t 検定"]).round(4)

# %% 11-3
# 対応のある t 検定: 同じポケモンの 攻撃 と 特攻 の差 D = 攻撃 − 特攻
n_d = len(diff_as)
t_pair = diff_as.mean() / (diff_as.std(ddof=1) / np.sqrt(n_d))
p_pair = 2 * stats.t.sf(abs(t_pair), n_d - 1)
lib_pair = stats.ttest_rel(df["攻撃"], df["特攻"])
lib_ind = stats.ttest_ind(df["攻撃"], df["特攻"])   # 対応を無視した場合（比較用）
print(f"D の平均 {diff_as.mean():.2f}, 標準偏差 {diff_as.std(ddof=1):.2f}, n = {n_d}")
print(f"対応あり 手計算: t = {t_pair:.4f}, 自由度 {n_d - 1}, p値 = {p_pair:.3g}")
print(f"対応あり scipy : t = {lib_pair.statistic:.4f}, p値 = {lib_pair.pvalue:.3g}")
print(f"対応を無視した2標本 t 検定: t = {lib_ind.statistic:.4f}, p値 = {lib_ind.pvalue:.3g}")
print(f"攻撃と特攻の相関係数: {df['攻撃'].corr(df['特攻']):.3f}")

# %% 11-4
# 1標本の分散の χ² 検定: みずの合計種族値の母分散は σ0² = 全920行の分散 と等しいか
sigma0_sq = df["合計種族値"].var(ddof=0)   # 基準値として固定する
chi2_w = (n2 - 1) * v2 / sigma0_sq
# 両側 p値: 小さい側の裾確率の2倍
p_chi2 = 2 * min(stats.chi2.cdf(chi2_w, n2 - 1), stats.chi2.sf(chi2_w, n2 - 1))
print(f"H0: σ² = {sigma0_sq:.1f}（σ = {np.sqrt(sigma0_sq):.1f}）, 不偏分散 {v2:.1f}, n = {n2}")
print(f"χ² = (n-1)s²/σ0² = {chi2_w:.3f}, 自由度 {n2 - 1}")
print(f"棄却域: χ² < {stats.chi2.ppf(0.025, n2 - 1):.2f} または χ² > {stats.chi2.ppf(0.975, n2 - 1):.2f}（有意水準5%）")
print(f"両側 p値 = {p_chi2:.4f}")

# %% 11-5
# 等分散の F 検定: ほのお と みず の合計種族値の分散
f_stat = v1 / v2
p_f = 2 * min(stats.f.cdf(f_stat, n1 - 1, n2 - 1), stats.f.sf(f_stat, n1 - 1, n2 - 1))
print(f"F = s1²/s2² = {f_stat:.4f}, 自由度 ({n1 - 1}, {n2 - 1}), 両側 p値 = {p_f:.4f}")
print(f"棄却域: F < {stats.f.ppf(0.025, n1 - 1, n2 - 1):.3f} または F > {stats.f.ppf(0.975, n1 - 1, n2 - 1):.3f}")
# 参考: 正規性に頑健な Levene 検定（中央値版 = Brown-Forsythe）
lev = stats.levene(fire11, water11, center="median")
print(f"参考 Levene（中央値）: W = {lev.statistic:.4f}, p値 = {lev.pvalue:.4f}")

# %% 11-6
# 正規性の確認: Q-Q プロットと Shapiro-Wilk 検定
targets11 = {"ほのお 合計種族値": fire11, "みず 合計種族値": water11,
             "でんき 素早": elec_speed, "全体 攻撃−特攻": diff_as,
             "全体 合計種族値": df["合計種族値"].to_numpy(dtype=float)}
rows_sw = []
for name, x in targets11.items():
    sw = stats.shapiro(x)
    rows_sw.append({"対象": name, "n": len(x), "歪度": stats.skew(x), "尖度(-3)": stats.kurtosis(x),
                    "W": sw.statistic, "p値": sw.pvalue})
print(pd.DataFrame(rows_sw).round(4).to_string(index=False))

fig, axes = plt.subplots(1, 3, figsize=(12, 4))
for ax, name in zip(axes, ["ほのお 合計種族値", "みず 合計種族値", "全体 攻撃−特攻"]):
    x = np.sort(targets11[name])
    q = stats.norm.ppf((np.arange(1, len(x) + 1) - 0.5) / len(x))   # 理論分位点
    ax.scatter(q, x, s=8, color=PALETTE[0])
    ax.plot(q, x.mean() + x.std(ddof=1) * q, color=INK["muted"], linewidth=1, label="正規分布なら乗る直線")
    ax.set(title=f"{name}（n={len(x)}）", xlabel="標準正規分布の分位点", ylabel="観測値")
axes[0].legend(loc="upper left", fontsize=9)
fig.suptitle("正規 Q-Q プロット", fontsize=12, fontweight="bold")
fig.tight_layout()
plt.show()
