"""第28章 分割表."""
from poke import *

df = load_data()

# %% 28-0
import statsmodels.api as sm
import statsmodels.formula.api as smf

# 2×2 表の要因と結果
ct = df.assign(
    高種族値=np.where(df["合計種族値"] >= 570, "570以上", "570未満"),
    性別不明=np.where(df["性別"] == "不明", "不明", "あり"),
)
print("合計種族値570以上:", (df["合計種族値"] >= 570).sum(), "匹 / 性別不明:", (df["性別"] == "不明").sum(), "匹")
print("\nタイプ1の件数（少ない順に5つ）")
print(df["タイプ1"].value_counts().tail(5).to_string())
print("\n世代ごとの件数")
print(df["世代"].value_counts().sort_index().to_string())

# %% 28-1
# 2×2 表: 行 = 要因（高種族値か）, 列 = 結果（性別不明か）
tab22 = pd.crosstab(ct["高種族値"], ct["性別不明"]).loc[["570以上", "570未満"], ["不明", "あり"]]
print(tab22, "\n")
a, b = tab22.iloc[0]
c, d = tab22.iloc[1]
z975 = stats.norm.ppf(0.975)

# 相対リスク（リスク = 性別不明の割合）
p1, p0 = a / (a + b), c / (c + d)
rr = p1 / p0
se_log_rr = np.sqrt(1 / a - 1 / (a + b) + 1 / c - 1 / (c + d))
ci_rr = np.exp(np.log(rr) + np.array([-1, 1]) * z975 * se_log_rr)

# オッズとオッズ比
odds1, odds0 = a / b, c / d
or22 = odds1 / odds0            # = ad / bc
se_log_or = np.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
ci_or = np.exp(np.log(or22) + np.array([-1, 1]) * z975 * se_log_or)

print(f"リスク: 570以上 {p1:.3f}, 570未満 {p0:.3f}")
print(f"相対リスク RR = {rr:.2f}  SE(log RR) = {se_log_rr:.3f}  95%CI = [{ci_rr[0]:.2f}, {ci_rr[1]:.2f}]")
print(f"オッズ: 570以上 {odds1:.3f}, 570未満 {odds0:.3f}")
print(f"オッズ比 OR = ad/bc = {or22:.2f}  log OR = {np.log(or22):.3f}  SE(log OR) = {se_log_or:.3f}")
print(f"  95%CI = [{ci_or[0]:.2f}, {ci_or[1]:.2f}]")

# statsmodels の Table2x2 と照合
t22 = sm.stats.Table2x2(tab22.values)
print(f"\nstatsmodels: RR = {t22.riskratio:.2f} CI = {np.round(t22.riskratio_confint(), 2)}, "
      f"OR = {t22.oddsratio:.2f} CI = {np.round(t22.oddsratio_confint(), 2)}")

# %% 28-2
# ケースコントロール型の抽出を模擬: 結果（性別不明か）で層を分け、各層から同数を抽出する
rng = get_rng()
is_case = (df["性別"] == "不明").to_numpy()
is_exp = (df["合計種族値"] >= 570).to_numpy()
case_idx, ctrl_idx = np.flatnonzero(is_case), np.flatnonzero(~is_case)
n_each, n_rep = 60, 2000
cc_rr, cc_or = [], []
for _ in range(n_rep):
    s = np.concatenate([rng.choice(case_idx, n_each, replace=False),
                        rng.choice(ctrl_idx, n_each, replace=False)])
    ca, ex = is_case[s], is_exp[s]
    aa, bb = np.sum(ex & ca) + 0.5, np.sum(ex & ~ca) + 0.5    # 0セル対策に0.5を加える
    cc_, dd = np.sum(~ex & ca) + 0.5, np.sum(~ex & ~ca) + 0.5
    cc_rr.append((aa / (aa + bb)) / (cc_ / (cc_ + dd)))
    cc_or.append(aa * dd / (bb * cc_))
cc_summary = pd.DataFrame({
    "母集団の値": [rr, or22],
    "ケースコントロール抽出での中央値": [np.median(cc_rr), np.median(cc_or)],
}, index=["相対リスク", "オッズ比"]).round(2)
print(f"各層 {n_each} 匹ずつ抽出を {n_rep} 回（抽出後の「性別不明」の割合は常に50%）")
cc_summary

# %% 28-3
# フィッシャーの正確検定: ドラゴン（タイプ1）に絞った小さな 2×2 表
drg = ct[df["タイプ1"] == "ドラゴン"]
tab_drg = pd.crosstab(drg["高種族値"], drg["性別不明"]).loc[["570以上", "570未満"], ["不明", "あり"]]
print(tab_drg, "\n")
(fa, fb), (fc, fd) = tab_drg.values
n_row1, n_col1, n_tot = fa + fb, fa + fc, fa + fb + fc + fd

