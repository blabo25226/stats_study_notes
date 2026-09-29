"""第10章 検定の基礎と検定法の導出."""
from poke import *

df = load_data()

# %% 10-0
# 使う列: 合計種族値（全体・ドラゴン）、雄率（性別比の種類）
total_all = df["合計種族値"].to_numpy()
mu0_all, sigma_all = total_all.mean(), total_all.std(ddof=0)   # 全920行を母集団とみたときの母平均・母標準偏差
dragon_any = df.loc[types_of(df, "ドラゴン"), "合計種族値"].to_numpy()
dragon_t1 = df.loc[df["タイプ1"] == "ドラゴン", "合計種族値"].to_numpy()
print(f"全920行: 平均 {mu0_all:.1f}, 標準偏差(n割) {sigma_all:.1f}")
print(f"ドラゴンを含む（{len(dragon_any)}匹）: 平均 {dragon_any.mean():.1f}, 標準偏差(n割) {dragon_any.std():.1f}")
print(f"タイプ1がドラゴン（{len(dragon_t1)}匹）: 平均 {dragon_t1.mean():.1f}")
print("\n雄率ごとの行数（NaN は性別不明）")
print(df["雄率"].value_counts(dropna=False).sort_index().to_string())

# %% 10-1
# 仮説・棄却域・p値: タイプ1がドラゴンの合計種族値の平均は μ0 = 全体平均 と等しいか（σ は既知とする）
alpha = 0.05
n_d = len(dragon_t1)
z_obs = (dragon_t1.mean() - mu0_all) / (sigma_all / np.sqrt(n_d))
z_crit = stats.norm.ppf(1 - alpha / 2)
p_two = 2 * stats.norm.sf(abs(z_obs))
print(f"H0: μ = {mu0_all:.1f}  H1: μ ≠ {mu0_all:.1f}  σ = {sigma_all:.1f}（既知とする）, n = {n_d}")
print(f"z = {z_obs:.3f}, 棄却域 |z| > {z_crit:.3f}（有意水準5%）, p値 = {p_two:.2e}")
print("判定:", "H0 を棄却" if p_two < alpha else "H0 を棄却しない")

zz = np.linspace(-6, 6, 600)
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.plot(zz, stats.norm.pdf(zz), color=PALETTE[0], label="H0 のもとでの z の分布 N(0,1)")
for side in [zz > z_crit, zz < -z_crit]:
    ax.fill_between(zz[side], stats.norm.pdf(zz[side]), color=PALETTE[1], alpha=0.5)
ax.fill_between([], [], color=PALETTE[1], alpha=0.5, label="棄却域（両側で5%）")
ax.axvline(z_obs, color=INK["primary"], linewidth=1.2, label=f"観測値 z = {z_obs:.2f}")
ax.set(title="両側 z 検定の棄却域と観測値", xlabel="検定統計量 z", ylabel="確率密度")
ax.legend(loc="upper left", fontsize=9)
fig.tight_layout()
plt.show()

# %% 10-2
# 検出力関数と必要サンプルサイズ（片側 z 検定 H0: μ = μ0, H1: μ > μ0）
z_a = stats.norm.ppf(1 - alpha)


def power_z(mu1, n, mu0=mu0_all, sigma0=sigma_all, sigma1=None):
    """棄却域 xbar > μ0 + z_α σ0/√n のもとで、真の平均が mu1（標準偏差 sigma1）のときの検出力."""
    sigma1 = sigma0 if sigma1 is None else sigma1
    crit = mu0 + z_a * sigma0 / np.sqrt(n)
    return stats.norm.sf((crit - mu1) / (sigma1 / np.sqrt(n)))


mus = np.linspace(mu0_all - 50, mu0_all + 200, 300)
fig, ax = plt.subplots(figsize=(7, 4.2))
for i, n in enumerate([5, 10, 20, 40]):
    ax.plot(mus, power_z(mus, n), color=PALETTE[i], label=f"n = {n}")
ax.axhline(alpha, color=INK["muted"], linestyle="--", linewidth=1)
ax.axvline(mu0_all, color=INK["muted"], linestyle=":", linewidth=1)
ax.set(title="片側 z 検定の検出力関数（α = 5%, σ = 120.3）", xlabel="真の母平均 μ（合計種族値）",
       ylabel="H0 を棄却する確率")
ax.legend(title="標本の大きさ")
fig.tight_layout()
plt.show()

