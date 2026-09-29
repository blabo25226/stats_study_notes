"""第32章 シミュレーション."""
from poke import *

df = load_data()

# %% 32-0
# 真値（全920行を母集団とみなしたときの値）
total_pop = df["合計種族値"].to_numpy()
speed_pop = df["素早"].to_numpy()
attack_pop = df["攻撃"].to_numpy()
share_pop = speed_pop / total_pop                        # 素早が合計種族値に占める割合
slope_pop = np.polyfit(speed_pop, total_pop, 1)[0]       # 合計種族値 = a + b・素早 の傾き
sim_true = pd.Series({
    "合計種族値の平均": total_pop.mean(),
    "合計種族値の中央値": np.median(total_pop),
    "相関係数 r(攻撃, 合計種族値)": np.corrcoef(attack_pop, total_pop)[0, 1],
    "回帰の傾き（合計種族値 ~ 素早）": slope_pop,
    "素早の割合の平均": share_pop.mean(),
    "素早の割合の標準偏差": share_pop.std(),
})
print(sim_true.round(4).to_string())
print("\n合計種族値の異なる値の数:", len(np.unique(total_pop)))


# %% 32-1
# 擬似乱数: シードと再現性、線形合同法
print("同じシードなら同じ列:", get_rng(1).uniform(size=3).round(4), get_rng(1).uniform(size=3).round(4))
print("違うシード          :", get_rng(2).uniform(size=3).round(4))

def lcg(a, c, m, x0, n):
    """線形合同法 x_{k+1} = (a x_k + c) mod m."""
    xs = [x0]
    for _ in range(n - 1):
        xs.append((a * xs[-1] + c) % m)
    return np.array(xs)

# 小さな例: m = 16。周期が最大 16 になる条件（c と m が互いに素, a−1 が m の素因数と4で割り切れる）
print("\nm=16, a=5, c=3:", lcg(5, 3, 16, 7, 20))
print("m=16, a=3, c=3:", lcg(3, 3, 16, 7, 20), "（a−1=2 が4で割り切れず周期が短い）")

# 実用的な例: パーク・ミラーの最小標準（a=16807, c=0, m=2^31−1）で一様性をカイ二乗検定
m_pm = 2 ** 31 - 1
u_pm = lcg(16807, 0, m_pm, 12345, 20000) / m_pm
obs_pm, _ = np.histogram(u_pm, bins=10, range=(0, 1))
chi2_pm = ((obs_pm - len(u_pm) / 10) ** 2 / (len(u_pm) / 10)).sum()
print(f"\nパーク・ミラー 20000個: 10区間の度数 {obs_pm}")
print(f"カイ二乗統計量 {chi2_pm:.2f}, 自由度 9, p値 {stats.chi2.sf(chi2_pm, 9):.3f}（scipy: {stats.chisquare(obs_pm).pvalue:.3f}）")
# 初期値を20通り変えて同じ検定を繰り返す（H0 が正しければ p値は U(0,1) に従い、約5%で p < 0.05 となる）
p_seeds = [stats.chisquare(np.histogram(lcg(16807, 0, m_pm, x0, 20000) / m_pm, bins=10, range=(0, 1))[0]).pvalue
           for x0 in range(1, 21)]
print("初期値 1〜20 での p値:", np.round(p_seeds, 2), f"→ p<0.05 は {np.sum(np.array(p_seeds) < 0.05)} 回")
# 連続する2つの値の組 (u_k, u_{k+1}) の相関
print(f"隣り合う値の相関 {np.corrcoef(u_pm[:-1], u_pm[1:])[0, 1]:.4f}")


# %% 32-2
# 逆関数法: 指数分布と、合計種族値の経験分布
rng_inv = get_rng()
n_inv = 5000
lam = 0.5
u_inv = rng_inv.uniform(size=n_inv)
x_exp = -np.log(1 - u_inv) / lam                       # F(x) = 1 − e^{−λx} の逆関数
ks_exp = stats.kstest(x_exp, stats.expon(scale=1 / lam).cdf)
print(f"指数分布 Exp(λ={lam}): 標本平均 {x_exp.mean():.3f}（理論 {1 / lam}）, 標本分散 {x_exp.var():.3f}（理論 {1 / lam ** 2}）")
print(f"  KS検定: D={ks_exp.statistic:.4f}, p値={ks_exp.pvalue:.3f}")

