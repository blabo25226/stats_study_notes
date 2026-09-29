"""第31章 ベイズ法."""
from poke import *

df = load_data()

# %% 31-0
from scipy import optimize, special
import statsmodels.api as sm

# 真値（全920行を母集団とみなしたときの値）
bayes_true = {
    "いわタイプを含む割合": types_of(df, "いわ").mean(),
    "複合タイプの割合": df["複合タイプ"].mean(),
    "性別不明の割合": df["雄率"].isna().mean(),
    "素早の平均": df["素早"].mean(),
    "素早の分散（母分散）": df["素早"].var(ddof=0),
}
print(pd.Series(bayes_true).round(4).to_string())

# 図鑑番号ごとの姿違いの数（行数 − 1）
forms_per_no = df.groupby("図鑑番号").size() - 1
print("\n図鑑番号ごとの姿違いの数（件数）")
print(forms_per_no.value_counts().sort_index().to_string())

# タイプ1ごとの件数と合計種族値の平均
print("\nタイプ1ごとの件数（少ない順に5つ）")
print(df["タイプ1"].value_counts().sort_values().head().to_string())


# %% 31-1
# ベータ二項モデル: 20匹の標本から「いわタイプを含む割合」を推定する
rng_bb = get_rng()
n_rock = 20
idx_rock = rng_bb.integers(0, len(df), n_rock)          # 母集団からの復元抽出（i.i.d.）
y_rock = int(types_of(df, "いわ").to_numpy()[idx_rock].sum())
print(f"標本 n={n_rock} 中のいわタイプ: y={y_rock}")

priors_rock = {
    "一様 Be(1,1)": (1, 1),
    "ジェフリーズ Be(0.5,0.5)": (0.5, 0.5),
    "弱い事前知識 Be(2,18)": (2, 18),
    "誤った強い事前 Be(40,60)": (40, 60),
}
rows = []
for name, (a0, b0) in priors_rock.items():
    a1, b1 = a0 + y_rock, b0 + n_rock - y_rock          # 事後分布 Be(a+y, b+n-y)
    post = stats.beta(a1, b1)
    rows.append({"事前分布": name, "事前平均": a0 / (a0 + b0),
                 "事後分布": f"Be({a1:g},{b1:g})", "事後平均": a1 / (a1 + b1),
                 "MAP": (a1 - 1) / (a1 + b1 - 2) if (a1 > 1 and b1 > 1) else np.nan,
                 "95%下限": post.ppf(0.025), "95%上限": post.ppf(0.975)})
print(f"最尤推定値 y/n = {y_rock / n_rock:.3f}, 真値 = {bayes_true['いわタイプを含む割合']:.3f}")

grid_p = np.linspace(0.0005, 0.9995, 1000)
fig, axes = plt.subplots(2, 2, figsize=(10, 6), sharex=True)
for ax, (name, (a0, b0)) in zip(axes.ravel(), priors_rock.items()):
    ax.plot(grid_p, stats.beta(a0, b0).pdf(grid_p), color=PALETTE[1], ls="--", lw=1.5, label="事前分布")
    ax.plot(grid_p, stats.beta(a0 + y_rock, b0 + n_rock - y_rock).pdf(grid_p), color=PALETTE[0], label="事後分布")
    ax.axvline(bayes_true["いわタイプを含む割合"], color=INK["muted"], lw=1, label="真値")
    ax.set(title=name, xlabel="いわタイプを含む割合 θ", ylabel="確率密度", xlim=(0, 0.8))
    ax.set_ylim(0, min(ax.get_ylim()[1], 20))
axes[0, 0].legend()
fig.tight_layout()
plt.show()
pd.DataFrame(rows).round(3)


