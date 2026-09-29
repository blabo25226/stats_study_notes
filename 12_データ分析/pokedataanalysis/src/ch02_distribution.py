"""第02章 確率分布と母関数."""
from poke import *

df = load_data()

# %% 02-0
# 使う列の要約
print(df[["合計種族値", "努力値合計", "世代"]].describe().round(2))
print("\nタイプ1の水準数:", df["タイプ1"].nunique())

# %% 02-1
# 経験累積分布関数 F_n(x) = (x 以下の匹数) / n
total_sorted = np.sort(df["合計種族値"].to_numpy())
n_ch2 = len(total_sorted)


def ecdf_ch2(x, data=total_sorted):
    """経験累積分布関数（右連続）: data <= x となる割合."""
    return np.searchsorted(data, x, side="right") / len(data)


for x0 in [300, 400, 500, 600]:
    print(f"F({x0}) = P(合計種族値 <= {x0}) = {ecdf_ch2(x0):.4f}")
print(f"P(400 < X <= 600) = F(600) - F(400) = {ecdf_ch2(600) - ecdf_ch2(400):.4f}")
# 離散なので P(X = 600) = F(600) - F(600-) が跳びの大きさ
print(f"P(X = 600) = F(600) - F(599) = {ecdf_ch2(600) - ecdf_ch2(599):.4f}（{(df['合計種族値'] == 600).sum()}匹）")

mu_t, sd_t = total_sorted.mean(), total_sorted.std()
grid_t = np.linspace(150, 800, 400)
fig, ax = plt.subplots(figsize=(7, 4))
ax.step(total_sorted, np.arange(1, n_ch2 + 1) / n_ch2, where="post", color=PALETTE[0], label="経験累積分布関数")
ax.plot(grid_t, stats.norm.cdf(grid_t, mu_t, sd_t), color=PALETTE[1], lw=1.5, ls="--",
        label=f"正規分布 N({mu_t:.0f}, {sd_t:.0f}²) の累積分布関数")
ax.set(title="合計種族値の経験累積分布関数", xlabel="合計種族値", ylabel="F(x)")
ax.legend(loc="upper left")
fig.tight_layout()
plt.show()

# %% 02-2
# 同時確率関数 p(x, y)：X = 世代, Y = 努力値合計
joint_gy = pd.crosstab(df["世代"], df["努力値合計"], normalize="all")
p_gen = joint_gy.sum(axis=1)        # 周辺確率関数 p_X(x) = Σ_y p(x, y)
p_evs = joint_gy.sum(axis=0)        # 周辺確率関数 p_Y(y) = Σ_x p(x, y)
cond_y_given_x = joint_gy.div(p_gen, axis=0)   # 条件付き確率関数 p(y|x) = p(x, y) / p_X(x)
print("同時確率の総和:", joint_gy.to_numpy().sum().round(10))
print("\n周辺 p_Y(y)（努力値合計）:", p_evs.round(4).to_dict())
print("\n条件付き確率関数 p(y | 世代)（各行の和は1）")
print(cond_y_given_x.round(3))

fig, ax = plt.subplots(figsize=(6, 4.5))
im = ax.imshow(joint_gy.to_numpy(), cmap=SEQ_CMAP, aspect="auto")
for i in range(joint_gy.shape[0]):
    for j in range(joint_gy.shape[1]):
        v = joint_gy.iat[i, j]
        ax.text(j, i, f"{v:.3f}", ha="center", va="center",
                color="white" if v > joint_gy.to_numpy().max() * 0.6 else INK["primary"], fontsize=9)
ax.set_xticks(range(joint_gy.shape[1]), joint_gy.columns)
ax.set_yticks(range(joint_gy.shape[0]), [f"第{g}世代" for g in joint_gy.index])
ax.set(title="同時確率関数 p(世代, 努力値合計)", xlabel="努力値合計（ポイント）", ylabel="世代")
ax.grid(False)
fig.colorbar(im, ax=ax, label="確率")
fig.tight_layout()
plt.show()
joint_gy.round(4)

# %% 02-3
# 確率変数の独立性：p(x, y) と p_X(x) p_Y(y) を比べる
prod_gy = np.outer(p_gen, p_evs)
diff_gy = joint_gy - prod_gy
print("世代 × 努力値合計: max |p(x,y) - p_X(x)p_Y(y)| =", f"{np.abs(diff_gy.to_numpy()).max():.4f}")
print("（参考）同時確率の最大値 =", f"{joint_gy.to_numpy().max():.4f}")

