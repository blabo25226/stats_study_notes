"""第12章 一般の分布に関する検定法."""
from poke import *

df = load_data()

# %% 12-0
# 使う列: 複合タイプ・世代・タイプ・努力値合計・is_mega
dragon12 = types_of(df, "ドラゴン")
print("世代ごとの行数・複合タイプ数・ドラゴンを含む数")
by_gen12 = pd.DataFrame({
    "行数": df.groupby("世代").size(),
    "複合タイプ": df.groupby("世代")["複合タイプ"].sum(),
    "ドラゴンを含む": dragon12.groupby(df["世代"]).sum(),
})
by_gen12["複合タイプの割合"] = (by_gen12["複合タイプ"] / by_gen12["行数"]).round(3)
print(by_gen12.to_string())
print("\n努力値合計の度数:", df["努力値合計"].value_counts().sort_index().to_dict())

# %% 12-1
# 母比率の検定: 複合タイプの割合は 1/2 か（全920行）
x_dual, n_dual = int(df["複合タイプ"].sum()), len(df)
p0_dual = 0.5
z_dual = (x_dual - n_dual * p0_dual) / np.sqrt(n_dual * p0_dual * (1 - p0_dual))
p_z_dual = 2 * stats.norm.sf(abs(z_dual))
p_exact_dual = stats.binomtest(x_dual, n_dual, p0_dual).pvalue
print(f"複合タイプ {x_dual}/{n_dual} = {x_dual / n_dual:.4f}")
print(f"正規近似: z = {z_dual:.4f}, 両側 p値 = {p_z_dual:.4f} / 二項分布の正確な p値 = {p_exact_dual:.4f}")

# 母比率の差の検定: 複合タイプの割合は 第1世代 と 第7世代 で等しいか（プールした比率を使う）
g1 = df.loc[df["世代"] == 1, "複合タイプ"]
g7 = df.loc[df["世代"] == 7, "複合タイプ"]
x1, m1, x7, m7 = int(g1.sum()), len(g1), int(g7.sum()), len(g7)
p_pool = (x1 + x7) / (m1 + m7)
z_diff = (x7 / m7 - x1 / m1) / np.sqrt(p_pool * (1 - p_pool) * (1 / m1 + 1 / m7))
p_diff = 2 * stats.norm.sf(abs(z_diff))
tab17 = np.array([[x1, m1 - x1], [x7, m7 - x7]])
chi2_17 = stats.chi2_contingency(tab17, correction=False)
print(f"\n第1世代 {x1}/{m1} = {x1 / m1:.3f}, 第7世代 {x7}/{m7} = {x7 / m7:.3f}, プール {p_pool:.3f}")
print(f"z = {z_diff:.4f}, 両側 p値 = {p_diff:.4f}")
print(f"2×2 分割表の χ²（補正なし）= {chi2_17.statistic:.4f} = z² = {z_diff**2:.4f}, p値 = {chi2_17.pvalue:.4f}")

# %% 12-2
# ポアソン分布に関する検定（少数の法則）: 各世代のドラゴンを含む数 X は、他の世代の割合から期待される数より多いか
# 他の世代の割合 p を既知とみなすと X ~ Bin(n, p) ≈ Po(λ0 = n p)（p が小さいため）
def two_sided(dist, x):
    """離散分布の両側 p値: 小さい側の裾確率の2倍（1で打ち切る）."""
    return min(1.0, 2 * min(dist.cdf(x), dist.sf(x - 1)))


rows_po = []
for g, row in by_gen12.iterrows():
    others = by_gen12.drop(index=g)
    p_other = others["ドラゴンを含む"].sum() / others["行数"].sum()
    lam0 = row["行数"] * p_other
    x_obs = row["ドラゴンを含む"]
    rows_po.append({
        "世代": g, "n": row["行数"], "観測 X": x_obs, "λ0": lam0,
        "z": (x_obs - lam0) / np.sqrt(lam0),
        "p値（正規近似・両側）": 2 * stats.norm.sf(abs((x_obs - lam0) / np.sqrt(lam0))),
        "p値（ポアソン・両側）": two_sided(stats.poisson(lam0), x_obs),
        "p値（二項・両側）": two_sided(stats.binom(row["行数"], p_other), x_obs),
    })
