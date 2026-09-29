"""第26章 その他の多変量解析手法."""
from poke import *

df = load_data()

# %% 26-0
from scipy.spatial.distance import pdist, squareform
from sklearn.cross_decomposition import CCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from matplotlib.transforms import Bbox
from sklearn.manifold import MDS


def place_labels(ax, xy, names, fontsize=9):
    """点の名前を、既に置いたラベルや他の点と重ならない位置（8方向×3距離の候補）を選んで置く（簡易版）.
    軸の範囲と tight_layout を確定させてから呼ぶ。"""
    fig = ax.figure
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    cands = [(dx * r, dy * r, ha, va) for r in (1, 3, 5)
             for dx, dy, ha, va in [(3, 3, "left", "bottom"), (3, -3, "left", "top"), (-3, 3, "right", "bottom"),
                                    (-3, -3, "right", "top"), (0, 5, "center", "bottom"),
                                    (0, -5, "center", "top"), (6, 0, "left", "center"), (-6, 0, "right", "center")]]
    # 点（マーカー）も障害物として扱う
    pix = ax.transData.transform(np.asarray(xy, float))
    dots = [Bbox.from_extents(px - 4, py - 4, px + 4, py + 4) for px, py in pix]
    placed = []
    for i_, ((x_, y_), nm) in enumerate(zip(xy, names)):
        best = None
        for dx, dy, ha, va in cands:
            t = ax.annotate(nm, (x_, y_), xytext=(dx, dy), textcoords="offset points",
                            ha=ha, va=va, fontsize=fontsize)
            bb = t.get_window_extent(rend)
            n_ov = sum(bb.overlaps(q) for q in placed) + sum(bb.overlaps(q) for k_, q in enumerate(dots) if k_ != i_)
            if best is None or n_ov < best[0]:
                if best is not None:
                    best[1].remove()
                best = (n_ov, t, bb)
            else:
                t.remove()
            if n_ov == 0:
                break
        placed.append(best[2])

# 標準化した種族値（不偏分散で標準化）
Z_mds = ((df[STATS] - df[STATS].mean()) / df[STATS].std(ddof=1)).to_numpy()
# MDS の小さい例: 第1世代・姿違いを除く・合計種族値500以上（第24章と同じ33匹）
g1s_mds = df[(df["世代"] == 1) & ~df["is_form"] & (df["合計種族値"] >= 500)].reset_index(drop=True)
print("MDS（全体）:", len(df), "匹 / MDS（小さい例）:", len(g1s_mds), "匹")
print("正準相関分析: 体格2変数 × 種族値6変数,", len(df), "匹")
df[["log高さ", "log重さ"] + STATS].describe().T[["mean", "std", "min", "max"]].round(2)

# %% 26-1
# 古典的 MDS（計量 MDS）を二重中心化で自作し、PCA の主成分得点と比べる
def classical_mds(D, k=2):
    """距離行列 D から B = -1/2 J D^2 J を作り、上位 k 個の固有値・固有ベクトルで座標を返す."""
    n = len(D)
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    w, U = np.linalg.eigh(B)
    w, U = w[::-1], U[:, ::-1]
    return U[:, :k] * np.sqrt(np.maximum(w[:k], 0)), w

D_all = squareform(pdist(Z_mds))                  # ユークリッド距離
X_mds, w_mds = classical_mds(D_all, k=2)

# PCA（相関行列の固有値分解）の主成分得点
lam, W = np.linalg.eigh(np.corrcoef(Z_mds.T))
lam, W = lam[::-1], W[:, ::-1]
W = W * np.sign(W[np.abs(W).argmax(axis=0), range(W.shape[1])])   # 第22章と同じ符号の向き（最大絶対値成分を正）
pc_scores = Z_mds @ W[:, :2]
X_mds_al = X_mds * np.sign((X_mds * pc_scores).sum(0))     # 符号をそろえる
print("B の上位6固有値 / (n-1):", (w_mds[:6] / (len(df) - 1)).round(4))
print("相関行列の固有値       :", lam.round(4))
print("B の7番目以降の固有値の最大絶対値:", np.abs(w_mds[6:]).max().round(8), "（階数は p=6）")
print("MDS 座標と主成分得点の最大差:", np.abs(X_mds_al - pc_scores).max().round(10))

fig, ax = plt.subplots(figsize=(6.5, 4.8))
ax.scatter(X_mds_al[:, 0], X_mds_al[:, 1], s=10, alpha=0.4, color=PALETTE[0])
for nm in ["ツボツボ", "テッカニン", "コイキング", "アルセウス"]:
    i = df.index[df["名前"] == nm][0]
    ax.annotate(nm, (X_mds_al[i, 0], X_mds_al[i, 1]), xytext=(4, 4), textcoords="offset points", fontsize=9)
