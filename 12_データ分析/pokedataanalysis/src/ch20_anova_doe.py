"""第20章 分散分析と実験計画法."""
from poke import *

df = load_data()

# %% 20-0
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.oneway import anova_oneway

fmt4 = lambda v: f"{v:.4g}"  # 表示用（p値が 0.0 に丸められないように有効数字4桁）

# タイプ1ごとの件数・平均・標準偏差（合計種族値）
aov_summary = (df.groupby("タイプ1", observed=True)["合計種族値"]
               .agg(件数="size", 平均="mean", 標準偏差="std")
               .sort_values("件数", ascending=False))
print(f"全体: n = {len(df)}, 平均 = {df['合計種族値'].mean():.1f}, 標準偏差 = {df['合計種族値'].std():.1f}")
aov_summary.round(1)

# %% 20-2
# 一元配置分散分析: 平方和の分解 S_T = S_A + S_E を定義式から計算する
y_all = df["合計種族値"].astype(float)
grp_all = df.groupby("タイプ1", observed=True)["合計種族値"]
n_i = grp_all.size()
mean_i = grp_all.mean()
grand_mean = y_all.mean()
n_total, a_levels = len(y_all), len(n_i)

S_T = ((y_all - grand_mean) ** 2).sum()
S_A = (n_i * (mean_i - grand_mean) ** 2).sum()
S_E = ((y_all - grp_all.transform("mean")) ** 2).sum()
df_A, df_E = a_levels - 1, n_total - a_levels
F_A = (S_A / df_A) / (S_E / df_E)
p_A = stats.f.sf(F_A, df_A, df_E)

aov_table = pd.DataFrame({
    "平方和": [S_A, S_E, S_T],
    "自由度": [df_A, df_E, n_total - 1],
    "平均平方": [S_A / df_A, S_E / df_E, np.nan],
    "F": [F_A, np.nan, np.nan],
    "p値": [p_A, np.nan, np.nan],
}, index=["水準間 A（タイプ1）", "誤差 E", "総 T"])
print("手計算の分散分析表")
print(aov_table.to_string(float_format=fmt4))
print(f"\nS_A + S_E - S_T = {S_A + S_E - S_T:.2e}（0 になれば分解が成立）")
print(f"F の5%棄却点 F_{{0.05}}({df_A}, {df_E}) = {stats.f.ppf(0.95, df_A, df_E):.3f}")
print(f"決定係数 η² = S_A / S_T = {S_A / S_T:.3f}")

# statsmodels・scipy と照合
ow_model = smf.ols("合計種族値 ~ C(タイプ1)", data=df).fit()
print("\nstatsmodels anova_lm")
print(sm.stats.anova_lm(ow_model, typ=1).to_string(float_format=fmt4))
f_sp, p_sp = stats.f_oneway(*[g.to_numpy() for _, g in grp_all])
print(f"\nscipy f_oneway: F = {f_sp:.4f}, p = {p_sp:.3g}")

# %% 20-2b
# 各水準の母平均の95%信頼区間（誤差分散の推定値 σ̂² = S_E/(n-a) を共通に使う）
sigma2_hat = S_E / df_E
t_crit = stats.t.ppf(0.975, df_E)
ci_half = t_crit * np.sqrt(sigma2_hat / n_i)
ci_order = mean_i.sort_values().index

fig, ax = plt.subplots(figsize=(7, 5.5))
ypos = np.arange(len(ci_order))
ax.errorbar(mean_i[ci_order], ypos, xerr=ci_half[ci_order], fmt="o",
            color=PALETTE[0], ecolor=PALETTE[0], elinewidth=1.5, capsize=3)
ax.axvline(grand_mean, color=INK["muted"], linestyle="--", linewidth=1, label=f"全体平均 {grand_mean:.0f}")
ax.set_yticks(ypos, [f"{t}（{n_i[t]}）" for t in ci_order])
ax.set(title="タイプ1別の合計種族値の平均と95%信頼区間",
       xlabel="合計種族値の平均（点）と95%信頼区間（横線）", ylabel="タイプ1（件数）")