# %% 31-2
# 標本サイズを増やすと事後分布が真値に集中する（複合タイプの割合, 事前分布 Be(1,1)）
rng_conc = get_rng()
dual_all = df["複合タイプ"].to_numpy()
seq_dual = dual_all[rng_conc.integers(0, len(df), 2560)]  # 1本の i.i.d. 列の先頭 n 個を使う
n_list = [10, 40, 160, 640, 2560]
conc_rows = []
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for k, n in enumerate(n_list):
    y = int(seq_dual[:n].sum())
    post = stats.beta(1 + y, 1 + n - y)
    conc_rows.append({"n": n, "y": y, "事後平均": post.mean(), "事後標準偏差": post.std(),
                      "sqrt(p(1-p)/n)": np.sqrt((y / n) * (1 - y / n) / n),   # p = y/n
                      "95%下限": post.ppf(0.025), "95%上限": post.ppf(0.975)})
    axes[0].plot(grid_p, post.pdf(grid_p), color=SEQ_CMAP(0.25 + 0.75 * k / (len(n_list) - 1)), label=f"n={n}")
axes[0].axvline(bayes_true["複合タイプの割合"], color=INK["muted"], lw=1, label="真値")
axes[0].set(title="事後分布 Be(1+y, 1+n−y)", xlabel="複合タイプの割合 θ", ylabel="確率密度", xlim=(0.2, 0.9))
axes[0].legend()
conc = pd.DataFrame(conc_rows)
axes[1].fill_between(conc["n"], conc["95%下限"], conc["95%上限"], color=PALETTE[0], alpha=0.2, label="95%信用区間")
axes[1].plot(conc["n"], conc["事後平均"], marker="o", color=PALETTE[0], label="事後平均")
axes[1].axhline(bayes_true["複合タイプの割合"], color=INK["muted"], lw=1, label="真値")
axes[1].set(xscale="log", title="標本サイズと事後分布の集中", xlabel="標本サイズ n（対数目盛）", ylabel="複合タイプの割合 θ")
axes[1].legend()
fig.tight_layout()
plt.show()
conc.round(4)


# %% 31-3
# 点推定・信用区間（等裾・HPD）・ベイズ予測分布（31-1 の標本, 事前分布 Be(1,1)）
a_post, b_post = 1 + y_rock, 1 + n_rock - y_rock
post_rock = stats.beta(a_post, b_post)
print(f"事後分布 Be({a_post}, {b_post})")
print(f"ベイズ推定量（事後平均） a/(a+b)       = {a_post / (a_post + b_post):.4f}")
print(f"MAP推定量（事後モード） (a-1)/(a+b-2) = {(a_post - 1) / (a_post + b_post - 2):.4f}  (= 最尤推定値 {y_rock / n_rock:.4f})")

# 等裾信用区間: 両側に 2.5% ずつ
et_lo, et_hi = post_rock.ppf([0.025, 0.975])
# HPD 区間: 確率 0.95 を含む区間のうち幅が最小のもの（単峰なので下側確率 q を動かして幅を最小化）
res_hpd = optimize.minimize_scalar(lambda q: post_rock.ppf(q + 0.95) - post_rock.ppf(q),
                                   bounds=(0, 0.05), method="bounded")
hpd_lo, hpd_hi = post_rock.ppf([res_hpd.x, res_hpd.x + 0.95])
print(f"95%等裾区間: [{et_lo:.4f}, {et_hi:.4f}]  幅 {et_hi - et_lo:.4f}")
print(f"95%HPD区間 : [{hpd_lo:.4f}, {hpd_hi:.4f}]  幅 {hpd_hi - hpd_lo:.4f}")
print(f"  HPD の両端の密度: {post_rock.pdf(hpd_lo):.3f}, {post_rock.pdf(hpd_hi):.3f}（等しい）")

# ベイズ予測分布: 次に m 匹選んだときのいわタイプの数（ベータ二項分布）
m_new = 20
k_new = np.arange(m_new + 1)
# 定義式: P(k) = C(m,k) B(a+k, b+m-k) / B(a, b)
pred_hand = special.comb(m_new, k_new) * np.exp(special.betaln(a_post + k_new, b_post + m_new - k_new)
                                                 - special.betaln(a_post, b_post))