# 必要サンプルサイズ: n = {(z_α + z_β) σ / δ}²
beta = 0.2
z_b = stats.norm.ppf(1 - beta)
delta_d = dragon_any.mean() - mu0_all
n_req_mean = ((z_a + z_b) * sigma_all / delta_d) ** 2
print(f"平均: δ = {delta_d:.1f}, 効果量 δ/σ = {delta_d / sigma_all:.3f}, 必要な n = {n_req_mean:.2f} → {int(np.ceil(n_req_mean))}")

# 比率: H0: p = p0, H1: p = p1（いわを含む割合 0.075 が 0.15 に増えたことを検出したい）
p0, p1 = types_of(df, "いわ").mean(), 0.15
n_req_prop = ((z_a * np.sqrt(p0 * (1 - p0)) + z_b * np.sqrt(p1 * (1 - p1))) / (p1 - p0)) ** 2
print(f"比率: p0 = {p0:.3f}, p1 = {p1}, 必要な n = {n_req_prop:.1f} → {int(np.ceil(n_req_prop))}")

# %% 10-3
# 抽出シミュレーション: 全体から抽出（H0 が正しい）/ ドラゴンを含む群から抽出（H1 が正しい）
rng = get_rng()
reps = 5000
rows_pw = []
for n in [5, int(np.ceil(n_req_mean)), 15, 25]:
    xb0 = rng.choice(total_all, size=(reps, n), replace=True).mean(axis=1)
    xb1 = rng.choice(dragon_any, size=(reps, n), replace=True).mean(axis=1)
    crit = mu0_all + z_a * sigma_all / np.sqrt(n)
    rows_pw.append({
        "n": n,
        "第1種の過誤率（シミュ）": np.mean(xb0 > crit),
        "検出力（シミュ）": np.mean(xb1 > crit),
        "検出力（式, σ1=σ0）": power_z(dragon_any.mean(), n),
        "検出力（式, σ1=ドラゴンのσ）": power_z(dragon_any.mean(), n, sigma1=dragon_any.std()),
    })
print(f"{reps}回の復元抽出, 片側有意水準5%")
pd.DataFrame(rows_pw).round(3)

# %% 10-4
# 生産者危険・消費者危険と OC 曲線
# 設定: 雄率 1/2 の種（合格 = H0）か雄率 7/8 の種（不合格 = H1）かを、タマゴ n 個中のオスの数 X で判定する
#       X ≥ c なら「7/8 の種」と判定（H0 を棄却）
pm0, pm1 = 0.5, 0.875
n_egg = 20
rows_oc = []
for c in range(12, 19):
    rows_oc.append({"c": c,
                    "生産者危険 P(X≥c | 1/2)": stats.binom.sf(c - 1, n_egg, pm0),
                    "消費者危険 P(X≤c-1 | 7/8)": stats.binom.cdf(c - 1, n_egg, pm1)})
print(f"n = {n_egg} 個のタマゴ, 判定基準 c ごとの2つの危険")
print(pd.DataFrame(rows_oc).round(4).to_string(index=False))

# OC 曲線 L(p) = P(H0 を受容 | p) = P(X ≤ c-1 | p)
pp = np.linspace(0, 1, 201)
fig, ax = plt.subplots(figsize=(7, 4.2))
for i, (n, c) in enumerate([(20, 15), (20, 13), (40, 27)]):
    ax.plot(pp, stats.binom.cdf(c - 1, n, pp), color=PALETTE[i], label=f"n = {n}, X が {c} 以上で棄却")
for pv in [pm0, pm1]:
    ax.axvline(pv, color=INK["muted"], linestyle=":", linewidth=1)
ax.set(title="OC 曲線（H0: 雄率 1/2 を受容する確率）", xlabel="真の雄率 p", ylabel="H0 を受容する確率")
ax.legend()
fig.tight_layout()
plt.show()
for n, c in [(20, 15), (20, 13), (40, 27)]:
    print(f"n={n}, c={c}: 生産者危険 {stats.binom.sf(c - 1, n, pm0):.4f}, 消費者危険 {stats.binom.cdf(c - 1, n, pm1):.4f}")

# %% 10-5
# ネイマン・ピアソンの補題: 尤度比の大きい x から棄却域に入れる検定が最強力
x_vals = np.arange(n_egg + 1)
f0 = stats.binom.pmf(x_vals, n_egg, pm0)
f1 = stats.binom.pmf(x_vals, n_egg, pm1)
lr = f1 / f0
print("尤度比 f1(x)/f0(x) は x の単調増加関数:", bool(np.all(np.diff(lr) > 0)))