# 経験分布の一般化逆関数 F_n^{-1}(u) = min{x : F_n(x) ≥ u} = x_(⌈nu⌉)
total_sorted = np.sort(total_pop)
n_pop = len(total_sorted)
x_emp = total_sorted[np.ceil(n_pop * u_inv).astype(int) - 1]
print(f"\n経験分布からの逆関数法: 平均 {x_emp.mean():.1f}（母集団 {total_pop.mean():.1f}）,"
      f" 標準偏差 {x_emp.std():.1f}（母集団 {total_pop.std():.1f}）")

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].hist(x_exp, bins=50, density=True, color=PALETTE[0], label="逆関数法の標本")
g_exp = np.linspace(0, x_exp.max(), 200)
axes[0].plot(g_exp, stats.expon(scale=1 / lam).pdf(g_exp), color=PALETTE[1], label="Exp(0.5) の密度")
axes[0].set(title="逆関数法: 指数分布", xlabel="x", ylabel="確率密度")
axes[0].legend()
bins_tot = np.arange(170, 800, 20)
axes[1].hist(total_pop, bins=bins_tot, density=True, color=PALETTE[0], alpha=0.6, label="母集団（920匹）")
axes[1].hist(x_emp, bins=bins_tot, density=True, histtype="step", color=PALETTE[1], lw=1.5, label="逆関数法の標本（5000個）")
axes[1].set(title="逆関数法: 合計種族値の経験分布", xlabel="合計種族値", ylabel="確率密度")
axes[1].legend()
fig.tight_layout()
plt.show()


# %% 32-3
# 採択・棄却法: 素早の割合をベータ分布で近似し、一様分布を提案分布として乱数を作る
m1, v1 = share_pop.mean(), share_pop.var()
k_mom = m1 * (1 - m1) / v1 - 1                         # モーメント法: a + b = m(1−m)/v − 1
a_beta, b_beta = m1 * k_mom, (1 - m1) * k_mom
beta_t = stats.beta(a_beta, b_beta)
mode_beta = (a_beta - 1) / (a_beta + b_beta - 2)
R_ar = beta_t.pdf(mode_beta)                           # f(x) ≤ R・g(x), g = U(0,1) の密度 1
print(f"モーメント法: Be({a_beta:.2f}, {b_beta:.2f}), モード {mode_beta:.3f}, R = max f = {R_ar:.3f}")

rng_ar = get_rng()
n_prop = 30000
y_ar = rng_ar.uniform(size=n_prop)                     # 提案 y ~ g
u_ar = rng_ar.uniform(size=n_prop)
accept = u_ar <= beta_t.pdf(y_ar) / (R_ar * 1.0)       # u ≤ f(y) / (R g(y)) なら採択
x_ar = y_ar[accept]
print(f"受容率: 実測 {accept.mean():.4f} / 理論 1/R = {1 / R_ar:.4f}")
print(f"採択された {len(x_ar)} 個: 平均 {x_ar.mean():.4f}（理論 {beta_t.mean():.4f}）, KS検定 p値 {stats.kstest(x_ar, beta_t.cdf).pvalue:.3f}")

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
g_b = np.linspace(0, 0.45, 300)
axes[0].scatter(y_ar[:2000][~accept[:2000]], (u_ar * R_ar)[:2000][~accept[:2000]], s=3, color=INK["muted"], alpha=0.4, label="棄却")
axes[0].scatter(y_ar[:2000][accept[:2000]], (u_ar * R_ar)[:2000][accept[:2000]], s=3, color=PALETTE[0], alpha=0.6, label="採択")
axes[0].plot(np.linspace(0, 1, 400), beta_t.pdf(np.linspace(0, 1, 400)), color=PALETTE[1], label="f(x)")
axes[0].axhline(R_ar, color=PALETTE[1], ls="--", lw=1, label="R・g(x)")
axes[0].set(title="採択・棄却法（最初の2000組）", xlabel="提案値 y", ylabel="u・R")
axes[0].legend(loc="upper right", frameon=True, facecolor=INK["surface"], framealpha=0.95)
axes[1].hist(share_pop, bins=40, range=(0, 0.45), density=True, color=PALETTE[0], alpha=0.6, label="母集団（920匹）")
axes[1].hist(x_ar, bins=40, range=(0, 0.45), density=True, histtype="step", color=PALETTE[1], lw=1.5, label="採択された乱数")
axes[1].plot(g_b, beta_t.pdf(g_b), color=PALETTE[2], label="当てはめたベータ分布")
axes[1].set(title="素早 / 合計種族値 の分布", xlabel="素早の割合", ylabel="確率密度")
axes[1].legend()
fig.tight_layout()
plt.show()


