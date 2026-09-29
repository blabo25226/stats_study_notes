"""第21章 標本調査法."""
from poke import *

df = load_data()

# %% 21-0
# 全920行を「真の値がわかっている有限母集団」とみなす。調査項目は合計種族値
pop_y = df["合計種族値"].to_numpy(dtype=float)
N_pop = len(pop_y)
mu_pop = pop_y.mean()
sigma2_pop = pop_y.var(ddof=0)   # 母分散 σ²（N で割る）
S2_pop = pop_y.var(ddof=1)       # 修正母分散 S²（N-1 で割る）
R_SIM = 5000                     # シミュレーションの反復回数
print(f"母集団の大きさ N = {N_pop}")
print(f"母平均 μ = {mu_pop:.3f}")
print(f"母分散 σ² = {sigma2_pop:.1f}（σ = {np.sqrt(sigma2_pop):.2f}）,  S² = {S2_pop:.1f}")


def srs_means(y, n, reps, rng):
    """y から大きさ n の非復元単純無作為抽出を reps 回行い、標本平均を返す."""
    keys = rng.random((reps, len(y)))
    idx = np.argpartition(keys, n - 1, axis=1)[:, :n]   # 一様乱数の小さい n 個 = 非復元の無作為抽出
    return y[idx].mean(axis=1)


# %% 21-1
# 単純無作為抽出（非復元）: E[ȳ] = μ,  V[ȳ] = (N-n)/(N-1) · σ²/n
rng = get_rng()
srs_rows = []
for n in [10, 50, 100, 300, 600, 900]:
    means = srs_means(pop_y, n, R_SIM, rng)
    fpc = (N_pop - n) / (N_pop - 1)
    srs_rows.append({"n": n, "有限修正項": fpc,
                     "V理論(非復元)": fpc * sigma2_pop / n,
                     "V理論(復元)": sigma2_pop / n,
                     "Vシミュレーション": means.var(ddof=1),
                     "平均シミュレーション": means.mean()})
srs_tab = pd.DataFrame(srs_rows).set_index("n")
print(f"母平均 μ = {mu_pop:.2f}（標本平均の平均がこれに近ければ不偏）  反復 {R_SIM} 回")
srs_tab.round(3)

# %% 21-1b
# 標本平均の分散と n の関係（理論曲線とシミュレーション）
n_grid = np.arange(5, N_pop + 1)
fig, ax = plt.subplots(figsize=(7, 4.3))
ax.plot(n_grid, sigma2_pop / n_grid, color=PALETTE[1], label="復元抽出  σ²/n")
ax.plot(n_grid, (N_pop - n_grid) / (N_pop - 1) * sigma2_pop / n_grid, color=PALETTE[0],
        label="非復元抽出  (N−n)/(N−1)·σ²/n")
ax.scatter(srs_tab.index, srs_tab["Vシミュレーション"], color=INK["primary"], zorder=3, s=25,
           label=f"シミュレーション（非復元, {R_SIM}回）")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_ylim(0.1, 5000)   # n → N で分散は 0 に近づくので下限を切る
ax.set(title="標本平均の分散と標本の大きさ（N = 920）", xlabel="標本の大きさ n（対数目盛）",
       ylabel="標本平均の分散（対数目盛）")
ax.legend()
fig.tight_layout()
plt.show()

# 標準誤差を c0 以下にする最小の n: V ≤ c より n ≥ N / (1 + (N-1)c/σ²)
for se_target in [10, 5]:
    c = se_target ** 2
    n_need = N_pop / (1 + (N_pop - 1) * c / sigma2_pop)
    print(f"標準誤差 ≤ {se_target}: n ≥ {n_need:.1f} → n = {int(np.ceil(n_need))}"
          f"（無限母集団なら σ²/c = {sigma2_pop / c:.1f}）")

# %% 21-2
# 層化抽出法: 3通りの層化で、比例配分とネイマン配分を比べる（標本の大きさ n = 100）
n_st = 100
d21 = df[["合計種族値", "タイプ1", "世代", "経験値"]].copy()
d21["タイプ1"] = d21["タイプ1"].astype(str)
d21["経験値4分位"] = pd.qcut(d21["経験値"], 4, labels=["Q1", "Q2", "Q3", "Q4"]).astype(str)
strata_defs = {"世代（7層）": "世代", "タイプ1（18層）": "タイプ1", "経験値の4分位（4層）": "経験値4分位"}


