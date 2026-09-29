"""第08章 統計的推定の基礎."""
from poke import *

df = load_data()

# %% 08-0
# 真値既知の母集団（全920行）の値
bst08 = df["合計種族値"].to_numpy(float)
wt08 = df["重さ"].to_numpy(float)
atk08 = df["攻撃"].to_numpy(float)
dual08 = df["複合タイプ"].to_numpy(int)
true08 = pd.DataFrame({
    "母平均": [bst08.mean(), wt08.mean(), atk08.mean(), dual08.mean()],
    "母分散（N で割る）": [bst08.var(), wt08.var(), atk08.var(), dual08.var()],
    "尖度(-3)": [stats.kurtosis(bst08), stats.kurtosis(wt08), stats.kurtosis(atk08), np.nan],
}, index=["合計種族値", "重さ (kg)", "攻撃", "複合タイプ (0/1)"])


def draw08(values, n, reps, rng):
    """母集団 values から大きさ n の標本を reps 組、復元抽出した (reps, n) 配列."""
    return values[rng.integers(0, len(values), size=(reps, n))]

true08.round(3)

# %% 08-1
# モーメント法と最尤法: ガンマ分布 Ga(a, b)（a: 形状, b: 尺度）
from scipy.optimize import brentq
from scipy.special import digamma


def gamma_mom(x):
    """モーメント法: E[X] = ab, V[X] = ab² を標本平均と（n で割った）標本分散で解く."""
    m, v = x.mean(), x.var()
    return m**2 / v, v / m


def gamma_mle(x):
    """最尤法: 尤度方程式 log a - ψ(a) = log x̄ - mean(log x) を a について解き、b = x̄/a."""
    c = np.log(x.mean()) - np.log(x).mean()             # イェンセンの不等式より c > 0
    a = brentq(lambda a: np.log(a) - digamma(a) - c, 1e-3, 1e4)
    return a, x.mean() / a

# 実データ（攻撃の全920行）に当てはめる
a_mm, b_mm = gamma_mom(atk08)
a_ml, b_ml = gamma_mle(atk08)
a_sp, _, b_sp = stats.gamma.fit(atk08, floc=0)
print(f"攻撃: モーメント法 a = {a_mm:.3f}, b = {b_mm:.3f}")
print(f"      最尤法（手計算）a = {a_ml:.3f}, b = {b_ml:.3f}   scipy: a = {a_sp:.3f}, b = {b_sp:.3f}")

# この (a, b) を真値とするガンマ分布から n = 30 の標本を 2000 回取り、2つの推定量を比べる
rng = get_rng()
n_g, reps_g = 30, 2000
xs = rng.gamma(a_ml, b_ml, size=(reps_g, n_g))
est_mm = np.array([gamma_mom(x) for x in xs])
est_ml = np.array([gamma_mle(x) for x in xs])
rows_g = []
for name, est in [("モーメント法", est_mm), ("最尤法", est_ml)]:
    for j, (par, true) in enumerate([("a", a_ml), ("b", b_ml)]):
        e = est[:, j]
        rows_g.append({"推定量": name, "母数": par, "真値": true, "平均": e.mean(), "バイアス": e.mean() - true,
                       "標準偏差": e.std(), "MSE": ((e - true) ** 2).mean()})
pd.DataFrame(rows_g).round(3)

# %% 08-2
# 最尤推定量の漸近正規性: 幾何分布（失敗回数）Geo(p)、簡略化モデル p = 捕獲率/255 と仮定
# 対数尤度 l(p) = n log p + Σx log(1-p) → p̂ = 1/(1 + x̄)（モーメント法 E[X] = (1-p)/p とも一致）
# フィッシャー情報量（1観測）I₁(p) = 1/(p²(1-p)) → V[p̂] ≈ p²(1-p)/n
rng = get_rng()
p0 = 45 / 255
n_geo, reps_geo = 50, 4000
xg = rng.geometric(p0, size=(reps_geo, n_geo)) - 1
p_hat = 1 / (1 + xg.mean(axis=1))
se_theory = np.sqrt(p0**2 * (1 - p0) / n_geo)
se_plug = np.sqrt(p_hat**2 * (1 - p_hat) / n_geo)      # p̂ を代入した標準誤差
cover = (np.abs(p_hat - p0) <= 1.96 * se_plug).mean()
# フィッシャー情報量の2つの表し方: E[スコア²] と -E[対数尤度の2階微分]
x1 = xg.ravel()                                        # 1観測ごとの値（4000 × 50 個）
score = 1 / p0 - x1 / (1 - p0)
hess = -1 / p0**2 - x1 / (1 - p0) ** 2
print(f"I₁(p): 理論 1/(p²(1-p)) = {1 / (p0**2 * (1 - p0)):.2f}   E[スコア²] ≈ {np.mean(score**2):.2f}"
      f"   -E[2階微分] ≈ {-hess.mean():.2f}   E[スコア] ≈ {score.mean():.3f}")