# 尤度比検定（X ≥ k）の (有意水準, 検出力) と、ランダムに作った棄却域の (有意水準, 検出力)
np_size = np.array([f0[x_vals >= k].sum() for k in range(n_egg + 2)])
np_power = np.array([f1[x_vals >= k].sum() for k in range(n_egg + 2)])
rng = get_rng()
regions = rng.random((20000, n_egg + 1)) < rng.random((20000, 1))   # 各 x を確率 q で棄却域に入れる
rand_size, rand_power = regions @ f0, regions @ f1

# 有意水準 5% ちょうどの確率化検定（X ≥ 15 で棄却、X = 14 のとき確率 γ で棄却）
k_np = 15
gamma = (alpha - f0[x_vals >= k_np].sum()) / f0[k_np - 1]
power_np = f1[x_vals >= k_np].sum() + gamma * f1[k_np - 1]
best_rand = rand_power[rand_size <= alpha].max()
print(f"X≥15 の有意水準 {np_size[k_np]:.4f}, 検出力 {np_power[k_np]:.4f}")
print(f"確率化検定（γ = {gamma:.3f}）: 有意水準 {alpha}, 検出力 {power_np:.4f}")
print(f"ランダムな棄却域のうち有意水準 5% 以下で最大の検出力: {best_rand:.4f}")

fig, ax = plt.subplots(figsize=(6.5, 5))
ax.scatter(rand_size, rand_power, s=2, color=PALETTE[0], alpha=0.15, label="ランダムに作った棄却域")
ax.plot(np_size, np_power, "o-", color=PALETTE[1], markersize=3, label="尤度比検定: X が k 以上で棄却（点の間は確率化）")
ax.axvline(alpha, color=INK["muted"], linestyle="--", linewidth=1)
ax.set(title="棄却域ごとの有意水準と検出力（n = 20）", xlabel="有意水準 P(棄却 | p = 1/2)",
       ylabel="検出力 P(棄却 | p = 7/8)")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=9, markerscale=2)
fig.tight_layout()
plt.show()

# %% 10-6
# p値の分布: H0 が正しいと一様分布 U(0,1) になる
rng = get_rng()
n_p = 20
samp0 = rng.choice(total_all, size=(reps, n_p), replace=True)      # H0 が正しい（全体から抽出）
samp1 = rng.choice(dragon_any, size=(reps, n_p), replace=True)     # H1 が正しい（ドラゴンを含む群から抽出）
pv0 = stats.ttest_1samp(samp0, mu0_all, axis=1).pvalue
pv1 = stats.ttest_1samp(samp1, mu0_all, axis=1).pvalue
print(f"H0 のもと: P(p ≤ 0.05) = {np.mean(pv0 <= 0.05):.3f}, P(p ≤ 0.5) = {np.mean(pv0 <= 0.5):.3f}")
ks = stats.kstest(pv0, "uniform")
print(f"一様分布への KS 検定: D = {ks.statistic:.4f}, p値 = {ks.pvalue:.3f}")
print(f"H1 のもと: P(p ≤ 0.05) = {np.mean(pv1 <= 0.05):.3f}（検出力）")

# 離散分布の検定では p値は一様にならない（二項検定 H0: p = 1/2, n = 20, 片側）
pv_binom = stats.binom.sf(x_vals - 1, n_egg, pm0)          # 観測値 x の p値 P(X ≥ x)
print(f"二項検定: P(p値 ≤ 0.05 | H0) = {f0[pv_binom <= 0.05].sum():.4f}（0.05 より小さい）")

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
bins = np.linspace(0, 1, 21)
axes[0].hist(pv0, bins=bins, color=PALETTE[0])
axes[0].axhline(reps / 20, color=INK["muted"], linestyle="--", linewidth=1, label="一様分布の期待度数")
axes[0].set(title="H0 が正しい（全体から抽出）", xlabel="p値", ylabel="回数")
axes[0].set_ylim(0, reps / 20 * 1.4)
axes[0].legend(loc="upper right", fontsize=9)
axes[1].hist(pv1, bins=bins, color=PALETTE[1])
axes[1].set(title="H1 が正しい（ドラゴンを含む群から抽出）", xlabel="p値", ylabel="回数")
fig.suptitle(f"1標本 t 検定の p値の分布（n = {n_p}, {reps}回）", fontsize=12, fontweight="bold")
fig.tight_layout()
plt.show()