ax.legend(loc="lower right")
fig.tight_layout()
plt.show()

# %% 20-3
# 等分散性の検定（帰無仮説: 全水準の母分散が等しい）
groups_list = [g.to_numpy() for _, g in grp_all]
bt = stats.bartlett(*groups_list)
lv_mean = stats.levene(*groups_list, center="mean")
lv_med = stats.levene(*groups_list, center="median")
print(f"Bartlett 検定         : 統計量 = {bt.statistic:.3f}（近似 χ²({a_levels - 1})）, p = {bt.pvalue:.4f}")
print(f"Levene 検定（平均中心）: F = {lv_mean.statistic:.3f}（F({df_A}, {df_E})）, p = {lv_mean.pvalue:.4f}")
print(f"Levene 検定（中央値中心, Brown-Forsythe）: F = {lv_med.statistic:.3f}, p = {lv_med.pvalue:.4f}")

# Bartlett 統計量を定義式から計算して照合
s2_i = grp_all.var()
M_b = df_E * np.log(sigma2_hat) - ((n_i - 1) * np.log(s2_i)).sum()
C_b = 1 + (1 / (3 * (a_levels - 1))) * ((1 / (n_i - 1)).sum() - 1 / df_E)
print(f"Bartlett（手計算）      : {M_b / C_b:.3f}")

# 等分散を仮定しない Welch の分散分析（参考）
welch = anova_oneway(y_all, df["タイプ1"].astype(str), use_var="unequal")
print(f"\nWelch の分散分析: F = {welch.statistic:.3f}, 自由度 = ({welch.df[0]:.0f}, {welch.df[1]:.1f}), p = {welch.pvalue:.3g}")
print(f"標準偏差の範囲: {grp_all.std().min():.1f}（{grp_all.std().idxmin()}）〜 {grp_all.std().max():.1f}（{grp_all.std().idxmax()}）")

# %% 20-4
# 多重比較: Tukey HSD と Bonferroni（全 a(a-1)/2 対）
n_pairs = a_levels * (a_levels - 1) // 2
tukey = pairwise_tukeyhsd(y_all, df["タイプ1"].astype(str), alpha=0.05)
tk = pd.DataFrame(tukey.summary().data[1:], columns=tukey.summary().data[0])

# Bonferroni: 共通の σ̂² を使う2群の t 検定を n_pairs 倍で補正
rows = []
levels = list(mean_i.index)
for i in range(a_levels):
    for j in range(i + 1, a_levels):
        gi, gj = levels[i], levels[j]
        diff = mean_i[gj] - mean_i[gi]
        se = np.sqrt(sigma2_hat * (1 / n_i[gi] + 1 / n_i[gj]))
        t_ij = diff / se
        p_raw = 2 * stats.t.sf(abs(t_ij), df_E)
        q_ij = abs(diff) / np.sqrt(sigma2_hat / 2 * (1 / n_i[gi] + 1 / n_i[gj]))  # スチューデント化範囲
        rows.append({"群1": gi, "群2": gj, "差": diff, "t": t_ij, "p(無補正)": p_raw,
                     "p(Bonferroni)": min(1.0, p_raw * n_pairs),
                     "p(Tukey手計算)": stats.studentized_range.sf(q_ij, a_levels, df_E)})
pairs = pd.DataFrame(rows)

print(f"比較する対の数: {n_pairs}")
print(f"5%で有意な対の数  無補正: {(pairs['p(無補正)'] < 0.05).sum()}"
      f"  Bonferroni: {(pairs['p(Bonferroni)'] < 0.05).sum()}"
      f"  Tukey HSD: {tk['reject'].sum()}（statsmodels） / {(pairs['p(Tukey手計算)'] < 0.05).sum()}（手計算）")
print(f"Bonferroni の各検定の有意水準: 0.05 / {n_pairs} = {0.05 / n_pairs:.5f}")
print(f"Tukey の棄却点 q_0.05({a_levels}, {df_E}) = {stats.studentized_range.ppf(0.95, a_levels, df_E):.3f}")
print("\nTukey HSD で有意（5%）な対")
tk[tk["reject"]].sort_values("meandiff", key=abs, ascending=False)

