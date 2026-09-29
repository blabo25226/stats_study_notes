"""第05章 離散型分布."""
from poke import *

df = load_data()

# %% 05-0
# この章で使う列の要約
d05 = df[["図鑑番号", "雄率", "捕獲率", "タイプ1"]]
print("図鑑番号の範囲:", d05["図鑑番号"].min(), "〜", d05["図鑑番号"].max(),
      " 種類数:", d05["図鑑番号"].nunique())
print("\n雄率の値ごとの行数（NaN は性別不明）")
print(d05["雄率"].value_counts(dropna=False).sort_index().to_string())
print("\n捕獲率の要約")
print(d05["捕獲率"].describe().round(1).to_string())
print("\nタイプ1の上位5水準")
print(d05["タイプ1"].value_counts().head(5).to_string())

# %% 05-1
# 離散一様分布: 全国図鑑番号 1〜k を等確率で1つ選ぶ
k_uni = int(df["図鑑番号"].max())            # 807
rng = get_rng()
draws_uni = rng.integers(1, k_uni + 1, size=10000)
print(f"k = {k_uni}")
print(f"期待値  理論 (k+1)/2      = {(k_uni + 1) / 2:.1f}   シミュレーション = {draws_uni.mean():.1f}")
print(f"分散    理論 (k^2-1)/12   = {(k_uni**2 - 1) / 12:.0f}  シミュレーション = {draws_uni.var():.0f}")

# 図鑑番号が一様でも、その番号の「世代」は一様ではない（世代ごとの種類数が違う）
gen_of_no = pd.cut(draws_uni, GEN_BOUNDS, labels=range(1, 8)).astype(int)
gen_theory = np.diff(np.minimum(GEN_BOUNDS, k_uni)) / k_uni   # 第7世代は 722〜807 の86種（GEN_BOUNDS の上限809より小さい）
pd.DataFrame({"理論確率 (種類数/807)": gen_theory,
              "シミュレーション": pd.Series(gen_of_no).value_counts(normalize=True).sort_index().values},
             index=pd.Index(range(1, 8), name="世代")).round(3)

# %% 05-2
# ベルヌーイ分布・二項分布: 雄率 p のポケモンのタマゴ n 個に含まれるオスの数
rng = get_rng()
n_egg = 6
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
for ax, p_male in zip(axes, [0.5, 0.875]):
    eggs = rng.random((10000, n_egg)) < p_male          # 各タマゴは独立なベルヌーイ試行
    males = eggs.sum(axis=1)
    x = np.arange(n_egg + 1)
    sim_pmf = np.bincount(males, minlength=n_egg + 1) / len(males)
    ax.bar(x - 0.2, sim_pmf, width=0.4, color=PALETTE[0], label="シミュレーション")
    ax.bar(x + 0.2, stats.binom.pmf(x, n_egg, p_male), width=0.4, color=PALETTE[1], label="理論 Bin(n, p)")
    ax.set(title=f"雄率 p = {p_male}（{(df['雄率'] == p_male).sum()}行）",
           xlabel=f"タマゴ {n_egg} 個中のオスの数", ylabel="確率")
    ax.legend()
    print(f"p = {p_male}: 1個のベルヌーイ 平均 {eggs[:, 0].mean():.3f}（理論 {p_male}）"
          f" 分散 {eggs[:, 0].var():.3f}（理論 {p_male * (1 - p_male):.3f}）")
    print(f"          二項   平均 {males.mean():.3f}（理論 np = {n_egg * p_male:.3f}）"
          f" 分散 {males.var():.3f}（理論 np(1-p) = {n_egg * p_male * (1 - p_male):.3f}）")
fig.tight_layout()
plt.show()

