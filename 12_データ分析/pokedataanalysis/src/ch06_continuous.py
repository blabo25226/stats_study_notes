"""第06章 連続型分布と標本分布."""
from poke import *

df = load_data()

# %% 06-0
# この章で使う列の要約（歪度・尖度つき）
cols06 = ["合計種族値", "重さ", "log重さ", "攻撃", "特攻", "捕獲率"]
sum06 = df[cols06].describe().T[["count", "mean", "std", "min", "50%", "max"]]
sum06["歪度"] = df[cols06].skew()
sum06["尖度(-3)"] = df[cols06].kurt()
print("捕獲率 = 255（上限）の行数:", (df["捕獲率"] == 255).sum())
sum06.round(2)

# %% 06-1
# 正規分布: 合計種族値に N(μ, σ^2) を当てはめる（最尤推定: 標本平均と n で割った標準偏差）
bst = df["合計種族値"].to_numpy(float)
mu_b, sd_b = bst.mean(), bst.std(ddof=0)
mu_fit, sd_fit = stats.norm.fit(bst)                   # scipy の MLE と手計算の一致
print(f"手計算 μ̂ = {mu_b:.2f}, σ̂ = {sd_b:.2f}   scipy.stats.norm.fit: {mu_fit:.2f}, {sd_fit:.2f}")
print(f"歪度 {stats.skew(bst):.3f}  尖度(-3) {stats.kurtosis(bst):.3f}")
# 正規分布なら μ±σ に約68.3%, μ±2σ に約95.4% が入る
for k in [1, 2]:
    inside = (np.abs(bst - mu_b) <= k * sd_b).mean()
    print(f"μ±{k}σ に入る割合: データ {inside:.3f}  正規分布 {stats.norm.cdf(k) - stats.norm.cdf(-k):.3f}")

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
grid_b = np.linspace(150, 800, 300)
axes[0].hist(bst, bins=40, density=True, color=PALETTE[0], label="データ")
axes[0].plot(grid_b, stats.norm.pdf(grid_b, mu_b, sd_b), color=PALETTE[1], label="当てはめた正規分布")
axes[0].set(title="合計種族値のヒストグラム", xlabel="合計種族値", ylabel="密度")
axes[0].legend()
(osm, osr), (slope, icpt, _) = stats.probplot(bst, dist="norm")
axes[1].plot(osm, osr, "o", ms=3, color=PALETTE[0], label="データ")
axes[1].plot(osm, slope * osm + icpt, color=PALETTE[1], label="当てはめた正規分布の直線")
axes[1].set(title="正規 Q-Q プロット", xlabel="標準正規分布の分位点", ylabel="合計種族値の順序統計量")
axes[1].legend()
fig.tight_layout()
plt.show()

# %% 06-2
# 対数正規分布: 重さ X に対し log X ~ N(μ, σ^2) を当てはめる
wt = df["重さ"].to_numpy(float)
mu_l, sd_l = np.log(wt).mean(), np.log(wt).std(ddof=0)
shape_s, _, scale_s = stats.lognorm.fit(wt, floc=0)    # scipy の lognorm: s = σ, scale = e^μ
print(f"手計算 μ̂ = {mu_l:.3f}, σ̂ = {sd_l:.3f}   scipy: s = {shape_s:.3f}, log(scale) = {np.log(scale_s):.3f}")
print(f"中央値  モデル e^μ = {np.exp(mu_l):.1f} kg      データ {np.median(wt):.1f} kg")
print(f"平均    モデル e^(μ+σ²/2) = {np.exp(mu_l + sd_l**2 / 2):.1f} kg   データ {wt.mean():.1f} kg")
print(f"log重さの歪度 {stats.skew(np.log(wt)):.3f}  尖度(-3) {stats.kurtosis(np.log(wt)):.3f}")

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
grid_w = np.linspace(0.1, 400, 400)
# 400 kg 以下だけ表示するが、密度は全920行で割って対数正規分布の密度と比べられるようにする
frac = (wt <= 400).mean()
h, e = np.histogram(wt[wt <= 400], bins=50)
axes[0].bar(e[:-1], h / (len(wt) * np.diff(e)), width=np.diff(e), align="edge", color=PALETTE[0],
            label=f"データ（400 kg 以下 {frac:.1%} を表示）")