pred_scipy = stats.betabinom(m_new, a_post, b_post).pmf(k_new)
print(f"\n予測分布: 手計算と scipy.stats.betabinom の最大差 {np.abs(pred_hand - pred_scipy).max():.1e}")
plug_in = stats.binom(m_new, a_post / (a_post + b_post)).pmf(k_new)   # 事後平均を代入しただけの二項分布
print(f"予測分布の分散: ベイズ予測 {stats.betabinom(m_new, a_post, b_post).var():.3f}"
      f"  / 代入法の二項分布 {stats.binom(m_new, a_post / (a_post + b_post)).var():.3f}")

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].plot(grid_p, post_rock.pdf(grid_p), color=PALETTE[0])
axes[0].axvspan(et_lo, et_hi, color=PALETTE[1], alpha=0.15, label="95%等裾区間")
axes[0].hlines(post_rock.pdf(hpd_lo), hpd_lo, hpd_hi, color=PALETTE[2], lw=3, label="95%HPD区間")
axes[0].axvline(a_post / (a_post + b_post), color=PALETTE[0], ls="--", lw=1, label="事後平均")
axes[0].axvline((a_post - 1) / (a_post + b_post - 2), color=INK["muted"], ls=":", lw=1.5, label="MAP")
axes[0].set(title=f"事後分布 Be({a_post},{b_post}) と信用区間", xlabel="いわタイプを含む割合 θ", ylabel="確率密度", xlim=(0, 0.6))
axes[0].legend()
w = 0.4
axes[1].bar(k_new - w / 2, pred_scipy, width=w, color=PALETTE[0], label="ベイズ予測分布（ベータ二項）")
axes[1].bar(k_new + w / 2, plug_in, width=w, color=PALETTE[1], label="代入法 Bin(m, 事後平均)")
axes[1].set(title=f"次の{m_new}匹に含まれるいわタイプの数", xlabel="いわタイプの匹数", ylabel="確率", xlim=(-0.8, 14.8))
axes[1].legend()
fig.tight_layout()
plt.show()


# %% 31-4
# ガンマ・ポアソンモデル: 図鑑番号ごとの姿違いの数
rng_gp = get_rng()
n_gp = 100
y_gp = forms_per_no.to_numpy()[rng_gp.integers(0, len(forms_per_no), n_gp)]
print(f"標本 n={n_gp} 種の姿違いの数: 合計 {y_gp.sum()}, 平均 {y_gp.mean():.3f}")
print(f"母集団（全{len(forms_per_no)}種）: 平均 {forms_per_no.mean():.3f}, 分散 {forms_per_no.var(ddof=0):.3f}"
      f"（分散/平均 = {forms_per_no.var(ddof=0) / forms_per_no.mean():.2f}）")

# 事前分布 Ga(a, 1/b)（形状 a, 尺度 1/b, 平均 a/b）→ 事後分布 Ga(a + Σy, 1/(b + n))
gp_rows = []
for name, (a0, b0) in {"弱い事前 Ga(1, 1/1)": (1, 1), "情報のある事前 Ga(2, 1/10)": (2, 10)}.items():
    a1, b1 = a0 + y_gp.sum(), b0 + n_gp
    post = stats.gamma(a1, scale=1 / b1)
    gp_rows.append({"事前分布": name, "事前平均 a/b": a0 / b0, "事後分布": f"Ga({a1}, 1/{b1})",
                    "事後平均 a/b": a1 / b1, "MAP (a-1)/b": (a1 - 1) / b1 if a1 > 1 else np.nan,
                    "95%下限": post.ppf(0.025), "95%上限": post.ppf(0.975)})
gp_table = pd.DataFrame(gp_rows)