po_table = pd.DataFrame(rows_po).set_index("世代")
print("有意水準5%, 7世代を調べるので Bonferroni 補正なら 0.05/7 =", round(0.05 / 7, 4))
po_table.round(4)

# %% 12-3
# 適合度 χ² 検定
def pearson_gof(obs, expected):
    """Pearson の適合度統計量 Σ (O - E)² / E."""
    obs, expected = np.asarray(obs, float), np.asarray(expected, float)
    return ((obs - expected) ** 2 / expected).sum()


# (a) タイプ1の18種類は同じ割合か（k = 18, 自由度 17）
obs_t1 = df["タイプ1"].value_counts().to_numpy()
e_t1 = np.full(len(obs_t1), len(df) / len(obs_t1))
chi_t1 = pearson_gof(obs_t1, e_t1)
print(f"(a) タイプ1一様: χ² = {chi_t1:.2f}, 自由度 {len(obs_t1) - 1}, p値 = {stats.chi2.sf(chi_t1, len(obs_t1) - 1):.2e}",
      f"（期待度数 {e_t1[0]:.1f}）")

# (b) 努力値合計 1, 2, 3 は同じ割合か（k = 3, 自由度 2）
obs_ev = df["努力値合計"].value_counts().sort_index().to_numpy()
e_ev_uni = np.full(3, len(df) / 3)
chi_ev_uni = pearson_gof(obs_ev, e_ev_uni)
print(f"(b) 努力値合計一様: χ² = {chi_ev_uni:.2f}, 自由度 2, p値 = {stats.chi2.sf(chi_ev_uni, 2):.2e}")

# (c) 努力値合計 − 1 が二項分布 Bin(2, p) にしたがうか（p を最尤推定するので自由度 k − ℓ − 1 = 3 − 1 − 1 = 1）
y_ev = df["努力値合計"] - 1
p_hat_ev = y_ev.mean() / 2                       # Bin(2, p) の p の最尤推定量 = 標本平均 / 2
e_ev_bin = len(df) * stats.binom.pmf([0, 1, 2], 2, p_hat_ev)
chi_ev_bin = pearson_gof(obs_ev, e_ev_bin)
lib_ev_bin = stats.chisquare(obs_ev, e_ev_bin, ddof=1)
print(f"(c) Bin(2, p) 当てはめ: p̂ = {p_hat_ev:.4f}, 期待度数 {np.round(e_ev_bin, 1)}")
print(f"    χ² = {chi_ev_bin:.2f}, 自由度 1, p値 = {stats.chi2.sf(chi_ev_bin, 1):.2e}",
      f"（scipy ddof=1: {lib_ev_bin.statistic:.2f}, {lib_ev_bin.pvalue:.2e}）")
print(f"    誤って自由度 2 とした場合の p値 = {stats.chi2.sf(chi_ev_bin, 2):.2e}")

fig, ax = plt.subplots(figsize=(6.5, 4))
xpos = np.arange(3)
w = 0.27
ax.bar(xpos - w, obs_ev, width=w, color=PALETTE[0], label="観測度数")
ax.bar(xpos, e_ev_uni, width=w, color=PALETTE[1], label="一様分布の期待度数")
ax.bar(xpos + w, e_ev_bin, width=w, color=PALETTE[2], label=f"二項分布 Bin(2, {p_hat_ev:.3f}) の期待度数")
ax.set_xticks(xpos, ["1", "2", "3"])
ax.set(title="努力値合計の観測度数と期待度数", xlabel="努力値合計（ポイント）", ylabel="匹数", ylim=(0, 620))
ax.legend(loc="upper left", fontsize=9)
fig.tight_layout()
plt.show()

