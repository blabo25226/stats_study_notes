"""第25章 因子分析・グラフィカルモデル."""
from poke import *

df = load_data()

# %% 25-0
import warnings

from sklearn.decomposition import FactorAnalysis
from sklearn.exceptions import ConvergenceWarning

# sklearn の FactorAnalysis はこのデータでは収束しきらない（25-1 参照）ので警告を抑える
warnings.filterwarnings("ignore", category=ConvergenceWarning)

# 種族値6項目（全920行）を平均0・分散1（n で割る）に標準化: 標本共分散行列 = 標本相関行列 R
X_fa = df[STATS].to_numpy(float)
Z_fa = (X_fa - X_fa.mean(0)) / X_fa.std(0)
n_fa, p_fa = Z_fa.shape
R_fa = np.corrcoef(Z_fa.T)
print(f"n = {n_fa}, p = {p_fa}")
print("相関行列の固有値:", np.linalg.eigvalsh(R_fa)[::-1].round(3))
pd.DataFrame(R_fa, index=STATS, columns=STATS).round(2)

# %% 25-1
# 最尤法（自作）: Ψ を与えると Λ は Ψ^{-1/2} R Ψ^{-1/2} の固有値分解で決まるので、Ψ だけを数値最適化する
from scipy.optimize import minimize

def fa_loadings(psi, m, R):
    """Ψ を固定したときの最尤の Λ."""
    s = np.sqrt(psi)
    th, U = np.linalg.eigh(R / np.outer(s, s))
    th, U = th[::-1][:m], U[:, ::-1][:, :m]
    return s[:, None] * U * np.sqrt(np.maximum(th - 1, 0))

def fa_discrepancy(psi, m, R):
    """最尤法の不一致度 F = log|Σ| + tr(Σ^{-1}R) - log|R| - p."""
    L = fa_loadings(psi, m, R)
    Sig = L @ L.T + np.diag(psi)
    return np.linalg.slogdet(Sig)[1] + np.trace(np.linalg.solve(Sig, R)) - np.linalg.slogdet(R)[1] - len(R)

def fa_ml(R, m, lower=0.005):
    """独自性を [lower, 1] に制約した最尤推定（R の factanal と同じ考え方）."""
    res = minimize(fa_discrepancy, np.full(len(R), 0.5), args=(m, R), method="L-BFGS-B",
                   bounds=[(lower, 1.0)] * len(R))
    return fa_loadings(res.x, m, R), res.x, res.fun

rows = []
fa_fit = {}
for m in [1, 2, 3]:
    L, psi, F = fa_ml(R_fa, m)
    fa_fit[m] = (L, psi)
    chi2 = (n_fa - 1 - (2 * p_fa + 5) / 6 - 2 * m / 3) * F     # バートレットの補正
    dof = ((p_fa - m) ** 2 - (p_fa + m)) / 2
    k_par = p_fa * m + p_fa - m * (m - 1) / 2                   # 自由な母数の数
    rows.append({"因子数": m, "χ²": chi2, "自由度": dof,
                 "p値": stats.chi2.sf(chi2, dof) if dof > 0 else np.nan,
                 "AIC(=nF+2k の差だけ意味をもつ)": n_fa * F + 2 * k_par,
                 "独自性の最小値": psi.min(), "最小の変数": STATS[int(psi.argmin())]})
print(pd.DataFrame(rows).set_index("因子数").round(4).to_string())

# 2因子モデル（回転前）の負荷量・共通性・独自性
L2, psi2 = fa_fit[2]
L2 = L2 * np.sign(L2.sum(0))
comm = (L2 ** 2).sum(1)
fa_tab = pd.DataFrame(L2, index=STATS, columns=["因子1", "因子2"])
fa_tab["共通性"] = comm
fa_tab["独自性"] = psi2
fa_tab["共通性+独自性"] = comm + psi2
print("\n2因子モデル（回転前）")
print(fa_tab.round(3).to_string())
print("因子の寄与（負荷量の2乗和）:", (L2 ** 2).sum(0).round(3), " 寄与率:", ((L2 ** 2).sum(0) / p_fa).round(3))