# 予測分布（事前 Ga(1,1)）: 負の二項分布 NB(a, b/(b+1))。母集団の分布と比較する
a1, b1 = 1 + y_gp.sum(), 1 + n_gp
k_gp = np.arange(6)
pred_gp = stats.nbinom(a1, b1 / (b1 + 1)).pmf(k_gp)
pop_gp = forms_per_no.value_counts(normalize=True).reindex(k_gp, fill_value=0).to_numpy()
fig, ax = plt.subplots(figsize=(7, 4))
w = 0.4
ax.bar(k_gp - w / 2, pred_gp, width=w, color=PALETTE[0], label="ベイズ予測分布（負の二項）")
ax.bar(k_gp + w / 2, pop_gp, width=w, color=PALETTE[1], label="母集団の相対度数")
ax.set(title="1種あたりの姿違いの数: 予測分布と母集団", xlabel="姿違いの数", ylabel="確率（対数目盛）", yscale="log")
ax.legend()
fig.tight_layout()
plt.show()
print(pd.DataFrame({"予測分布": pred_gp, "母集団": pop_gp}, index=k_gp).round(4).to_string())
gp_table.round(4)


# %% 31-5
# 正規-正規モデルによる経験ベイズ（タイプ1別の合計種族値の平均の縮小推定）
eb = df.groupby("タイプ1", observed=True)["合計種族値"].agg(n="count", 標本平均="mean", 分散="var")
# 群内の分散はプールした値 σ² を既知とみなす
sigma2_eb = ((eb["n"] - 1) * eb["分散"]).sum() / (eb["n"] - 1).sum()
se2_eb = sigma2_eb / eb["n"].to_numpy()              # 標本平均の分散 σ²/n_j
ybar_eb = eb["標本平均"].to_numpy()

# 周辺分布 ȳ_j ~ N(μ, τ² + σ²/n_j) の対数尤度を最大化して (μ, τ²) を推定
def eb_negloglik(par):
    mu, log_tau2 = par
    v = np.exp(log_tau2) + se2_eb
    return 0.5 * np.sum(np.log(2 * np.pi * v) + (ybar_eb - mu) ** 2 / v)

res_eb = optimize.minimize(eb_negloglik, x0=[ybar_eb.mean(), np.log(ybar_eb.var())], method="Nelder-Mead")
mu_eb, tau2_eb = res_eb.x[0], np.exp(res_eb.x[1])
# モーメント法: E[ȳ_j の標本分散] ≈ τ² + mean(σ²/n_j)
tau2_mm = max(0.0, ybar_eb.var(ddof=1) - se2_eb.mean())
print(f"プールした群内分散 σ² = {sigma2_eb:.0f}（σ = {np.sqrt(sigma2_eb):.1f}）")
print(f"周辺尤度最大化: μ = {mu_eb:.1f}, τ² = {tau2_eb:.0f}（τ = {np.sqrt(tau2_eb):.1f}）")
print(f"モーメント法  : τ² = {tau2_mm:.0f}（τ = {np.sqrt(tau2_mm):.1f}）")

# 事後平均 = B_j μ + (1 − B_j) ȳ_j,  縮小係数 B_j = (σ²/n_j) / (σ²/n_j + τ²)
eb["縮小係数B"] = se2_eb / (se2_eb + tau2_eb)
eb["経験ベイズ推定"] = eb["縮小係数B"] * mu_eb + (1 - eb["縮小係数B"]) * ybar_eb
eb["事後標準偏差"] = np.sqrt(1 / (1 / se2_eb + 1 / tau2_eb))
eb = eb.sort_values("n")

fig, ax = plt.subplots(figsize=(8, 5))
for t, r in eb.iterrows():
    ax.plot([0, 1], [r["標本平均"], r["経験ベイズ推定"]], color=PALETTE[0], lw=1, marker="o", ms=4)
    if r["n"] < 20 or abs(r["標本平均"] - mu_eb) > 45:
        ax.annotate(f"{t}（n={int(r['n'])}）", (0, r["標本平均"]), xytext=(-6, 0), textcoords="offset points",
                    ha="right", va="center", fontsize=8, color=INK["secondary"])
