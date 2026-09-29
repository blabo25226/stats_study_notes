"""第13章 ノンパラメトリック法."""
from poke import *

df = load_data()

# %% 13-0
# 使う群はタイプ1で作る（各ポケモンがちょうど1群に入る）
groups13 = {t: df.loc[df["タイプ1"] == t, "合計種族値"].to_numpy(dtype=float)
            for t in ["ほのお", "みず", "くさ", "むし", "ドラゴン"]}
print(pd.DataFrame({t: {"n": len(x), "中央値": np.median(x), "平均": x.mean()} for t, x in groups13.items()}).T)
d13 = (df["攻撃"] - df["特攻"]).to_numpy(dtype=float)
print(f"\n攻撃 − 特攻: 正 {np.sum(d13 > 0)}, 負 {np.sum(d13 < 0)}, 0 {np.sum(d13 == 0)}")
print(f"高さの同じ値の重複 {df['高さ'].duplicated().sum()} 行, 重さの重複 {df['重さ'].duplicated().sum()} 行（タイが多い）")

# %% 13-1
# 符号検定: 攻撃 − 特攻 の中央値は 0 か（0 の行は除く）
d_nz = d13[d13 != 0]
n_sign = len(d_nz)
t_plus = int(np.sum(d_nz > 0))
p_sign_exact = stats.binomtest(t_plus, n_sign, 0.5).pvalue
z_sign = (t_plus - n_sign / 2) / np.sqrt(n_sign / 4)       # Bin(n, 1/2) ≈ N(n/2, n/4)
p_sign_z = 2 * stats.norm.sf(abs(z_sign))
print(f"0 を除いた n = {n_sign}, 正の個数 T = {t_plus}（期待値 {n_sign / 2}）")
print(f"正確な p値（二項分布）= {p_sign_exact:.3g}")
print(f"正規近似: z = {z_sign:.4f}, p値 = {p_sign_z:.3g}")

# %% 13-2
# ウィルコクソンの符号付き順位検定: 攻撃 − 特攻 の分布は 0 について対称か
abs_rank = stats.rankdata(np.abs(d_nz))                   # 同順位は平均順位
T_plus = abs_rank[d_nz > 0].sum()
T_minus = abs_rank[d_nz < 0].sum()
E_T = n_sign * (n_sign + 1) / 4
_, tie_cnt = np.unique(np.abs(d_nz), return_counts=True)
V_T = n_sign * (n_sign + 1) * (2 * n_sign + 1) / 24 - (tie_cnt**3 - tie_cnt).sum() / 48   # タイの補正
z_sr = (T_plus - E_T) / np.sqrt(V_T)
p_sr = 2 * stats.norm.sf(abs(z_sr))
lib_sr = stats.wilcoxon(d13, zero_method="wilcox", correction=False, method="approx")
print(f"T+ = {T_plus:.1f}, T− = {T_minus:.1f}, T+ + T− = n(n+1)/2 = {n_sign * (n_sign + 1) / 2:.0f}")
print(f"E[T+] = {E_T:.1f}, V[T+] = {V_T:.1f}（タイ補正なし {n_sign * (n_sign + 1) * (2 * n_sign + 1) / 24:.1f}）")
print(f"手計算: z = {z_sr:.4f}, p値 = {p_sr:.3g}")
print(f"scipy : 統計量 min(T+, T−) = {lib_sr.statistic:.1f}, p値 = {lib_sr.pvalue:.3g}")

# %% 13-3
# ウィルコクソンの順位和検定 / マン・ホイットニーの U 検定: ほのお vs みず の合計種族値
x_f, x_w = groups13["ほのお"], groups13["みず"]
m_f, n_w = len(x_f), len(x_w)
N_fw = m_f + n_w
r_all = stats.rankdata(np.concatenate([x_f, x_w]))
W_f = r_all[:m_f].sum()                                   # ほのおの順位和
U_f = W_f - m_f * (m_f + 1) / 2                           # U = W − m(m+1)/2（ほのお > みず となる組の数、同点は 1/2）
U_pairs = (x_f[:, None] > x_w[None, :]).sum() + 0.5 * (x_f[:, None] == x_w[None, :]).sum()
E_W = m_f * (N_fw + 1) / 2
_, tc = np.unique(np.concatenate([x_f, x_w]), return_counts=True)
V_W = m_f * n_w / 12 * ((N_fw + 1) - (tc**3 - tc).sum() / (N_fw * (N_fw - 1)))   # タイの補正つき
z_rs = (W_f - E_W) / np.sqrt(V_W)
p_rs = 2 * stats.norm.sf(abs(z_rs))
lib_mw = stats.mannwhitneyu(x_f, x_w, use_continuity=False, method="asymptotic")
print(f"W（ほのおの順位和）= {W_f:.1f}, U = W − m(m+1)/2 = {U_f:.1f}, 組を数えた U = {U_pairs:.1f}")
print(f"E[W] = {E_W:.1f}, V[W] = {V_W:.1f}（E[U] = mn/2 = {m_f * n_w / 2:.1f}）")
print(f"手計算: z = {z_rs:.4f}, p値 = {p_rs:.4f}")
print(f"scipy mannwhitneyu: U = {lib_mw.statistic:.1f}, p値 = {lib_mw.pvalue:.4f}")
print(f"参考 Welch の t 検定: p値 = {stats.ttest_ind(x_f, x_w, equal_var=False).pvalue:.4f}")