axes[0].plot(grid_w, stats.lognorm.pdf(grid_w, sd_l, scale=np.exp(mu_l)), color=PALETTE[1], label="対数正規分布")
axes[0].set(title="重さと対数正規分布", xlabel="重さ (kg)", ylabel="密度", ylim=(0, 0.03))
axes[0].legend()
(osm, osr), (slope, icpt, _) = stats.probplot(np.log(wt), dist="norm")
axes[1].plot(osm, osr, "o", ms=3, color=PALETTE[0], label="データ")
axes[1].plot(osm, slope * osm + icpt, color=PALETTE[1], label="直線")
axes[1].set(title="log重さの正規 Q-Q プロット", xlabel="標準正規分布の分位点", ylabel="log(重さ)")
axes[1].legend()
fig.tight_layout()
plt.show()

# %% 06-3
# 指数分布・ガンマ分布（・対数正規分布）を最尤法で当てはめ、対数尤度と AIC で比べる
def fit_positive_06(x):
    """正値データに3つの分布を最尤推定で当てはめ、(表, 当てはめた分布の辞書) を返す."""
    n = len(x)
    lam_hat = 1 / x.mean()                              # 指数分布の MLE は 1/標本平均
    a_hat, _, b_hat = stats.gamma.fit(x, floc=0)        # ガンマ分布 Ga(a, b)（b は尺度）
    s_hat, _, sc_hat = stats.lognorm.fit(x, floc=0)
    dists = {"指数 Exp(λ)": (stats.expon(scale=1 / lam_hat), 1),
             "ガンマ Ga(a, b)": (stats.gamma(a_hat, scale=b_hat), 2),
             "対数正規 Λ(μ, σ²)": (stats.lognorm(s_hat, scale=sc_hat), 2)}
    rows = []
    for name, (dist, k) in dists.items():
        ll = dist.logpdf(x).sum()
        rows.append({"分布": name, "パラメータ数": k, "対数尤度": ll, "AIC": -2 * ll + 2 * k})
    # 手計算の確認: 指数分布の最大対数尤度 = n log λ̂ - λ̂ Σx = -n(log x̄ + 1)
    assert np.isclose(rows[0]["対数尤度"], -n * (np.log(x.mean()) + 1))
    return pd.DataFrame(rows).set_index("分布"), {k: v[0] for k, v in dists.items()}, (lam_hat, a_hat, b_hat)

tab_w, fits_w, (lam_w, a_w, b_w) = fit_positive_06(wt)
print(f"重さ: λ̂ = {lam_w:.4f}（平均 {1 / lam_w:.1f} kg）, ガンマ a = {a_w:.3f}, b = {b_w:.1f}")
print(tab_w.round(1).to_string())
atk = df["攻撃"].to_numpy(float)
tab_a, fits_a, (lam_a, a_a, b_a) = fit_positive_06(atk)
ll_norm_a = stats.norm(atk.mean(), atk.std()).logpdf(atk).sum()
tab_a.loc["正規 N(μ, σ²)"] = [2, ll_norm_a, -2 * ll_norm_a + 4]
print(f"\n攻撃: ガンマ a = {a_a:.2f}, b = {b_a:.2f}")
print(tab_a.round(1).to_string())

# 図: log(重さ) の尺度で比べる（Y = log X の密度は f_X(e^y) e^y）
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
y_grid = np.linspace(np.log(wt).min() - 0.5, np.log(wt).max() + 0.5, 300)
axes[0].hist(np.log(wt), bins=40, density=True, color=INK["grid"], label="データ")
for c, (name, dist) in zip(PALETTE, fits_w.items()):
    axes[0].plot(y_grid, dist.pdf(np.exp(y_grid)) * np.exp(y_grid), color=c, label=name)
axes[0].set(title="重さ（対数軸で表示）", xlabel="log(重さ)（重さは kg）", ylabel="log(重さ) の密度")
axes[0].legend(fontsize=8)
x_grid = np.linspace(1, 200, 300)
axes[1].hist(atk, bins=40, density=True, color=INK["grid"], label="データ")
# 指数分布は明らかに合わないので図では省き（表には載せている）、3本に絞る。色は分布ごとに左図と揃える
for c, name in zip(PALETTE[1:3], ["ガンマ Ga(a, b)", "対数正規 Λ(μ, σ²)"]):
    axes[1].plot(x_grid, fits_a[name].pdf(x_grid), color=c, label=name)
