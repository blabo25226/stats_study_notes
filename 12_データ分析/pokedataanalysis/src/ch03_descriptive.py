"""第03章 分布の特性値."""
from poke import *

df = load_data()

# %% 03-0
# 使う列の要約
cols_ch3 = STATS + ["合計種族値", "高さ", "重さ"]
df[cols_ch3].describe().round(2)

# %% 03-1
# 分位点・四分位範囲・最頻値（合計種族値）
x_tot = df["合計種族値"]
q_tot = x_tot.quantile([0.25, 0.5, 0.75])
print(f"合計種族値: Q1 = {q_tot[0.25]:.0f}, 中央値 = {q_tot[0.5]:.0f}, Q3 = {q_tot[0.75]:.0f}, "
      f"IQR = {q_tot[0.75] - q_tot[0.25]:.0f}")
# 分位点の定義（隣り合う順序統計量の補間の仕方）による違い：重さで比べる
q_methods = ["linear", "lower", "higher", "midpoint", "nearest", "hazen", "weibull"]
quant_tab = pd.DataFrame(
    {m: np.quantile(df["重さ"], [0.25, 0.5, 0.75], method=m) for m in q_methods},
    index=["Q1 (25%)", "中央値", "Q3 (75%)"]).T
quant_tab["IQR"] = quant_tab["Q3 (75%)"] - quant_tab["Q1 (25%)"]
print("\n重さ (kg) の四分位数：分位点の定義による違い")
print(quant_tab)
print(f"\n最頻値（値そのものの最頻値）: {x_tot.mode().tolist()}（{(x_tot == x_tot.mode()[0]).sum()}匹）")
# 連続量とみなした最頻値：幅10の階級の最頻階級と、カーネル密度推定の最大点
bins_tot = np.arange(170, 800, 10)
cnt_tot, edges_tot = np.histogram(x_tot, bins_tot)
k_max = cnt_tot.argmax()
print(f"最頻階級（幅10）: [{edges_tot[k_max]}, {edges_tot[k_max + 1]})  度数 {cnt_tot[k_max]}")
kde_tot = stats.gaussian_kde(x_tot)
grid_tot = np.linspace(150, 800, 651)
print(f"カーネル密度推定の最大点: {grid_tot[kde_tot(grid_tot).argmax()]:.0f}")

fig, ax = plt.subplots(figsize=(8, 4))
ax.boxplot([df[c] for c in STATS], labels=STATS, widths=0.5,
           medianprops={"color": PALETTE[1]}, flierprops={"markersize": 3, "markeredgecolor": INK["muted"]})
ax.set(title="種族値6項目の箱ひげ図（ひげは1.5×IQRまで）", xlabel="種族値の項目", ylabel="種族値")
fig.tight_layout()
plt.show()

# %% 03-2
# 変動係数 CV = σ / μ（種族値6項目）
cv_tab = pd.DataFrame({
    "平均": df[STATS].mean(),
    "標準偏差(ddof=0)": df[STATS].std(ddof=0),
})
cv_tab["変動係数"] = cv_tab["標準偏差(ddof=0)"] / cv_tab["平均"]
cv_tab.loc["合計種族値"] = [x_tot.mean(), x_tot.std(ddof=0), x_tot.std(ddof=0) / x_tot.mean()]
# 単位の違う量（高さ m と重さ kg）も CV なら比べられる
for c in ["高さ", "重さ"]:
    cv_tab.loc[c] = [df[c].mean(), df[c].std(ddof=0), df[c].std(ddof=0) / df[c].mean()]
cv_tab.round(3)

# %% 03-3
# 歪度・尖度：定義式からの手計算と pandas / scipy の照合