ax.axhline(mu_eb, color=INK["muted"], ls="--", lw=1, label=f"全体の平均の推定値 {mu_eb:.0f}")
ax.set(xticks=[0, 1], xticklabels=["タイプ別の標本平均", "経験ベイズ推定"], xlim=(-0.6, 1.2),
       title="タイプ1別の合計種族値の平均: 縮小推定", ylabel="合計種族値の平均")
ax.legend(loc="lower right")
fig.tight_layout()
plt.show()
eb.round(3)


# %% 31-6
# 縮小推定の検証: 各タイプから5匹だけ抜き出して平均を推定し、タイプ全体の平均（真値）との誤差を比べる
rng_ebv = get_rng()
true_type_mean = df.groupby("タイプ1", observed=True)["合計種族値"].mean()
type_codes = df["タイプ1"].cat.remove_unused_categories()
groups_ebv = [df.loc[type_codes == t, "合計種族値"].to_numpy() for t in true_type_mean.index]
n_small, n_rep_ebv = 5, 2000
mse_raw = mse_eb = 0.0
for _ in range(n_rep_ebv):
    samp = np.array([rng_ebv.choice(g, n_small, replace=True) for g in groups_ebv])   # 18×5
    yb = samp.mean(axis=1)
    s2 = samp.var(axis=1, ddof=1).mean()                   # プールした群内分散
    se2 = s2 / n_small
    mu_hat = yb.mean()
    tau2_hat = max(0.0, yb.var(ddof=1) - se2)              # モーメント法（全群で n が等しい）
    B = se2 / (se2 + tau2_hat)
    est = B * mu_hat + (1 - B) * yb
    mse_raw += np.mean((yb - true_type_mean.to_numpy()) ** 2) / n_rep_ebv
    mse_eb += np.mean((est - true_type_mean.to_numpy()) ** 2) / n_rep_ebv
print(f"各タイプ {n_small} 匹・{n_rep_ebv} 回の反復")
print(f"平均二乗誤差: 標本平均 {mse_raw:.0f} / 経験ベイズ {mse_eb:.0f}  （比 {mse_eb / mse_raw:.2f}）")


# %% 31-7
# メトロポリス法: ロジスティック回帰 P(性別不明) = 1 / (1 + exp(−(β0 + β1 z))), z = 合計種族値の標準化
y_lr = df["雄率"].isna().astype(int).to_numpy()
z_lr = ((df["合計種族値"] - df["合計種族値"].mean()) / df["合計種族値"].std()).to_numpy()
X_lr = np.column_stack([np.ones(len(df)), z_lr])
prior_sd_lr = 10.0                                         # 事前分布 β0, β1 ~ N(0, 10²) 独立

def log_post_lr(beta):
    eta = X_lr @ beta
    loglik = np.sum(y_lr * eta - np.logaddexp(0, eta))
    return loglik - 0.5 * np.sum(beta ** 2) / prior_sd_lr ** 2

mle_lr = sm.Logit(y_lr, X_lr).fit(disp=0)
cov_mle = mle_lr.cov_params()

def metropolis(log_post, init, step_cov, n_iter, rng):
    """ランダムウォーク・メトロポリス法（提案 θ' = θ + u, u ~ N(0, step_cov)）."""
    chol = np.linalg.cholesky(step_cov)
    draws = np.empty((n_iter, len(init)))
    cur, lp_cur, acc = np.asarray(init, float), log_post(init), 0
    for t in range(n_iter):
        prop = cur + chol @ rng.standard_normal(len(cur))
        lp_prop = log_post(prop)
        if np.log(rng.uniform()) < lp_prop - lp_cur:          # r = π(θ')/π(θ) ≥ v なら採用
            cur, lp_cur, acc = prop, lp_prop, acc + 1
        draws[t] = cur
    return draws, acc / n_iter