axes[1].plot(x_grid, stats.norm.pdf(x_grid, atk.mean(), atk.std()), color=PALETTE[3], label="正規 N(μ, σ²)")
axes[1].set(title="攻撃", xlabel="攻撃（種族値）", ylabel="密度")
axes[1].legend(fontsize=8)
fig.tight_layout()
plt.show()

# %% 06-4
# ベータ分布: 捕獲率/255 は (0, 1] の値（255 が上限なので 1 ちょうどの行がある）
y_cr = df["捕獲率"].to_numpy(float) / 255
n_cr = len(y_cr)
print(f"1 ちょうどの行: {(y_cr == 1).sum()}  最小値: {y_cr.min():.4f}")
# ベータ分布の密度は端点 0, 1 で 0 か ∞ になり得るので、(y(n-1) + 0.5)/n で端点を少し内側に寄せる
y_sq = (y_cr * (n_cr - 1) + 0.5) / n_cr
# モーメント法: 平均 m = a/(a+b), 分散 v = m(1-m)/(a+b+1) を解く
m_cr, v_cr = y_sq.mean(), y_sq.var()
common = m_cr * (1 - m_cr) / v_cr - 1
a_mm, b_mm = m_cr * common, (1 - m_cr) * common
a_ml, b_ml, _, _ = stats.beta.fit(y_sq, floc=0, fscale=1)
print(f"モーメント法: a = {a_mm:.3f}, b = {b_mm:.3f}")
print(f"最尤法    : a = {a_ml:.3f}, b = {b_ml:.3f}")
print(f"最尤法の平均 a/(a+b) = {a_ml / (a_ml + b_ml):.3f}  データの平均 {m_cr:.3f}")
print("\nよく現れる値（捕獲率）:", df["捕獲率"].value_counts().head(5).to_dict())
# 雄率は 0〜1 の7値しかとらず 0 と 1 もあるので、連続分布（ベータ分布）の当てはめには向かない
print("雄率の値:", sorted(df["雄率"].dropna().unique()))

fig, ax = plt.subplots(figsize=(7, 3.8))
g = np.linspace(0.001, 0.999, 400)
ax.hist(y_sq, bins=np.linspace(0, 1, 52), density=True, color=INK["grid"], label="データ（端点を寄せた後）")
ax.plot(g, stats.beta.pdf(g, a_mm, b_mm), color=PALETTE[0], label="ベータ（モーメント法）")
ax.plot(g, stats.beta.pdf(g, a_ml, b_ml), color=PALETTE[1], label="ベータ（最尤法）")
ax.set(title="捕獲率/255 とベータ分布（縦軸は8で打ち切り）", xlabel="捕獲率/255", ylabel="密度", ylim=(0, 8))
ax.legend()
plt.show()

# %% 06-5
# 一様分布: 確率積分変換 U = F(X) は、X が連続で F が真の分布関数なら U(0, 1) に従う
u_norm = stats.norm.cdf(bst, mu_b, sd_b)               # 合計種族値 × 当てはめた正規分布
u_logn = stats.lognorm.cdf(wt, sd_l, scale=np.exp(mu_l))  # 重さ × 当てはめた対数正規分布
u_expo = stats.expon.cdf(wt, scale=wt.mean())          # 重さ × 当てはめた指数分布
print("U(0, 1) の理論値: 平均 1/2 = 0.5, 分散 1/12 = 0.0833")
rows_pit = []
for name, u in [("合計種族値 × 正規", u_norm), ("重さ × 対数正規", u_logn), ("重さ × 指数", u_expo)]:
    # KS 距離 D = sup|F_n(u) - u| を定義から計算
    us = np.sort(u)
    i = np.arange(1, len(us) + 1)
    d_hand = max((i / len(us) - us).max(), (us - (i - 1) / len(us)).max())
    rows_pit.append({"組合せ": name, "平均": u.mean(), "分散": u.var(),
                     "KS距離 D（手計算）": d_hand, "KS距離 D（scipy）": stats.kstest(u, "uniform").statistic})
print(pd.DataFrame(rows_pit).round(4).to_string(index=False))

fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), sharey=True)
for ax, (name, u) in zip(axes, [("合計種族値 × 正規", u_norm), ("重さ × 対数正規", u_logn), ("重さ × 指数", u_expo)]):
    ax.hist(u, bins=20, range=(0, 1), density=True, color=PALETTE[0])
    ax.axhline(1, color=PALETTE[1], label="U(0, 1) の密度")
    ax.set(ylim=(0, 2.6), title=name, xlabel="u = F(x)（F は当てはめた分布関数）", ylabel="密度")