print(f"p̂ の平均 {p_hat.mean():.4f}（真値 {p0:.4f}）  標準偏差 {p_hat.std():.4f}（漸近理論 {se_theory:.4f}）")
print(f"p̂ ± 1.96 SE(p̂) が真値を含む割合: {cover:.3f}（名目 0.95）")

fig, ax = plt.subplots(figsize=(7, 3.8))
g = np.linspace(p_hat.min(), p_hat.max(), 300)
ax.hist(p_hat, bins=50, density=True, color=PALETTE[0], label="最尤推定値（シミュレーション）")
ax.plot(g, stats.norm.pdf(g, p0, se_theory), color=PALETTE[1], label="漸近正規分布 N(p, p²(1-p)/n)")
ax.axvline(p0, color=INK["primary"], lw=1, ls="--", label=f"真値 p = {p0:.3f}")
ax.set(title=f"幾何分布の p の最尤推定量の分布（n = {n_geo}）", xlabel="p の最尤推定値", ylabel="密度")
ax.legend(fontsize=8)
plt.show()

# %% 08-3
# バイアス・バリアンス分解: 母分散 σ² を Σ(X - X̄)²/c（c = n-1, n, n+1）で推定する
rng = get_rng()
n_v, reps_v = 10, 20000
rows_bv = []
for name, pop in [("合計種族値", bst08), ("重さ", wt08)]:
    sig2, kap = pop.var(), stats.kurtosis(pop)
    ss = draw08(pop, n_v, reps_v, rng).var(axis=1, ddof=0) * n_v   # 偏差平方和
    var_s2 = sig2**2 * (2 / (n_v - 1) + kap / n_v)                   # V[S²]（S² は不偏分散）
    for c in [n_v - 1, n_v, n_v + 1]:
        est = ss / c
        bias, var = est.mean() - sig2, est.var()
        # 理論: E = (n-1)σ²/c, V = (n-1)² V[S²]/c²
        mse_th = ((n_v - 1) / c - 1) ** 2 * sig2**2 + (n_v - 1) ** 2 * var_s2 / c**2
        rows_bv.append({"母集団": name, "割る数": c, "バイアス²/σ⁴": bias**2 / sig2**2, "分散/σ⁴": var / sig2**2,
                        "MSE/σ⁴": ((est - sig2) ** 2).mean() / sig2**2,
                        "分散+バイアス²（/σ⁴）": (var + bias**2) / sig2**2, "理論 MSE/σ⁴": mse_th / sig2**2})
    # MSE を最小にする割る数 c を理論式から数値的に探す（正規母集団なら c = n+1）
    cs = np.linspace(n_v - 1, 4 * n_v, 2000)
    mse_c = ((n_v - 1) / cs - 1) ** 2 * sig2**2 + (n_v - 1) ** 2 * var_s2 / cs**2
    print(f"{name}: 尖度 κ = {kap:.2f}  MSE を最小にする割る数（理論） c* ≈ {cs[mse_c.argmin()]:.1f}")
print(f"n = {n_v}、各 {reps_v} 回。値は σ⁴ で割って無次元化")
pd.DataFrame(rows_bv).round(4)

# %% 08-4
# 不偏推定量: 復元抽出と非復元抽出で、X̄・S²・S の期待値を真値と比べる（合計種族値, n = 30）
rng = get_rng()
n_u, reps_u = 30, 5000
N08 = len(bst08)
mu_t, sig2_N = bst08.mean(), bst08.var(ddof=0)
smp_with = draw08(bst08, n_u, reps_u, rng)
smp_wo = np.array([rng.choice(bst08, n_u, replace=False) for _ in range(reps_u)])
rows_u = []
for name, smp in [("復元抽出（i.i.d.）", smp_with), ("非復元抽出", smp_wo)]:
    s2 = smp.var(axis=1, ddof=1)
    rows_u.append({"抽出": name, "E[X̄]/μ": smp.mean(axis=1).mean() / mu_t,
                   "E[S²]/σ²（N で割る）": s2.mean() / sig2_N,
                   "E[S²]/σ²（N-1 で割る）": s2.mean() / bst08.var(ddof=1),
                   "E[S]/σ": np.sqrt(s2).mean() / np.sqrt(sig2_N)})
