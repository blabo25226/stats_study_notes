"""第04章 変数変換."""
from poke import *

df = load_data()

# %% 04-0
# 使う列の要約（歪度つき）
from scipy import integrate, optimize

cols_ch4 = ["重さ", "log重さ", "高さ", "log高さ", "孵化", "攻撃", "特攻", "捕獲率", "合計種族値"]
summ_ch4 = df[cols_ch4].describe().T[["mean", "std", "min", "50%", "max"]]
summ_ch4["歪度"] = df[cols_ch4].skew()
print("孵化のとる値の種類:", df["孵化"].nunique(), " 捕獲率=255 の匹数:", (df["捕獲率"] == 255).sum())
summ_ch4.round(3)

# %% 04-1
# Y = g(X) の密度：log重さ X ~ N(μ, σ²) とみなすと、重さ W = e^X の密度は
# f_W(w) = f_X(log w) · |d(log w)/dw| = φ((log w - μ)/σ) / (σ w)
mu_lw = df["log重さ"].mean()
sd_lw = df["log重さ"].std(ddof=0)          # 正規分布の最尤推定（n で割る）


def dens_weight_ch4(w, mu=mu_lw, sd=sd_lw):
    """変換公式で求めた重さの密度（対数正規分布）."""
    return stats.norm.pdf(np.log(w), mu, sd) / w


grid_w = np.linspace(0.05, 300, 2000)
assert np.allclose(dens_weight_ch4(grid_w), stats.lognorm.pdf(grid_w, s=sd_lw, scale=np.exp(mu_lw)))
print(f"log重さ ~ N({mu_lw:.3f}, {sd_lw:.3f}²) とみなす")
int_w = integrate.quad(dens_weight_ch4, 1e-9, 1000, points=[0.1, 1, 10, 100], limit=200)[0]
print(f"密度の積分（0〜1000kg）: {int_w:.4f}（Φ((log1000-μ)/σ) = {stats.norm.cdf((np.log(1000) - mu_lw) / sd_lw):.4f}）")
print(f"対数正規の中央値 e^μ = {np.exp(mu_lw):.2f} kg（データの中央値 {df['重さ'].median():.2f}）")
print(f"対数正規の平均 e^(μ+σ²/2) = {np.exp(mu_lw + sd_lw**2 / 2):.2f} kg（データの平均 {df['重さ'].mean():.2f}）")
print(f"P(W > 200kg): 対数正規 {stats.lognorm.sf(200, s=sd_lw, scale=np.exp(mu_lw)):.4f}, データ {(df['重さ'] > 200).mean():.4f}")

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].hist(df["log重さ"], bins=40, density=True, color=PALETTE[0], label="データ")
gx = np.linspace(df["log重さ"].min() - 0.5, df["log重さ"].max() + 0.5, 300)
axes[0].plot(gx, stats.norm.pdf(gx, mu_lw, sd_lw), color=PALETTE[1], label="正規分布")
axes[0].set(title="log重さ と正規分布", xlabel="log(重さ / kg)", ylabel="密度")
axes[0].legend()
axes[1].hist(df["重さ"], bins=np.arange(0, 1005, 5), density=True, color=PALETTE[0], label="データ")
axes[1].plot(grid_w, dens_weight_ch4(grid_w), color=PALETTE[1], label="変換公式による密度")
axes[1].set(title="重さ と変換公式による密度（0〜300kgを表示）", xlabel="重さ (kg)", ylabel="密度（1/kg）", xlim=(0, 300))
axes[1].legend()
fig.tight_layout()
plt.show()