# タイプ1 × 世代 でも同じ比較を行う
joint_tg = pd.crosstab(df["タイプ1"], df["世代"], normalize="all")
prod_tg = np.outer(joint_tg.sum(axis=1), joint_tg.sum(axis=0))
ratio_tg = joint_tg / prod_tg        # 独立なら全セルで1
print("タイプ1 × 世代: max |p(x,y) - p_X(x)p_Y(y)| =", f"{np.abs((joint_tg - prod_tg).to_numpy()).max():.4f}")
print("同時確率が0のセル数（独立なら周辺が正なので0にはならない）:", int((joint_tg.to_numpy() == 0).sum()))

fig, axes = plt.subplots(1, 2, figsize=(11, 5), gridspec_kw={"width_ratios": [1, 1.6]})
lim_gy = np.abs(diff_gy.to_numpy()).max()
im0 = axes[0].imshow(diff_gy.to_numpy(), cmap=DIV_CMAP, vmin=-lim_gy, vmax=lim_gy, aspect="auto")
axes[0].set_xticks(range(3), diff_gy.columns)
axes[0].set_yticks(range(7), [f"第{g}世代" for g in diff_gy.index])
axes[0].set(title="世代×努力値合計\np(x,y) − p_X(x)p_Y(y)", xlabel="努力値合計（ポイント）", ylabel="世代")
axes[0].grid(False)
fig.colorbar(im0, ax=axes[0], label="確率の差")
# 比は対数で表示（1 → 0 が中央の灰色）。0 のセルは下限で切る
log_ratio_tg = np.log2(ratio_tg.clip(lower=1 / 8))
im1 = axes[1].imshow(log_ratio_tg.to_numpy(), cmap=DIV_CMAP, vmin=-3, vmax=3, aspect="auto")
axes[1].set_xticks(range(7), [f"{g}" for g in ratio_tg.columns])
axes[1].set_yticks(range(len(ratio_tg)), ratio_tg.index.astype(str))
axes[1].set(title="タイプ1×世代\nlog2{p(x,y) / p_X(x)p_Y(y)}", xlabel="世代", ylabel="タイプ1")
axes[1].grid(False)
fig.colorbar(im1, ax=axes[1], label="log2(比)（独立なら0）")
fig.tight_layout()
plt.show()

# %% 02-4
# 条件付き期待値 E[Y | X = x]（Y = 合計種族値, X = 努力値合計）と繰り返し期待値の法則
cond_mean_ev = df.groupby("努力値合計")["合計種族値"].mean()       # E[Y | X = x]
p_x_ev = df["努力値合計"].value_counts(normalize=True).sort_index()  # p_X(x)
iterated = np.sum(cond_mean_ev * p_x_ev)                             # E[E[Y|X]] = Σ_x E[Y|X=x] p_X(x)
print("E[Y | X = x]:", cond_mean_ev.round(2).to_dict())
print(f"E[E[Y|X]] = {iterated:.4f}")
print(f"E[Y]      = {df['合計種族値'].mean():.4f}")
assert np.isclose(iterated, df["合計種族値"].mean())
# 条件付き期待値 E[Y|X] は X の関数（確率変数）。その分散は Y の分散の一部
cond_mean_rv = df["努力値合計"].map(cond_mean_ev)
print(f"V[Y] = {df['合計種族値'].var(ddof=0):.1f},  V[E[Y|X]] = {cond_mean_rv.var(ddof=0):.1f}"
      f"  （比 {cond_mean_rv.var(ddof=0) / df['合計種族値'].var(ddof=0):.3f}）")

fig, ax = plt.subplots(figsize=(6.5, 4.2))
jit = get_rng().uniform(-0.15, 0.15, len(df))
ax.scatter(df["努力値合計"] + jit, df["合計種族値"], s=8, alpha=0.3, color=PALETTE[0], label="各ポケモン")
ax.plot(cond_mean_ev.index, cond_mean_ev.values, "o-", color=PALETTE[1], label="E[合計種族値 | 努力値合計]")
ax.axhline(df["合計種族値"].mean(), color=INK["muted"], lw=1, ls="--", label="E[合計種族値]")
ax.set(title="努力値合計ごとの合計種族値の条件付き期待値", xlabel="努力値合計（ポイント）", ylabel="合計種族値",
       xticks=[1, 2, 3])
ax.legend(loc="upper left")
fig.tight_layout()
plt.show()