rng_mh = get_rng()
n_iter_mh, burn_mh = 20000, 2000
init_lr = np.array([3.0, -3.0])                               # わざと離れた初期値
mh_runs = {}
for label, scale in [("小さすぎる歩幅", 0.02), ("適切な歩幅", 2.4 / np.sqrt(2)), ("大きすぎる歩幅", 15.0)]:
    mh_runs[label] = metropolis(log_post_lr, init_lr, scale ** 2 * cov_mle, n_iter_mh, rng_mh)
    print(f"{label:>8}: 受容率 {mh_runs[label][1]:.3f}")

fig, axes = plt.subplots(3, 1, figsize=(9, 7), sharex=True, sharey=True)
for ax, (label, (draws, acc)) in zip(axes, mh_runs.items()):
    ax.plot(draws[:, 1], color=PALETTE[0], lw=0.6)
    ax.axvline(burn_mh, color=INK["muted"], ls="--", lw=1)
    ax.axhline(mle_lr.params[1], color=PALETTE[1], lw=1)
    ax.set(title=f"{label}（受容率 {acc:.2f}）", ylabel="β1")
axes[-1].set_xlabel("反復回数 t（破線: バーンイン 2000 回）")
fig.suptitle("トレースプロット（橙線: 最尤推定値）", fontsize=12, fontweight="bold")
fig.tight_layout()
plt.show()


# %% 31-8
# メトロポリス・ヘイスティングス法（独立提案）と、事後分布・最尤推定の比較
# 提案分布 q: 最尤推定値を中心とした多変量 t 分布（自由度4）。対称でないので q の比を r に掛ける
prop_dist = stats.multivariate_t(loc=mle_lr.params, shape=1.5 * cov_mle, df=4)

def mh_independence(log_post, q, n_iter, rng):
    draws = np.empty((n_iter, 2))
    cur = q.rvs(random_state=rng)
    lw_cur = log_post(cur) - q.logpdf(cur)
    props = q.rvs(size=n_iter, random_state=rng)
    acc = 0
    for t in range(n_iter):
        lw_prop = log_post(props[t]) - q.logpdf(props[t])
        # r = π(θ') q(θ) / {π(θ) q(θ')}
        if np.log(rng.uniform()) < lw_prop - lw_cur:
            cur, lw_cur, acc = props[t], lw_prop, acc + 1
        draws[t] = cur
    return draws, acc / n_iter

rng_mhi = get_rng()
draws_ind, acc_ind = mh_independence(log_post_lr, prop_dist, n_iter_mh, rng_mhi)
draws_rw = mh_runs["適切な歩幅"][0][burn_mh:]
draws_ind = draws_ind[burn_mh:]
print(f"独立提案 MH の受容率: {acc_ind:.3f}")

cmp_lr = pd.DataFrame({
    "最尤推定値": mle_lr.params, "MLE標準誤差": mle_lr.bse,
    "事後平均(RW)": draws_rw.mean(axis=0), "事後SD(RW)": draws_rw.std(axis=0),
    "事後平均(独立MH)": draws_ind.mean(axis=0), "事後SD(独立MH)": draws_ind.std(axis=0),
    "95%信用区間(RW)": [f"[{lo:.3f}, {hi:.3f}]" for lo, hi in np.percentile(draws_rw, [2.5, 97.5], axis=0).T],
}, index=["β0", "β1"])

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for j, ax in enumerate(axes):
    ax.hist(draws_rw[:, j], bins=60, density=True, color=PALETTE[0], alpha=0.6, label="RW メトロポリス")
    ax.hist(draws_ind[:, j], bins=60, density=True, histtype="step", color=PALETTE[1], lw=1.5, label="独立提案 MH")
    g = np.linspace(*ax.get_xlim(), 200)
    ax.plot(g, stats.norm(mle_lr.params[j], mle_lr.bse[j]).pdf(g), color=PALETTE[2], label="MLE の正規近似")
    ax.set(title=f"β{j} の事後分布", xlabel=f"β{j}", ylabel="確率密度")