# %% 04-2
# 線形変換（標準化）：Z = (X - μ)/σ。f_Z(z) = σ f_X(μ + σ z)
x_std = df["合計種族値"].to_numpy(float)
mu_x, sd_x = x_std.mean(), x_std.std()
z_std = (x_std - mu_x) / sd_x
print(f"Z の平均 {z_std.mean():.2e}, 分散 {z_std.var():.4f}")
print(f"歪度 X: {stats.skew(x_std):.4f}, Z: {stats.skew(z_std):.4f}（正の尺度倍・平行移動で不変）")
# 密度の関係をカーネル密度推定で確認（帯域幅は標準偏差に比例するので同じ比率の推定になる）
kde_x, kde_z = stats.gaussian_kde(x_std), stats.gaussian_kde(z_std)
for z0 in [-1.5, 0.0, 1.0]:
    print(f"z = {z0:+.1f}: f_Z(z) = {kde_z(z0)[0]:.4f},  σ f_X(μ+σz) = {sd_x * kde_x(mu_x + sd_x * z0)[0]:.4f}")
# 偏差値 T = 50 + 10Z（これも線形変換）
t_score = 50 + 10 * z_std
print(f"偏差値の平均 {t_score.mean():.2f}, 標準偏差 {t_score.std():.2f}")
top_t = df.assign(偏差値=t_score).nlargest(3, "合計種族値")[["名前", "合計種族値", "偏差値"]]
top_t.round(1)

# %% 04-3
# X + Y の分布：攻撃 X と特攻 Y を独立とみなした畳み込み p_{X+Y}(s) = Σ_x p_X(x) p_Y(s - x) と実データの和
max_st = 256
p_atk = np.bincount(df["攻撃"], minlength=max_st) / len(df)
p_spa = np.bincount(df["特攻"], minlength=max_st) / len(df)
p_conv = np.convolve(p_atk, p_spa)                     # 独立なら X+Y の確率関数
s_vals = np.arange(len(p_conv))
sum_obs = (df["攻撃"] + df["特攻"]).to_numpy()
mean_conv = np.sum(s_vals * p_conv)
var_conv = np.sum((s_vals - mean_conv) ** 2 * p_conv)
print(f"畳み込み（独立）: 平均 {mean_conv:.2f}, 分散 {var_conv:.1f}  （= V[X]+V[Y] = {df['攻撃'].var(ddof=0) + df['特攻'].var(ddof=0):.1f}）")
print(f"実データの和    : 平均 {sum_obs.mean():.2f}, 分散 {sum_obs.var():.1f}  （= V[X]+V[Y]+2Cov）")
for thr in [100, 250, 300]:
    op = "<=" if thr == 100 else ">="
    p_ind = p_conv[: thr + 1].sum() if thr == 100 else p_conv[thr:].sum()
    p_obs = (sum_obs <= thr).mean() if thr == 100 else (sum_obs >= thr).mean()
    print(f"P(X+Y {op} {thr}): 独立とみなした場合 {p_ind:.4f},  実データ {p_obs:.4f}")
# 独立なら、特攻の並びをランダムに入れ替えた和と同じ分布になる（シミュレーションで確認）
rng_ch4 = get_rng()
perm_sums = np.concatenate([df["攻撃"].to_numpy() + rng_ch4.permutation(df["特攻"].to_numpy()) for _ in range(20)])
print(f"並べ替え20回の和: 平均 {perm_sums.mean():.2f}, 分散 {perm_sums.var():.1f}")

fig, ax = plt.subplots(figsize=(7, 4))
bw = 10
edges_s = np.arange(0, 400, bw)
ax.hist(sum_obs, bins=edges_s, density=True, color=PALETTE[0], label="実データの 攻撃+特攻")
conv_binned = np.add.reduceat(p_conv[:edges_s[-1]], edges_s[:-1]) / bw
ax.step(edges_s[:-1], conv_binned, where="post", color=PALETTE[1], lw=2, label="独立とみなした畳み込み")
ax.set(title="攻撃+特攻 の分布：実データと独立を仮定した畳み込み", xlabel="攻撃+特攻", ylabel="密度（幅10の階級）")
ax.legend()
fig.tight_layout()
plt.show()