# 参考: sklearn（SVD に基づく反復法, 独自性に実質的な下限なし）で同じモデル
fa_sk = FactorAnalysis(n_components=2, max_iter=1000, tol=1e-6, random_state=SEED).fit(Z_fa)
print("sklearn の独自性:", fa_sk.noise_variance_.round(4), "（防御の独自性が0に近づき続け、収束が遅い）")

# %% 25-2
# バリマックス回転: 自作関数を sklearn（rotation="varimax"）と照合してから、25-1 の解を回転する
def varimax(L, tol=1e-10, max_iter=500):
    """バリマックス回転（正規化なし）。回転後の負荷量と回転行列を返す."""
    p, k = L.shape
    T = np.eye(k)
    crit = 0
    for _ in range(max_iter):
        A = L @ T
        u, s, vt = np.linalg.svd(L.T @ (A ** 3 - A @ np.diag((A ** 2).sum(0)) / p))
        T = u @ vt
        if s.sum() < crit * (1 + tol):
            break
        crit = s.sum()
    return L @ T, T

def varimax_crit(L):
    """各因子の負荷量の2乗の分散の和（大きいほど単純構造）."""
    return ((L ** 2).var(axis=0)).sum()

def align(A, B):
    """B の列の並びと符号を A に合わせる（2因子用）."""
    best = None
    for perm in [(0, 1), (1, 0)]:
        Bp = B[:, perm]
        Bp = Bp * np.sign((A * Bp).sum(0))
        err = np.abs(A - Bp).max()
        if best is None or err < best[0]:
            best = (err, Bp)
    return best[1]

# 照合: 同じ設定の sklearn（回転なし）の負荷量を自作関数で回転し、rotation="varimax" の結果と比べる
fa_sk_v = FactorAnalysis(n_components=2, rotation="varimax", max_iter=1000, tol=1e-6, random_state=SEED).fit(Z_fa)
L_sk_rot, _ = varimax(fa_sk.components_.T)
print("自作バリマックスと sklearn の負荷量の最大差:",
      np.abs(L_sk_rot - align(L_sk_rot, fa_sk_v.components_.T)).max().round(8))

L2v, T2v = varimax(L2)
L2v = L2v * np.sign(L2v.sum(0))                        # 負荷量の和が正になる向きにそろえる
print("回転角（度）:", np.degrees(np.arctan2(T2v[1, 0], T2v[0, 0])).round(1))
print(f"バリマックス基準: 回転前 {varimax_crit(L2):.4f} → 回転後 {varimax_crit(L2v):.4f}")
print("共通性は回転で不変:", np.allclose((L2 ** 2).sum(1), (L2v ** 2).sum(1)))

fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), sharex=True, sharey=True)
for ax, (L_, ttl) in zip(axes, [(L2, "回転前"), (L2v, "バリマックス回転後")]):
    ax.axhline(0, color=INK["axis"], lw=1)
    ax.axvline(0, color=INK["axis"], lw=1)
    ax.scatter(L_[:, 0], L_[:, 1], color=PALETTE[0], s=30)
    for j, s in enumerate(STATS):
        off_ = {"攻撃": (-8, -16)}.get(s, (5, 3))      # 近接する攻撃と特防のラベルをずらす
        ax.annotate(s, (L_[j, 0], L_[j, 1]), xytext=off_, textcoords="offset points", fontsize=10)
    ax.set(title=f"因子負荷量（{ttl}）", xlabel="因子1の負荷量", ylabel="因子2の負荷量",
           xlim=(-0.4, 1.1), ylim=(-0.6, 1.1), aspect="equal")
fig.tight_layout()
plt.show()
pd.DataFrame(L2v, index=STATS, columns=["因子1(回転後)", "因子2(回転後)"]).round(3)

# %% 25-3
# プロマックス回転（斜交回転）: バリマックス解を累乗した目標行列に最小2乗で近づける
def promax(Lv, power=4):
    """パターン行列と因子間相関行列を返す（正規化なし）."""
    P = Lv * np.abs(Lv) ** (power - 1)                  # 目標行列: 大きい負荷量を強調
    U = np.linalg.lstsq(Lv, P, rcond=None)[0]
    U = U @ np.diag(np.sqrt(np.diag(np.linalg.inv(U.T @ U))))   # 因子の分散が1になるよう列を調整
    pattern = Lv @ U
    Uinv = np.linalg.inv(U)
    phi = Uinv @ Uinv.T                                 # 因子間相関行列
    return pattern, phi

