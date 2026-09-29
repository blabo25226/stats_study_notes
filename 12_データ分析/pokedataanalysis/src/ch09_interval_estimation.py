"""第09章 区間推定."""
from poke import *

df = load_data()

# %% 09-0
# 使う列とタイプ別の件数（タイプ1で分類。各ポケモンはちょうど1群に入る）
print("合計種族値の要約（全920行）")
print(df["合計種族値"].describe().round(1).to_string())
print(f"歪度 {df['合計種族値'].skew():.2f}  尖度(-3) {df['合計種族値'].kurt():.2f}")
print("\nタイプ1別の件数")
print(df["タイプ1"].value_counts().to_string())
print("\nいわタイプを含む（タイプ1かタイプ2）:", types_of(df, "いわ").sum(), "匹")
print("努力値合計の度数:", df["努力値合計"].value_counts().sort_index().to_dict())

# %% 09-1
# 母平均の信頼区間（t分布）: タイプ1別の合計種族値
def t_interval(x, level=0.95):
    """定義式 xbar ± t_{α/2}(n-1) s/√n による母平均の信頼区間."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    xbar, s = x.mean(), x.std(ddof=1)
    tq = stats.t.ppf(1 - (1 - level) / 2, n - 1)   # 上側 α/2 点
    return xbar - tq * s / np.sqrt(n), xbar + tq * s / np.sqrt(n)


rows_ci = []
for t, g in df.groupby("タイプ1", observed=True)["合計種族値"]:
    lo, hi = t_interval(g)
    rows_ci.append({"タイプ1": t, "n": len(g), "平均": g.mean(), "下限": lo, "上限": hi})
ci_mean = pd.DataFrame(rows_ci).sort_values("平均").reset_index(drop=True)

# 手計算と scipy の照合（みず）
water_total = df.loc[df["タイプ1"] == "みず", "合計種族値"]
own = t_interval(water_total)
lib = stats.t.interval(0.95, len(water_total) - 1, loc=water_total.mean(), scale=stats.sem(water_total))
print(f"みず: 手計算 ({own[0]:.2f}, {own[1]:.2f})  scipy ({lib[0]:.2f}, {lib[1]:.2f})")

fig, ax = plt.subplots(figsize=(7, 6))
ypos = np.arange(len(ci_mean))
ax.errorbar(ci_mean["平均"], ypos,
            xerr=[ci_mean["平均"] - ci_mean["下限"], ci_mean["上限"] - ci_mean["平均"]],
            fmt="o", color=PALETTE[0], ecolor=PALETTE[0], capsize=3)
ax.axvline(df["合計種族値"].mean(), color=INK["muted"], linestyle="--", linewidth=1, label="全920行の平均")
ax.set_yticks(ypos, [f"{t}（n={n}）" for t, n in zip(ci_mean["タイプ1"], ci_mean["n"])])
ax.set(title="タイプ1別 合計種族値の母平均の95%信頼区間", xlabel="合計種族値")
ax.legend(loc="lower right")
fig.tight_layout()
plt.show()
ci_mean.round(1)

# %% 09-2
# 母分散の信頼区間（χ²分布）: みずタイプ（タイプ1）の合計種族値
n_w = len(water_total)
s2_w = water_total.var(ddof=1)
chi_hi = stats.chi2.ppf(0.975, n_w - 1)   # 上側2.5%点
chi_lo = stats.chi2.ppf(0.025, n_w - 1)   # 上側97.5%点
var_ci = ((n_w - 1) * s2_w / chi_hi, (n_w - 1) * s2_w / chi_lo)
print(f"n = {n_w}, 不偏分散 = {s2_w:.1f}（標準偏差 {np.sqrt(s2_w):.1f}）")
print(f"χ²(0.025) = {chi_hi:.2f}, χ²(0.975) = {chi_lo:.2f}（自由度 {n_w - 1}）")
print(f"σ² の95%信頼区間: ({var_ci[0]:.1f}, {var_ci[1]:.1f})")
print(f"σ  の95%信頼区間: ({np.sqrt(var_ci[0]):.1f}, {np.sqrt(var_ci[1]):.1f})")

# %% 09-3
# 母比率の信頼区間: いわタイプを含む割合（Wald / Wilson / Clopper-Pearson）
def prop_intervals(x, n, level=0.95):
    """3種類の母比率の信頼区間を定義式から計算する."""
    z = stats.norm.ppf(1 - (1 - level) / 2)
    p = x / n
    # Wald: p̂ ± z √(p̂(1-p̂)/n)
    half = z * np.sqrt(p * (1 - p) / n)
    wald = (p - half, p + half)
    # Wilson: |p̂ - p| ≤ z √(p(1-p)/n) を p について解いた区間
    center = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    half_w = z / (1 + z**2 / n) * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    wilson = (center - half_w, center + half_w)
    # Clopper-Pearson: 二項分布の裾確率をベータ分布の分位点で表したもの
    a = 1 - level
    cp_lo = stats.beta.ppf(a / 2, x, n - x + 1) if x > 0 else 0.0
    cp_hi = stats.beta.ppf(1 - a / 2, x + 1, n - x) if x < n else 1.0
    return {"Wald": wald, "Wilson": wilson, "Clopper-Pearson": (cp_lo, cp_hi)}


rock = types_of(df, "いわ")
x_rock, n_all = int(rock.sum()), len(df)
print(f"全920行: いわを含む {x_rock} 匹, 標本比率 {x_rock / n_all:.4f}")
res_all = pd.DataFrame(prop_intervals(x_rock, n_all), index=["下限", "上限"]).T
res_all["幅"] = res_all["上限"] - res_all["下限"]

# 小標本（無作為に30匹を抽出）での比較
rng = get_rng()
idx30 = rng.choice(len(df), size=30, replace=False)
x30 = int(rock.iloc[idx30].sum())
print(f"無作為抽出30匹: いわを含む {x30} 匹")
res_30 = pd.DataFrame(prop_intervals(x30, 30), index=["下限", "上限"]).T
res_30["幅"] = res_30["上限"] - res_30["下限"]

# scipy（binomtest）の Wilson / Clopper-Pearson と照合
bt = stats.binomtest(x30, 30)
print("scipy Wilson:", np.round(bt.proportion_ci(method="wilson"), 4),
      " Clopper-Pearson:", np.round(bt.proportion_ci(method="exact"), 4))
pd.concat({"全920行": res_all, "30匹の標本": res_30}).round(4)

# %% 09-4
# 母平均の差・母比率の差の信頼区間
fire_total = df.loc[df["タイプ1"] == "ほのお", "合計種族値"]
n1, n2 = len(fire_total), len(water_total)
m1, m2 = fire_total.mean(), water_total.mean()
v1, v2 = fire_total.var(ddof=1), water_total.var(ddof=1)

# (a) 等分散を仮定: プールした分散と自由度 n1+n2-2
sp2 = ((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2)
se_pool = np.sqrt(sp2 * (1 / n1 + 1 / n2))
t_pool = stats.t.ppf(0.975, n1 + n2 - 2)
# (b) Welch: 自由度をサタスウェイトの近似で求める
se_w = np.sqrt(v1 / n1 + v2 / n2)
df_w = se_w**4 / ((v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1))
t_w = stats.t.ppf(0.975, df_w)
diff = m1 - m2
print(f"ほのお n={n1} 平均 {m1:.1f} / みず n={n2} 平均 {m2:.1f} / 差 {diff:.1f}")
print(f"等分散: 自由度 {n1 + n2 - 2}, 95%CI ({diff - t_pool * se_pool:.1f}, {diff + t_pool * se_pool:.1f})")
print(f"Welch : 自由度 {df_w:.1f}, 95%CI ({diff - t_w * se_w:.1f}, {diff + t_w * se_w:.1f})")

# 母比率の差: 複合タイプの割合（第1世代 と 第7世代）
g1 = df.loc[df["世代"] == 1, "複合タイプ"]
g7 = df.loc[df["世代"] == 7, "複合タイプ"]
p1_, p7_ = g1.mean(), g7.mean()
se_p = np.sqrt(p1_ * (1 - p1_) / len(g1) + p7_ * (1 - p7_) / len(g7))
z975 = stats.norm.ppf(0.975)
print(f"\n複合タイプの割合: 第1世代 {p1_:.3f}（n={len(g1)}）, 第7世代 {p7_:.3f}（n={len(g7)}）")
print(f"差（第7−第1） {p7_ - p1_:.3f}, 95%CI ({p7_ - p1_ - z975 * se_p:.3f}, {p7_ - p1_ + z975 * se_p:.3f})")

# %% 09-5
# 分散の比の信頼区間（F分布）: σ²_ほのお / σ²_みず
ratio = v1 / v2
f_up = stats.f.ppf(0.975, n1 - 1, n2 - 1)    # F(n1-1, n2-1) の上側2.5%点
f_low = stats.f.ppf(0.025, n1 - 1, n2 - 1)   # F(n1-1, n2-1) の上側97.5%点
ci_ratio = (ratio / f_up, ratio / f_low)
# 別の書き方: 比 × F(n2-1, n1-1) の分位点（F(a,b) の上側 α 点 = 1 / F(b,a) の上側 1-α 点）
ci_ratio2 = (ratio * stats.f.ppf(0.025, n2 - 1, n1 - 1), ratio * stats.f.ppf(0.975, n2 - 1, n1 - 1))
print(f"不偏分散 ほのお {v1:.1f}, みず {v2:.1f}, 比 {ratio:.3f}")
print(f"95%CI: ({ci_ratio[0]:.3f}, {ci_ratio[1]:.3f})  別表現: ({ci_ratio2[0]:.3f}, {ci_ratio2[1]:.3f})")

# %% 09-6
# 多項分布の比率の差: 努力値合計が2の割合 − 1の割合（同じ920匹の中の2カテゴリ）
counts_ev = df["努力値合計"].value_counts().sort_index()
n_ev = counts_ev.sum()
q1, q2 = counts_ev[1] / n_ev, counts_ev[2] / n_ev
d_ev = q2 - q1
# 同一多項分布では Cov(p̂1, p̂2) = -p1 p2 / n なので V(p̂2 - p̂1) = {p1(1-p1) + p2(1-p2) + 2 p1 p2} / n
se_multi = np.sqrt((q1 * (1 - q1) + q2 * (1 - q2) + 2 * q1 * q2) / n_ev)
se_wrong = np.sqrt((q1 * (1 - q1) + q2 * (1 - q2)) / n_ev)   # 共分散を無視した（誤った）式
print(f"n = {n_ev}, p̂1 = {q1:.3f}, p̂2 = {q2:.3f}, 差 = {d_ev:.3f}")
print(f"共分散を考慮: SE {se_multi:.4f}, 95%CI ({d_ev - z975 * se_multi:.3f}, {d_ev + z975 * se_multi:.3f})")
print(f"共分散を無視: SE {se_wrong:.4f}, 95%CI ({d_ev - z975 * se_wrong:.3f}, {d_ev + z975 * se_wrong:.3f})")

# シミュレーションで V(p̂2 - p̂1) を確認（全920行を母集団とみなし n=920 の復元抽出）
rng = get_rng()
sim_ev = rng.multinomial(n_ev, (counts_ev / n_ev).values, size=5000)
sim_d = sim_ev[:, 1] / n_ev - sim_ev[:, 0] / n_ev
print(f"シミュレーションの SD {sim_d.std():.4f}")

# %% 09-7
# 信頼区間の意味: 全920行を母集団とみなし、n=20 の復元抽出を繰り返して被覆率を調べる
rng = get_rng()
pop_total = df["合計種族値"].to_numpy()
mu_true, var_true = pop_total.mean(), pop_total.var(ddof=0)
n_s, reps = 20, 5000
samp = rng.choice(pop_total, size=(reps, n_s), replace=True)
xbar_s = samp.mean(axis=1)
s_s = samp.std(axis=1, ddof=1)
tq20 = stats.t.ppf(0.975, n_s - 1)
lo_s, hi_s = xbar_s - tq20 * s_s / np.sqrt(n_s), xbar_s + tq20 * s_s / np.sqrt(n_s)
cover_mean = (lo_s <= mu_true) & (mu_true <= hi_s)
# 母分散の χ² 区間（母集団が正規分布でないと被覆率がずれる）
v_lo = (n_s - 1) * s_s**2 / stats.chi2.ppf(0.975, n_s - 1)
v_hi = (n_s - 1) * s_s**2 / stats.chi2.ppf(0.025, n_s - 1)
cover_var = (v_lo <= var_true) & (var_true <= v_hi)
# 母比率（いわを含む, 真値 69/920）の3種類の区間, n=30
p_true = rock.mean()
xs = rng.binomial(30, p_true, size=reps)
cover_prop = {}
for name in ["Wald", "Wilson", "Clopper-Pearson"]:
    ints = np.array([prop_intervals(x, 30)[name] for x in xs])
    cover_prop[name] = np.mean((ints[:, 0] <= p_true) & (p_true <= ints[:, 1]))
print(f"母平均 {mu_true:.1f}, 母分散 {var_true:.0f}, いわの母比率 {p_true:.4f}（{reps}回）")
print(f"母平均の t 区間（n=20）の被覆率: {cover_mean.mean():.3f}")
print(f"母分散の χ² 区間（n=20）の被覆率: {cover_var.mean():.3f}")
for k, v in cover_prop.items():
    print(f"母比率 {k} 区間（n=30）の被覆率: {v:.3f}")

# 最初の100回の区間を描く（真値を含まない区間を別の色に）
k_show = 100
fig, ax = plt.subplots(figsize=(8, 4.5))
for i in range(k_show):
    c = PALETTE[0] if cover_mean[i] else PALETTE[1]
    ax.plot([i, i], [lo_s[i], hi_s[i]], color=c, linewidth=1.2)
    ax.plot(i, xbar_s[i], "o", color=c, markersize=2.5)
ax.axhline(mu_true, color=INK["primary"], linewidth=1, label=f"母平均 {mu_true:.1f}")
ax.plot([], [], color=PALETTE[0], label="母平均を含む区間")
ax.plot([], [], color=PALETTE[1], label="母平均を含まない区間")
ax.set(title=f"n=20 の95%信頼区間を100回（含まない: {(~cover_mean[:k_show]).sum()}回）",
       xlabel="抽出の回", ylabel="合計種族値")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=9)
fig.tight_layout()
plt.show()
