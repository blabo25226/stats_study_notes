"""第29章 不完全データの統計処理."""
from poke import *

df = load_data()

# %% 29-0
from scipy import optimize
from scipy.special import expit

miss_cols = ["攻撃", "素早", "防御", "HP", "捕獲率", "雄率"]
print(df[miss_cols].describe().T[["count", "mean", "std", "min", "max"]].round(1))
print(f"\n捕獲率 = 255（上限）の行: {(df['捕獲率'] == 255).sum()} 匹, 捕獲率 = 3（下限）の行: {(df['捕獲率'] == 3).sum()} 匹")
print(f"雄率の欠損: {df['雄率'].isna().sum()} 行")

# %% 29-1
# 捕獲率の分布: 値域の上限255と下限3に度数が集中する
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.hist(df["捕獲率"], bins=np.arange(0, 265, 10), color=PALETTE[0])
ax.axvline(255, color=INK["secondary"], lw=1, ls="--")
ax.text(250, ax.get_ylim()[1] * 0.9, "上限255", ha="right", fontsize=9)
ax.set(title="捕獲率の分布", xlabel="捕獲率（3〜255）", ylabel="匹数")
fig.tight_layout()
plt.show()

# %% 29-2
# 1変量正規分布の打ち切り・トランケーション: 素早を c = 100 で人工的に欠測させる
spe = df["素早"].to_numpy(float)
c_cut = 100.0
sigma_known = spe.std()            # 母分散は既知とする（全データの値）
mu_true = spe.mean()
obs_spe = spe[spe < c_cut]         # c 未満だけ値が観測される
n_all, m_obs = len(spe), len(obs_spe)
print(f"真の平均 {mu_true:.2f}, 既知とする σ = {sigma_known:.2f}")
print(f"c = {c_cut:.0f} 未満が観測: m = {m_obs}, 欠測 n-m = {n_all - m_obs}, 観測値の平均 {obs_spe.mean():.2f}")


def mle_censored(x_obs, n, c, sigma, tol=1e-10, max_iter=500):
    """打ち切り（c 以上は個数だけわかる）での μ の最尤推定（EM 反復）."""
    mu, path = x_obs.mean(), []
    for _ in range(max_iter):
        a = (c - mu) / sigma
        e_tail = mu + sigma * stats.norm.pdf(a) / stats.norm.sf(a)     # E[X | X >= c]
        mu_new = (x_obs.sum() + (n - len(x_obs)) * e_tail) / n
        path.append(mu_new)
        if abs(mu_new - mu) < tol:
            break
        mu = mu_new
    return mu_new, np.array(path)


def mle_truncated(x_obs, c, sigma, tol=1e-10, max_iter=5000):
    """トランケーション（c 以上は個数もわからない）での μ の最尤推定（不動点反復）."""
    mu, path, xbar = x_obs.mean(), [], x_obs.mean()
    for _ in range(max_iter):
        a = (c - mu) / sigma
        mu_new = xbar + sigma * stats.norm.pdf(a) / stats.norm.cdf(a)   # x̄ = E[X | X < c] を解く
        path.append(mu_new)
        if abs(mu_new - mu) < tol:
            break
        mu = mu_new
    return mu_new, np.array(path)


mu_cen, path_cen = mle_censored(obs_spe, n_all, c_cut, sigma_known)
mu_tru, path_tru = mle_truncated(obs_spe, c_cut, sigma_known)

# 対数尤度を直接最大化して照合
ll_cen = lambda mu: -(stats.norm.logpdf(obs_spe, mu, sigma_known).sum()
                      + (n_all - m_obs) * stats.norm.logsf(c_cut, mu, sigma_known))
ll_tru = lambda mu: -(stats.norm.logpdf(obs_spe, mu, sigma_known).sum()
                      - m_obs * stats.norm.logcdf(c_cut, mu, sigma_known))