def allocate(weights, n, caps):
    """weights に比例する整数配分（最大剰余法。各層1以上・層の大きさ以下）."""
    raw = n * weights / weights.sum()
    alloc = np.clip(np.floor(raw).astype(int), 1, caps)
    while alloc.sum() < n:                      # 余りを端数の大きい層から配る
        room = alloc < caps
        k = np.argmax(np.where(room, raw - alloc, -np.inf))
        alloc[k] += 1
    while alloc.sum() > n:                      # 下限1のために超えた分を削る
        k = np.argmax(np.where(alloc > 1, alloc - raw, -np.inf))
        alloc[k] -= 1
    return alloc


def strat_var(N_h, S2_h, n_h):
    """層化抽出の標本平均の分散 Σ W_h² (1 - n_h/N_h) S_h² / n_h."""
    W_h = N_h / N_h.sum()
    return np.sum(W_h ** 2 * (1 - n_h / N_h) * S2_h / n_h)


rng = get_rng()
strat_rows, strat_sims, strat_alloc = [], {}, {}
v_srs_100 = (N_pop - n_st) / (N_pop - 1) * sigma2_pop / n_st
strat_sims["単純無作為抽出"] = srs_means(pop_y, n_st, R_SIM, rng)
for label, col in strata_defs.items():
    groups = [g["合計種族値"].to_numpy(float) for _, g in d21.groupby(col)]
    N_h = np.array([len(g) for g in groups])
    S2_h = np.array([g.var(ddof=1) for g in groups])
    mu_h = np.array([g.mean() for g in groups])
    # 層間変動の割合（層内が均質なほど大きい）
    ss_between = np.sum(N_h * (mu_h - mu_pop) ** 2)
    eta2 = ss_between / ((N_pop - 1) * S2_pop)
    for alloc_name, w in [("比例配分", N_h.astype(float)), ("ネイマン配分", N_h * np.sqrt(S2_h))]:
        n_h = allocate(w, n_st, N_h)
        est = np.zeros(R_SIM)
        for g, nh in zip(groups, n_h):
            est += (len(g) / N_pop) * srs_means(g, nh, R_SIM, rng)   # ȳ_st = Σ W_h ȳ_h
        v_th = strat_var(N_h, S2_h, n_h)
        strat_sims[f"{label}\n{alloc_name}"] = est
        strat_alloc[(label, alloc_name)] = n_h
        strat_rows.append({"層化": label, "配分": alloc_name, "層間変動の割合η²": eta2,
                           "V理論": v_th, "Vシミュレーション": est.var(ddof=1),
                           "平均シミュレーション": est.mean(), "相対効率 V_SRS/V": v_srs_100 / v_th})
print(f"n = {n_st}, 単純無作為抽出の分散（理論）= {v_srs_100:.2f}, シミュレーション = {strat_sims['単純無作為抽出'].var(ddof=1):.2f}")
print(f"母平均 μ = {mu_pop:.2f}")
pd.DataFrame(strat_rows).set_index(["層化", "配分"]).round(3)

# %% 21-2b
# 配分の中身（経験値の4分位）と、推定量の分布の比較
lab = "経験値の4分位（4層）"
alloc_tab = pd.DataFrame({
    "N_h": d21.groupby("経験値4分位").size(),
    "S_h": d21.groupby("経験値4分位")["合計種族値"].std(),
    "比例配分 n_h": strat_alloc[(lab, "比例配分")],
    "ネイマン配分 n_h": strat_alloc[(lab, "ネイマン配分")],
})
print(alloc_tab.round(1).to_string())

show = ["単純無作為抽出", "世代（7層）\n比例配分", "タイプ1（18層）\n比例配分",
        "経験値の4分位（4層）\n比例配分", "経験値の4分位（4層）\nネイマン配分"]
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.boxplot([strat_sims[k] for k in show], vert=False, widths=0.5,
           medianprops={"color": PALETTE[0]}, flierprops={"markersize": 2, "markeredgecolor": INK["muted"]})