def moments_ch3(x):
    """標本の歪度・尖度を定義式から計算する（b: n で割る版, G: pandas の補正版）."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    d = x - x.mean()
    m2, m3, m4 = (d**2).mean(), (d**3).mean(), (d**4).mean()
    g1 = m3 / m2**1.5                  # 歪度（n で割る中心モーメント）
    g2 = m4 / m2**2 - 3                # 尖度（正規分布で0になるよう3を引く）
    G1 = g1 * np.sqrt(n * (n - 1)) / (n - 2)                       # 補正済み歪度
    G2 = ((n + 1) * g2 + 6) * (n - 1) / ((n - 2) * (n - 3))        # 補正済み尖度
    return g1, g2, G1, G2


sk_rows = {}
for c in STATS + ["合計種族値", "重さ", "log重さ"]:
    g1, g2, G1, G2 = moments_ch3(df[c])
    sk_rows[c] = {"歪度 g1": g1, "scipy skew": stats.skew(df[c]),
                  "歪度 G1(補正)": G1, "pandas skew": df[c].skew(),
                  "尖度 g2": g2, "scipy kurtosis": stats.kurtosis(df[c]),
                  "尖度 G2(補正)": G2, "pandas kurt": df[c].kurt()}
sk_tab = pd.DataFrame(sk_rows).T
assert np.allclose(sk_tab["歪度 g1"], sk_tab["scipy skew"]) and np.allclose(sk_tab["歪度 G1(補正)"], sk_tab["pandas skew"])
assert np.allclose(sk_tab["尖度 g2"], sk_tab["scipy kurtosis"]) and np.allclose(sk_tab["尖度 G2(補正)"], sk_tab["pandas kurt"])
print("手計算と scipy（bias=True, 既定）・pandas（補正版）はすべて一致")
sk_tab.round(3)

# %% 03-4
# 共分散と相関係数（攻撃 X と 特攻 Y）
x_atk = df["攻撃"].to_numpy(float)
y_spa = df["特攻"].to_numpy(float)
cov_def = np.mean((x_atk - x_atk.mean()) * (y_spa - y_spa.mean()))          # E[(X-μX)(Y-μY)]
cov_short = np.mean(x_atk * y_spa) - x_atk.mean() * y_spa.mean()            # E[XY] - E[X]E[Y]
r_def = cov_def / (x_atk.std() * y_spa.std())
print(f"Cov[X,Y] 定義式 = {cov_def:.2f},  E[XY]-E[X]E[Y] = {cov_short:.2f},  np.cov(ddof=0) = {np.cov(x_atk, y_spa, ddof=0)[0, 1]:.2f}")
print(f"ρ = Cov/(σXσY) = {r_def:.4f}（np.corrcoef: {np.corrcoef(x_atk, y_spa)[0, 1]:.4f}）")
# 分散の加法：V[X+Y] = V[X] + V[Y] + 2Cov[X,Y]
print(f"V[X+Y] = {np.var(x_atk + y_spa):.1f},  V[X]+V[Y]+2Cov = {np.var(x_atk) + np.var(y_spa) + 2 * cov_def:.1f},"
      f"  V[X]+V[Y]（独立なら）= {np.var(x_atk) + np.var(y_spa):.1f}")
# 線形変換：Cov[aX+b, cY+d] = ac Cov[X,Y]、相関係数は ac>0 なら不変
a3, b3, c3, d3 = 2, 5, 0.5, -10
print(f"Cov[{a3}X+{b3}, {c3}Y{d3:+}] = {np.cov(a3 * x_atk + b3, c3 * y_spa + d3, ddof=0)[0, 1]:.2f}"
      f"（ac Cov = {a3 * c3 * cov_def:.2f}）、相関 {np.corrcoef(a3 * x_atk + b3, c3 * y_spa + d3)[0, 1]:.4f}")

fig, ax = plt.subplots(figsize=(5.5, 5))
ax.scatter(x_atk, y_spa, s=8, alpha=0.4, color=PALETTE[0])
ax.set(title=f"攻撃と特攻（相関係数 {r_def:.2f}）", xlabel="攻撃", ylabel="特攻")
fig.tight_layout()
plt.show()

# %% 03-5
# 分散共分散行列・相関行列（種族値6項目）
X6 = df[STATS].to_numpy(float)
S6 = np.cov(X6, rowvar=False, ddof=1)                  # 標本分散共分散行列（n-1 で割る）
D_inv = np.diag(1 / np.sqrt(np.diag(S6)))
R6 = D_inv @ S6 @ D_inv                                # R = D^{-1/2} S D^{-1/2}
assert np.allclose(R6, df[STATS].corr().to_numpy())
print("分散共分散行列 S（n-1で割る）")
print(pd.DataFrame(S6, index=STATS, columns=STATS).round(1))
print("\n固有値（半正定値なら全て0以上）:", np.linalg.eigvalsh(S6).round(1))
# 合計種族値 = 1ᵀx の分散は 1ᵀ S 1
ones6 = np.ones(6)
print(f"1ᵀS1 = {ones6 @ S6 @ ones6:.1f},  V[合計種族値] = {x_tot.var(ddof=1):.1f}")

fig, ax = plt.subplots(figsize=(5.8, 4.8))
im = ax.imshow(R6, cmap=DIV_CMAP, vmin=-1, vmax=1)
for i in range(6):
    for j in range(6):
        ax.text(j, i, f"{R6[i, j]:.2f}", ha="center", va="center", fontsize=9, color=INK["primary"])
ax.set_xticks(range(6), STATS)
ax.set_yticks(range(6), STATS)
ax.set(title="種族値6項目の相関行列")
ax.grid(False)
fig.colorbar(im, ax=ax, label="相関係数")
fig.tight_layout()
plt.show()

# %% 03-6
# 偏相関係数：Z の影響を除いた X と Y の相関


def partial_corr_ch3(data, x, y, z):
    """公式 (r_xy - r_xz r_yz) / sqrt((1-r_xz^2)(1-r_yz^2)) と、残差どうしの相関の両方を返す."""
    r = data[[x, y, z]].corr()
    rxy, rxz, ryz = r.loc[x, y], r.loc[x, z], r.loc[y, z]
    formula = (rxy - rxz * ryz) / np.sqrt((1 - rxz**2) * (1 - ryz**2))
    # Z への単回帰の残差どうしの相関
    zc = data[z] - data[z].mean()
    res = {}
    for v in [x, y]:
        vc = data[v] - data[v].mean()
        res[v] = vc - (vc @ zc) / (zc @ zc) * zc
    resid = np.corrcoef(res[x], res[y])[0, 1]
    return rxy, rxz, ryz, formula, resid


pc_cases = [("攻撃", "特攻", "合計種族値"), ("攻撃", "防御", "合計種族値"),
            ("高さ", "重さ", "合計種族値"), ("高さ", "合計種族値", "重さ"),
            ("log高さ", "log重さ", "合計種族値"), ("log高さ", "合計種族値", "log重さ")]
pc_tab = pd.DataFrame(
    [partial_corr_ch3(df, *c) for c in pc_cases],
    index=[f"{x}・{y} | {z}" for x, y, z in pc_cases],
    columns=["r_xy", "r_xz", "r_yz", "偏相関(公式)", "偏相関(残差)"])
assert np.allclose(pc_tab["偏相関(公式)"], pc_tab["偏相関(残差)"])
pc_tab.round(3)

# %% 03-7
# 加重平均・幾何平均・調和平均（重さ：正の値）
w_kg = df["重さ"].to_numpy(float)
am_w = w_kg.mean()
gm_w = np.exp(np.log(w_kg).mean())             # 幾何平均 = exp(log の算術平均)
hm_w = len(w_kg) / np.sum(1 / w_kg)            # 調和平均
print(f"重さ  算術平均 {am_w:.2f} kg ≥ 幾何平均 {gm_w:.2f} kg ≥ 調和平均 {hm_w:.2f} kg")
print(f"  scipy: gmean {stats.gmean(w_kg):.2f}, hmean {stats.hmean(w_kg):.2f},  中央値 {np.median(w_kg):.2f}")
print(f"  最小の3匹（kg）: {np.sort(w_kg)[:3]}")
for c in ["高さ", "合計種族値"]:
    v = df[c].to_numpy(float)
    print(f"{c}: 算術 {v.mean():.3f} ≥ 幾何 {stats.gmean(v):.3f} ≥ 調和 {stats.hmean(v):.3f}")
# 加重平均：タイプ1ごとの平均合計種族値を匹数で重みづけると全体平均
g_type = df.groupby("タイプ1", observed=True)["合計種族値"].agg(["mean", "size"])
wmean = np.sum(g_type["mean"] * g_type["size"]) / g_type["size"].sum()
print(f"\nタイプ1別平均の加重平均（重み=匹数）: {wmean:.3f}（全体平均 {x_tot.mean():.3f}）")
print(f"タイプ1別平均の単純平均（重みなし）:   {g_type['mean'].mean():.3f}")