# %% 05-3
# 超幾何分布: 920匹から n 匹を非復元抽出したときの「タイプ1がみず」の数
N_pop = len(df)
is_water = (df["タイプ1"] == "みず").to_numpy()
M_water = int(is_water.sum())
rng = get_rng()
rows_hg = []
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
for ax, n_draw in zip(axes, [20, 300]):
    # 実際にデータの行を非復元で選ぶ
    counts = np.array([is_water[rng.choice(N_pop, n_draw, replace=False)].sum() for _ in range(4000)])
    hg = stats.hypergeom(N_pop, M_water, n_draw)       # scipy の引数は (母集団, 当たり数, 抽出数)
    bn = stats.binom(n_draw, M_water / N_pop)
    x = np.arange(counts.min(), counts.max() + 1)
    ax.hist(counts, bins=np.arange(x[0] - 0.5, x[-1] + 1.5), density=True,
            color=PALETTE[0], label="非復元抽出のシミュレーション")
    ax.plot(x, hg.pmf(x), "o-", ms=3, color=PALETTE[1], label="超幾何分布")
    ax.plot(x, bn.pmf(x), "--", color=PALETTE[2], label="二項近似")
    ax.set(title=f"n = {n_draw} 匹抽出", xlabel="みずタイプの数（匹）", ylabel="確率")
    fpc = (N_pop - n_draw) / (N_pop - 1)             # 有限母集団修正
    p_w = M_water / N_pop
    rows_hg.append({"n": n_draw, "平均(シミュ)": counts.mean(), "平均 nM/N": n_draw * p_w,
                    "分散(シミュ)": counts.var(), "超幾何の分散": n_draw * p_w * (1 - p_w) * fpc,
                    "二項の分散": n_draw * p_w * (1 - p_w), "修正項 (N-n)/(N-1)": fpc})
axes[0].legend(fontsize=8)
fig.tight_layout()
plt.show()
print(f"N = {N_pop}, M = {M_water}（みず）, M/N = {M_water / N_pop:.4f}")
pd.DataFrame(rows_hg).round(3)

# %% 05-4
# ポアソン分布（少数の法則）: 捕獲率3のポケモンにボールを n 回投げたときの成功回数
# 簡略化モデル: 1回あたりの成功確率を p = 捕獲率/255 と仮定する（実際のゲームの捕獲式はより複雑）
lam = 100 * 3 / 255                                   # λ = np を一定に保つ
x = np.arange(0, 9)
rows_po = []
for n_throw in [5, 20, 100, 1000]:
    p_throw = lam / n_throw
    b = stats.binom.pmf(x, n_throw, p_throw)
    po = stats.poisson.pmf(x, lam)
    # 全変動距離 (1/2)Σ|P(X=x) - P(Y=x)|（x の全範囲で計算）
    xx = np.arange(0, n_throw + 1)
    tv = 0.5 * (np.abs(stats.binom.pmf(xx, n_throw, p_throw) - stats.poisson.pmf(xx, lam)).sum()
                + stats.poisson.sf(n_throw, lam))
    rows_po.append({"n": n_throw, "p": p_throw, "P(X=0) 二項": b[0], "P(X=0) ポアソン": po[0], "全変動距離": tv})
print(f"λ = np = {lam:.3f}")
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.bar(x - 0.2, stats.binom.pmf(x, 20, lam / 20), width=0.4, color=PALETTE[0], label="Bin(20, λ/20)")
ax.bar(x + 0.2, stats.poisson.pmf(x, lam), width=0.4, color=PALETTE[1], label="Po(λ)")
ax.set(title=f"少数の法則（λ = {lam:.2f}）", xlabel="成功回数", ylabel="確率")
ax.legend()
plt.show()
pd.DataFrame(rows_po).round(4)

# %% 05-5
# 幾何分布: 捕まるまでの失敗回数（簡略化モデル: p = 捕獲率/255 と仮定）
rng = get_rng()
examples_geo = {"捕獲率45（御三家など）": 45, "捕獲率190": 190, "捕獲率3（伝説など）": 3}
rows_geo = []
for label, rate in examples_geo.items():
    p_c = rate / 255
    fails = rng.geometric(p_c, size=20000) - 1         # numpy は「試行回数」を返すので1を引いて失敗回数に
    rows_geo.append({"例": label, "p": p_c, "平均(シミュ)": fails.mean(), "平均 (1-p)/p": (1 - p_c) / p_c,
                     "分散(シミュ)": fails.var(), "分散 (1-p)/p^2": (1 - p_c) / p_c**2})
print(pd.DataFrame(rows_geo).round(3).to_string(index=False))

