"""第07章 極限定理・漸近理論."""
from poke import *

df = load_data()

# %% 07-0
# 母集団（全920行）の真値。以降は行を復元抽出して i.i.d. 標本を作る
wt07 = df["重さ"].to_numpy(float)
bst07 = df["合計種族値"].to_numpy(float)
water07 = (df["タイプ1"] == "みず").to_numpy()
pop07 = pd.DataFrame({
    "母平均 μ": [wt07.mean(), bst07.mean(), water07.mean()],
    "母標準偏差 σ": [wt07.std(), bst07.std(), water07.std()],
    "歪度": [stats.skew(wt07), stats.skew(bst07), stats.skew(water07)],
    "尖度(-3)": [stats.kurtosis(wt07), stats.kurtosis(bst07), stats.kurtosis(water07)],
}, index=["重さ (kg)", "合計種族値", "タイプ1がみず (0/1)"])


def sample_means_07(values, n, reps, rng):
    """母集団 values から大きさ n の標本を reps 組復元抽出し、(標本平均, 不偏標準偏差) を返す."""
    smp = values[rng.integers(0, len(values), size=(reps, n))]
    return smp.mean(axis=1), smp.std(axis=1, ddof=1)

pop07.round(3)

# %% 07-1
# 大数の弱法則: 重さの標本平均が母平均に近づく
rng = get_rng()
mu_w, sd_w = wt07.mean(), wt07.std()
n_max = 3000
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
for j in range(3):                                       # 3本の独立な標本経路
    path = wt07[rng.integers(0, len(wt07), n_max)]
    axes[0].plot(np.arange(1, n_max + 1), np.cumsum(path) / np.arange(1, n_max + 1),
                 lw=1.2, color=PALETTE[j], label=f"経路 {j + 1}")
axes[0].axhline(mu_w, color=INK["primary"], lw=1, ls="--", label=f"母平均 μ = {mu_w:.1f}")
axes[0].set(xscale="log", title="重さの標本平均の経路", xlabel="標本の大きさ n（対数軸）", ylabel="標本平均 (kg)")
axes[0].legend(fontsize=8)

# P(|X̄ - μ| > ε) とチェビシェフの不等式の上界 σ²/(nε²)
eps = 20.0
rows_lln = []
for n in [10, 30, 100, 300, 1000]:
    xbar, _ = sample_means_07(wt07, n, 2000, rng)
    rows_lln.append({"n": n, "P(|X̄-μ|>ε) シミュ": (np.abs(xbar - mu_w) > eps).mean(),
                     "チェビシェフの上界": min(1.0, sd_w**2 / (n * eps**2)), "X̄ の標準偏差": xbar.std(),
                     "理論 σ/√n": sd_w / np.sqrt(n)})
tab_lln = pd.DataFrame(rows_lln)
axes[1].plot(tab_lln["n"], tab_lln["P(|X̄-μ|>ε) シミュ"], "o-", color=PALETTE[0], label="シミュレーション")
axes[1].plot(tab_lln["n"], tab_lln["チェビシェフの上界"], "s--", color=PALETTE[1], label="チェビシェフの上界 σ²/(nε²)")
axes[1].set(xscale="log", title=f"標本平均が μ から {eps:.0f} kg 以上離れる確率", xlabel="標本の大きさ n（対数軸）", ylabel="確率")
axes[1].legend(fontsize=8)
fig.tight_layout()
plt.show()
tab_lln.round(4)

# %% 07-2
# 中心極限定理: 歪んだ母集団（重さ）の標本平均を標準化した Z = (X̄ - μ)/(σ/√n)
rng = get_rng()
gamma_w = stats.skew(wt07)
fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
g = np.linspace(-4, 6, 300)
rows_clt = []
for ax, n in zip(axes, [5, 30, 100]):
    xbar, _ = sample_means_07(wt07, n, 5000, rng)
    z = (xbar - mu_w) / (sd_w / np.sqrt(n))
    rows_clt.append({"n": n, "Z の歪度（シミュ）": stats.skew(z), "理論 γ/√n": gamma_w / np.sqrt(n),
                     "KS距離 vs N(0,1)": stats.kstest(z, "norm").statistic,
                     "P(Z > 1.645)": (z > 1.645).mean(), "P(Z < -1.645)": (z < -1.645).mean()})
    ax.hist(z[(z > -4) & (z < 6)], bins=60, density=True, color=PALETTE[0], label="シミュレーション")
    ax.plot(g, stats.norm.pdf(g), color=PALETTE[1], label="N(0, 1)")
    ax.set(title=f"n = {n}", xlabel="標準化した標本平均 Z", ylabel="密度")