# %% 04-4
# ヤコビアン（2変数の変換）
# (1) 線形変換 U = X + Y, V = X - Y（X=攻撃, Y=特攻 に2変量正規分布を当てはめる）
#     逆変換 x = (u+v)/2, y = (u-v)/2、ヤコビアン J = det[[1/2, 1/2], [1/2, -1/2]] = -1/2
xy = df[["攻撃", "特攻"]].to_numpy(float)
mu_xy = xy.mean(axis=0)
cov_xy = np.cov(xy, rowvar=False, ddof=0)
mvn_xy = stats.multivariate_normal(mu_xy, cov_xy)
A_uv = np.array([[1, 1], [1, -1]])
mvn_uv = stats.multivariate_normal(A_uv @ mu_xy, A_uv @ cov_xy @ A_uv.T)   # 線形変換後の正規分布
J_uv = np.linalg.det(np.array([[0.5, 0.5], [0.5, -0.5]]))
print(f"ヤコビアン J = {J_uv:.2f}")
for u0, v0 in [(150, 0), (200, 40), (120, -30)]:
    f_change = mvn_xy.pdf([(u0 + v0) / 2, (u0 - v0) / 2]) * abs(J_uv)
    print(f"(u, v) = ({u0}, {v0}): f_XY(x(u,v), y(u,v))·|J| = {f_change:.3e},  N(Aμ, AΣAᵀ) の密度 = {mvn_uv.pdf([u0, v0]):.3e}")
uv = xy @ A_uv.T
print(f"Cov[U, V] = V[X] - V[Y] = {cov_xy[0, 0] - cov_xy[1, 1]:.1f}（データ {np.cov(uv, rowvar=False, ddof=0)[0, 1]:.1f}）")

# (2) 非線形変換：(log高さ, log重さ) ~ 2変量正規 とみなし、(H, W) = (e^S, e^T) の密度
#     f_{H,W}(h, w) = f_{S,T}(log h, log w) · 1/(h w)  （ヤコビアン |∂(s,t)/∂(h,w)| = 1/(hw)）
st = df[["log高さ", "log重さ"]].to_numpy(float)
mvn_st = stats.multivariate_normal(st.mean(axis=0), np.cov(st, rowvar=False, ddof=0))


def dens_hw_ch4(w, h):
    return mvn_st.pdf([np.log(h), np.log(w)]) / (h * w)


h0, w0 = 1.0, 30.0
p_int, _ = integrate.dblquad(dens_hw_ch4, 1e-3, h0, 1e-3, w0)      # ∫∫_{h≤1, w≤30} f(h,w) dw dh（0付近の寄与は無視できる）
p_cdf = mvn_st.cdf([np.log(h0), np.log(w0)])
p_emp = ((df["高さ"] <= h0) & (df["重さ"] <= w0)).mean()
print(f"\nP(高さ ≤ {h0} m, 重さ ≤ {w0} kg): 変換した密度の数値積分 {p_int:.4f},"
      f"  2変量正規のCDF {p_cdf:.4f},  データ {p_emp:.4f}")

# %% 04-5
# Box-Cox 変換：y(λ) = (x^λ - 1)/λ（λ≠0）, log x（λ=0）。λ を最尤推定する


def boxcox_profile_ll_ch4(lam, x):
    """Box-Cox 変換後が正規分布とみなしたときのプロファイル対数尤度（定数項を除く）."""
    y = np.log(x) if abs(lam) < 1e-12 else (x**lam - 1) / lam
    return -len(x) / 2 * np.log(y.var()) + (lam - 1) * np.sum(np.log(x))


bc_rows, bc_data = {}, {}
for c in ["重さ", "高さ", "孵化"]:
    x = df[c].to_numpy(float)
    y_bc, lam_sp, ci_bc = stats.boxcox(x, alpha=0.05)          # scipy の最尤推定と95%信頼区間
    lam_hand = optimize.minimize_scalar(lambda l: -boxcox_profile_ll_ch4(l, x), bounds=(-3, 3), method="bounded").x
    bc_data[c] = (x, y_bc, lam_sp)
    bc_rows[c] = {"λ(scipy)": lam_sp, "λ(手計算)": lam_hand, "95%CI下限": ci_bc[0], "95%CI上限": ci_bc[1],
                  "歪度(変換前)": stats.skew(x), "歪度(変換後)": stats.skew(y_bc),
                  "歪度(log)": stats.skew(np.log(x)), "値の種類": len(np.unique(x))}