# 無記憶性 P(X >= m+n | X >= m) = P(X >= n) を捕獲率45で確認
p_c = 45 / 255
fails45 = rng.geometric(p_c, size=200000) - 1
n_more = 3
print(f"\n無記憶性（p = 45/255, n = {n_more}）: 理論 P(X >= n) = (1-p)^n = {(1 - p_c) ** n_more:.4f}")
for m in [0, 5, 10]:
    cond = (fails45[fails45 >= m] >= m + n_more).mean()
    print(f"  m = {m:2d}: シミュレーション P(X >= m+n | X >= m) = {cond:.4f}")

# %% 05-6
# 負の二項分布: 捕獲率45のポケモンを r = 3 匹捕まえるまでの失敗回数
# 再生性の確認: 独立な Geo(p) を r 個足すと NB(r, p) になる
rng = get_rng()
r_nb, p_c = 3, 45 / 255
geo_sum = (rng.geometric(p_c, size=(20000, r_nb)) - 1).sum(axis=1)
x = np.arange(0, 60)
nb = stats.nbinom(r_nb, p_c)                          # scipy の nbinom は「r 回成功までの失敗回数」
print(f"平均  シミュ {geo_sum.mean():.2f}  理論 r(1-p)/p   = {r_nb * (1 - p_c) / p_c:.2f}")
print(f"分散  シミュ {geo_sum.var():.1f}  理論 r(1-p)/p^2 = {r_nb * (1 - p_c) / p_c**2:.1f}")
# pmf の定義式 C(x+r-1, x) p^r (1-p)^x と scipy の一致
from scipy.special import comb
pmf_hand = comb(x + r_nb - 1, x) * p_c**r_nb * (1 - p_c) ** x
print("定義式と scipy.stats.nbinom.pmf の最大差:", np.abs(pmf_hand - nb.pmf(x)).max())

fig, ax = plt.subplots(figsize=(7, 3.8))
ax.hist(geo_sum, bins=np.arange(-0.5, 60.5), density=True, color=PALETTE[0], label="Geo(p) 3個の和（シミュレーション）")
ax.plot(x, nb.pmf(x), "o-", ms=3, color=PALETTE[1], label="NB(3, p) の確率関数")
ax.set(title="3匹捕まえるまでの失敗回数（p = 45/255 と仮定）", xlabel="失敗回数（回）", ylabel="確率")
ax.legend()
plt.show()

# %% 05-7
# 多項分布: タイプ1の構成比を p として n 匹を復元抽出したときの各タイプの数
top3 = ["みず", "ノーマル", "くさ"]
type_group = df["タイプ1"].astype(str).where(df["タイプ1"].isin(top3), "その他")
cats = top3 + ["その他"]
p_multi = type_group.value_counts(normalize=True)[cats].to_numpy()
n_multi = 30
rng = get_rng()
codes = pd.Categorical(type_group, categories=cats).codes
samp = codes[rng.integers(0, len(df), size=(10000, n_multi))]      # データの行を復元抽出
counts_multi = np.stack([(samp == j).sum(axis=1) for j in range(len(cats))], axis=1)

cov_theory = n_multi * (np.diag(p_multi) - np.outer(p_multi, p_multi))  # Var = np(1-p), Cov = -n p_i p_j
sd_t = np.sqrt(np.diag(cov_theory))
corr_theory = cov_theory / np.outer(sd_t, sd_t)
print("構成比 p:", dict(zip(cats, p_multi.round(4))))
print("\n共分散行列（上: 理論 n(diag(p) - pp^T), 下: シミュレーション）")
print(pd.DataFrame(cov_theory, index=cats, columns=cats).round(3).to_string())
print(pd.DataFrame(np.cov(counts_multi.T), index=cats, columns=cats).round(3).to_string())
print("\n相関行列（上: 理論 -sqrt(p_i p_j / ((1-p_i)(1-p_j))), 下: シミュレーション）")
print(pd.DataFrame(corr_theory, index=cats, columns=cats).round(3).to_string())
pd.DataFrame(np.corrcoef(counts_multi.T), index=cats, columns=cats).round(3)
