"""第01章 事象と確率."""
from poke import *

df = load_data()

# %% 01-0
# この章で使う事象と確率変数
N_ch1 = len(df)
ev_dragon = types_of(df, "ドラゴン")          # A: ドラゴンタイプを持つ
ev_strong = df["合計種族値"] >= 600            # B: 合計種族値が600以上
print(f"全体 N = {N_ch1}")
print(f"ドラゴンタイプを持つ（タイプ1かタイプ2）: {ev_dragon.sum()}")
print(f"合計種族値 >= 600: {ev_strong.sum()}")
print(f"複合タイプ: {df['複合タイプ'].sum()}")
print("\n努力値合計の度数")
print(df["努力値合計"].value_counts().sort_index().to_string())

# %% 01-1
# 条件付き確率 P(B|A) = P(A∩B) / P(A) と P(A|B) = P(A∩B) / P(B)
p_A = ev_dragon.mean()
p_B = ev_strong.mean()
p_AB = (ev_dragon & ev_strong).mean()
p_B_given_A = p_AB / p_A
p_A_given_B = p_AB / p_B
print(f"P(A) = P(ドラゴン)          = {p_A:.4f}")
print(f"P(B) = P(合計種族値>=600)   = {p_B:.4f}")
print(f"P(A∩B)                      = {p_AB:.4f}  （{(ev_dragon & ev_strong).sum()}匹）")
print(f"P(B|A) = P(600以上 | ドラゴン) = {p_B_given_A:.4f}")
print(f"P(A|B) = P(ドラゴン | 600以上) = {p_A_given_B:.4f}")
# 乗法定理 P(A∩B) = P(B|A)P(A) = P(A|B)P(B) の確認
print(f"\n乗法定理: P(B|A)P(A) = {p_B_given_A * p_A:.4f},  P(A|B)P(B) = {p_A_given_B * p_B:.4f}")

# %% 01-2
# ベイズの定理：事前確率 P(A) → 「合計種族値が600以上」と知った後の事後確率 P(A|B)
p_B_given_notA = (~ev_dragon & ev_strong).sum() / (~ev_dragon).sum()   # P(B|A^c)
evidence = p_B_given_A * p_A + p_B_given_notA * (1 - p_A)             # 全確率の公式で P(B)
posterior = p_B_given_A * p_A / evidence
print(f"事前確率 P(A)     = {p_A:.4f}")
print(f"尤度 P(B|A)       = {p_B_given_A:.4f}")
print(f"尤度 P(B|A^c)     = {p_B_given_notA:.4f}")
print(f"全確率 P(B)       = {evidence:.4f}（度数から直接: {p_B:.4f}）")
print(f"事後確率 P(A|B)   = {posterior:.4f}（度数から直接: {p_A_given_B:.4f}）")
assert np.isclose(posterior, p_A_given_B)
print(f"事後/事前 = {posterior / p_A:.2f} 倍")

# %% 01-3
# 包除原理 P(A∪B) = P(A) + P(B) - P(A∩B)
p_union_formula = p_A + p_B - p_AB
p_union_direct = (ev_dragon | ev_strong).mean()
print(f"P(A)+P(B)-P(A∩B) = {p_union_formula:.4f}")
print(f"度数から直接     = {p_union_direct:.4f}")
print(f"単純な和 P(A)+P(B) = {p_A + p_B:.4f}（A∩Bを二重に数えている）")
# 3事象の包除原理：C = 素早 >= 100 を加える
ev_fast = df["素早"] >= 100
sets_ch1 = {"A": ev_dragon, "B": ev_strong, "C": ev_fast}
p3 = (sum(s.mean() for s in sets_ch1.values())
      - (ev_dragon & ev_strong).mean() - (ev_dragon & ev_fast).mean() - (ev_strong & ev_fast).mean()
      + (ev_dragon & ev_strong & ev_fast).mean())
print(f"\n3事象（C: 素早>=100）: 包除原理 {p3:.4f}, 直接 {(ev_dragon | ev_strong | ev_fast).mean():.4f}")

# %% 01-4
# 事象の独立性：D = 複合タイプ と E_t = 「タイプ1が t」 について P(D∩E_t) と P(D)P(E_t) を比べる
p_dual = df["複合タイプ"].mean()
indep_rows = []
for t in df["タイプ1"].cat.categories:
    e_t = df["タイプ1"] == t
    indep_rows.append({
        "タイプ1": t, "件数": e_t.sum(),
        "P(E)": e_t.mean(),
        "P(D∩E)": (e_t & df["複合タイプ"]).mean(),
        "P(D)P(E)": p_dual * e_t.mean(),
        "P(D|E)": df.loc[e_t, "複合タイプ"].mean(),
    })