# %% 20-5
# 二元配置分散分析: タイプ1（件数の多い6水準）× 成長（主な3水準）
tw_types = ["みず", "ノーマル", "くさ", "むし", "エスパー", "ほのお"]
tw_growth = ["100万", "106万", "125万"]
tw = df[df["タイプ1"].isin(tw_types) & df["成長"].isin(tw_growth)].copy()
tw["タイプ1"] = tw["タイプ1"].cat.remove_unused_categories()
tw["成長"] = tw["成長"].cat.remove_unused_categories()
print(f"対象: {len(tw)} 行（6 × 3 = 18 セル）")
print("セルの件数（不釣り合い）")
print(pd.crosstab(tw["タイプ1"], tw["成長"]).to_string())

tw_full = smf.ols("合計種族値 ~ C(タイプ1) * C(成長)", data=tw).fit()
tw_rev = smf.ols("合計種族値 ~ C(成長) * C(タイプ1)", data=tw).fit()
tw_add = smf.ols("合計種族値 ~ C(タイプ1) + C(成長)", data=tw).fit()
print("\n交互作用あり・type I（タイプ1 → 成長 の順に投入）")
print(sm.stats.anova_lm(tw_full, typ=1).to_string(float_format=fmt4))
print("\n交互作用あり・type I（成長 → タイプ1 の順に投入）")
print(sm.stats.anova_lm(tw_rev, typ=1).to_string(float_format=fmt4))
print("\n交互作用あり・type II")
print(sm.stats.anova_lm(tw_full, typ=2).to_string(float_format=fmt4))
print("\n交互作用なし（主効果のみ）・type II")
print(sm.stats.anova_lm(tw_add, typ=2).to_string(float_format=fmt4))

# %% 20-5b
# 交互作用プロット: 線が平行なら交互作用なし
cell_mean = tw.groupby(["タイプ1", "成長"], observed=True)["合計種族値"].mean().unstack()
fig, ax = plt.subplots(figsize=(7.5, 4.5))
xs = np.arange(len(tw_types))
for k, gr in enumerate(tw_growth):
    ax.plot(xs, cell_mean.loc[tw_types, gr], marker="o", color=PALETTE[k], label=f"成長 {gr}")
ax.set_xticks(xs, tw_types)
ax.set(title="交互作用プロット（タイプ1 × 成長）", xlabel="タイプ1", ylabel="合計種族値のセル平均")
ax.legend(title="成長（経験値）")
fig.tight_layout()
plt.show()

# %% 20-6
# 乱塊法: 因子 = タイプ1、ブロック = 世代。
# 全世代にいるタイプに限り、(タイプ, 世代) のセル平均を1観測とする a × r の表を作る
cnt = pd.crosstab(df["タイプ1"], df["世代"])
rb_types = cnt.index[(cnt > 0).all(axis=1)].tolist()
rb = (df[df["タイプ1"].isin(rb_types)]
      .groupby(["タイプ1", "世代"], observed=True)["合計種族値"].mean().unstack())
a_rb, r_rb = rb.shape
print(f"因子 A（タイプ1）: {a_rb} 水準 {rb_types}")
print(f"ブロック R（世代）: {r_rb} 個、1セル1観測（セル平均）")