# 周辺度数を固定すると、左上セル X は超幾何分布 HG(N=n_tot, K=n_col1, n=n_row1) に従う
x_vals = np.arange(max(0, n_row1 + n_col1 - n_tot), min(n_row1, n_col1) + 1)
from math import comb
pmf = np.array([comb(n_col1, x) * comb(n_tot - n_col1, n_row1 - x) / comb(n_tot, n_row1) for x in x_vals])
p_one = pmf[x_vals >= fa].sum()                       # 片側（OR > 1）
p_obs = pmf[x_vals == fa][0]
p_two = pmf[pmf <= p_obs * (1 + 1e-7)].sum()          # 両側（観測以下の確率の表をすべて足す）
print("X の値と確率（手計算）")
print(pd.Series(pmf, index=x_vals).round(4).to_string())
print(f"\n観測 X = {fa}: P(X = {fa}) = {p_obs:.5f}")
print(f"手計算:  片側 p = {p_one:.5f}, 両側 p = {p_two:.5f}")
res_g = stats.fisher_exact(tab_drg.values, alternative="greater")
res_2 = stats.fisher_exact(tab_drg.values)
print(f"scipy:   片側 p = {res_g.pvalue:.5f}, 両側 p = {res_2.pvalue:.5f}  （標本オッズ比 {res_2.statistic:.2f}）")
print("有意水準5%で、ドラゴンでも「高種族値と性別不明は独立」は棄却される" if res_2.pvalue < 0.05
      else "有意水準5%で独立は棄却されない")
# 全データの表でも実施
print(f"\n全920匹の表: フィッシャーの両側 p = {stats.fisher_exact(tab22.values).pvalue:.2e}")

# %% 28-4
# 独立性の χ² 検定（2×2 表）: 定義式と scipy の照合
obs22 = tab22.values.astype(float)
exp22 = obs22.sum(1, keepdims=True) * obs22.sum(0, keepdims=True) / obs22.sum()
chi2_def = ((obs22 - exp22) ** 2 / exp22).sum()
n22 = obs22.sum()
chi2_ad = n22 * (a * d - b * c) ** 2 / ((a + b) * (c + d) * (a + c) * (b + d))
chi2_yates = n22 * (abs(a * d - b * c) - n22 / 2) ** 2 / ((a + b) * (c + d) * (a + c) * (b + d))
sp_raw = stats.chi2_contingency(obs22, correction=False)
sp_yat = stats.chi2_contingency(obs22, correction=True)
print(f"定義式 χ² = {chi2_def:.2f}, (ad-bc)²の式 = {chi2_ad:.2f}, scipy = {sp_raw.statistic:.2f}")
print(f"イエーツ補正: 手計算 {chi2_yates:.2f}, scipy {sp_yat.statistic:.2f}, 自由度 1, p = {sp_yat.pvalue:.2e}")
print(f"クラメールの V = {np.sqrt(chi2_def / n22):.3f}（2×2 では |φ係数|）")

# %% 28-5
# r×c 表: タイプ1 × 世代。期待度数5未満のセルの割合を確認する
def expected_counts(tab):
    """独立のもとでの期待度数 n_i+ n_+j / n."""
    t = np.asarray(tab, dtype=float)
    return t.sum(1, keepdims=True) * t.sum(0, keepdims=True) / t.sum()


tab_tg = pd.crosstab(df["タイプ1"].astype(str), df["世代"])
e_tg = expected_counts(tab_tg)
print(f"元の表 {tab_tg.shape[0]}×{tab_tg.shape[1]}: 期待度数5未満のセル {np.mean(e_tg < 5):.0%}, 最小 {e_tg.min():.2f}")

# 水準をまとめる: タイプ1は上位8タイプ以外を「その他」、世代は 1-2 / 3-4 / 5 / 6-7
top_types = df["タイプ1"].value_counts().index[:8]
type_grp = df["タイプ1"].astype(str).where(df["タイプ1"].isin(top_types), "その他")
gen_grp = pd.cut(df["世代"], [0, 2, 4, 5, 7], labels=["1-2", "3-4", "5", "6-7"])
tab_rc = pd.crosstab(type_grp, gen_grp).loc[list(top_types) + ["その他"]]
e_rc = expected_counts(tab_rc)
print(f"まとめた表 {tab_rc.shape[0]}×{tab_rc.shape[1]}: 期待度数5未満のセル {np.mean(e_rc < 5):.0%}, 最小 {e_rc.min():.2f}")