axes[1].legend(loc="upper center")
fig.tight_layout()
plt.show()

# %% 06-6
# 混合正規分布: 合計種族値の多峰性を EM アルゴリズムで。成分数は BIC で比べる
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")      # Windows での joblib の警告を抑える
from sklearn.mixture import GaussianMixture

X_b = bst.reshape(-1, 1)
rows_gmm, gmms = [], {}
for k in range(1, 8):
    gm = GaussianMixture(k, n_init=10, tol=1e-6, max_iter=2000, random_state=SEED).fit(X_b)
    gmms[k] = gm
    rows_gmm.append({"成分数": k, "対数尤度": gm.score(X_b) * len(X_b), "BIC": gm.bic(X_b),
                     "成分の平均（小さい順）": np.sort(gm.means_.ravel()).round(0).astype(int).tolist()})
tab_gmm = pd.DataFrame(rows_gmm).set_index("成分数")
print(tab_gmm.round(1).to_string())

# 2成分の EM を定義式どおりに実装して sklearn と比べる
pi1, m1, m2, s1, s2 = 0.5, np.percentile(bst, 25), np.percentile(bst, 75), bst.std(), bst.std()
for _ in range(2000):
    # E ステップ: 各点が成分1から来た事後確率 γ_i
    f1 = pi1 * stats.norm.pdf(bst, m1, s1)
    f2 = (1 - pi1) * stats.norm.pdf(bst, m2, s2)
    gam = f1 / (f1 + f2)
    # M ステップ: γ_i を重みにした平均・分散・混合比
    pi1 = gam.mean()
    m1, m2 = (gam * bst).sum() / gam.sum(), ((1 - gam) * bst).sum() / (1 - gam).sum()
    s1 = np.sqrt((gam * (bst - m1) ** 2).sum() / gam.sum())
    s2 = np.sqrt(((1 - gam) * (bst - m2) ** 2).sum() / (1 - gam).sum())
ll_hand = np.log(pi1 * stats.norm.pdf(bst, m1, s1) + (1 - pi1) * stats.norm.pdf(bst, m2, s2)).sum()
g2 = gmms[2]
order = np.argsort(g2.means_.ravel())
print()
print(f"手作り EM : π = ({pi1:.3f}, {1 - pi1:.3f}), μ = ({m1:.1f}, {m2:.1f}), σ = ({s1:.1f}, {s2:.1f})  対数尤度 {ll_hand:.1f}")
print(f"sklearn   : π = {g2.weights_[order].round(3)}, μ = {g2.means_.ravel()[order].round(1)},"
      f" σ = {np.sqrt(g2.covariances_.ravel()[order]).round(1)}")

best_k = int(tab_gmm["BIC"].idxmin())
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
for ax, k in zip(axes, [2, best_k]):
    gk = gmms[k]
    ax.hist(bst, bins=40, density=True, color=INK["grid"], label="データ")
    for j in np.argsort(gk.means_.ravel()):
        comp = gk.weights_[j] * stats.norm.pdf(grid_b, gk.means_[j, 0], np.sqrt(gk.covariances_[j].item()))
        ax.plot(grid_b, comp, "--", lw=1.2, color=PALETTE[0])
    ax.plot([], [], "--", lw=1.2, color=PALETTE[0], label="各成分 π_j φ_j")
    ax.plot(grid_b, np.exp(gk.score_samples(grid_b.reshape(-1, 1))), color=PALETTE[1], label="混合密度")
    ax.set(title=f"{k}成分（BIC {tab_gmm.loc[k, 'BIC']:.0f}）", xlabel="合計種族値", ylabel="密度")
    ax.legend(fontsize=8)
fig.tight_layout()
plt.show()