Y = rb.to_numpy()
m_all = Y.mean()
S_T_rb = ((Y - m_all) ** 2).sum()
S_A_rb = r_rb * ((Y.mean(axis=1) - m_all) ** 2).sum()
S_R_rb = a_rb * ((Y.mean(axis=0) - m_all) ** 2).sum()
S_E_rb = S_T_rb - S_A_rb - S_R_rb
dfs = [a_rb - 1, r_rb - 1, (a_rb - 1) * (r_rb - 1)]
ms = [S_A_rb / dfs[0], S_R_rb / dfs[1], S_E_rb / dfs[2]]
rb_table = pd.DataFrame({
    "平方和": [S_A_rb, S_R_rb, S_E_rb, S_T_rb],
    "自由度": dfs + [a_rb * r_rb - 1],
    "平均平方": ms + [np.nan],
    "F": [ms[0] / ms[2], ms[1] / ms[2], np.nan, np.nan],
    "p値": [stats.f.sf(ms[0] / ms[2], dfs[0], dfs[2]), stats.f.sf(ms[1] / ms[2], dfs[1], dfs[2]), np.nan, np.nan],
}, index=["因子 A（タイプ1）", "ブロック R（世代）", "誤差 E", "総 T"])
print("\n乱塊法の分散分析表（手計算）")
print(rb_table.to_string(float_format=fmt4))

# statsmodels と照合（加法モデル: 交互作用項なし）
rb_long = rb.stack().rename("セル平均").reset_index()
rb_long["タイプ1"] = rb_long["タイプ1"].astype(str)  # 未使用のカテゴリ水準を残さない
rb_long["世代"] = rb_long["世代"].astype(str)
print("\nstatsmodels（セル平均 ~ タイプ1 + 世代）")
print(sm.stats.anova_lm(smf.ols("セル平均 ~ C(タイプ1) + C(世代)", data=rb_long).fit(), typ=1).to_string(float_format=fmt4))

# ブロックを無視した一元配置（完全無作為化法として解析）との比較
S_E_crd = S_R_rb + S_E_rb
df_E_crd = dfs[1] + dfs[2]
F_crd = ms[0] / (S_E_crd / df_E_crd)
print(f"\nブロックを無視した一元配置: F = {F_crd:.3f}（F({dfs[0]}, {df_E_crd})）, p = {stats.f.sf(F_crd, dfs[0], df_E_crd):.4f}")
print(f"誤差の平均平方  乱塊法: {ms[2]:.1f}  ブロック無視: {S_E_crd / df_E_crd:.1f}")

# %% 20-7
# 直交表 L8(2^7): 基本列 a, b, c の組み合わせで7列を作る（成分表示）
# 行 r = 0..7 の2進表示 (a, b, c)。列 j = 1..7 の2進表示のビットが立つ基本列の和を mod 2 で求める
basis = np.array([[(r >> 2) & 1, (r >> 1) & 1, r & 1] for r in range(8)])  # 列: a, b, c
comp_names = {1: "a", 2: "b", 3: "ab", 4: "c", 5: "ac", 6: "bc", 7: "abc"}
L8 = np.zeros((8, 7), dtype=int)
for j in range(1, 8):
    bits = np.array([j & 1, (j >> 1) & 1, (j >> 2) & 1])  # a, b, c を使うか
    L8[:, j - 1] = (basis @ bits) % 2 + 1                 # 水準 1, 2
L8_df = pd.DataFrame(L8, index=[f"実験{r + 1}" for r in range(8)],
                     columns=[f"[{j}] {comp_names[j]}" for j in range(1, 8)])
print("L8(2^7) 直交表")
print(L8_df.to_string())

# 直交性: どの2列を取っても (1,1),(1,2),(2,1),(2,2) が2回ずつ現れる
ok = all(pd.crosstab(L8[:, i], L8[:, j]).to_numpy().min() == 2 and
         pd.crosstab(L8[:, i], L8[:, j]).to_numpy().max() == 2
         for i in range(7) for j in range(i + 1, 7))
print("\n全ての2列の組で各水準組み合わせが2回ずつ:", ok)

# 2列の交互作用が現れる列（成分の積。a² = b² = c² = 1 なので列番号の排他的論理和）
inter = pd.DataFrame([[(i ^ j) if i != j else 0 for j in range(1, 8)] for i in range(1, 8)],
                     index=range(1, 8), columns=range(1, 8))
print("\n列 i と列 j の交互作用が現れる列（0 は同じ列）")
print(inter.to_string())
print(f"\n例: [3]({comp_names[3]}) × [6]({comp_names[6]}) → [{3 ^ 6}]({comp_names[3 ^ 6]})")
