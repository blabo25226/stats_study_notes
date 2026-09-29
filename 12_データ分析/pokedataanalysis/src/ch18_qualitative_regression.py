"""第18章 質的回帰."""
from poke import *

df = load_data()

# %% 18-0
import statsmodels.api as sm
import statsmodels.formula.api as smf

d18 = df.assign(
    性別不明=df["雄率"].isna().astype(int),
    はがね=types_of(df, "はがね").astype(int),
    合計100=df["合計種族値"] / 100,      # 合計種族値（100単位）
    孵化千=df["孵化"] / 1000,            # 孵化歩数（1000歩単位）
    努力値m1=df["努力値合計"] - 1,        # 努力値合計 − 1（0〜2 の計数）
)
print("性別不明:", d18["性別不明"].sum(), "/", len(d18), "  はがねタイプ（タイプ1か2）:", d18["はがね"].sum())
print("努力値合計−1 の分布:", d18["努力値m1"].value_counts().sort_index().to_dict())
d18.groupby("性別不明")[["合計種族値", "孵化", "log重さ", "防御"]].mean().round(2)

# %% 18-1
# 一般化線形モデル: 正規分布・恒等リンクの GLM は OLS と一致する
glm_gauss = smf.glm("経験値 ~ HP + 攻撃 + 防御 + 特攻 + 特防 + 素早", d18, family=sm.families.Gaussian()).fit()
ols18 = smf.ols("経験値 ~ HP + 攻撃 + 防御 + 特攻 + 特防 + 素早", d18).fit()
print("GLM(正規, 恒等) と OLS の係数の最大差:", np.abs(glm_gauss.params - ols18.params).max())
print(f"正規 GLM の逸脱度 = {glm_gauss.deviance:.1f} = OLS の残差平方和 {ols18.ssr:.1f}")

# 代表的な GLM（分布・正準リンク・分散関数）
pd.DataFrame({
    "応答の分布": ["正規", "二項（ベルヌーイ）", "ポアソン"],
    "正準リンク g(μ)": ["μ", "log(μ/(1-μ))", "log μ"],
    "分散関数 V(μ)": ["1（×σ²）", "μ(1-μ)", "μ"],
    "この章の例": ["16章の重回帰", "性別不明か・はがねタイプか", "努力値合計−1"],
}, index=["線形回帰", "ロジスティック回帰", "ポアソン回帰"])

# %% 18-2
# ロジスティック回帰: 性別不明 ~ 合計種族値 + 孵化歩数 + log重さ
# ニュートン・ラフソン法（= IRLS）を numpy で実装し、statsmodels と照合する
X18 = np.column_stack([np.ones(len(d18)), d18[["合計100", "孵化千", "log重さ"]].to_numpy(float)])
y18 = d18["性別不明"].to_numpy(float)
beta18 = np.zeros(X18.shape[1])
for it in range(50):
    pi18 = 1 / (1 + np.exp(-X18 @ beta18))
    grad = X18.T @ (y18 - pi18)                         # スコア関数
    info = X18.T @ (X18 * (pi18 * (1 - pi18))[:, None])  # フィッシャー情報行列
    step = np.linalg.solve(info, grad)
    beta18 = beta18 + step
    if np.abs(step).max() < 1e-10:
        break
se18 = np.sqrt(np.diag(np.linalg.inv(info)))
pi18 = 1 / (1 + np.exp(-X18 @ beta18))
ll18 = np.sum(y18 * np.log(pi18) + (1 - y18) * np.log(1 - pi18))

logit18 = smf.logit("性別不明 ~ 合計100 + 孵化千 + log重さ", d18).fit(disp=0)
print(f"ニュートン法の反復回数 {it + 1}, 係数の最大差 {np.abs(beta18 - logit18.params.to_numpy()).max():.2e}, "
      f"対数尤度 {ll18:.3f}（sm {logit18.llf:.3f}）")