# %% 06-7
# 多変量正規分布: (攻撃, 特攻) に2変量正規分布を当てはめる
xy = df[["攻撃", "特攻"]].to_numpy(float)
mu_v = xy.mean(axis=0)
S_v = np.cov(xy.T, ddof=0)                             # 最尤推定（n で割る）
s1v, s2v = np.sqrt(np.diag(S_v))
rho = S_v[0, 1] / (s1v * s2v)
print(f"平均ベクトル {mu_v.round(1)}  標準偏差 ({s1v:.1f}, {s2v:.1f})  相関 ρ = {rho:.3f}")
# 1次結合 攻撃+特攻 の分散 = σ1² + σ2² + 2ρσ1σ2
print(f"V[攻撃+特攻]: 公式 {s1v**2 + s2v**2 + 2 * rho * s1v * s2v:.1f}  直接計算 {xy.sum(axis=1).var():.1f}")
# マハラノビス距離の2乗は、2変量正規なら χ²(2) に従う → 95%楕円の内側の割合
d2 = np.einsum("ij,jk,ik->i", xy - mu_v, np.linalg.inv(S_v), xy - mu_v)
print(f"95%楕円（χ²(2) の上側5%点 {stats.chi2.ppf(0.95, 2):.2f}）の内側: {(d2 <= stats.chi2.ppf(0.95, 2)).mean():.3f}")
# 条件付き分布: 特攻 | 攻撃 = x は平均 μ2 + ρ(σ2/σ1)(x - μ1)、分散 σ2²(1 - ρ²) の正規分布
bins_atk = pd.cut(df["攻撃"], [0, 50, 75, 100, 125, 200])
cond_tab = df.groupby(bins_atk, observed=True).agg(件数=("特攻", "size"), 攻撃の平均=("攻撃", "mean"),
                                                   特攻の平均=("特攻", "mean"), 特攻の分散=("特攻", "var"))
cond_tab["条件付き期待値(理論)"] = mu_v[1] + rho * s2v / s1v * (cond_tab["攻撃の平均"] - mu_v[0])
print(f"条件付き分散（理論）σ2²(1-ρ²) = {s2v**2 * (1 - rho**2):.0f}  （無条件の分散 {s2v**2:.0f}）")

fig, ax = plt.subplots(figsize=(6.5, 5))
ax.scatter(xy[:, 0], xy[:, 1], s=8, alpha=0.5, color=PALETTE[0], label="ポケモン")
gx, gy = np.meshgrid(np.linspace(0, 200, 200), np.linspace(0, 200, 200))
dens = stats.multivariate_normal(mu_v, S_v).pdf(np.dstack([gx, gy]))
cs = ax.contour(gx, gy, dens, levels=5, cmap=SEQ_CMAP)
xl = np.array([0, 200])
ax.plot(xl, mu_v[1] + rho * s2v / s1v * (xl - mu_v[0]), color=PALETTE[1], label="E[特攻 | 攻撃]（2変量正規）")
ax.set(title="攻撃と特攻の2変量正規分布の等高線", xlabel="攻撃（種族値）", ylabel="特攻（種族値）", xlim=(0, 200), ylim=(0, 200))
ax.legend(loc="upper left")
plt.show()
cond_tab.round(1)

# %% 06-8
# 標本分布（χ² 分布）: 全ポケモンを母集団とみなし、大きさ n の標本を繰り返し抽出する
# 復元抽出なので各標本は母集団分布からの i.i.d. 標本。母分散は n ではなく N で割った値（ddof=0）
def draw_samples_06(values, n, reps, rng):
    """母集団 values から大きさ n の標本を reps 組、復元抽出した (reps, n) 配列."""
    return values[rng.integers(0, len(values), size=(reps, n))]

rng = get_rng()
n_s, reps_s = 10, 5000
pops_06 = {"合計種族値": bst, "重さ": wt}
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
for ax, (name, pop) in zip(axes, pops_06.items()):
    sig2 = pop.var(ddof=0)
    kappa = stats.kurtosis(pop)                         # 母集団の尖度（正規なら0）
    smp = draw_samples_06(pop, n_s, reps_s, rng)
    W = (n_s - 1) * smp.var(axis=1, ddof=1) / sig2      # 正規母集団なら χ²(n-1)
    # 非正規母集団での理論分散: V[S²] = σ⁴(2/(n-1) + κ/n) より V[W] = (n-1)²(2/(n-1) + κ/n)
    print(f"{name}: 尖度 κ = {kappa:.2f}  W の平均 {W.mean():.2f}（χ² の理論 {n_s - 1}）"
          f"  分散 {W.var():.1f}（χ² の理論 {2 * (n_s - 1)}、尖度を考慮 {(n_s - 1) ** 2 * (2 / (n_s - 1) + kappa / n_s):.1f}）"
          f"  P(W > χ²_0.05(9)) = {(W > stats.chi2.ppf(0.95, n_s - 1)).mean():.3f}")
    xmax = np.percentile(W, 99)
    ax.hist(W[W <= xmax], bins=50, density=True, color=PALETTE[0], label="シミュレーション（上位1%は省略）")
    g = np.linspace(0.01, xmax, 300)
    ax.plot(g, stats.chi2.pdf(g, n_s - 1), color=PALETTE[1], label=f"χ²({n_s - 1})")
    ax.set(title=f"{name}: (n-1)S²/σ²（n = {n_s}）", xlabel="(n-1)S²/σ²", ylabel="密度")
    ax.legend(fontsize=8)