pattern2, phi2 = promax(L2v)
structure2 = pattern2 @ phi2                            # 構造行列 = 変数と因子の相関
print("因子間相関 φ12 =", phi2[0, 1].round(3), " 対角:", np.diag(phi2).round(6))
print("再現される共通性が回転前と一致:", np.allclose(np.diag(pattern2 @ phi2 @ pattern2.T), (L2 ** 2).sum(1)))
pd.concat({"バリマックス": pd.DataFrame(L2v, index=STATS, columns=["因子1", "因子2"]),
           "プロマックス(パターン)": pd.DataFrame(pattern2, index=STATS, columns=["因子1", "因子2"]),
           "プロマックス(構造)": pd.DataFrame(structure2, index=STATS, columns=["因子1", "因子2"])},
          axis=1).round(3)

# %% 25-4
# 因子得点（回帰法 = 事後平均）: E[f|x] = (I + Λ'Ψ^{-1}Λ)^{-1} Λ'Ψ^{-1} x
def factor_scores(Z, L, psi):
    Pinv = np.diag(1 / psi)
    return (Z - Z.mean(0)) @ np.linalg.solve(np.eye(L.shape[1]) + L.T @ Pinv @ L, L.T @ Pinv).T

# 式の照合: sklearn の推定値を代入すると transform と一致する
print("手計算と sklearn transform の最大差:",
      np.abs(factor_scores(Z_fa, fa_sk_v.components_.T, fa_sk_v.noise_variance_) - fa_sk_v.transform(Z_fa)).max().round(10))
fscore = factor_scores(Z_fa, L2v, psi2)                # 25-2 のバリマックス解の因子得点
print("因子得点の分散（1より小さい）:", fscore.var(0).round(3), " 相関:", np.corrcoef(fscore.T)[0, 1].round(3))

fig, ax = plt.subplots(figsize=(7, 5.2))
ax.scatter(fscore[:, 0], fscore[:, 1], s=10, alpha=0.4, color=PALETTE[0])
for nm in ["ツボツボ", "テッカニン", "ハピナス", "メガミュウツーY", "コイキング", "メガハガネール", "フェローチェ"]:
    i = df.index[df["名前"] == nm][0]
    ax.scatter(fscore[i, 0], fscore[i, 1], s=18, color=INK["primary"])
    ax.annotate(nm, (fscore[i, 0], fscore[i, 1]), xytext=(4, 4), textcoords="offset points", fontsize=9)
ax.set(title="因子得点（2因子・バリマックス回転）", xlabel="因子1の得点", ylabel="因子2の得点")
fig.tight_layout()
plt.show()

# %% 25-5
# 主成分分析との比較: 2成分の PCA 負荷量と 2因子の負荷量、相関行列の再現誤差
ev, evec = np.linalg.eigh(R_fa)
ev, evec = ev[::-1][:2], evec[:, ::-1][:, :2]
L_pca = evec * np.sqrt(ev)
L_pca = L_pca * np.sign(L_pca.sum(0))
off = ~np.eye(p_fa, dtype=bool)
res_fa = R_fa - (L2 @ L2.T + np.diag(psi2))
res_pca = R_fa - L_pca @ L_pca.T
print("相関行列の非対角成分の再現誤差（RMS）  因子分析: {:.4f} / PCA: {:.4f}".format(
    np.sqrt((res_fa[off] ** 2).mean()), np.sqrt((res_pca[off] ** 2).mean())))
print("対角成分（分散）の再現  因子分析: 共通性+独自性=1 / PCA: 負荷量の2乗和 =", (L_pca ** 2).sum(1).round(3))
pd.DataFrame(np.c_[L_pca, (L_pca ** 2).sum(1), L2, comm], index=STATS,
             columns=["PC1", "PC2", "PCA 説明率", "因子1", "因子2", "共通性"]).round(3)