ax.set(title="古典的 MDS の2次元布置（= 第1・第2主成分得点）", xlabel="第1座標", ylabel="第2座標")
ax.margins(x=0.12, y=0.08)
fig.tight_layout()
plt.show()

# %% 26-2
# ユークリッドでない距離（マンハッタン距離）: 古典的 MDS と非計量 MDS（33匹）
Z_s = ((g1s_mds[STATS] - df[STATS].mean()) / df[STATS].std(ddof=1)).to_numpy()
D_man = squareform(pdist(Z_s, metric="cityblock"))
X_cl, w_cl = classical_mds(D_man, k=2)
print("マンハッタン距離の B の固有値（負の値が出る = ユークリッド空間に埋め込めない）:")
print("  正:", (w_cl > 1e-9).sum(), "個, 負:", (w_cl < -1e-9).sum(), "個, 最小:", w_cl.min().round(3))

# 非計量 MDS（SMACOF 法）は局所解に陥りやすいので、古典的 MDS の布置を初期値にする
def nonmetric_mds(D, init=None):
    m = MDS(n_components=2, metric=False, dissimilarity="precomputed", n_init=1 if init is not None else 8,
            max_iter=3000, eps=1e-9, random_state=SEED, normalized_stress=True)
    return m.fit_transform(D, init=init), m.stress_

X_nm, stress_nm = nonmetric_mds(D_man, init=X_cl)
X_nm_rand, stress_rand = nonmetric_mds(D_man)
iu = np.triu_indices(len(D_man), 1)
rank_corr = lambda X: stats.spearmanr(D_man[iu], pdist(X))[0]   # 距離の順位がどれだけ保たれたか
print("ストレス（正規化, 0に近いほど良い）  非計量MDS（古典的MDSを初期値）: {:.3f} / ランダム初期値8回の最良: {:.3f}".format(
    stress_nm, stress_rand))
print("元の距離と布置上の距離の順位相関  古典的MDS: {:.3f} / 非計量MDS: {:.3f} / 非計量MDS(ランダム初期値): {:.3f}".format(
    rank_corr(X_cl), rank_corr(X_nm), rank_corr(X_nm_rand)))

fig, ax = plt.subplots(figsize=(10, 8))
ax.scatter(X_nm[:, 0], X_nm[:, 1], s=18, color=PALETTE[0])
ax.set(title="非計量 MDS（マンハッタン距離, 第1世代・合計種族値500以上）", xlabel="第1座標", ylabel="第2座標")
ax.margins(x=0.1, y=0.06)
fig.tight_layout()
place_labels(ax, X_nm, g1s_mds["名前"], fontsize=8)     # ラベルが重ならない向きを選んで置く
plt.show()

# %% 26-3
# 正準相関分析: 体格 x = (log高さ, log重さ) と 種族値 y（6項目）
Xc = df[["log高さ", "log重さ"]].to_numpy(float)
Yc = df[STATS].to_numpy(float)
Rall = np.corrcoef(np.c_[Xc, Yc].T)
p_c, q_c = Xc.shape[1], Yc.shape[1]
R11, R12, R22 = Rall[:p_c, :p_c], Rall[:p_c, p_c:], Rall[p_c:, p_c:]
M_cc = np.linalg.solve(R11, R12) @ np.linalg.solve(R22, R12.T)   # R11^{-1} R12 R22^{-1} R21
rho2, A_cc = np.linalg.eig(M_cc)
o_cc = np.argsort(rho2.real)[::-1]
rho2, A_cc = rho2.real[o_cc], A_cc.real[:, o_cc]
rho = np.sqrt(rho2)
# 正準係数（標準化した変数に対する）: var(u)=var(v)=1 に規格化
A_cc = A_cc / np.sqrt(np.einsum("ik,ij,jk->k", A_cc, R11, A_cc))
B_cc = np.linalg.solve(R22, R12.T) @ A_cc / rho
Xs = (Xc - Xc.mean(0)) / Xc.std(0, ddof=1)
Ys = (Yc - Yc.mean(0)) / Yc.std(0, ddof=1)
U_cc, V_cc = Xs @ A_cc, Ys @ B_cc
print("正準相関係数（固有値問題）:", rho.round(4))
print("正準変量どうしの相関     :", [np.corrcoef(U_cc[:, k], V_cc[:, k])[0, 1].round(4) for k in range(2)])

cca = CCA(n_components=2, max_iter=5000, tol=1e-10).fit(Xc, Yc)
xs_sk, ys_sk = cca.transform(Xc, Yc)
print("sklearn CCA の正準相関   :", [np.corrcoef(xs_sk[:, k], ys_sk[:, k])[0, 1].round(4) for k in range(2)])