# %% 32-4
# モンテカルロ積分: I = ∫_0^1 e^x dx = e − 1。誤差が 1/√n で減ることを確かめる
rng_mc = get_rng()
I_true = np.e - 1
n_grid = np.array([10, 100, 1000, 10000, 100000])
n_rep_mc = 200
rmse_mc, se_mc = [], []
for n in n_grid:
    est = np.exp(rng_mc.uniform(size=(n_rep_mc, n))).mean(axis=1) if n <= 10000 else \
        np.array([np.exp(rng_mc.uniform(size=n)).mean() for _ in range(n_rep_mc)])
    rmse_mc.append(np.sqrt(np.mean((est - I_true) ** 2)))
    se_mc.append(np.sqrt(np.var(np.exp(rng_mc.uniform(size=n)), ddof=1) / n))   # 1回分の標準誤差の推定値
sigma_g = np.sqrt((np.e ** 2 - 1) / 2 - I_true ** 2)    # V[e^U] の理論値の平方根
mc_tab = pd.DataFrame({"n": n_grid, "RMSE（200回）": rmse_mc, "標準誤差の推定 s/√n": se_mc,
                       "理論 σ/√n": sigma_g / np.sqrt(n_grid)})
slope_mc = np.polyfit(np.log(n_grid), np.log(rmse_mc), 1)[0]
print(f"log RMSE を log n に回帰した傾き: {slope_mc:.3f}（理論 −0.5）")