ax.set_yticks(range(1, len(show) + 1), [k.replace("\n", "・") for k in show])
ax.invert_yaxis()
ax.axvline(mu_pop, color=PALETTE[1], linestyle="--", linewidth=1.2, label=f"母平均 μ = {mu_pop:.1f}")
ax.set(title=f"抽出法ごとの標本平均の分布（n = {n_st}, {R_SIM}回）", xlabel="標本平均（合計種族値）")
ax.legend(loc="lower right")
fig.tight_layout()
plt.show()

# %% 21-3
# 比推定: 補助変数 x = 経験値（母平均 X̄ が既知）を使って ȳ_R = (ȳ / x̄) · X̄
pop_x = df["経験値"].to_numpy(dtype=float)
X_bar = pop_x.mean()
R_pop = mu_pop / X_bar                   # 母集団の比 R = Ȳ / X̄
n_r = 100
rng = get_rng()
keys = rng.random((R_SIM, N_pop))
idx_r = np.argpartition(keys, n_r - 1, axis=1)[:, :n_r]
ybar_s, xbar_s = pop_y[idx_r].mean(axis=1), pop_x[idx_r].mean(axis=1)
ratio_est = ybar_s / xbar_s * X_bar

# 回帰推定（参考）: ȳ_reg = ȳ + b (X̄ - x̄)、b は標本ごとの最小二乗の傾き
xc = pop_x[idx_r] - xbar_s[:, None]
b_s = (xc * (pop_y[idx_r] - ybar_s[:, None])).sum(axis=1) / (xc ** 2).sum(axis=1)
reg_est = ybar_s + b_s * (X_bar - xbar_s)

f_r = n_r / N_pop
v_ratio_th = (1 - f_r) / n_r * np.sum((pop_y - R_pop * pop_x) ** 2) / (N_pop - 1)
rho = np.corrcoef(pop_x, pop_y)[0, 1]
v_reg_th = (1 - f_r) / n_r * S2_pop * (1 - rho ** 2)
v_srs_r = (1 - f_r) / n_r * S2_pop
ratio_tab = pd.DataFrame({
    "V近似理論": [v_srs_r, v_ratio_th, v_reg_th],
    "Vシミュレーション": [ybar_s.var(ddof=1), ratio_est.var(ddof=1), reg_est.var(ddof=1)],
    "偏り(平均−μ)": [ybar_s.mean() - mu_pop, ratio_est.mean() - mu_pop, reg_est.mean() - mu_pop],
}, index=["標本平均 ȳ", "比推定 ȳ_R", "回帰推定 ȳ_reg"])
print(f"相関係数 ρ(経験値, 合計種族値) = {rho:.3f},  母集団の比 R = {R_pop:.3f}")
print(f"原点を通る直線の当てはまり: 残差 y − R x の標準偏差 = {np.std(pop_y - R_pop * pop_x, ddof=1):.1f}"
      f"（y の標準偏差 {np.sqrt(S2_pop):.1f}）")
# 比推定が ȳ より有利になる近似条件: ρ > (C_x / C_y) / 2（C は変動係数）
C_x, C_y = pop_x.std(ddof=1) / X_bar, np.sqrt(S2_pop) / mu_pop
print(f"変動係数 C_x = {C_x:.3f}, C_y = {C_y:.3f} → 条件 ρ > C_x/(2C_y) = {C_x / (2 * C_y):.3f}")
ratio_tab.round(3)

# %% 21-4
# 集落抽出: 図鑑番号10番ごとの「ページ」を集落とし、集落を単純無作為抽出して中の全員を調べる
page = (df["図鑑番号"] - 1) // 10
clusters = [pop_y[page == p] for p in np.sort(page.unique())]
M_cl = len(clusters)
T_c = np.array([c.sum() for c in clusters])          # 集落ごとの合計
size_c = np.array([len(c) for c in clusters])
m_cl = int(round(n_st / size_c.mean()))              # 期待標本サイズがおよそ n_st になる集落数
print(f"集落数 M = {M_cl}, 集落の大きさ 平均 {size_c.mean():.2f}（{size_c.min()}〜{size_c.max()}）, 抽出する集落数 m = {m_cl}")