print(f"非復元抽出の理論: E[S²] = N/(N-1)·σ²_N（比 {N08 / (N08 - 1):.4f}）")
from scipy.special import gammaln
c4 = np.sqrt(2 / (n_u - 1)) * np.exp(gammaln(n_u / 2) - gammaln((n_u - 1) / 2))
print(f"正規母集団なら E[S]/σ = c₄ = √(2/(n-1))·Γ(n/2)/Γ((n-1)/2) = {c4:.4f}")
pd.DataFrame(rows_u).round(4)

# %% 08-5
# ジャックナイフ推定量: 1つずつ除いた推定量 θ̂_(i) から偏りを補正し、標準誤差を求める
def jackknife08(x, stat):
    """(元の推定量, ジャックナイフ推定量, ジャックナイフ標準誤差) を返す. stat は各行に適用される."""
    n = x.shape[-1]
    theta = stat(x)
    loo = np.stack([stat(np.delete(x, i, axis=-1)) for i in range(n)], axis=-1)  # θ̂_(i)
    loo_mean = loo.mean(axis=-1)
    theta_jack = n * theta - (n - 1) * loo_mean
    se_jack = np.sqrt((n - 1) / n * ((loo - loo_mean[..., None]) ** 2).sum(axis=-1))
    return theta, theta_jack, se_jack

rng = get_rng()
# (1) n で割る標本分散のジャックナイフは不偏分散 S² に一致する
x_one = draw08(bst08, 12, 1, rng)[0]
_, jk_var, _ = jackknife08(x_one, lambda z: z.var(axis=-1, ddof=0))
print(f"(1) n で割る分散 {x_one.var():.2f} → ジャックナイフ {jk_var:.2f}   不偏分散 S² = {x_one.var(ddof=1):.2f}")

# (2) θ = log μ（重さの母平均の対数）を θ̂ = log X̄ で推定（log は凹関数なので下向きの偏り）
n_j, reps_j = 20, 3000
xs_j = draw08(wt08, n_j, reps_j, rng)
th, th_jk, se_jk = jackknife08(xs_j, lambda z: np.log(z.mean(axis=-1)))
theta_true = np.log(wt08.mean())
pd.DataFrame({
    "推定量": ["log X̄（そのまま）", "ジャックナイフ補正"],
    "バイアス": [th.mean() - theta_true, th_jk.mean() - theta_true],
    "標準偏差": [th.std(), th_jk.std()],
    "RMSE": [np.sqrt(((th - theta_true) ** 2).mean()), np.sqrt(((th_jk - theta_true) ** 2).mean())],
    "ジャックナイフSEの平均": [se_jk.mean(), np.nan],
}).round(4)

# %% 08-6
# クラメール・ラオの不等式: 不偏推定量の分散 ≥ 1/(n I₁(θ))
rng = get_rng()
# (a) ベルヌーイ: 複合タイプか（p = 母集団の割合）。I₁(p) = 1/(p(1-p)) → 下限 p(1-p)/n
p_d = dual08.mean()
rows_cr = []
for n in [10, 30, 100]:
    ph = draw08(dual08, n, 20000, rng).mean(axis=1)
    rows_cr.append({"モデル": "ベルヌーイ（複合タイプ）", "推定量": "標本割合", "n": n,
                    "分散（シミュ）": ph.var(), "CR下限": p_d * (1 - p_d) / n})
# (b) 正規分布の平均（σ 既知）: I₁(μ) = 1/σ² → 下限 σ²/n。合計種族値の μ, σ をもつ正規分布から生成
mu_n, sd_n = bst08.mean(), bst08.std()
for n in [11, 51]:
    xn = rng.normal(mu_n, sd_n, size=(10000, n))
    for name, est in [("標本平均", xn.mean(axis=1)), ("標本中央値", np.median(xn, axis=1))]:
        rows_cr.append({"モデル": "正規（μ, σ は合計種族値）", "推定量": name, "n": n,
                        "分散（シミュ）": est.var(), "CR下限": sd_n**2 / n})
tab_cr = pd.DataFrame(rows_cr)
tab_cr["分散/CR下限"] = tab_cr["分散（シミュ）"] / tab_cr["CR下限"]
print(f"p（複合タイプの割合）= {p_d:.4f}")
tab_cr.round(4)