# 分散減少法（同じ乱数の個数 n = 10000 で比較）
n_vr = 10000
u_vr = rng_mc.uniform(size=n_vr)
g_plain = np.exp(u_vr)
g_anti = (np.exp(u_vr[: n_vr // 2]) + np.exp(1 - u_vr[: n_vr // 2])) / 2   # 負の相関を利用: m = n/2 組
g_ctrl = np.exp(u_vr) - (1 + u_vr) + 1.5                                  # 主部の分離: h(x)=1+x, ∫h = 1.5
vr_tab = pd.DataFrame({
    "推定値": [g_plain.mean(), g_anti.mean(), g_ctrl.mean()],
    "標準誤差": [g_plain.std(ddof=1) / np.sqrt(n_vr), g_anti.std(ddof=1) / np.sqrt(n_vr // 2),
                 g_ctrl.std(ddof=1) / np.sqrt(n_vr)],
}, index=["素朴なモンテカルロ", "負の相関の利用", "主部の分離"])
vr_tab["分散の比（素朴=1）"] = (vr_tab["標準誤差"] / vr_tab["標準誤差"].iloc[0]) ** 2
print(f"真値 e − 1 = {I_true:.6f}")
print(vr_tab.round(6).to_string())
print(f"corr(e^U, e^(1−U)) = {np.corrcoef(np.exp(u_vr), np.exp(1 - u_vr))[0, 1]:.3f}")

fig, ax = plt.subplots(figsize=(7, 4.2))
ax.loglog(n_grid, rmse_mc, marker="o", color=PALETTE[0], label="実測の RMSE")
ax.loglog(n_grid, sigma_g / np.sqrt(n_grid), ls="--", color=PALETTE[1], label="理論 σ/√n")
ax.set(title="モンテカルロ積分の誤差", xlabel="乱数の個数 n（対数目盛）", ylabel="平均二乗誤差の平方根（対数目盛）")
ax.legend()
fig.tight_layout()
plt.show()
mc_tab


# %% 32-5
# モンテカルロ法で確率を求める: 2匹を無作為に選んだとき、1匹目の素早が2匹目より大きい確率
rng_pair = get_rng()
n_pair = 20000
i1, i2 = rng_pair.integers(0, len(df), n_pair), rng_pair.integers(0, len(df), n_pair)
hit = speed_pop[i1] > speed_pop[i2]
p_mc = hit.mean()
# 厳密値: 全 920×920 組で数える
p_exact = (speed_pop[:, None] > speed_pop[None, :]).mean()
print(f"モンテカルロ推定 {p_mc:.4f} ± {1.96 * np.sqrt(p_mc * (1 - p_mc) / n_pair):.4f}（95%）, 厳密値 {p_exact:.4f}")
print(f"同じ素早になる確率（厳密値）: {(speed_pop[:, None] == speed_pop[None, :]).mean():.4f}")


# %% 32-6
# 経験分布関数: 標本を増やすと母集団の分布関数に近づく
rng_ecdf = get_rng()
F_pop = lambda x: np.searchsorted(total_sorted, x, side="right") / n_pop   # 母集団の分布関数
x_eval = np.arange(170, 790)
fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True)
ecdf_rows = []
for ax, n in zip(axes, [20, 100, 500]):
    samp = np.sort(rng_ecdf.choice(total_pop, n, replace=True))
    Fn = np.searchsorted(samp, x_eval, side="right") / n
    D = np.abs(Fn - F_pop(x_eval)).max()
    eps = np.sqrt(np.log(2 / 0.05) / (2 * n))            # DKW 不等式による95%バンドの半幅
    ecdf_rows.append({"n": n, "sup|F_n − F|": D, "√n・sup": np.sqrt(n) * D, "DKWバンド半幅": eps})
    ax.fill_between(x_eval, np.clip(Fn - eps, 0, 1), np.clip(Fn + eps, 0, 1), step="post", color=PALETTE[0], alpha=0.15, label="95% DKW バンド")
    ax.step(x_eval, F_pop(x_eval), where="post", color=PALETTE[1], lw=1.5, label="母集団の分布関数 F")
    ax.step(x_eval, Fn, where="post", color=PALETTE[0], lw=1.5, label="経験分布関数 F_n")
    ax.set(title=f"n = {n}（sup 距離 {D:.3f}）", xlabel="合計種族値")
axes[0].set_ylabel("累積確率")
axes[0].legend(loc="upper left", fontsize=8)
fig.tight_layout()
plt.show()
pd.DataFrame(ecdf_rows).round(4)


# %% 32-7
# ジャックナイフ法: n = 40 の標本で標準誤差とバイアスを推定し、真の標本分布と比べる
rng_jk = get_rng()
n_jk = 40
idx_jk = rng_jk.integers(0, len(df), n_jk)
tot_jk, atk_jk = total_pop[idx_jk], attack_pop[idx_jk]

def jackknife(stat, *arrays):
    """1個ずつ除いた推定値から (推定値, 標準誤差, バイアス) を返す."""
    n = len(arrays[0])
    theta = stat(*arrays)
    loo = np.array([stat(*[a[np.arange(n) != j] for a in arrays]) for j in range(n)])
    se = np.sqrt((n - 1) / n * np.sum((loo - loo.mean()) ** 2))
    bias = (n - 1) * (loo.mean() - theta)
    return theta, se, bias

jk_stats = {
    "平均": (lambda x: x.mean(), (tot_jk,)),
    "標本分散（1/n）": (lambda x: x.var(ddof=0), (tot_jk,)),
    "中央値": (lambda x: np.median(x), (tot_jk,)),
    "相関係数 r(攻撃, 合計)": (lambda x, y: np.corrcoef(x, y)[0, 1], (atk_jk, tot_jk)),
}
# 真の標準誤差: 母集団から n=40 の標本を 5000 回取り直して推定量の標準偏差を求める
idx_true = get_rng(SEED + 1).integers(0, len(df), (5000, n_jk))
T, A = total_pop[idx_true], attack_pop[idx_true]
Tc, Ac = T - T.mean(axis=1, keepdims=True), A - A.mean(axis=1, keepdims=True)
true_draws = {
    "平均": T.mean(axis=1), "標本分散（1/n）": T.var(axis=1),
    "中央値": np.median(T, axis=1),
    "相関係数 r(攻撃, 合計)": (Ac * Tc).sum(1) / np.sqrt((Ac ** 2).sum(1) * (Tc ** 2).sum(1)),
}
jk_rows = []
for name, (f, arrs) in jk_stats.items():
    th, se, bias = jackknife(f, *arrs)
    jk_rows.append({"推定量": name, "推定値": th, "ジャックナイフSE": se, "真のSE（5000回）": true_draws[name].std(),
                    "ジャックナイフのバイアス推定": bias, "バイアス補正後": th - bias})
jk_tab = pd.DataFrame(jk_rows).set_index("推定量")
# 定義式との照合
print(f"平均: ジャックナイフSE = s/√n か → {jk_tab.loc['平均', 'ジャックナイフSE']:.4f} vs {tot_jk.std(ddof=1) / np.sqrt(n_jk):.4f}")
print(f"標本分散: バイアス補正後 = 不偏分散 か → {jk_tab.loc['標本分散（1/n）', 'バイアス補正後']:.2f} vs {tot_jk.var(ddof=1):.2f}")
print(f"標本の異なる値の数 {len(np.unique(tot_jk))}（中央値の1個抜き推定値は高々2通り:"
      f" {np.unique([np.median(np.delete(tot_jk, j)) for j in range(n_jk)])}）")
jk_tab.round(4)


# %% 32-8
# ブートストラップ法: 同じ n = 40 の標本から、中央値・相関係数・回帰の傾きの標準誤差と信頼区間を求める
rng_bs = get_rng()
B_bs = 4000
spd_jk = speed_pop[idx_jk]

def boot_stats(x_tot, x_atk, x_spd, idx):
    """復元抽出の添字行列 idx（B × n）から3つの推定量を一度に計算する."""
    t, a, s = x_tot[idx], x_atk[idx], x_spd[idx]
    tc, ac, sc = (v - v.mean(axis=1, keepdims=True) for v in (t, a, s))
    med = np.median(t, axis=1)
    r = (ac * tc).sum(1) / np.sqrt((ac ** 2).sum(1) * (tc ** 2).sum(1))
    slope = (sc * tc).sum(1) / (sc ** 2).sum(1)
    return {"中央値": med, "相関係数": r, "回帰の傾き": slope}

theta_hat = boot_stats(tot_jk, atk_jk, spd_jk, np.arange(n_jk)[None, :])
idx_boot = rng_bs.integers(0, n_jk, (B_bs, n_jk))
boot = boot_stats(tot_jk, atk_jk, spd_jk, idx_boot)
# 真の標本分布（母集団から n=40 を5000回）
true_sd = {k: v.std() for k, v in boot_stats(total_pop, attack_pop, speed_pop, idx_true).items()}
true_val = {"中央値": sim_true["合計種族値の中央値"], "相関係数": sim_true["相関係数 r(攻撃, 合計種族値)"],
            "回帰の傾き": sim_true["回帰の傾き（合計種族値 ~ 素早）"]}

bs_rows = []
for k in boot:
    th = theta_hat[k][0]
    lo, hi = np.percentile(boot[k], [2.5, 97.5])
    bs_rows.append({"推定量": k, "推定値": th, "真値": true_val[k],
                    "ブートストラップSE": boot[k].std(ddof=1), "真のSE（5000回）": true_sd[k],
                    "バイアス推定": boot[k].mean() - th, "95%パーセンタイル区間": f"[{lo:.3f}, {hi:.3f}]"})
# 正規理論との比較: 回帰の傾きの OLS 標準誤差, 相関係数のフィッシャー z 区間
res_ols = stats.linregress(spd_jk, tot_jk)
z = np.arctanh(theta_hat["相関係数"][0])
fz_lo, fz_hi = np.tanh(z + np.array([-1, 1]) * 1.96 / np.sqrt(n_jk - 3))
print(f"回帰の傾き: OLS の標準誤差 {res_ols.stderr:.4f}")
print(f"相関係数: フィッシャー z 変換の95%区間 [{fz_lo:.3f}, {fz_hi:.3f}]")

fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
units = {"中央値": "合計種族値の中央値", "相関係数": "r(攻撃, 合計種族値)", "回帰の傾き": "傾き（合計種族値 / 素早）"}
for ax, k in zip(axes, boot):
    ax.hist(boot[k], bins=40, color=PALETTE[0])
    ax.axvline(theta_hat[k][0], color=PALETTE[1], lw=1.5, label="標本の推定値")
    ax.axvline(true_val[k], color=INK["primary"], ls="--", lw=1, label="真値")
    for q in np.percentile(boot[k], [2.5, 97.5]):
        ax.axvline(q, color=PALETTE[2], ls=":", lw=1.5)
    ax.set(title=f"{k}（B={B_bs}）", xlabel=units[k], ylabel="度数")
axes[0].legend(fontsize=8)
fig.suptitle("ブートストラップ分布（緑の点線: 95%パーセンタイル区間）", fontsize=12, fontweight="bold")
fig.tight_layout()
plt.show()
pd.DataFrame(bs_rows).set_index("推定量").round(4)


# %% 32-9
# 被覆率の確認: 母集団から n=40 を取り直して区間を作り、真値を含む割合を数える
rng_cov = get_rng()
n_rep_cov, B_cov, n_cov = 1000, 1000, 40
cover = {k: 0 for k in true_val}
cover_normal = {"相関係数（フィッシャー z）": 0, "回帰の傾き（OLS の t 区間）": 0}
width = {k: [] for k in true_val}
t_crit = stats.t(n_cov - 2).ppf(0.975)
for _ in range(n_rep_cov):
    idx_s = rng_cov.integers(0, len(df), n_cov)
    t_s, a_s, s_s = total_pop[idx_s], attack_pop[idx_s], speed_pop[idx_s]
    bst = boot_stats(t_s, a_s, s_s, rng_cov.integers(0, n_cov, (B_cov, n_cov)))
    for k in true_val:
        lo, hi = np.percentile(bst[k], [2.5, 97.5])
        cover[k] += lo <= true_val[k] <= hi
        width[k].append(hi - lo)
    est = boot_stats(t_s, a_s, s_s, np.arange(n_cov)[None, :])
    zc = np.arctanh(est["相関係数"][0])
    cover_normal["相関係数（フィッシャー z）"] += np.tanh(zc - 1.96 / np.sqrt(n_cov - 3)) <= true_val["相関係数"] <= np.tanh(zc + 1.96 / np.sqrt(n_cov - 3))
    lr = stats.linregress(s_s, t_s)
    cover_normal["回帰の傾き（OLS の t 区間）"] += abs(lr.slope - true_val["回帰の傾き"]) <= t_crit * lr.stderr
cov_tab = pd.DataFrame({
    "被覆率": [cover[k] / n_rep_cov for k in true_val] + [v / n_rep_cov for v in cover_normal.values()],
}, index=[f"{k}（パーセンタイル）" for k in true_val] + list(cover_normal))
cov_tab["被覆率の95%範囲（名目0.95なら）"] = f"[{0.95 - 1.96 * np.sqrt(0.95 * 0.05 / n_rep_cov):.3f}, {0.95 + 1.96 * np.sqrt(0.95 * 0.05 / n_rep_cov):.3f}]"
print(f"反復 {n_rep_cov} 回, B = {B_cov}, n = {n_cov}")
print("パーセンタイル区間の平均の幅:", {k: round(np.mean(v), 3) for k, v in width.items()})
cov_tab