# オッズ比 exp(beta) とその 95% 信頼区間（ワルド型: exp(beta ± 1.96 SE)）
z975 = stats.norm.ppf(0.975)
or_tab = pd.DataFrame({
    "係数": beta18, "標準誤差": se18, "z": beta18 / se18,
    "p値": 2 * stats.norm.sf(np.abs(beta18 / se18)),
    "オッズ比": np.exp(beta18),
    "95%CI下限": np.exp(beta18 - z975 * se18), "95%CI上限": np.exp(beta18 + z975 * se18),
}, index=logit18.params.index)

# 予測確率 0.5 で分類したときの分割表
pred18 = (pi18 >= 0.5).astype(int)
print("\n分割表（行: 実際, 列: 予測）")
print(pd.crosstab(y18.astype(int), pred18, rownames=["実際"], colnames=["予測"]).to_string())
print(f"正解率 {np.mean(pred18 == y18):.3f}（全部「性別あり」と予測した場合 {1 - y18.mean():.3f}）")
or_tab.round(4)

# %% 18-3
# プロビット回帰との比較
probit18 = smf.probit("性別不明 ~ 合計100 + 孵化千 + log重さ", d18).fit(disp=0)
cmp18 = pd.DataFrame({"ロジット係数": logit18.params, "プロビット係数": probit18.params,
                      "比（ロジット/プロビット）": logit18.params / probit18.params})
print(cmp18.round(4).to_string())
print(f"\n対数尤度: ロジット {logit18.llf:.2f}, プロビット {probit18.llf:.2f}")

# 平均での限界効果 dP/dx_j: ロジット π(1-π) beta_j, プロビット φ(x̄'beta) beta_j
xbar18 = X18.mean(axis=0)
p_l = 1 / (1 + np.exp(-xbar18 @ logit18.params.to_numpy()))
me_logit = p_l * (1 - p_l) * logit18.params.to_numpy()[1:]
me_probit = stats.norm.pdf(xbar18 @ probit18.params.to_numpy()) * probit18.params.to_numpy()[1:]
me_sm = probit18.get_margeff(at="mean").margeff
print(pd.DataFrame({"ロジット限界効果": me_logit, "プロビット限界効果": me_probit, "プロビット(sm)": me_sm},
                   index=["合計100", "孵化千", "log重さ"]).round(4).to_string())

# 1変数の例で確率曲線を比べる: はがねタイプか ~ 防御
lg_st = smf.logit("はがね ~ 防御", d18).fit(disp=0)
pb_st = smf.probit("はがね ~ 防御", d18).fit(disp=0)
print(f"\nはがね ~ 防御: ロジット 防御の係数 {lg_st.params['防御']:.4f}（オッズ比 {np.exp(lg_st.params['防御']):.4f}/1, "
      f"{np.exp(10 * lg_st.params['防御']):.3f}/10）, プロビット {pb_st.params['防御']:.4f}")

grid18 = pd.DataFrame({"防御": np.linspace(0, 240, 200)})
bins18 = pd.cut(d18["防御"], np.arange(0, 250, 20))
emp18 = d18.groupby(bins18, observed=True)["はがね"].agg(["mean", "size"])
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.scatter([b.mid for b in emp18.index], emp18["mean"], s=np.clip(emp18["size"], 8, 200),
           color=INK["muted"], alpha=0.6, label="防御20ごとの実際の割合（点の大きさ=匹数）")
ax.plot(grid18["防御"], lg_st.predict(grid18), color=PALETTE[0], label="ロジスティック回帰")
ax.plot(grid18["防御"], pb_st.predict(grid18), color=PALETTE[1], ls="--", label="プロビット回帰")
ax.set(title="はがねタイプである確率と防御", xlabel="防御（種族値）", ylabel="はがねタイプである確率")
ax.legend(loc="upper left")
plt.show()

# %% 18-4
# ポアソン回帰（人工的な設定）: 努力値合計−1（0〜2）~ 合計種族値
pois18 = smf.glm("努力値m1 ~ 合計100", d18, family=sm.families.Poisson()).fit()
print(pois18.summary().tables[1])
print(f"exp(係数) = {np.exp(pois18.params['合計100']):.3f}（合計種族値が100増えると平均が何倍になるか）")