o_rc = tab_rc.values
chi2_rc = ((o_rc - e_rc) ** 2 / e_rc).sum()
df_rc = (o_rc.shape[0] - 1) * (o_rc.shape[1] - 1)
sp_rc = stats.chi2_contingency(o_rc)
v_rc = np.sqrt(chi2_rc / (o_rc.sum() * (min(o_rc.shape) - 1)))
print(f"\nχ² = {chi2_rc:.2f}（scipy {sp_rc.statistic:.2f}）, 自由度 {df_rc}, p = {stats.chi2.sf(chi2_rc, df_rc):.4f}")
print(f"クラメールの V = {v_rc:.3f}")

# 標準化残差 (O-E)/sqrt(E) の図
resid_rc = (o_rc - e_rc) / np.sqrt(e_rc)
fig, ax = plt.subplots(figsize=(6.5, 5))
lim = np.abs(resid_rc).max()
im = ax.imshow(resid_rc, cmap=DIV_CMAP, vmin=-lim, vmax=lim, aspect="auto")
ax.set_xticks(range(o_rc.shape[1]), [f"第{g}世代" for g in tab_rc.columns])
ax.set_yticks(range(o_rc.shape[0]), tab_rc.index)
for i in range(o_rc.shape[0]):
    for j in range(o_rc.shape[1]):
        ax.text(j, i, f"{o_rc[i, j]}", ha="center", va="center", fontsize=9)
ax.grid(False)
ax.set(title="タイプ1×世代の標準化残差（数字は観測度数）", xlabel="世代区分", ylabel="タイプ1")
fig.colorbar(im, ax=ax, label="(O−E)/√E")
fig.tight_layout()
plt.show()

# %% 28-6
# 逸脱度 G² = 2 Σ O log(O/E): 独立モデルの飽和モデルに対する逸脱度
def g2_stat(obs, exp):
    obs, exp = np.asarray(obs, float), np.asarray(exp, float)
    m = obs > 0                          # 0 log 0 = 0
    return 2 * np.sum(obs[m] * np.log(obs[m] / exp[m]))


g2_22, g2_rc = g2_stat(obs22, exp22), g2_stat(o_rc, e_rc)
print(f"2×2 表:  G² = {g2_22:.2f}（Pearson χ² {chi2_def:.2f}）, 自由度 1, p = {stats.chi2.sf(g2_22, 1):.2e}")
print(f"9×4 表:  G² = {g2_rc:.2f}（Pearson χ² {chi2_rc:.2f}）, 自由度 {df_rc}, p = {stats.chi2.sf(g2_rc, df_rc):.4f}")
print("scipy (lambda_='log-likelihood'):", round(stats.chi2_contingency(o_rc, lambda_="log-likelihood").statistic, 2))

# Poisson GLM（独立モデル）の残差逸脱度とも一致する
long_rc = tab_rc.stack().rename("n").reset_index()
long_rc.columns = ["タイプ", "世代区分", "n"]
glm_ind = smf.glm("n ~ C(タイプ) + C(世代区分)", long_rc, family=sm.families.Poisson()).fit()
print(f"Poisson GLM（独立モデル）の逸脱度 = {glm_ind.deviance:.2f}, 残差自由度 = {glm_ind.df_resid:.0f}")

# %% 28-7
# 3元表: A = 複合タイプ, B = 世代区分, C = 成長区分
d3 = pd.DataFrame({
    "因子A": np.where(df["複合タイプ"], "複合", "単"),
    "因子B": pd.cut(df["世代"], [0, 3, 5, 7], labels=["1-3", "4-5", "6-7"]).astype(str),
    "因子C": pd.cut(df["成長経験値"], [0, 1_000_000, 1_100_000, 2_000_000],
                labels=["100万以下", "105-106万", "125万以上"]).astype(str),
})
tab3 = d3.value_counts().rename("n").reset_index().sort_values(["因子A", "因子B", "因子C"])
print(pd.crosstab([d3["因子A"], d3["因子B"]], d3["因子C"]), "\n")

# 階層的対数線形モデル（生成集合で表記）
models3 = {
    "[ABC]": "C(因子A)*C(因子B)*C(因子C)",
    "[AB][AC][BC]": "(C(因子A) + C(因子B) + C(因子C))**2",
    "[AB][BC]": "C(因子A)*C(因子B) + C(因子B)*C(因子C)",
    "[AC][BC]": "C(因子A)*C(因子C) + C(因子B)*C(因子C)",
    "[AB][AC]": "C(因子A)*C(因子B) + C(因子A)*C(因子C)",
    "[A][BC]": "C(因子A) + C(因子B)*C(因子C)",
    "[AB][C]": "C(因子A)*C(因子B) + C(因子C)",
    "[AC][B]": "C(因子A)*C(因子C) + C(因子B)",
    "[A][B][C]": "C(因子A) + C(因子B) + C(因子C)",
}
import warnings
with warnings.catch_warnings():   # 飽和モデルは残差自由度0のため警告が出るが問題ない
    warnings.simplefilter("ignore")
    fits3 = {k: smf.glm("n ~ " + f, tab3, family=sm.families.Poisson()).fit() for k, f in models3.items()}