# %% 12-4
# イエーツの補正: 度数の小さい 2×2 分割表（ドラゴンを含むか × メガシンカか）
tab_dm = pd.crosstab(dragon12.rename("ドラゴンを含む"), df["is_mega"].rename("メガシンカ・ゲンシ"))
print(tab_dm)
a, b, c, d = tab_dm.to_numpy().ravel()
n_dm = a + b + c + d
den = (a + b) * (c + d) * (a + c) * (b + d)
chi_raw = n_dm * (a * d - b * c) ** 2 / den
chi_yates = n_dm * (abs(a * d - b * c) - n_dm / 2) ** 2 / den
lib_raw = stats.chi2_contingency(tab_dm, correction=False)
lib_yates = stats.chi2_contingency(tab_dm, correction=True)
fisher = stats.fisher_exact(tab_dm)
print(f"\n期待度数の最小値: {lib_raw.expected_freq.min():.2f}")
pd.DataFrame({
    "χ²（手計算）": [chi_raw, chi_yates, np.nan],
    "χ²（scipy）": [lib_raw.statistic, lib_yates.statistic, np.nan],
    "p値": [lib_raw.pvalue, lib_yates.pvalue, fisher.pvalue],
}, index=["Pearson（補正なし）", "イエーツの補正", "Fisher の正確検定"]).round(4)

# %% 12-5
# 尤度比検定: 複合タイプの割合は 7つの世代で等しいか（各世代 X_g ~ Bin(n_g, p_g), H0: p_1 = … = p_7）
x_g = by_gen12["複合タイプ"].to_numpy(float)
n_g = by_gen12["行数"].to_numpy(float)


def binom_loglik(x, n, p):
    """二項分布の対数尤度（二項係数は H0/H1 で共通なので省く）."""
    return (x * np.log(p) + (n - x) * np.log(1 - p)).sum()


p_hat_g = x_g / n_g                       # H1（制約なし）の最尤推定値
p_hat_0 = x_g.sum() / n_g.sum()           # H0（共通の p）の最尤推定値
lr_stat = 2 * (binom_loglik(x_g, n_g, p_hat_g) - binom_loglik(x_g, n_g, p_hat_0))
df_lr = len(x_g) - 1                      # パラメータ数 7 − 1
tab_gen = np.column_stack([x_g, n_g - x_g])
lib_g = stats.chi2_contingency(tab_gen, lambda_="log-likelihood")
lib_p = stats.chi2_contingency(tab_gen)
print(f"共通の p̂ = {p_hat_0:.4f}, 世代ごとの p̂ = {np.round(p_hat_g, 3)}")
print(f"2 log λ = {lr_stat:.4f}（scipy G 統計量 {lib_g.statistic:.4f}）, 自由度 {df_lr}, p値 = {stats.chi2.sf(lr_stat, df_lr):.4f}")
print(f"Pearson χ² = {lib_p.statistic:.4f}, 自由度 {lib_p.dof}, p値 = {lib_p.pvalue:.4f}")
print(f"χ²(0.05; {df_lr}) = {stats.chi2.ppf(0.95, df_lr):.3f}")

fig, ax = plt.subplots(figsize=(6.5, 4))
se_g = np.sqrt(p_hat_g * (1 - p_hat_g) / n_g)
ax.errorbar(by_gen12.index, p_hat_g, yerr=1.96 * se_g, fmt="o", color=PALETTE[0], capsize=3,
            label="世代ごとの割合（±1.96 SE）")
ax.axhline(p_hat_0, color=INK["muted"], linestyle="--", linewidth=1, label=f"H0 の共通の割合 {p_hat_0:.3f}")
ax.set(title="世代ごとの複合タイプの割合", xlabel="世代", ylabel="複合タイプの割合")
ax.legend(loc="upper left", fontsize=9)
fig.tight_layout()
plt.show()