bc_tab = pd.DataFrame(bc_rows).T
assert np.allclose(bc_tab["λ(scipy)"], bc_tab["λ(手計算)"], atol=1e-3)
print("95%信頼区間は尤度比 2{ℓ(λ̂)-ℓ(λ)} ≤ χ²_1(0.05) = 3.84（自由度1のカイ二乗分布の上側5%点）となる λ の範囲")

fig, axes = plt.subplots(2, 3, figsize=(12, 7))
for j, (c, (x, y_bc, lam)) in enumerate(bc_data.items()):
    for i, (v, lab) in enumerate([(x, f"{c}（変換前）"), (y_bc, f"{c}（Box-Cox λ={lam:.2f}）")]):
        (osm, osr), (slope, icpt, _) = stats.probplot(v, dist="norm")
        axes[i, j].scatter(osm, osr, s=6, color=PALETTE[0], alpha=0.6)
        axes[i, j].plot(osm, slope * osm + icpt, color=PALETTE[1], lw=1.5)
        axes[i, j].set(title=f"Q-Qプロット：{lab}", xlabel="標準正規分布の分位点", ylabel="データの分位点")
fig.tight_layout()
plt.show()
bc_tab.round(3)

# %% 04-6
# ロジット変換：p = 捕獲率/255 ∈ (0, 1] → logit p = log(p/(1-p))
# p = 1（捕獲率255）では logit が発散するので、0.5 を加える経験ロジット log((c+0.5)/(255-c+0.5)) を使う
cr = df["捕獲率"].to_numpy(float)
p_cr = cr / 255
logit_cr = np.log((cr + 0.5) / (255 - cr + 0.5))
print(f"p = 1 の匹数: {(p_cr == 1).sum()}（通常のロジットは +∞ になる）")
print(f"経験ロジットの範囲: {logit_cr.min():.2f} 〜 {logit_cr.max():.2f}")
# 逆変換（ロジスティック関数）で元に戻ることの確認（p < 1 の行で通常のロジット）
m_lt1 = p_cr < 1
lg = np.log(p_cr[m_lt1] / (1 - p_cr[m_lt1]))
assert np.allclose(1 / (1 + np.exp(-lg)), p_cr[m_lt1])
tot_cr = df["合計種族値"].to_numpy(float)
print(f"相関係数 合計種族値 と 捕獲率: {np.corrcoef(tot_cr, cr)[0, 1]:.3f}")
print(f"相関係数 合計種族値 と 経験ロジット: {np.corrcoef(tot_cr, logit_cr)[0, 1]:.3f}")
print(f"歪度 捕獲率: {stats.skew(cr):.3f},  経験ロジット: {stats.skew(logit_cr):.3f}")
# 単調増加な変換では順位は変わらないので、スピアマンの順位相関は変換前後で同じ
print(f"スピアマン順位相関: 捕獲率 {stats.spearmanr(tot_cr, cr)[0]:.3f}, 経験ロジット {stats.spearmanr(tot_cr, logit_cr)[0]:.3f}")
print("捕獲率の上位の値と匹数:", df["捕獲率"].value_counts().head(5).to_dict())

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].scatter(tot_cr, p_cr, s=8, alpha=0.4, color=PALETTE[0])
axes[0].set(title="合計種族値 と 捕獲率/255", xlabel="合計種族値", ylabel="p = 捕獲率/255")
axes[1].scatter(tot_cr, logit_cr, s=8, alpha=0.4, color=PALETTE[0])
axes[1].set(title="合計種族値 と 経験ロジット", xlabel="合計種族値", ylabel="log{(c+0.5)/(255−c+0.5)}")
fig.tight_layout()
plt.show()