# %% 25-6
# グラフィカルモデル: 精度行列 Ω = R^{-1} から偏相関、t 検定で辺を選ぶ
Omega = np.linalg.inv(R_fa)
pcor = -Omega / np.sqrt(np.outer(np.diag(Omega), np.diag(Omega)))
np.fill_diagonal(pcor, 1)
# 照合: HP と攻撃の偏相関 = 他の4変数に回帰した残差どうしの相関
others = [2, 3, 4, 5]
A_ = np.c_[np.ones(n_fa), Z_fa[:, others]]
res0 = Z_fa[:, 0] - A_ @ np.linalg.lstsq(A_, Z_fa[:, 0], rcond=None)[0]
res1 = Z_fa[:, 1] - A_ @ np.linalg.lstsq(A_, Z_fa[:, 1], rcond=None)[0]
print("偏相関(HP, 攻撃): 精度行列から {:.4f} / 残差の相関 {:.4f}".format(pcor[0, 1], np.corrcoef(res0, res1)[0, 1]))

# H0: 偏相関 = 0。t = r √{(n-p)/(1-r²)} ~ t(n-p)（多変量正規を仮定）。15ペアでボンフェローニ補正
edges = []
for i in range(p_fa):
    for j in range(i + 1, p_fa):
        r = pcor[i, j]
        t = r * np.sqrt((n_fa - p_fa) / (1 - r ** 2))
        pv = 2 * stats.t.sf(abs(t), n_fa - p_fa)
        edges.append({"変数1": STATS[i], "変数2": STATS[j], "相関": R_fa[i, j], "偏相関": r,
                      "t": t, "p値": pv, "辺(p<0.05/15)": pv < 0.05 / 15})
edge_df = pd.DataFrame(edges)
print(f"自由度 n-p = {n_fa - p_fa}, 有意水準 5%（ボンフェローニ補正で各 {0.05 / 15:.4f}）")
print("辺の数:", int(edge_df["辺(p<0.05/15)"].sum()), "/ 15")

edge_df["辺(|偏相関|≥0.2)"] = edge_df["偏相関"].abs() >= 0.2
print("辺の数（|偏相関| ≥ 0.2 の閾値）:", int(edge_df["辺(|偏相関|≥0.2)"].sum()), "/ 15")

fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), gridspec_kw={"width_ratios": [1.2, 1, 1]})
im = axes[0].imshow(pcor, cmap=DIV_CMAP, vmin=-1, vmax=1)
for (i, j), v in np.ndenumerate(pcor):
    if i != j:
        axes[0].text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=9)
axes[0].set(xticks=range(p_fa), xticklabels=STATS, yticks=range(p_fa), yticklabels=STATS, title="偏相関行列")
axes[0].grid(False)
fig.colorbar(im, ax=axes[0], fraction=0.046, label="偏相関係数")
ang = np.pi / 2 - 2 * np.pi * np.arange(p_fa) / p_fa
pos = np.c_[np.cos(ang), np.sin(ang)]
for ax, col, ttl in [(axes[1], "辺(p<0.05/15)", "検定で選んだ辺（ボンフェローニ）"),
                     (axes[2], "辺(|偏相関|≥0.2)", "閾値で選んだ辺（|偏相関| ≥ 0.2）")]:
    for _, e in edge_df[edge_df[col]].iterrows():
        i, j = STATS.index(e["変数1"]), STATS.index(e["変数2"])
        ax.plot(*pos[[i, j]].T, color=PALETTE[0] if e["偏相関"] < 0 else PALETTE[7],
                lw=1 + 12 * abs(e["偏相関"]), solid_capstyle="round", zorder=1)
    ax.scatter(*pos.T, s=1100, color=INK["surface"], edgecolor=INK["secondary"], zorder=2)
    for k, s_ in enumerate(STATS):
        ax.text(*pos[k], s_, ha="center", va="center", fontsize=11, zorder=4)
    ax.plot([], [], color=PALETTE[7], lw=3, label="正の偏相関")
    ax.plot([], [], color=PALETTE[0], lw=3, label="負の偏相関")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    ax.set(xlim=(-1.35, 1.35), ylim=(-1.35, 1.35), aspect="equal", title=f"{ttl}\n{int(edge_df[col].sum())}本, 線の太さ ∝ |偏相関|")
    ax.axis("off")
fig.tight_layout()
plt.show()
edge_df.round(4)
