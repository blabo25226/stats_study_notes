"""第24章 クラスター分析."""
from poke import *

df = load_data()

# %% 24-0
import warnings

# Windows 環境で出る KMeans・joblib の実行環境に関する警告を抑える（結果には影響しない）
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")
warnings.filterwarnings("ignore", message="KMeans is known to have a memory leak")
warnings.filterwarnings("ignore", message="Could not find the number of physical cores")

from scipy.cluster.hierarchy import cophenet, dendrogram, fcluster, linkage
from scipy.spatial.distance import pdist
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

# 階層的クラスタリング: 第1世代の姿違いを除く151匹
g1 = df[(df["世代"] == 1) & ~df["is_form"]].reset_index(drop=True)
Z_g1 = ((g1[STATS] - g1[STATS].mean()) / g1[STATS].std(ddof=1)).to_numpy()
# K-means: 全920行
Z_all = ((df[STATS] - df[STATS].mean()) / df[STATS].std(ddof=1)).to_numpy()
print("階層的クラスタリングの対象:", len(g1), "匹（第1世代・姿違いを除く）")
print("K-means の対象:", len(df), "匹（全行）")
g1[STATS].describe().T[["mean", "std", "min", "max"]].round(1)

# %% 24-1
# 5つの連結法の比較（ユークリッド距離、標準化データ）
methods = {"single": "最短距離法", "complete": "最長距離法", "average": "群平均法",
           "centroid": "重心法", "ward": "ウォード法"}
d_g1 = pdist(Z_g1)                     # 個体間のユークリッド距離
links = {m: linkage(Z_g1, method=m) for m in methods}   # 重心法・ウォード法は観測値から計算
rows = []
for m, lk in links.items():
    sizes = np.sort(np.bincount(fcluster(lk, t=4, criterion="maxclust"))[1:])[::-1]
    heights = lk[:, 2]
    rows.append({"方法": methods[m], "コーフェン相関": cophenet(lk, d_g1)[0],
                 "4クラスターの大きさ": sizes.tolist(),
                 "併合距離の逆転": int((np.diff(heights) < -1e-12).sum())})
print(pd.DataFrame(rows).set_index("方法").round(3).to_string())
for m in ["single", "ward"]:
    cut = fcluster(links[m], t=4, criterion="maxclust")
    small = [", ".join(g1["名前"][cut == c].head(4)) for c in np.unique(cut) if (cut == c).sum() <= 15]
    print(f"{methods[m]} の小さいクラスター:", " / ".join(small))

fig, axes = plt.subplots(2, 3, figsize=(13, 7))
for ax, (m, lk) in zip(axes.ravel(), links.items()):
    dendrogram(lk, ax=ax, truncate_mode="lastp", p=25, no_labels=True,
               color_threshold=0, above_threshold_color=PALETTE[0])
    ax.set(title=methods[m], ylabel="併合時のクラスター間距離")
    ax.grid(False, axis="x")
axes[1, 2].axis("off")
fig.suptitle("連結法ごとのデンドログラム（第1世代151匹, 最後の25クラスターまで表示）", fontsize=12)
fig.tight_layout()
plt.show()

# %% 24-2
# ウォード法のデンドログラム（名前つき）: 第1世代で合計種族値500以上の33匹
g1s = g1[g1["合計種族値"] >= 500].reset_index(drop=True)
Z_g1s = ((g1s[STATS] - g1[STATS].mean()) / g1[STATS].std(ddof=1)).to_numpy()   # 151匹の平均・SDで標準化
lk_s = linkage(Z_g1s, method="ward")
cut_s = fcluster(lk_s, t=4, criterion="maxclust")
fig, ax = plt.subplots(figsize=(7, 8))
dendrogram(lk_s, labels=g1s["名前"].tolist(), orientation="left", ax=ax,
           color_threshold=0, above_threshold_color=PALETTE[0], leaf_font_size=10)