opt_cen = optimize.minimize_scalar(ll_cen, bounds=(0, 200), method="bounded").x
opt_tru = optimize.minimize_scalar(ll_tru, bounds=(0, 200), method="bounded").x
print(f"\n打ち切り:        反復 {len(path_cen)} 回で μ̂ = {mu_cen:.3f}（直接最大化 {opt_cen:.3f}）")
print(f"トランケーション: 反復 {len(path_tru)} 回で μ̂ = {mu_tru:.3f}（直接最大化 {opt_tru:.3f}）")

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(np.arange(len(path_cen) + 1), np.r_[obs_spe.mean(), path_cen], marker="o", ms=3, label="打ち切り")
ax.plot(np.arange(len(path_tru) + 1), np.r_[obs_spe.mean(), path_tru], marker="o", ms=3, label="トランケーション")
ax.axhline(mu_true, color=INK["muted"], ls="--", lw=1, label="全データの平均")
ax.set(title="素早の平均の最尤推定: 反復の収束", xlabel="反復回数 t", ylabel="μ(t)（素早）",
       xlim=(-0.5, min(max(len(path_cen), len(path_tru)), 40) + 0.5))
ax.legend()
fig.tight_layout()
plt.show()

# %% 29-3
# 雄率の欠損は「性別不明」と完全に一致する構造的欠損
print(pd.crosstab(df["性別"], df["雄率"].isna().rename("雄率が欠損")))

# 人工的な欠測: 攻撃を平均20%欠測させる 3 つのメカニズム
def make_missing(data, mech, rng, rate=0.2, slope=1.5):
    """攻撃を欠測させる指標（True = 欠測）を返す."""
    n = len(data)
    if mech == "MCAR":
        return rng.random(n) < rate
    z_src = data["素早"] if mech == "MAR" else data["攻撃"]      # MNAR は欠測する値そのものに依存
    z = ((z_src - z_src.mean()) / z_src.std()).to_numpy()
    b0 = optimize.brentq(lambda b: expit(b + slope * z).mean() - rate, -10, 10)   # 平均欠測率を rate に合わせる
    return rng.random(n) < expit(b0 + slope * z)


rng_demo = get_rng()
mech_list = ["MCAR", "MAR", "MNAR"]
demo_rows = []
for mech in mech_list:
    r_miss = make_missing(df, mech, rng_demo)
    demo_rows.append({
        "メカニズム": mech, "欠測率": r_miss.mean(),
        "観測された攻撃の平均": df.loc[~r_miss, "攻撃"].mean(),
        "素早の平均(欠測群)": df.loc[r_miss, "素早"].mean(),
        "素早の平均(観測群)": df.loc[~r_miss, "素早"].mean(),
        "素早の差のt検定 p値": stats.ttest_ind(df.loc[r_miss, "素早"], df.loc[~r_miss, "素早"]).pvalue,
    })
print(f"\n全データの攻撃の平均（真値）: {df['攻撃'].mean():.2f}")
pd.DataFrame(demo_rows).set_index("メカニズム").round(3)

# %% 29-4
# 欠測への対処法を1組のデータで比較（MAR）。多重代入はルービンのルールで統合する
def ols(X, y):
    """最小二乗: 係数, 残差分散（自由度 n-p）, (X'X)^{-1}."""
    xtx_inv = np.linalg.inv(X.T @ X)
    beta = xtx_inv @ X.T @ y
    resid = y - X @ beta
    return beta, resid @ resid / (len(y) - X.shape[1]), xtx_inv


def estimate(y, x):
    """解析モデル: 攻撃の平均と、攻撃 = b0 + b1 素早 の傾き。(推定値, 標準誤差) を返す."""
    n = len(y)
    X = np.column_stack([np.ones(n), x])
    beta, s2, xtx_inv = ols(X, y)
    return np.array([y.mean(), beta[1]]), np.array([y.std(ddof=1) / np.sqrt(n), np.sqrt(s2 * xtx_inv[1, 1])])