# %% 13-4
# 並べ替え検定: むし vs ドラゴン の合計種族値の平均の差
x_b, x_d = groups13["むし"], groups13["ドラゴン"]
pooled_bd = np.concatenate([x_b, x_d])
obs_diff = x_d.mean() - x_b.mean()
rng = get_rng()
B = 10000
perm_diff = np.empty(B)
for i in range(B):
    perm = rng.permutation(pooled_bd)                      # 群のラベルをランダムに付け替える
    perm_diff[i] = perm[len(x_b):].mean() - perm[:len(x_b)].mean()
p_perm = (np.sum(np.abs(perm_diff) >= abs(obs_diff)) + 1) / (B + 1)
lib_perm = stats.permutation_test((x_d, x_b), lambda a, b: a.mean() - b.mean(), n_resamples=B,
                                  random_state=SEED)
print(f"むし n={len(x_b)} 平均 {x_b.mean():.1f}, ドラゴン n={len(x_d)} 平均 {x_d.mean():.1f}, 差 {obs_diff:.1f}")
print(f"並べ替えで |差| ≥ 観測値 となった回数: {np.sum(np.abs(perm_diff) >= abs(obs_diff))} / {B}")
print(f"並べ替え検定の p値 = {p_perm:.2e}（scipy permutation_test {lib_perm.pvalue:.2e}）")
print(f"参考 Welch の t 検定 p値 = {stats.ttest_ind(x_d, x_b, equal_var=False).pvalue:.2e}, "
      f"マン・ホイットニー p値 = {stats.mannwhitneyu(x_d, x_b).pvalue:.2e}")

fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(perm_diff, bins=50, color=PALETTE[0], label="ラベルを並べ替えたときの差")
ax.axvline(obs_diff, color=PALETTE[1], linewidth=2, label=f"観測された差 {obs_diff:.1f}")
ax.set(title=f"並べ替え分布（{B}回）: 平均の差（ドラゴン − むし）", xlabel="合計種族値の平均の差", ylabel="回数")
ax.legend(loc="upper left", fontsize=9)
fig.tight_layout()
plt.show()

# %% 13-5
# クラスカル・ウォリス検定: くさ・ほのお・みず（タイプ1）の合計種族値
kw_types = ["くさ", "ほのお", "みず"]
kw_data = [groups13[t] for t in kw_types]
# タイプ2まで数えると重複所属が生じることの確認
for t1, t2 in [("くさ", "ほのお"), ("くさ", "みず"), ("ほのお", "みず")]:
    both = types_of(df, t1) & types_of(df, t2)
    print(f"{t1} と {t2} を両方もつ: {df.loc[both, '名前'].tolist()}")
print("→ 各群をタイプ1だけで作り、1匹が1群にだけ入るようにする\n")

x_kw = np.concatenate(kw_data)
N_kw = len(x_kw)
r_kw = stats.rankdata(x_kw)
bounds = np.cumsum([0] + [len(x) for x in kw_data])
R_i = np.array([r_kw[bounds[i]:bounds[i + 1]].sum() for i in range(len(kw_data))])
n_i = np.array([len(x) for x in kw_data])
H_raw = 12 / (N_kw * (N_kw + 1)) * np.sum(R_i**2 / n_i) - 3 * (N_kw + 1)
_, tk = np.unique(x_kw, return_counts=True)
H = H_raw / (1 - (tk**3 - tk).sum() / (N_kw**3 - N_kw))                  # タイの補正
lib_kw = stats.kruskal(*kw_data)
lib_anova = stats.f_oneway(*kw_data)
print("群ごとの平均順位:", dict(zip(kw_types, np.round(R_i / n_i, 1))))
print(f"H（補正前）= {H_raw:.4f}, H（タイ補正）= {H:.4f}, 自由度 {len(kw_data) - 1}, p値 = {stats.chi2.sf(H, len(kw_data) - 1):.4f}")
print(f"scipy kruskal: H = {lib_kw.statistic:.4f}, p値 = {lib_kw.pvalue:.4f}")
print(f"参考 一元配置分散分析: F = {lib_anova.statistic:.4f}, p値 = {lib_anova.pvalue:.4f}")

fig, ax = plt.subplots(figsize=(6.5, 4))
ax.boxplot(kw_data, widths=0.5, patch_artist=True,
           boxprops=dict(facecolor=PALETTE[0], alpha=0.35, edgecolor=PALETTE[0]),
           medianprops=dict(color=PALETTE[0], linewidth=2), whiskerprops=dict(color=INK["secondary"]),
           capprops=dict(color=INK["secondary"]), flierprops=dict(markeredgecolor=INK["muted"]))
ax.set_xticks(range(1, len(kw_types) + 1), [f"{t}（n={len(x)}）" for t, x in zip(kw_types, kw_data)])
ax.set(title="タイプ1別の合計種族値", xlabel="タイプ1", ylabel="合計種族値")
fig.tight_layout()
plt.show()