ax.set(title="ウォード法（第1世代・合計種族値500以上の33匹）", xlabel="併合時の距離（ウォード法）")
ax.grid(False, axis="y")
fig.tight_layout()
plt.show()
prof_s = g1s.assign(クラスター=cut_s).groupby("クラスター")[STATS].mean().round(0)
prof_s["名前の例"] = [", ".join(g1s["名前"][cut_s == k].head(5)) for k in prof_s.index]
prof_s

# %% 24-3
# K-means（全920行）: エルボー法とシルエット係数
ks = range(2, 11)
inertias, sils = [], []
for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit(Z_all)
    inertias.append(km.inertia_)
    sils.append(silhouette_score(Z_all, km.labels_))
print(pd.DataFrame({"k": list(ks), "クラスター内平方和": inertias, "シルエット係数": sils}).round(3).to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
axes[0].plot(list(ks), inertias, marker="o", color=PALETTE[0])
axes[0].set(title="エルボー法", xlabel="クラスター数 k", ylabel="クラスター内平方和")
axes[1].plot(list(ks), sils, marker="o", color=PALETTE[0])
axes[1].set(title="平均シルエット係数", xlabel="クラスター数 k", ylabel="シルエット係数")
fig.tight_layout()
plt.show()

# %% 24-4
# 初期値依存性: n_init=1 で初期値だけを変えて20回
k_fix = 4
runs = [KMeans(n_clusters=k_fix, n_init=1, init="random", random_state=s).fit(Z_all) for s in range(20)]
inert = np.array([r.inertia_ for r in runs])
best = runs[int(inert.argmin())]
ari = np.array([adjusted_rand_score(best.labels_, r.labels_) for r in runs])
print(f"k={k_fix}, n_init=1（ランダム初期値）20回")
print("  クラスター内平方和: 最小 {:.1f} / 最大 {:.1f} / 最小値から1%以内の回数 {}/20".format(
    inert.min(), inert.max(), int((inert <= inert.min() * 1.01).sum())))
print("  最良解との調整ランド指数: 最小 {:.3f} / 中央値 {:.3f}".format(ari.min(), np.median(ari)))
km_best = KMeans(n_clusters=k_fix, n_init=20, random_state=SEED).fit(Z_all)
print(f"n_init=20（k-means++）の平方和: {km_best.inertia_:.1f}")

# %% 24-5
# クラスターの解釈: k=4 の各クラスターの平均種族値プロファイル（元の単位）
lab4 = km_best.labels_
# 合計種族値の平均が小さい順にクラスター番号を付け直す
order4 = df.groupby(lab4)["合計種族値"].mean().sort_values().index
relabel = {old: new for new, old in enumerate(order4, start=1)}
cl4 = pd.Series(lab4, index=df.index).map(relabel)
prof4 = df.groupby(cl4)[STATS + ["合計種族値"]].mean().round(0)
prof4.insert(0, "匹数", cl4.value_counts().sort_index())
centers = df.groupby(cl4)[STATS].mean()
dist_c = {k: ((Z_all[cl4 == k] - Z_all[cl4 == k].mean(0)) ** 2).sum(1) for k in prof4.index}
prof4["中心に近い例"] = [", ".join(df.loc[cl4 == k, "名前"].iloc[np.argsort(dist_c[k])[:4]]) for k in prof4.index]

fig, axes = plt.subplots(1, 4, figsize=(13, 3.6), sharey=True)
overall = df[STATS].mean()
for ax, k in zip(axes, prof4.index):
    ax.bar(STATS, centers.loc[k], color=PALETTE[0])
    ax.plot(STATS, overall, color=INK["secondary"], marker="_", ls="none", markersize=18, mew=2, label="全体平均")
    ax.set(title=f"クラスター{k}（{prof4.loc[k, '匹数']}匹）", ylim=(0, 150))
    ax.tick_params(axis="x", labelsize=9)
axes[0].set_ylabel("平均種族値")
axes[0].legend(loc="upper left")
fig.suptitle("K-means（k=4）の各クラスターの平均種族値", fontsize=12)
fig.tight_layout()
plt.show()
prof4