# 不偏推定量: ȳ_cl = (M/m) Σ T_c / N,  V = (M/N)² (1 - m/M) S_T² / m（S_T² は集落合計の分散）
v_cl_th = (M_cl / N_pop) ** 2 * (1 - m_cl / M_cl) * T_c.var(ddof=1) / m_cl
rng = get_rng()
keys = rng.random((R_SIM, M_cl))
idx_c = np.argpartition(keys, m_cl - 1, axis=1)[:, :m_cl]
cl_est = M_cl / m_cl * T_c[idx_c].sum(axis=1) / N_pop
n_equiv = m_cl * size_c.mean()
v_srs_equiv = (N_pop - n_equiv) / (N_pop - 1) * sigma2_pop / n_equiv

# 集落内の類似度（級内相関の目安）: 集落平均の分散のうち、無作為な並びで期待される分を超える割合
within_ss = sum(((c - c.mean()) ** 2).sum() for c in clusters)
between_ss = sum(len(c) * (c.mean() - mu_pop) ** 2 for c in clusters)
print(f"集落間変動の割合 = {between_ss / (within_ss + between_ss):.3f}"
      f"（集落が無作為な寄せ集めなら約 {(M_cl - 1) / (N_pop - 1):.3f}）")
print(f"集落抽出  V理論 = {v_cl_th:.1f}, Vシミュレーション = {cl_est.var(ddof=1):.1f}, 平均 = {cl_est.mean():.2f}")
print(f"同じ期待標本サイズ（{n_equiv:.0f}）の単純無作為抽出 V = {v_srs_equiv:.1f}")
print(f"デザイン効果 V_cl / V_SRS = {v_cl_th / v_srs_equiv:.2f}")

# %% 21-5
# 系統抽出: 図鑑番号順（姿違いを含む行の並び）に、間隔 k ごとに抽出する。
# 開始点 s = 0..k-1 の k 通りが等確率なので、平均二乗誤差（N が k で割り切れないときの偏りも含む）は k 通りの標本平均から正確に求まる
sys_rows = []
for k in range(2, 31):
    sys_means = np.array([pop_y[s::k].mean() for s in range(k)])
    n_k = N_pop / k
    v_srs_k = (N_pop - n_k) / (N_pop - 1) * sigma2_pop / n_k
    sys_rows.append({"k": k, "n≈N/k": n_k, "MSE系統": np.mean((sys_means - mu_pop) ** 2),
                     "V単純無作為": v_srs_k})
sys_tab = pd.DataFrame(sys_rows).set_index("k")
sys_tab["比 MSE系統/V単純"] = sys_tab["MSE系統"] / sys_tab["V単純無作為"]
print("図鑑番号順に並べたときの自己相関（ラグ1〜6）:",
      [round(pd.Series(pop_y).autocorr(l), 3) for l in range(1, 7)])
print(sys_tab.round(2).to_string())
print(f"比が1未満の k: {(sys_tab['比 MSE系統/V単純'] < 1).sum()} / {len(sys_tab)}")

fig, ax = plt.subplots(figsize=(7.5, 4))
ax.plot(sys_tab.index, sys_tab["比 MSE系統/V単純"], marker="o", color=PALETTE[0])
ax.axhline(1, color=INK["muted"], linestyle="--", linewidth=1, label="単純無作為抽出と同じ精度")
ax.set(title="系統抽出の平均二乗誤差 ÷ 単純無作為抽出の分散（図鑑番号順）", xlabel="抽出間隔 k",
       ylabel="比（1未満なら系統抽出が高精度）")
ax.legend()
fig.tight_layout()
plt.show()

# %% 21-5b
# 周期性が効く例: 第1世代の御三家（図鑑番号1〜9、姿違いを除く）は「たね → 1進化 → 2進化」の周期3
starters = df[(df["図鑑番号"] <= 9) & ~df["is_form"]][["図鑑番号", "名前", "合計種族値"]]
y9 = starters["合計種族値"].to_numpy(float)
print(starters.to_string(index=False))
for s in range(3):
    print(f"k = 3, 開始 {s + 1}: {starters['名前'].iloc[s::3].tolist()} → 平均 {y9[s::3].mean():.1f}")
v_sys9 = np.var([y9[s::3].mean() for s in range(3)])
v_srs9 = (9 - 3) / (9 - 1) * y9.var() / 3
print(f"系統抽出（k=3）の分散 = {v_sys9:.1f},  単純無作為抽出（n=3）の分散 = {v_srs9:.1f},  比 = {v_sys9 / v_srs9:.2f}")