def rubin(q_list, u_list):
    """ルービンのルール: 推定値, 全分散の平方根, 自由度, 欠測情報の割合の近似."""
    q, u = np.asarray(q_list), np.asarray(u_list)
    M = len(q)
    q_bar = q.mean(0)
    w_bar = u.mean(0)                        # 代入内分散
    b_var = q.var(0, ddof=1)                 # 代入間分散
    t_var = w_bar + (1 + 1 / M) * b_var      # 全分散
    r_inc = (1 + 1 / M) * b_var / w_bar
    nu = (M - 1) * (1 + 1 / r_inc) ** 2      # 自由度
    return q_bar, np.sqrt(t_var), nu, (1 + 1 / M) * b_var / t_var


def run_methods(data, miss, rng, n_imp=20):
    """各手法で (推定値, SE, 自由度) を返す。自由度 np.inf は正規近似."""
    y_full, x_ana = data["攻撃"].to_numpy(float), data["素早"].to_numpy(float)
    Z = np.column_stack([np.ones(len(data)), data[["素早", "防御", "HP"]].to_numpy(float)])   # 代入モデルの説明変数
    obs = ~miss
    out = {"完全データ": (*estimate(y_full, x_ana), np.inf),
           "CC解析": (*estimate(y_full[obs], x_ana[obs]), np.inf)}
    y_mean = y_full.copy(); y_mean[miss] = y_full[obs].mean()
    out["平均値代入"] = (*estimate(y_mean, x_ana), np.inf)
    g, s2, zz_inv = ols(Z[obs], y_full[obs])
    y_reg = y_full.copy(); y_reg[miss] = Z[miss] @ g
    out["回帰代入"] = (*estimate(y_reg, x_ana), np.inf)
    y_sto = y_reg.copy(); y_sto[miss] += rng.normal(0, np.sqrt(s2), miss.sum())
    out["確率的回帰代入"] = (*estimate(y_sto, x_ana), np.inf)
    # 多重代入: パラメータの不確実性も反映する（σ² と係数を事後分布から引き直す）
    dof_imp = obs.sum() - Z.shape[1]
    L = np.linalg.cholesky(zz_inv)
    q_list, u_list = [], []
    for _ in range(n_imp):
        s2_star = s2 * dof_imp / rng.chisquare(dof_imp)
        g_star = g + np.sqrt(s2_star) * L @ rng.standard_normal(Z.shape[1])
        y_imp = y_full.copy()
        y_imp[miss] = Z[miss] @ g_star + rng.normal(0, np.sqrt(s2_star), miss.sum())
        est, se = estimate(y_imp, x_ana)
        q_list.append(est); u_list.append(se ** 2)
    q_bar, t_se, nu, lam = rubin(q_list, u_list)
    out["多重代入"] = (q_bar, t_se, nu)
    return out, lam


rng_one = get_rng()
samp_one = df.iloc[rng_one.choice(len(df), 300, replace=True)].reset_index(drop=True)
miss_one = make_missing(samp_one, "MAR", rng_one)
res_one, lam_one = run_methods(samp_one, miss_one, rng_one)
one_table = pd.DataFrame({
    "平均 推定値": [v[0][0] for v in res_one.values()], "平均 SE": [v[1][0] for v in res_one.values()],
    "傾き 推定値": [v[0][1] for v in res_one.values()], "傾き SE": [v[1][1] for v in res_one.values()],
}, index=res_one.keys())
print(f"n = 300（復元抽出）, 欠測 {miss_one.sum()} 行（MAR）")
print(f"多重代入（M = 20）の欠測情報の割合の近似: 平均 {lam_one[0]:.2f}, 傾き {lam_one[1]:.2f}")
one_table.round(3)

# %% 29-5
# 反復シミュレーション: 母集団（920匹）から n = 300 を復元抽出 → 欠測 → 各手法で推定
X_pop = np.column_stack([np.ones(len(df)), df["素早"]])
true_vals = np.array([df["攻撃"].mean(), np.linalg.lstsq(X_pop, df["攻撃"].to_numpy(float), rcond=None)[0][1]])
print(f"真値: 攻撃の平均 {true_vals[0]:.3f}, 攻撃〜素早の傾き {true_vals[1]:.4f}")