axes[0].legend(fontsize=8)
fig.suptitle("重さの標本平均の分布と正規近似", fontsize=12, fontweight="bold")
fig.tight_layout()
plt.show()
print(f"母集団（重さ）の歪度 γ = {gamma_w:.2f}。正規近似なら P(Z > 1.645) = P(Z < -1.645) = 0.05")
pd.DataFrame(rows_clt).round(4)

# %% 07-3
# 連続修正: X ~ Bin(n, p) を N(np, np(1-p)) で近似するとき、区間の端を 0.5 ずつ広げる
# 例: 捕獲率45のポケモンに30回ボールを投げたときの成功回数（簡略化モデル: p = 45/255 と仮定）
n_b, p_b = 30, 45 / 255
m_b, s_b = n_b * p_b, np.sqrt(n_b * p_b * (1 - p_b))
print(f"Bin({n_b}, {p_b:.4f}): 平均 np = {m_b:.2f}, 標準偏差 √(np(1-p)) = {s_b:.2f}")
rows_cc = []
for a, b in [(0, 3), (4, 7), (5, 5), (8, 30), (3, 8)]:
    exact = stats.binom.cdf(b, n_b, p_b) - stats.binom.cdf(a - 1, n_b, p_b)
    no_cc = stats.norm.cdf(b, m_b, s_b) - stats.norm.cdf(a, m_b, s_b)
    with_cc = stats.norm.cdf(b + 0.5, m_b, s_b) - stats.norm.cdf(a - 0.5, m_b, s_b)
    rows_cc.append({"事象": f"{a} ≤ X ≤ {b}", "正確（二項）": exact, "正規近似（修正なし）": no_cc, "正規近似（連続修正）": with_cc})
tab_cc = pd.DataFrame(rows_cc).set_index("事象")

# P(X ≤ k) の近似誤差を k ごとに比べる
k = np.arange(0, 16)
err_no = stats.norm.cdf(k, m_b, s_b) - stats.binom.cdf(k, n_b, p_b)
err_cc = stats.norm.cdf(k + 0.5, m_b, s_b) - stats.binom.cdf(k, n_b, p_b)
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.axhline(0, color=INK["axis"], lw=1)
ax.plot(k, err_no, "o-", color=PALETTE[0], label="修正なし Φ((k - np)/σ)")
ax.plot(k, err_cc, "s-", color=PALETTE[1], label="連続修正 Φ((k + 0.5 - np)/σ)")
ax.set(title="累積確率 P(X が k 以下) の正規近似の誤差（Bin(30, 45/255)）", xlabel="k（成功回数）", ylabel="近似値 − 正確な値")
ax.legend()
plt.show()
print(f"最大絶対誤差: 修正なし {np.abs(err_no).max():.4f}  連続修正 {np.abs(err_cc).max():.4f}")
tab_cc.round(4)

# %% 07-4
# スルツキーの補題: σ を標本標準偏差 S に置き換えた T = √n (X̄ - μ)/S も N(0,1) に分布収束する
rng = get_rng()
rows_sl = []
for n in [10, 30, 100, 500]:
    xbar, s = sample_means_07(wt07, n, 5000, rng)
    z_known = np.sqrt(n) * (xbar - mu_w) / sd_w             # σ 既知
    t_plug = np.sqrt(n) * (xbar - mu_w) / s                # σ を S で置き換え
    rows_sl.append({"n": n, "S/σ の平均": (s / sd_w).mean(), "|S/σ - 1| > 0.1 の割合": (np.abs(s / sd_w - 1) > 0.1).mean(),
                    "Z: P(<-1.96)": (z_known < -1.96).mean(), "Z: P(>1.96)": (z_known > 1.96).mean(),
                    "T: P(<-1.96)": (t_plug < -1.96).mean(), "T: P(>1.96)": (t_plug > 1.96).mean()})
