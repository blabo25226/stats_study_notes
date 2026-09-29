"""第22章 主成分分析."""
from poke import *

df = load_data()

# %% 22-0
from sklearn.decomposition import PCA
from sklearn.neural_network import MLPRegressor

# 種族値6項目（全920行）。標準化は不偏分散（ddof=1）で行い、Z の共分散行列＝標本相関行列にする
X_pca = df[STATS].astype(float)
Z_pca = (X_pca - X_pca.mean()) / X_pca.std(ddof=1)
n_pca, p_pca = Z_pca.shape
print(f"n = {n_pca}, p = {p_pca}")
print("\n要約統計")
print(X_pca.describe().T[["mean", "std", "min", "max"]].round(1).to_string())
print("\n標本相関行列")
X_pca.corr().round(2)

# %% 22-1
# 相関行列の固有値分解（numpy）と sklearn PCA の照合
R_pca = np.corrcoef(Z_pca.T)
eigval, eigvec = np.linalg.eigh(R_pca)          # 昇順で返るので並べ替える
order = np.argsort(eigval)[::-1]
eigval, eigvec = eigval[order], eigvec[:, order]
# 固有ベクトルの符号は任意。最大絶対値成分が正になるようにそろえる
sign = np.sign(eigvec[np.abs(eigvec).argmax(axis=0), range(p_pca)])
eigvec = eigvec * sign

pca_full = PCA().fit(Z_pca)
comp_sk = pca_full.components_.T * np.sign(np.sum(pca_full.components_.T * eigvec, axis=0))
print("固有値（numpy）   :", eigval.round(4))
print("固有値（sklearn） :", pca_full.explained_variance_.round(4))
print("固有値の和 =", eigval.sum().round(4), "（= p）")
print("固有ベクトルの最大差:", np.abs(comp_sk - eigvec).max().round(10))
pc_names = [f"PC{i+1}" for i in range(p_pca)]
pd.DataFrame(eigvec, index=STATS, columns=pc_names).round(3)

# %% 22-2
# 寄与率・累積寄与率とスクリープロット
contrib = eigval / eigval.sum()
contrib_tab = pd.DataFrame({"固有値": eigval, "寄与率": contrib, "累積寄与率": contrib.cumsum()},
                           index=pc_names)
print(contrib_tab.round(3).to_string())
print("\nカイザー基準（固有値 > 1）で選ぶ成分数:", int((eigval > 1).sum()))
print("累積寄与率 80% を超える最小の成分数:", int(np.argmax(contrib.cumsum() >= 0.8) + 1))

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
axes[0].plot(range(1, p_pca + 1), eigval, marker="o", color=PALETTE[0])
axes[0].axhline(1, color=INK["muted"], ls="--", lw=1)
axes[0].text(p_pca, 1.05, "固有値 = 1（カイザー基準）", ha="right", va="bottom", fontsize=9)
axes[0].set(title="スクリープロット", xlabel="主成分の番号", ylabel="固有値（主成分の分散）")
axes[1].bar(range(1, p_pca + 1), contrib, color=PALETTE[0], label="寄与率")
axes[1].plot(range(1, p_pca + 1), contrib.cumsum(), marker="o", color=PALETTE[1], label="累積寄与率")
axes[1].axhline(0.8, color=INK["muted"], ls="--", lw=1)
axes[1].set(title="寄与率と累積寄与率", xlabel="主成分の番号", ylabel="割合", ylim=(0, 1.05))
axes[1].legend(loc="center right")
fig.tight_layout()
plt.show()

# %% 22-3
# 主成分負荷量 = 固有ベクトル × √固有値 = 標準化変数と主成分得点の相関係数
scores_pca = Z_pca.values @ eigvec                 # 主成分得点
loading = eigvec * np.sqrt(eigval)
corr_zs = np.array([[np.corrcoef(Z_pca.values[:, j], scores_pca[:, k])[0, 1]
                     for k in range(p_pca)] for j in range(p_pca)])
print("負荷量と相関係数の最大差:", np.abs(loading - corr_zs).max().round(10))
print("主成分得点の分散（= 固有値）:", scores_pca.var(axis=0, ddof=1).round(4))
loading_df = pd.DataFrame(loading, index=STATS, columns=pc_names)
print("\n各変数の負荷量の2乗和（全成分）= 1:", (loading_df ** 2).sum(axis=1).round(4).tolist())

fig, ax = plt.subplots(figsize=(5.5, 4))
im = ax.imshow(loading_df.iloc[:, :3], cmap=DIV_CMAP, vmin=-1, vmax=1, aspect="auto")
for (j, k), v in np.ndenumerate(loading_df.iloc[:, :3].values):
    ax.text(k, j, f"{v:.2f}", ha="center", va="center", fontsize=10)
ax.set(xticks=range(3), xticklabels=pc_names[:3], yticks=range(p_pca), yticklabels=STATS,
       title="主成分負荷量（第1〜3主成分）")
ax.grid(False)
fig.colorbar(im, ax=ax, label="相関係数")
fig.tight_layout()
plt.show()
loading_df.iloc[:, :3].round(3)