# %% 08-7
# 有効推定量と相対効率: 正規母集団と実際の母集団（合計種族値）で、平均の推定量どうしを比べる
rng = get_rng()
n_e = 25
rows_eff = []
pops_eff = {"正規分布 N(μ, σ²)": rng.normal(mu_n, sd_n, size=(10000, n_e)),
            "合計種族値（実際の母集団）": draw08(bst08, n_e, 10000, rng)}
for pname, xe in pops_eff.items():
    ests = {"標本平均": xe.mean(axis=1), "標本中央値": np.median(xe, axis=1),
            "10%刈込平均": stats.trim_mean(xe, 0.1, axis=1),
            "中点 (最大+最小)/2": (xe.max(axis=1) + xe.min(axis=1)) / 2}
    v_mean = ests["標本平均"].var()
    for ename, e in ests.items():
        rows_eff.append({"母集団": pname, "推定量": ename, "平均": e.mean(), "分散": e.var(),
                         "相対効率（標本平均の分散/分散）": v_mean / e.var(), "分散/(σ²/n)": e.var() / (sd_n**2 / n_e)})
print(f"n = {n_e}。正規分布での中央値の漸近相対効率は 2/π ≈ {2 / np.pi:.3f}")
pd.DataFrame(rows_eff).round(3)

# %% 08-8
# 十分統計量: ベルヌーイ列で T = ΣX を与えると、並び方の条件付き分布は p によらない
rng = get_rng()
n_s, k_s = 5, 2
p_water = (df["タイプ1"] == "みず").mean()
rows_suf = {}
for label, p in [(f"p = {p_d:.3f}（複合タイプ）", p_d), (f"p = {p_water:.3f}（みず）", p_water)]:
    seq = rng.random((400000, n_s)) < p
    sel = seq[seq.sum(axis=1) == k_s]                     # T = 2 の列だけを残す
    patterns = ["".join("1" if b else "0" for b in row) for row in sel]
    rows_suf[label] = pd.Series(patterns).value_counts(normalize=True).sort_index()
    print(f"{label}: T = {k_s} となった列 {len(sel)} 本、P(X₁ = 1 | T = {k_s}) = {sel[:, 0].mean():.3f}（理論 k/n = {k_s / n_s}）")
tab_suf = pd.DataFrame(rows_suf)
tab_suf["理論 1/C(5,2)"] = 1 / 10
tab_suf.round(4)

# %% 08-9
# 順序統計量: n = 11 の標本の最大値と中央値（6番目）の分布
# 母集団の分布関数 F について、P(X_(k) ≤ x) = Σ_{j=k}^{n} C(n,j) F(x)^j (1-F(x))^{n-j}（最大値は F(x)^n）
rng = get_rng()
n_o, reps_o = 11, 10000
smp_o = np.sort(draw08(bst08, n_o, reps_o, rng), axis=1)
xs_o = np.unique(bst08)
F_pop = np.searchsorted(np.sort(bst08), xs_o, side="right") / len(bst08)   # 母集団の分布関数 F(x)


def order_cdf(F, k, n):
    """k 番目の順序統計量の分布関数（F は母集団の分布関数の値）."""
    return stats.binom.sf(k - 1, n, F)                    # P(Bin(n, F) ≥ k)

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
rows_os = []
for ax, (name, k) in zip(axes, [("最大値", n_o), ("中央値", (n_o + 1) // 2)]):
    v = smp_o[:, k - 1]
    ecdf = np.searchsorted(np.sort(v), xs_o, side="right") / reps_o
    th = order_cdf(F_pop, k, n_o)
    ax.step(xs_o, ecdf, where="post", color=PALETTE[0], label="シミュレーション")
    ax.step(xs_o, th, where="post", color=PALETTE[1], ls="--", label="理論")
    ax.step(xs_o, F_pop, where="post", color=INK["muted"], lw=1, label="母集団の分布関数 F")
    ax.set(title=f"標本{name}（{k}番目, n = {n_o}）の分布関数", xlabel="合計種族値", ylabel="累積確率")
    ax.legend(fontsize=8)
    pmf_th = np.diff(np.r_[0, th])
    rows_os.append({"統計量": name, "平均（シミュ）": v.mean(), "平均（理論）": (xs_o * pmf_th).sum(),
                    "最大差 |F_sim - F_th|": np.abs(ecdf - th).max()})
fig.tight_layout()
plt.show()
print(f"母集団: 最大値 {bst08.max():.0f}, 中央値 {np.median(bst08):.0f}")
pd.DataFrame(rows_os).round(3)