indep_tab = pd.DataFrame(indep_rows).set_index("タイプ1").sort_values("P(D|E)")
indep_tab["比 P(D∩E)/P(D)P(E)"] = indep_tab["P(D∩E)"] / indep_tab["P(D)P(E)"]
print(f"P(D) = P(複合タイプ) = {p_dual:.4f}")
print("独立なら P(D|E) = P(D)、比 = 1")

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.barh(indep_tab.index.astype(str), indep_tab["P(D|E)"], color=PALETTE[0], label="P(複合タイプ | タイプ1)")
ax.axvline(p_dual, color=PALETTE[1], lw=1.5, label=f"P(複合タイプ) = {p_dual:.2f}")
ax.set(title="タイプ1ごとの複合タイプの割合", xlabel="確率", ylabel="タイプ1", xlim=(0, 1))
ax.legend(loc="lower right")
fig.tight_layout()
plt.show()
indep_tab.round(3)

# %% 01-5
# 条件付き独立：A' = 攻撃>=100, B' = 特攻>=100 は全体では独立でないが、
# 合計種族値の層 C で条件づけると P(A'∩B'|C) ≈ P(A'|C)P(B'|C) となるか
ev_atk = df["攻撃"] >= 100
ev_spa = df["特攻"] >= 100
layer_ch1 = pd.cut(df["合計種族値"], [0, 400, 500, 600, 800],
                   labels=["～400", "401～500", "501～600", "601～"])
ci_rows = [{"層": "全体", "件数": N_ch1, "P(A')": ev_atk.mean(), "P(B')": ev_spa.mean(),
            "P(A'∩B')": (ev_atk & ev_spa).mean(), "P(A')P(B')": ev_atk.mean() * ev_spa.mean()}]
for lv in layer_ch1.cat.categories:
    m = layer_ch1 == lv
    a, b = ev_atk[m], ev_spa[m]
    ci_rows.append({"層": f"合計種族値 {lv}", "件数": m.sum(), "P(A')": a.mean(), "P(B')": b.mean(),
                    "P(A'∩B')": (a & b).mean(), "P(A')P(B')": a.mean() * b.mean()})
# 2層（500以下 / 501以上）
for name, m in [("合計種族値 <=500", df["合計種族値"] <= 500), ("合計種族値 >500", df["合計種族値"] > 500)]:
    a, b = ev_atk[m], ev_spa[m]
    ci_rows.append({"層": name, "件数": m.sum(), "P(A')": a.mean(), "P(B')": b.mean(),
                    "P(A'∩B')": (a & b).mean(), "P(A')P(B')": a.mean() * b.mean()})
ci_tab = pd.DataFrame(ci_rows).set_index("層")
ci_tab["差 P(A'∩B')-P(A')P(B')"] = ci_tab["P(A'∩B')"] - ci_tab["P(A')P(B')"]
ci_tab.round(3)

# %% 01-6
# 離散確率変数 X = 努力値合計（1匹を等確率で選んだときの値）の期待値・分散
pmf_ev = df["努力値合計"].value_counts(normalize=True).sort_index()
x_ev = pmf_ev.index.to_numpy()
p_ev = pmf_ev.to_numpy()
EX = np.sum(x_ev * p_ev)
EX2 = np.sum(x_ev**2 * p_ev)
VX_def = np.sum((x_ev - EX) ** 2 * p_ev)     # 定義 E[(X-μ)^2]
VX_short = EX2 - EX**2                      # 公式 E[X^2] - (E[X])^2
print("確率関数 p(x):", dict(zip(x_ev, p_ev.round(4))))
print(f"E[X] = Σ x p(x) = {EX:.4f}（pandas mean: {df['努力値合計'].mean():.4f}）")
print(f"V[X] 定義式 = {VX_def:.4f},  E[X^2]-E[X]^2 = {VX_short:.4f}（pandas var(ddof=0): {df['努力値合計'].var(ddof=0):.4f}）")
# 線形変換 Y = aX + b： E[Y] = aE[X]+b, V[Y] = a^2 V[X]
a_lin, b_lin = 0.25, 0  # 例：Lv100では努力値4で能力値が1上がるので、Y = X/4 は能力値換算の目安
y_ev = a_lin * x_ev + b_lin
print(f"Y = {a_lin}X + {b_lin}: E[Y] = {np.sum(y_ev * p_ev):.4f}（aE[X]+b = {a_lin * EX + b_lin:.4f}）, "
      f"V[Y] = {np.sum((y_ev - np.sum(y_ev * p_ev))**2 * p_ev):.4f}（a^2 V[X] = {a_lin**2 * VX_def:.4f}）")

fig, ax = plt.subplots(figsize=(6, 3.8))
ax.bar(x_ev, p_ev, width=0.6, color=PALETTE[0])
ax.axvline(EX, color=PALETTE[1], lw=1.5, label=f"E[X] = {EX:.2f}")
ax.set(title="努力値合計の確率関数", xlabel="努力値合計（ポイント）", ylabel="確率 p(x)", xticks=x_ev)
ax.legend()
fig.tight_layout()
plt.show()