rng_sim = get_rng()
n_sim, n_samp = 500, 300
sim_rows = []
for mech in mech_list:
    for _ in range(n_sim):
        samp = df.iloc[rng_sim.choice(len(df), n_samp, replace=True)].reset_index(drop=True)
        res, _ = run_methods(samp, make_missing(samp, mech, rng_sim), rng_sim, n_imp=10)
        for meth, (est, se, nu) in res.items():
            crit = stats.t.ppf(0.975, nu) if np.all(np.isfinite(nu)) else stats.norm.ppf(0.975)
            for k, target in enumerate(["平均", "傾き"]):
                c_k = crit[k] if np.ndim(crit) else crit
                sim_rows.append((mech, meth, target, est[k], se[k], abs(est[k] - true_vals[k]) <= c_k * se[k]))
sim_df = pd.DataFrame(sim_rows, columns=["メカニズム", "手法", "推定対象", "推定値", "SE", "被覆"])
truth_map = dict(zip(["平均", "傾き"], true_vals))
sim_df["偏り"] = sim_df["推定値"] - sim_df["推定対象"].map(truth_map)
method_order = list(res.keys())
sim_df["推定対象"] = pd.Categorical(sim_df["推定対象"], ["平均", "傾き"])
sim_df["メカニズム"] = pd.Categorical(sim_df["メカニズム"], mech_list)
sim_df["手法"] = pd.Categorical(sim_df["手法"], method_order)
sim_summary = (sim_df.groupby(["推定対象", "メカニズム", "手法"], observed=True)
               .agg(偏り=("偏り", "mean"), 推定値のSD=("推定値", "std"), SEの平均=("SE", "mean"), 被覆率=("被覆", "mean")))
sim_summary.round(3)

# %% 29-6
# シミュレーション結果の図: 偏り ± 推定値のSD
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
ypos = np.arange(len(method_order))
for ax, target, unit in zip(axes, ["平均", "傾き"], ["攻撃", "攻撃/素早"]):
    for j, mech in enumerate(mech_list):
        s = sim_summary.loc[(target, mech)].reindex(method_order)
        ax.errorbar(s["偏り"], ypos + (j - 1) * 0.22, xerr=s["推定値のSD"], fmt="o", ms=5,
                    color=PALETTE[j], capsize=0, lw=1.5, label=mech)
    ax.axvline(0, color=INK["muted"], lw=1)
    ax.set(title=f"攻撃の{target}の推定: 偏り ± SD", xlabel=f"推定値 − 真値（{unit}）")
    ax.set_yticks(ypos, method_order)
axes[0].invert_yaxis()
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, title="欠測メカニズム", loc="lower center", ncol=3)
fig.tight_layout(rect=(0, 0.1, 1, 1))
plt.show()

# %% 29-7
# 2変量正規分布で Y（攻撃）だけが MAR で欠測するときの最尤推定: 閉形式と EM アルゴリズム
rng_bv = get_rng()
x_bv = df["素早"].to_numpy(float)
y_bv = df["攻撃"].to_numpy(float)
miss_bv = make_missing(df, "MAR", rng_bv)
obs_bv = ~miss_bv
n_bv, m_bv = len(x_bv), obs_bv.sum()
xo, yo = x_bv[obs_bv], y_bv[obs_bv]

# 閉形式（最尤推定なので分母は n, m）
mu_x = x_bv.mean(); s2_x = x_bv.var()                       # ① X は n 個すべて使う
xbar_m, ybar_m = xo.mean(), yo.mean()                       # ② 観測された m 組
sxx_m, syy_m = xo.var(), yo.var()
sxy_m = np.mean((xo - xbar_m) * (yo - ybar_m))
beta_ml = sxy_m / sxx_m                                     # ③ Y|X ~ N(α + βx, τ²)
alpha_ml = ybar_m - beta_ml * xbar_m
tau2_ml = syy_m - beta_ml ** 2 * sxx_m
mu_y_ml = alpha_ml + beta_ml * mu_x                         # ④
s2_y_ml = tau2_ml + beta_ml ** 2 * s2_x
sxy_ml = beta_ml * s2_x