llm_table = pd.DataFrame({
    "逸脱度G²": [m.deviance for m in fits3.values()],
    "自由度": [m.df_resid for m in fits3.values()],
    "p値(対飽和)": [stats.chi2.sf(m.deviance, m.df_resid) if m.df_resid > 0 else np.nan for m in fits3.values()],
    "AIC": [m.aic for m in fits3.values()],
}, index=fits3.keys())
llm_table.round(3)

# %% 28-8
# 入れ子モデルの比較（逸脱度の差 ~ χ²）
def compare(small, big):
    ds, db = fits3[small], fits3[big]
    diff, ddf = ds.deviance - db.deviance, ds.df_resid - db.df_resid
    print(f"{small:>13} vs {big:<13}: ΔG² = {diff:6.2f}, 自由度 {ddf:.0f}, p = {stats.chi2.sf(diff, ddf):.4f}")


compare("[AB][AC][BC]", "[ABC]")     # 3因子交互作用
compare("[AB][AC]", "[AB][AC][BC]")  # BC 交互作用
compare("[AB][BC]", "[AB][AC][BC]")  # AC 交互作用
compare("[AC][BC]", "[AB][AC][BC]")  # AB 交互作用
compare("[AB][C]", "[AB][AC]")       # [AB][AC] からさらに AC を除く
compare("[AC][B]", "[AB][AC]")       # [AB][AC] からさらに AB を除く

# 分解可能モデル [AB][AC]（B と C は A を与えたもとで条件付き独立）の期待度数は周辺度数から直接求まる
n_ab = d3.value_counts(["因子A", "因子B"])
n_ac = d3.value_counts(["因子A", "因子C"])
n_a = d3["因子A"].value_counts()
m_closed = np.array([n_ab[(r.因子A, r.因子B)] * n_ac[(r.因子A, r.因子C)] / n_a[r.因子A] for r in tab3.itertuples()])
print(f"\n[AB][AC] の期待度数: 閉形式 m = n_(ij+) n_(i+k) / n_(i++) と GLM の最大差 = "
      f"{np.max(np.abs(m_closed - fits3['[AB][AC]'].fittedvalues.to_numpy())):.2e}")

# A の水準ごとに B×C の独立性を見る（条件付き独立の直接の確認）
for lev, sub in d3.groupby("因子A"):
    r = stats.chi2_contingency(pd.crosstab(sub["因子B"], sub["因子C"]), lambda_="log-likelihood")
    print(f"  因子A = {lev}: B×C の G² = {r.statistic:.2f}, 自由度 {r.dof}, p = {r.pvalue:.3f}")

# %% 28-9
# 無向独立グラフ: 2因子交互作用があれば辺を引く
graph_models = ["[AB][AC][BC]", "[AB][AC]", "[A][B][C]"]
node_pos = {"A": (0, 1), "B": (-0.9, -0.5), "C": (0.9, -0.5)}
node_name = {"A": "A 複合タイプ", "B": "B 世代区分", "C": "C 成長区分"}
fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
for ax, mname in zip(axes, graph_models):
    gens = [g for g in mname.strip("[]").split("][")]
    edges = {tuple(sorted((u, v))) for g in gens for u in g for v in g if u < v}
    for u, v in edges:
        (x0, y0), (x1, y1) = node_pos[u], node_pos[v]
        ax.plot([x0, x1], [y0, y1], color=INK["secondary"], lw=2, zorder=1)
    for k, (x, y) in node_pos.items():
        ax.scatter(x, y, s=900, color=PALETTE[0], zorder=2)
        ax.text(x, y, k, ha="center", va="center", color="white", fontsize=13, fontweight="bold", zorder=3)
        ax.text(x, y - 0.32 if y < 0 else y + 0.3, node_name[k], ha="center", va="center", fontsize=9)
    ax.set(title=f"{mname}  G²={fits3[mname].deviance:.1f}, 自由度{fits3[mname].df_resid:.0f}",
           xlim=(-1.5, 1.5), ylim=(-1.0, 1.5))
    ax.axis("off")
fig.suptitle("対数線形モデルに対応する無向独立グラフ", fontweight="bold")
fig.tight_layout()
plt.show()