fig.tight_layout()
plt.show()

# %% 06-9
# 標本分布（t 分布）: T = (X̄ - μ)/(S/√n) を t(n-1) と比べる
rng = get_rng()
t_crit = stats.t.ppf(0.975, n_s - 1)
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
rows_t = []
for ax, (name, pop) in zip(axes, pops_06.items()):
    smp = draw_samples_06(pop, n_s, reps_s, rng)
    T = (smp.mean(axis=1) - pop.mean()) / (smp.std(axis=1, ddof=1) / np.sqrt(n_s))
    rows_t.append({"母集団": name, "P(T < -t)": (T < -t_crit).mean(), "P(T > t)": (T > t_crit).mean(),
                   "理論（各側）": 0.025, "T の平均": T.mean()})
    g = np.linspace(-6, 6, 300)
    # |T| ≥ 6 は表示しないが、密度は全 reps_s 回で割る（表示範囲だけで正規化すると高さが水増しされる）
    T_in = T[(T > -6) & (T < 6)]
    ax.hist(T_in, bins=60, range=(-6, 6), weights=np.full(len(T_in), 1 / (reps_s * 0.2)), color=PALETTE[0],
            label=f"シミュレーション（|T| ≥ 6 の {1 - len(T_in) / reps_s:.1%} は範囲外）")
    ax.plot(g, stats.t.pdf(g, n_s - 1), color=PALETTE[1], label=f"t({n_s - 1})")
    ax.set(title=f"{name}: t 統計量（n = {n_s}）", xlabel="T =（標本平均 − μ）/（S/√n）", ylabel="密度")
    ax.legend(fontsize=8)
fig.tight_layout()
plt.show()
print(f"t_0.025({n_s - 1}) = {t_crit:.3f}")
pd.DataFrame(rows_t).round(4)

# %% 06-10
# 標本分布（F 分布）: 同じ母集団からの独立な2標本の分散比 F = S1²/S2² を F(n1-1, n2-1) と比べる
rng = get_rng()
n1_f, n2_f = 10, 15
f_crit = stats.f.ppf(0.95, n1_f - 1, n2_f - 1)
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
rows_f = []
for ax, (name, pop) in zip(axes, pops_06.items()):
    s1_sq = draw_samples_06(pop, n1_f, reps_s, rng).var(axis=1, ddof=1)
    s2_sq = draw_samples_06(pop, n2_f, reps_s, rng).var(axis=1, ddof=1)
    Fv = s1_sq / s2_sq                                  # 同じ母集団なので σ1² = σ2² が約分される
    rows_f.append({"母集団": name, "P(F > F_0.05)": (Fv > f_crit).mean(), "理論": 0.05,
                   "F の中央値": np.median(Fv), "理論の中央値": stats.f.median(n1_f - 1, n2_f - 1)})
    g = np.linspace(0.01, 6, 300)
    # F ≥ 6 は表示しないが、密度は全 reps_s 回で割る（表示範囲だけで正規化すると高さが水増しされる）
    F_in = Fv[Fv < 6]
    ax.hist(F_in, bins=60, range=(0, 6), weights=np.full(len(F_in), 1 / (reps_s * 0.1)), color=PALETTE[0],
            label=f"シミュレーション（F ≥ 6 の {1 - len(F_in) / reps_s:.1%} は範囲外）")
    ax.plot(g, stats.f.pdf(g, n1_f - 1, n2_f - 1), color=PALETTE[1], label=f"F({n1_f - 1}, {n2_f - 1})")
    ax.set(title=f"{name}: 分散比（n1 = {n1_f}, n2 = {n2_f}）", xlabel="F = S1²/S2²", ylabel="密度")
    ax.legend(fontsize=8)
fig.tight_layout()
plt.show()
print(f"F_0.05({n1_f - 1}, {n2_f - 1}) = {f_crit:.3f}")
pd.DataFrame(rows_f).round(4)