axes[0].legend()
fig.tight_layout()
plt.show()
cmp_lr.round(4)


# %% 31-9
# ギブスサンプリング: 素早の正規モデル N(μ, σ²) の (μ, σ²) を 25 匹の標本から推定
rng_gibbs = get_rng()
n_gb = 25
y_gb = df["素早"].to_numpy()[rng_gibbs.integers(0, len(df), n_gb)]
ybar_gb, n_gb = y_gb.mean(), len(y_gb)
# 事前分布（半共役）: μ ~ N(μ0, τ0²), σ² ~ 逆ガンマ IG(α0, β0)。互いに独立
mu0, tau0_2, alpha0, beta0 = 70.0, 30.0 ** 2, 2.0, 2.0 * 30.0 ** 2
n_iter_gb, burn_gb = 10000, 500
mu_cur, s2_cur = 0.0, 100.0 ** 2                              # 離れた初期値
gibbs = np.empty((n_iter_gb, 2))
for t in range(n_iter_gb):
    # μ | σ², y ~ N(m, v),  1/v = 1/τ0² + n/σ²,  m = v (μ0/τ0² + n ȳ/σ²)
    v = 1 / (1 / tau0_2 + n_gb / s2_cur)
    mu_cur = rng_gibbs.normal(v * (mu0 / tau0_2 + n_gb * ybar_gb / s2_cur), np.sqrt(v))
    # σ² | μ, y ~ IG(α0 + n/2, β0 + Σ(y−μ)²/2)  （ガンマ乱数の逆数で生成）
    shape = alpha0 + n_gb / 2
    rate = beta0 + 0.5 * np.sum((y_gb - mu_cur) ** 2)
    s2_cur = 1 / rng_gibbs.gamma(shape, 1 / rate)
    gibbs[t] = mu_cur, s2_cur
gb = gibbs[burn_gb:]
print(f"標本: n={n_gb}, 平均 {ybar_gb:.1f}, 不偏分散 {y_gb.var(ddof=1):.0f}")
t_ci = stats.t(n_gb - 1).ppf(0.975) * y_gb.std(ddof=1) / np.sqrt(n_gb)
print(pd.DataFrame({
    "事後平均": gb.mean(axis=0),
    "95%信用区間": [f"[{lo:.1f}, {hi:.1f}]" for lo, hi in np.percentile(gb, [2.5, 97.5], axis=0).T],
    "真値（母集団）": [bayes_true["素早の平均"], bayes_true["素早の分散（母分散）"]],
}, index=["μ", "σ²"]).round(1).to_string())
print(f"参考: μ の t 区間（頻度論） [{ybar_gb - t_ci:.1f}, {ybar_gb + t_ci:.1f}]")

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
axes[0].scatter(gb[::5, 0], np.sqrt(gb[::5, 1]), s=4, color=PALETTE[0], alpha=0.3, label="標本（5個おき）")
axes[0].plot(gibbs[:15, 0], np.sqrt(gibbs[:15, 1]), color=PALETTE[1], lw=1, marker="o", ms=3, label="最初の15ステップ")
axes[0].plot(bayes_true["素早の平均"], np.sqrt(bayes_true["素早の分散（母分散）"]), marker="*", ms=14,
             color=PALETTE[2], ls="none", label="真値")
axes[0].set(title="(μ, σ) の同時事後分布", xlabel="μ（素早の平均）", ylabel="σ（素早の標準偏差）", ylim=(15, 65))
axes[0].legend()
axes[1].plot(gibbs[:300, 0], color=PALETTE[0], lw=0.8)
axes[1].set(title="μ のトレース（最初の300回）", xlabel="反復回数 t", ylabel="μ")
fig.tight_layout()
plt.show()