def em_bivariate(x, y, obs, n_iter=200, tol=1e-12):
    """Y のみ欠測する2変量正規分布の EM アルゴリズム。各反復の (μY, σY², σXY, 観測データ対数尤度)."""
    n = len(x)
    mu = np.array([x.mean(), y[obs].mean()])                # 初期値: CC の平均・分散（相関0）
    cov = np.diag([x.var(), y[obs].var()])
    hist = []
    for _ in range(n_iter):
        # E ステップ: 欠測した y の条件付き期待値 E[y|x], E[y²|x]
        b = cov[0, 1] / cov[0, 0]
        a = mu[1] - b * mu[0]
        t2 = cov[1, 1] - b * cov[0, 1]
        ey = np.where(obs, y, a + b * x)
        ey2 = np.where(obs, y ** 2, (a + b * x) ** 2 + t2)
        # M ステップ: 十分統計量の期待値から平均と共分散を更新
        mu_new = np.array([x.mean(), ey.mean()])
        cov_new = np.array([[np.mean(x ** 2), np.mean(x * ey)],
                            [np.mean(x * ey), np.mean(ey2)]]) - np.outer(mu_new, mu_new)
        # 観測データの対数尤度（x は周辺、観測された y は条件付き）
        b2 = cov_new[0, 1] / cov_new[0, 0]
        a2 = mu_new[1] - b2 * mu_new[0]
        t22 = cov_new[1, 1] - b2 * cov_new[0, 1]
        ll = (stats.norm.logpdf(x, mu_new[0], np.sqrt(cov_new[0, 0])).sum()
              + stats.norm.logpdf(y[obs], a2 + b2 * x[obs], np.sqrt(t22)).sum())
        hist.append((mu_new[1], cov_new[1, 1], cov_new[0, 1], ll))
        done = np.max(np.abs(mu_new - mu)) < tol and np.max(np.abs(cov_new - cov)) < tol
        mu, cov = mu_new, cov_new
        if done:
            break
    return np.array(hist)


em_hist = em_bivariate(x_bv, y_bv, obs_bv)
bv_table = pd.DataFrame({
    "全データ(真値)": [y_bv.mean(), y_bv.var(), np.mean((x_bv - x_bv.mean()) * (y_bv - y_bv.mean()))],
    "CC解析": [ybar_m, syy_m, sxy_m],
    "最尤(閉形式)": [mu_y_ml, s2_y_ml, sxy_ml],
    "最尤(EM)": em_hist[-1, :3],
}, index=["μY", "σY²", "σXY"])
print(f"n = {n_bv}, Y が観測された m = {m_bv}（MAR: 素早が大きいほど欠測しやすい）")
print(f"EM は {len(em_hist)} 回で収束。対数尤度は単調非減少: {np.all(np.diff(em_hist[:, 3]) >= -1e-8)}")
print(bv_table.round(3))

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].plot(np.arange(1, len(em_hist) + 1), em_hist[:, 0], marker="o", ms=3, color=PALETTE[0], label="EM の μY(t)")
axes[0].axhline(mu_y_ml, color=PALETTE[1], ls="--", lw=1.5, label="最尤推定（閉形式）")
axes[0].axhline(ybar_m, color=INK["muted"], ls=":", lw=1.5, label="CC解析の平均")
axes[0].set(title="攻撃の平均 μY の EM 反復", xlabel="反復回数 t", ylabel="μY(t)（攻撃）")
axes[0].legend()
err = np.abs(em_hist[:, 0] - mu_y_ml)
axes[1].semilogy(np.arange(1, len(em_hist) + 1), np.maximum(err, 1e-14), marker="o", ms=3, color=PALETTE[0])
axes[1].set(title="閉形式の最尤推定との差", xlabel="反復回数 t", ylabel="|μY(t) − 閉形式の値|（攻撃, 対数軸）")
fig.tight_layout()
plt.show()