# %% 02-5
# 確率母関数 G(s) = E[s^X] = Σ p(x) s^x（X = 努力値合計）
pgf_coef = np.zeros(4)
pgf_coef[p_x_ev.index] = p_x_ev.to_numpy()     # 係数 p(0), p(1), p(2), p(3)
G = np.polynomial.Polynomial(pgf_coef)
G1, G2 = G.deriv(1), G.deriv(2)
mean_pgf = G1(1)                              # G'(1) = E[X]
fact2 = G2(1)                                 # G''(1) = E[X(X-1)]
var_pgf = fact2 + mean_pgf - mean_pgf**2      # V[X] = G''(1) + G'(1) - G'(1)^2
print("G(s) =", " + ".join(f"{c:.4f} s^{k}" for k, c in enumerate(pgf_coef) if c > 0))
print(f"G(1) = {G(1):.4f}")
print(f"G'(1) = {mean_pgf:.4f}（E[X] = {df['努力値合計'].mean():.4f}）")
print(f"G''(1) = E[X(X-1)] = {fact2:.4f}")
print(f"V[X] = G''(1)+G'(1)-G'(1)^2 = {var_pgf:.4f}（var(ddof=0) = {df['努力値合計'].var(ddof=0):.4f}）")

# 独立な2匹の努力値合計の和 X1 + X2：母関数は G(s)^2、係数は確率関数の畳み込み
G_sum = G**2
pmf_conv = np.convolve(pgf_coef, pgf_coef)
rng_ch2 = get_rng()
sim_sum = rng_ch2.choice(df["努力値合計"], 10000) + rng_ch2.choice(df["努力値合計"], 10000)
pgf_sum_tab = pd.DataFrame({
    "G(s)^2 の係数": G_sum.coef[:7], "畳み込み": pmf_conv[:7],
    "シミュレーション(1万回)": pd.Series(sim_sum).value_counts(normalize=True).reindex(range(7), fill_value=0).values,
}, index=pd.Index(range(7), name="X1+X2"))
print(f"\nE[X1+X2] = (G^2)'(1) = {G_sum.deriv()(1):.4f}（2E[X] = {2 * mean_pgf:.4f}）")
pgf_sum_tab.round(4)

# %% 02-6
# モーメント母関数 M(t) = E[e^{tX}]（X = 合計種族値）を数値微分して平均・分散を求める
x_mgf = df["合計種族値"].to_numpy(dtype=float)


def mgf_ch2(t, data=x_mgf):
    """経験分布のモーメント母関数 M(t) = (1/n) Σ exp(t x_i)."""
    return np.mean(np.exp(t * data))


h_mgf = 1e-5
M1 = (mgf_ch2(h_mgf) - mgf_ch2(-h_mgf)) / (2 * h_mgf)                      # M'(0) ≈ E[X]
M2 = (mgf_ch2(h_mgf) - 2 * mgf_ch2(0) + mgf_ch2(-h_mgf)) / h_mgf**2         # M''(0) ≈ E[X^2]
print(f"M'(0)  ≈ {M1:.3f}（E[X] = {x_mgf.mean():.3f}）")
print(f"M''(0) ≈ {M2:.1f}（E[X^2] = {np.mean(x_mgf**2):.1f}）")
print(f"V[X] = M''(0) - M'(0)^2 ≈ {M2 - M1**2:.2f}（var(ddof=0) = {x_mgf.var():.2f}）")
# 刻み h による数値微分の誤差
for h in [1e-2, 1e-3, 1e-4, 1e-5]:
    m1 = (mgf_ch2(h) - mgf_ch2(-h)) / (2 * h)
    m2 = (mgf_ch2(h) - 2 * mgf_ch2(0) + mgf_ch2(-h)) / h**2
    print(f"  h = {h:.0e}: 平均 {m1:.3f}, 分散 {m2 - m1**2:.2f}")

# 中心化した X - μ のモーメント母関数 M_{X-μ}(t) = e^{-μt} M_X(t) なら、2階微分がそのまま分散になり、
# 指数の大きさが抑えられるので数値微分が安定する
xc_mgf = x_mgf - x_mgf.mean()
h_c = 1e-4
Mc2 = (mgf_ch2(h_c, xc_mgf) - 2 * mgf_ch2(0, xc_mgf) + mgf_ch2(-h_c, xc_mgf)) / h_c**2
print(f"中心化: M''_(X-μ)(0) ≈ {Mc2:.2f}（h = {h_c:.0e}）")