# %% 13-6
# 順位相関係数: 高さと重さ
h, w = df["高さ"].to_numpy(float), df["重さ"].to_numpy(float)
n_hw = len(h)
rh, rw = stats.rankdata(h), stats.rankdata(w)
r_pearson = np.corrcoef(h, w)[0, 1]
r_pearson_log = np.corrcoef(np.log(h), np.log(w))[0, 1]
rs_rank = np.corrcoef(rh, rw)[0, 1]                           # 順位のピアソン相関 = スピアマン
rs_formula = 1 - 6 * np.sum((rh - rw) ** 2) / (n_hw * (n_hw**2 - 1))   # タイがないときの公式
# ケンドール: 全 n(n-1)/2 組の符号の一致・不一致を数える
iu = np.triu_indices(n_hw, k=1)
sh = np.sign(h[:, None] - h[None, :])[iu]
sw = np.sign(w[:, None] - w[None, :])[iu]
P_c, N_d = np.sum(sh * sw > 0), np.sum(sh * sw < 0)
n_pair = n_hw * (n_hw - 1) / 2
tau_a = (P_c - N_d) / n_pair
tau_b = (P_c - N_d) / np.sqrt(float(np.sum(sh != 0)) * float(np.sum(sw != 0)))   # タイの補正（int32 の桁あふれを避ける）
lib_sp = stats.spearmanr(h, w)
lib_kt = stats.kendalltau(h, w)
print(f"ピアソン（そのまま）: {r_pearson:.4f}  ピアソン（両対数）: {r_pearson_log:.4f}")
print(f"スピアマン: 順位の相関 {rs_rank:.4f} / 1−6Σd²/(n(n²−1)) {rs_formula:.4f} / scipy {lib_sp.statistic:.4f}")
print(f"ケンドール: 一致 P = {P_c}, 不一致 N = {N_d}, 組数 {n_pair:.0f}")
print(f"  τ_a = {tau_a:.4f}, τ_b = {tau_b:.4f}, scipy（τ_b）= {lib_kt.statistic:.4f}, p値 = {lib_kt.pvalue:.2e}")
# 外れ値の影響: 重さ上位5匹を除いたとき
top5 = np.argsort(w)[-5:]
keep = np.setdiff1d(np.arange(n_hw), top5)
print(f"重さ上位5匹 {df['名前'].iloc[top5].tolist()} を除くと: "
      f"ピアソン {np.corrcoef(h[keep], w[keep])[0, 1]:.4f}, スピアマン {stats.spearmanr(h[keep], w[keep]).statistic:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].scatter(h, w, s=8, color=PALETTE[0], alpha=0.6)
axes[0].set(title=f"そのまま（ピアソン {r_pearson:.2f}）", xlabel="高さ (m)", ylabel="重さ (kg)")
axes[1].scatter(rh, rw, s=8, color=PALETTE[0], alpha=0.6)
axes[1].set(title=f"順位（スピアマン {lib_sp.statistic:.2f}）", xlabel="高さの順位", ylabel="重さの順位")
fig.tight_layout()
plt.show()

# %% 13-7
# t 検定との比較: 同じデータへの適用と、小標本での検出力のシミュレーション
compare13 = pd.DataFrame({
    "パラメトリック": [stats.ttest_rel(df["攻撃"], df["特攻"]).pvalue,
                  stats.ttest_ind(x_f, x_w, equal_var=False).pvalue,
                  stats.f_oneway(*kw_data).pvalue],
    "ノンパラメトリック": [lib_sr.pvalue, lib_mw.pvalue, lib_kw.pvalue],
}, index=["攻撃 vs 特攻（対応あり t / 符号付き順位）", "ほのお vs みず（Welch t / マン・ホイットニー）",
          "くさ・ほのお・みず（分散分析 / クラスカル・ウォリス）"])
print(compare13.to_string(float_format=lambda v: f"{v:.3g}"))

# 検出力: むし と ドラゴン（タイプ1）から各 n=8 を復元抽出, 両側5%（合計種族値 と 右に歪んだ重さ）
rng = get_rng()
reps13, n_sim = 2000, 8
rows_pw13 = []
for col in ["合計種族値", "重さ"]:
    pop_b = df.loc[df["タイプ1"] == "むし", col].to_numpy(float)
    pop_d = df.loc[df["タイプ1"] == "ドラゴン", col].to_numpy(float)
    sb = rng.choice(pop_b, size=(reps13, n_sim))
    sd = rng.choice(pop_d, size=(reps13, n_sim))
    rows_pw13.append({"変数": col, "むしの歪度": stats.skew(pop_b), "ドラゴンの歪度": stats.skew(pop_d),
                      "Welch t の検出力": np.mean(stats.ttest_ind(sd, sb, axis=1, equal_var=False).pvalue < 0.05),
                      "マン・ホイットニーの検出力": np.mean(stats.mannwhitneyu(sd, sb, axis=1).pvalue < 0.05)})
pd.DataFrame(rows_pw13).round(3)