# %% 22-4
# 主成分得点の散布図（第1・第2主成分）と負荷量の矢印（バイプロット）
fig, ax = plt.subplots(figsize=(7.5, 5.5))
ax.scatter(scores_pca[:, 0], scores_pca[:, 1], s=10, alpha=0.4, color=PALETTE[0], label="ポケモン")
label_names = ["ツボツボ", "テッカニン", "メガミュウツーY", "コイキング", "アルセウス", "メガハガネール"]
for nm in label_names:
    i = df.index[df["名前"] == nm][0]
    ax.annotate(nm, (scores_pca[i, 0], scores_pca[i, 1]), xytext=(4, 4),
                textcoords="offset points", fontsize=9)
    ax.scatter(scores_pca[i, 0], scores_pca[i, 1], s=18, color=INK["primary"])
arrow_scale = 3
for j, s in enumerate(STATS):
    ax.arrow(0, 0, loading[j, 0] * arrow_scale, loading[j, 1] * arrow_scale,
             color=PALETTE[1], width=0.02, head_width=0.12, length_includes_head=True)
    dy = {"HP": -0.25, "攻撃": 0.25}.get(s, 0)   # 向きの近い HP と攻撃のラベルをずらす
    ax.text(loading[j, 0] * arrow_scale * 1.12, loading[j, 1] * arrow_scale * 1.12 + dy, s,
            fontsize=10, ha="center", va="center")
ax.set(title="主成分得点（点）と主成分負荷量×3（矢印）",
       xlabel=f"第1主成分得点（寄与率 {contrib[0]:.0%}）", ylabel=f"第2主成分得点（寄与率 {contrib[1]:.0%}）")
fig.tight_layout()
plt.show()

# 第1・第2主成分の上位・下位
pc_tab = pd.DataFrame({"名前": df["名前"], "合計種族値": df["合計種族値"],
                       "PC1": scores_pca[:, 0], "PC2": scores_pca[:, 1]})
print("PC1 と合計種族値の相関:", np.corrcoef(pc_tab["PC1"], pc_tab["合計種族値"])[0, 1].round(3))
print("\nPC2 が大きい（素早・特攻寄り）5匹:", pc_tab.nlargest(5, "PC2")["名前"].tolist())
print("PC2 が小さい（防御・特防寄り）5匹:", pc_tab.nsmallest(5, "PC2")["名前"].tolist())

# %% 22-5
# 共分散行列 vs 相関行列: 単位の違う変数（重さ kg）を混ぜると差が大きい
def pca_first(M, cols):
    """行列 M の第1固有ベクトルと寄与率を返す."""
    w, v = np.linalg.eigh(M)
    v1 = v[:, -1] * np.sign(v[np.abs(v[:, -1]).argmax(), -1])
    return pd.Series(v1, index=cols), w[-1] / w.sum()

cols_mix = STATS + ["重さ"]
X_mix = df[cols_mix].astype(float)
res = {}
for label, cols in [("6項目", STATS), ("6項目+重さ", cols_mix)]:
    v_cov, r_cov = pca_first(np.cov(X_mix[cols].T), cols)
    v_cor, r_cor = pca_first(np.corrcoef(X_mix[cols].T), cols)
    res[(label, "共分散")] = v_cov
    res[(label, "相関")] = v_cor
    print(f"{label}: 第1主成分の寄与率  共分散行列 {r_cov:.3f} / 相関行列 {r_cor:.3f}")
print("\n標準偏差:", X_mix.std().round(1).to_dict())
print("\n第1主成分の係数（固有ベクトル）")
pd.DataFrame(res).reindex(cols_mix).round(3)

# %% 22-6
# 自己符号化器（2次元のボトルネック）と主成分分析の再構成誤差の比較
Zv = Z_pca.values
pca2 = PCA(n_components=2).fit(Zv)
recon_pca = pca2.inverse_transform(pca2.transform(Zv))
mse_pca = np.mean((Zv - recon_pca) ** 2)

# 線形（恒等活性化）の自己符号化器: 入力6 → 2 → 出力6
ae_lin = MLPRegressor(hidden_layer_sizes=(2,), activation="identity", solver="adam",
                      learning_rate_init=0.01, max_iter=3000, tol=1e-7, random_state=SEED).fit(Zv, Zv)
mse_lin = np.mean((Zv - ae_lin.predict(Zv)) ** 2)
# 非線形（tanh）の自己符号化器: 6 → 8 → 2 → 8 → 6
ae_tanh = MLPRegressor(hidden_layer_sizes=(8, 2, 8), activation="tanh", solver="adam",
                       learning_rate_init=0.01, max_iter=3000, tol=1e-7, random_state=SEED).fit(Zv, Zv)
mse_tanh = np.mean((Zv - ae_tanh.predict(Zv)) ** 2)

print(f"PCA（2成分）の再構成誤差（平均2乗誤差）: {mse_pca:.4f}")
print(f"  理論値 = 捨てた固有値の和 / p × (n-1)/n = {eigval[2:].sum() / p_pca * (n_pca - 1) / n_pca:.4f}")
print(f"線形自己符号化器（6-2-6）            : {mse_lin:.4f}")
print(f"非線形自己符号化器（6-8-2-8-6, tanh） : {mse_tanh:.4f}")

# 線形自己符号化器の中間層（符号）は PCA の2次元部分空間とほぼ同じか: 正準相関で確認
code_lin = Zv @ ae_lin.coefs_[0] + ae_lin.intercepts_[0]
q1, _ = np.linalg.qr(code_lin - code_lin.mean(axis=0))
q2, _ = np.linalg.qr(pca2.transform(Zv))
print("線形AEの符号とPCA得点が張る部分空間の正準相関:",
      np.linalg.svd(q1.T @ q2, compute_uv=False).round(4))