# 過分散の確認: ピアソン χ² / 残差自由度（ポアソンなら1に近いはず）
mu18 = pois18.fittedvalues
pearson18 = ((d18["努力値m1"] - mu18) ** 2 / mu18).sum()
print(f"ピアソン χ² / 自由度 = {pearson18:.1f} / {pois18.df_resid:.0f} = {pearson18 / pois18.df_resid:.3f}")
print(f"標本平均 {d18['努力値m1'].mean():.3f}, 標本分散 {d18['努力値m1'].var():.3f}")

# 上限が2の計数なので、二項分布 Bin(2, π)・ロジットリンクの GLM とも比べる
binom18 = smf.glm("I(努力値m1 / 2) ~ 合計100", d18, family=sm.families.Binomial(),
                  var_weights=np.full(len(d18), 2.0)).fit()
k18 = d18["努力値m1"].to_numpy()
pi_b = binom18.fittedvalues.to_numpy()
ll_binom = np.sum(stats.binom.logpmf(k18, 2, pi_b))
ll_pois = np.sum(stats.poisson.logpmf(k18, mu18))
print(f"\n対数尤度（手計算）: ポアソン {ll_pois:.2f}（sm {pois18.llf:.2f}）, 二項(2) {ll_binom:.2f}")
print(f"AIC = -2 logL + 2×2: ポアソン {-2 * ll_pois + 4:.1f}, 二項(2) {-2 * ll_binom + 4:.1f}")

# 観測度数と期待度数
exp_pois = [stats.poisson.pmf(k, mu18).sum() for k in [0, 1, 2]] + [stats.poisson.sf(2, mu18).sum()]
exp_binom = [stats.binom.pmf(k, 2, pi_b).sum() for k in [0, 1, 2]] + [0.0]
pd.DataFrame({"観測": [*np.bincount(k18, minlength=3), 0], "ポアソン期待": exp_pois, "二項(2)期待": exp_binom},
             index=["0", "1", "2", "3以上"]).round(1)

# %% 18-5
# 逸脱度と尤度比検定（ロジスティック回帰: 性別不明）
# 0/1 データでは飽和モデルの対数尤度は 0 なので、逸脱度 D = -2 logL
glm18 = smf.glm("性別不明 ~ 合計100 + 孵化千 + log重さ", d18, family=sm.families.Binomial()).fit()
null18 = smf.glm("性別不明 ~ 1", d18, family=sm.families.Binomial()).fit()
p0 = y18.mean()
ll_null = len(y18) * (p0 * np.log(p0) + (1 - p0) * np.log(1 - p0))
print(f"逸脱度: モデル {-2 * ll18:.2f}（sm {glm18.deviance:.2f}）, 帰無モデル {-2 * ll_null:.2f}（sm {null18.deviance:.2f}）")

# 全体の検定 H0: 3つの係数がすべて 0
G18 = -2 * ll_null - (-2 * ll18)
print(f"尤度比統計量 G = {G18:.2f}, 自由度 3, p = {stats.chi2.sf(G18, 3):.3g}")

# 入れ子モデルの検定: log重さ を除いたモデルとの比較（自由度1）。ワルド検定とも比べる
red18 = smf.glm("性別不明 ~ 合計100 + 孵化千", d18, family=sm.families.Binomial()).fit()
G_w = red18.deviance - glm18.deviance
wald_w = (glm18.params["log重さ"] / glm18.bse["log重さ"]) ** 2
print(f"log重さ: 尤度比 G = {G_w:.2f}, p = {stats.chi2.sf(G_w, 1):.3g}; ワルド z^2 = {wald_w:.2f}, p = {stats.chi2.sf(wald_w, 1):.3g}（自由度1）")
print(f"マクファデンの疑似 R^2 = 1 - logL/logL0 = {1 - ll18 / ll_null:.3f}")