# バートレットの検定: H0「第 k+1 以降の正準相関はすべて0」
n_c = len(df)
for k in range(2):
    lam_w = np.prod(1 - rho2[k:])
    chi2 = -(n_c - 1 - (p_c + q_c + 1) / 2) * np.log(lam_w)
    dof = (p_c - k) * (q_c - k)
    print(f"H0: ρ_{k+1} 以降 = 0 : χ² = {chi2:.1f}, 自由度 = {dof}, p値 = {stats.chi2.sf(chi2, dof):.2e}")

# 構造係数（元の変数と第1・第2正準変量の相関）
struct = pd.DataFrame(
    [[np.corrcoef(Xs[:, j], U_cc[:, k])[0, 1] for k in range(2)] for j in range(p_c)] +
    [[np.corrcoef(Ys[:, j], V_cc[:, k])[0, 1] for k in range(2)] for j in range(q_c)],
    index=["log高さ", "log重さ"] + STATS, columns=["第1正準変量との相関", "第2正準変量との相関"])

fig, ax = plt.subplots(figsize=(6, 4.5))
ax.scatter(U_cc[:, 0], V_cc[:, 0], s=10, alpha=0.4, color=PALETTE[0])
ax.set(title=f"第1正準変量（正準相関 {rho[0]:.2f}）", xlabel="u1（体格側）", ylabel="v1（種族値側）")
fig.tight_layout()
plt.show()
pd.concat([struct, pd.DataFrame(np.r_[A_cc, B_cc], index=struct.index,
                                columns=["第1正準係数", "第2正準係数"])], axis=1).round(3)

# %% 26-4
# 数量化III類（対応分析）: タイプ1 × タマゴ1 のクロス表を SVD で分解
ct_src = df[(df["タイプ1"] != "ひこう") & (df["タマゴ1"] != "メタモン")]
N_ct = pd.crosstab(ct_src["タイプ1"].astype(str), ct_src["タマゴ1"].astype(str))
n_ct = N_ct.to_numpy().sum()
P_ct = N_ct.to_numpy() / n_ct
r_m, c_m = P_ct.sum(1), P_ct.sum(0)
S_ct = (P_ct - np.outer(r_m, c_m)) / np.sqrt(np.outer(r_m, c_m))   # 標準化残差
U_ct, sv, Vt_ct = np.linalg.svd(S_ct, full_matrices=False)
chi2_ct = stats.chi2_contingency(N_ct, correction=False)[0]
print(f"クロス表: {N_ct.shape[0]}タイプ × {N_ct.shape[1]}タマゴグループ, n = {n_ct}")
print(f"総慣性 Σσ² = {np.sum(sv ** 2):.4f},  χ²/n = {chi2_ct / n_ct:.4f}")
print("各次元の寄与率:", (sv ** 2 / np.sum(sv ** 2))[:5].round(3))
F_row = U_ct / np.sqrt(r_m)[:, None] * sv            # 行（タイプ）の主座標
G_col = Vt_ct.T / np.sqrt(c_m)[:, None] * sv         # 列（タマゴ）の主座標
# 相互平均（推移式）: 行の座標 = 列の座標の重み付き平均 / σ
F_from_G = (P_ct / r_m[:, None]) @ G_col[:, :2] / sv[:2]
print("推移式の確認（最大差）:", np.abs(F_from_G - F_row[:, :2]).max().round(10))

# 数量化III類（個体×カテゴリの 0/1 表）として計算した固有値との関係: μ = (1 + σ) / 2
ind = pd.get_dummies(ct_src[["タイプ1", "タマゴ1"]].astype(str)).to_numpy(float)
Pi = ind / ind.sum()
ri, ci = Pi.sum(1), Pi.sum(0)
sv_ind = np.linalg.svd((Pi - np.outer(ri, ci)) / np.sqrt(np.outer(ri, ci)), compute_uv=False)
print("0/1表の固有値（上位3）:", (sv_ind[:3] ** 2).round(4), " (1+σ)/2:", ((1 + sv[:3]) / 2).round(4))

fig, axes = plt.subplots(1, 2, figsize=(13, 6), gridspec_kw={"width_ratios": [1, 1.3]})
zoom = dict(xlim=(-0.5, 0.3), ylim=(-0.9, 0.35))
for ax, is_zoom in zip(axes, [False, True]):
    ax.axhline(0, color=INK["axis"], lw=1)
    ax.axvline(0, color=INK["axis"], lw=1)
    ax.scatter(F_row[:, 0], F_row[:, 1], color=PALETTE[0], s=25, label="タイプ1")
    ax.scatter(G_col[:, 0], G_col[:, 1], color=PALETTE[1], s=25, marker="s", label="タマゴグループ")
    ax.set(xlabel=f"第1次元（寄与率 {sv[0] ** 2 / np.sum(sv ** 2):.0%}）",
           ylabel=f"第2次元（寄与率 {sv[1] ** 2 / np.sum(sv ** 2):.0%}）")