print("N(0,1) なら各側 0.025")
pd.DataFrame(rows_sl).round(3)

# %% 07-5
# 連続写像定理: Z_n → N(0,1) なら h(Z_n) = Z_n² → χ²(1)
rng = get_rng()
c95 = stats.chi2.ppf(0.95, 1)
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
g = np.linspace(0.02, 8, 300)
for ax, (name, pop, n) in zip(axes, [("合計種族値", bst07, 30), ("重さ", wt07, 100)]):
    xbar, _ = sample_means_07(pop, n, 5000, rng)
    q = n * (xbar - pop.mean()) ** 2 / pop.var()          # = Z_n²
    ax.hist(q[q < 8], bins=50, density=True, color=PALETTE[0], label="シミュレーション")
    ax.plot(g, stats.chi2.pdf(g, 1), color=PALETTE[1], label="χ²(1)")
    ax.set(title=f"{name}: n(X̄-μ)²/σ²（n = {n}）".replace("X̄", "平均"), xlabel="n(標本平均 − μ)²/σ²", ylabel="密度", ylim=(0, 1.5))
    ax.legend(fontsize=8)
    print(f"{name}（n = {n}）: P(Z² > {c95:.2f}) = {(q > c95).mean():.4f}（χ²(1) では 0.05）  Z² の平均 {q.mean():.3f}（理論 1）")
fig.tight_layout()
plt.show()

# %% 07-6
# デルタ法: √n (U_n - θ) → N(0, v) なら √n (h(U_n) - h(θ)) → N(0, h'(θ)² v)
rng = get_rng()
rows_dm = []
# (a) 重さの標本平均の対数: h(x) = log x, h'(μ) = 1/μ → V[log X̄] ≈ σ²/(nμ²)
for n in [30, 100, 300]:
    xbar, _ = sample_means_07(wt07, n, 5000, rng)
    lx = np.log(xbar)
    rows_dm.append({"推定量": "log(重さの標本平均)", "n": n, "平均 − h(θ)": lx.mean() - np.log(mu_w),
                    "分散（シミュ）": lx.var(), "デルタ法の分散": sd_w**2 / (n * mu_w**2)})
logs_100 = np.log(sample_means_07(wt07, 100, 5000, rng)[0])
# (b) みずタイプの割合のロジット: h(p) = log(p/(1-p)), h'(p) = 1/(p(1-p)) → V ≈ 1/(np(1-p))
p_w = water07.mean()
for n in [50, 200, 800]:
    ph = water07[rng.integers(0, len(water07), size=(5000, n))].mean(axis=1)
    ok = (ph > 0) & (ph < 1)                              # p̂ = 0, 1 ではロジットが定義できない
    lg = np.log(ph[ok] / (1 - ph[ok]))
    rows_dm.append({"推定量": "logit(みずの割合)", "n": n, "平均 − h(θ)": lg.mean() - np.log(p_w / (1 - p_w)),
                    "分散（シミュ）": lg.var(), "デルタ法の分散": 1 / (n * p_w * (1 - p_w)),
                    "除外（p̂ = 0 or 1）": int((~ok).sum())})

fig, ax = plt.subplots(figsize=(7, 3.8))
g = np.linspace(logs_100.min(), logs_100.max(), 300)
ax.hist(logs_100, bins=50, density=True, color=PALETTE[0], label="シミュレーション")
ax.plot(g, stats.norm.pdf(g, np.log(mu_w), sd_w / (np.sqrt(100) * mu_w)), color=PALETTE[1],
        label="デルタ法 N(log μ, σ²/(nμ²))")
ax.set(title="log(重さの標本平均) の分布（n = 100）", xlabel="log(標本平均)（重さは kg）", ylabel="密度")
ax.legend()
plt.show()
pd.DataFrame(rows_dm).round(5)