axes[0].add_patch(plt.Rectangle((zoom["xlim"][0], zoom["ylim"][0]), zoom["xlim"][1] - zoom["xlim"][0],
                                zoom["ylim"][1] - zoom["ylim"][0], fill=False, ec=INK["muted"], ls="--"))
axes[0].set_title("対応分析（数量化III類）: タイプ1 × タマゴ1")
axes[0].legend(loc="upper right")
axes[1].set(title="破線の枠内の拡大", **zoom)
fig.tight_layout()
# 左図は外側の点だけ、右図（拡大）は内側の点だけに名前を付ける（重ならない向きを選ぶ）
pts_all = np.r_[F_row[:, :2], G_col[:, :2]]
names_all = list(N_ct.index) + list(N_ct.columns)
inside = ((zoom["xlim"][0] < pts_all[:, 0]) & (pts_all[:, 0] < zoom["xlim"][1])
          & (zoom["ylim"][0] < pts_all[:, 1]) & (pts_all[:, 1] < zoom["ylim"][1]))
for ax, is_zoom in zip(axes, [False, True]):
    sel = inside == is_zoom
    place_labels(ax, pts_all[sel], [nm for nm, f in zip(names_all, sel) if f])
plt.show()

# %% 26-5
# 数量化I類・II類 = カテゴリをダミー変数にした重回帰・判別分析
dq = df[df["成長"] != "105万"].copy()                  # 105万は2匹しかいないので除く
dq["成長"] = dq["成長"].astype(str)
dq["タイプ1"] = dq["タイプ1"].astype(str)
Xq = pd.get_dummies(dq[["タイプ1", "成長"]], drop_first=True, dtype=float)

def category_scores(coef, cols, data):
    """ダミー係数をアイテムごとに「重み付き平均0」のカテゴリスコアに直す."""
    out = {}
    for item in ["タイプ1", "成長"]:
        cats = sorted(data[item].unique())
        raw = pd.Series({c: coef.get(f"{item}_{c}", 0.0) for c in cats})   # 基準カテゴリは0
        freq = data[item].value_counts(normalize=True)[cats]
        out[item] = raw - (raw * freq).sum()
    return out

# 数量化I類: 外的基準 = 合計種族値（量的）
yq = dq["合計種族値"].to_numpy(float)
Aq = np.c_[np.ones(len(Xq)), Xq.to_numpy()]
beta = np.linalg.lstsq(Aq, yq, rcond=None)[0]
r2 = 1 - np.sum((yq - Aq @ beta) ** 2) / np.sum((yq - yq.mean()) ** 2)
sc1 = category_scores(dict(zip(Xq.columns, beta[1:])), Xq.columns, dq)
print(f"数量化I類（合計種族値 ~ タイプ1 + 成長）: 決定係数 R² = {r2:.3f}")
for item, s in sc1.items():
    print(f"  {item} のレンジ（最大-最小）= {s.max() - s.min():.1f}")
print("  成長のカテゴリスコア:", s.round(1).to_dict())

# 数量化II類: 外的基準 = 合計種族値500以上か（2群）
yq2 = (dq["合計種族値"] >= 500).to_numpy(int)
lda_q = LinearDiscriminantAnalysis().fit(Xq, yq2)
score_q = lda_q.decision_function(Xq)
# 相関比 η² = 群間平方和 / 全平方和（判別得点について）
ss_between = sum((yq2 == g).sum() * (score_q[yq2 == g].mean() - score_q.mean()) ** 2 for g in [0, 1])
eta2 = ss_between / np.sum((score_q - score_q.mean()) ** 2)
sc2 = category_scores(dict(zip(Xq.columns, lda_q.coef_[0])), Xq.columns, dq)
print(f"\n数量化II類（合計種族値500以上か ~ タイプ1 + 成長）: 相関比 η² = {eta2:.3f}, "
      f"訓練正解率 = {lda_q.score(Xq, yq2):.3f}（多数派の割合 {1 - yq2.mean():.3f}）")
for item, s in sc2.items():
    print(f"  {item} のレンジ = {s.max() - s.min():.2f}")
pd.DataFrame({"I類スコア(合計種族値)": sc1["タイプ1"], "II類スコア(判別)": sc2["タイプ1"]}).sort_values(
    "I類スコア(合計種族値)", ascending=False).round(2)
