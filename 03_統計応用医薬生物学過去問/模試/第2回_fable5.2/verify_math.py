"""第2回模試・統計応用（医薬生物学）の検算。

模範解答のTeXは読み込まず、問題文のデータ・モデルから独立に再計算して
解答の式・数値と照合する。結果は 検算結果.json に保存する。

Run: python verify_math.py
Requires: NumPy, SciPy, SymPy
"""
import json
import math
from pathlib import Path

import numpy as np
import sympy as sp
from scipy import optimize, stats

SEED = 20261112
rng = np.random.default_rng(SEED)
results = []


def check(name, got, expected, tol=1e-9, kind="abs"):
    got = float(got)
    expected = float(expected)
    err = abs(got - expected)
    if kind == "rel":
        err = err / max(abs(expected), 1e-300)
    ok = bool(err <= tol)
    results.append({"name": name, "got": got, "expected": expected, "tol": tol, "ok": ok})
    print(("PASS" if ok else "FAIL"), name, f"got={got:.10g} expected={expected:.10g}")
    return ok


def check_true(name, cond, detail=""):
    ok = bool(cond)
    results.append({"name": name, "ok": ok, "detail": detail})
    print(("PASS" if ok else "FAIL"), name, detail)
    return ok


# 付表5（指数関数・常用対数）の値。手計算の再現に使う。
LOG10 = {0.8: -0.0969, 0.9: -0.0458, 2: 0.3010, 3: 0.4771, 5: 0.6990}
LN = lambda x: 2.3026 * LOG10[x]
EXP_TABLE = {0.01: 1.0101, 0.02: 1.0202, 0.05: 1.0513, 0.06: 1.0618, 0.38: 1.4623, 0.39: 1.4770,
             0.88: 2.4109, 0.89: 2.4351, 0.90: 2.4596, 1.00: 2.7183}


def exp_table(x):
    """付表5の線形補間による e^x（0.01<=x<2）。"""
    if x >= 1.0:
        return EXP_TABLE[1.00] * exp_table(round(x - 1.0, 10))
    lo = math.floor(x * 100 + 1e-9) / 100
    hi = round(lo + 0.01, 2)
    lo = round(lo, 2)
    return EXP_TABLE[lo] + (x - lo) / 0.01 * (EXP_TABLE[hi] - EXP_TABLE[lo])


# ---------------------------------------------------------------- 問1
print("== 問1 カプラン・マイヤー推定量とグリーンウッドの公式")
times = np.array([2, 3, 4, 5, 6, 7, 9, 10, 12, 15], dtype=float)
event = np.array([1, 1, 0, 0, 0, 1, 1, 0, 1, 0])


def km_table(times, event):
    rows = []
    s, g = 1.0, 0.0
    for t in np.unique(times[event == 1]):
        n_j = int(np.sum(times >= t))
        d_j = int(np.sum((times == t) & (event == 1)))
        s *= 1 - d_j / n_j
        g += d_j / (n_j * (n_j - d_j)) if n_j > d_j else float("inf")
        rows.append((t, n_j, d_j, s, g))
    return rows


tab = km_table(times, event)
exp_rows = [(2, 10, 1, 0.90, 0.0111), (3, 9, 1, 0.80, 0.0250), (7, 5, 1, 0.64, 0.0750),
            (9, 4, 1, 0.48, 0.1583), (12, 2, 1, 0.24, 0.6583)]
for got, ex in zip(tab, exp_rows):
    check_true(f"Q1 表1 t={ex[0]} の n_j,d_j", got[1] == ex[1] and got[2] == ex[2], f"n={got[1]} d={got[2]}")
    check(f"Q1 表1 S({ex[0]})", got[3], ex[3], tol=1e-12)
    check(f"Q1 表1 G_j (t={ex[0]})", got[4], ex[4], tol=5e-5)
median = min(t for (t, _, _, s, _) in tab if s <= 0.5)
check("Q1[1] 中央値", median, 9)
se3 = 0.80 * math.sqrt(tab[1][4])
se9 = 0.48 * math.sqrt(tab[3][4])
check("Q1[3] SE(S(3))", se3, 0.1265, tol=5e-5)
check("Q1[3] SE(S(9))", se9, 0.1910, tol=5e-5)
check("Q1[3] S(3) 下限", 0.80 - 1.96 * se3, 0.552, tol=5e-4)
check("Q1[3] S(3) 上限", 0.80 + 1.96 * se3, 1.048, tol=5e-4)
check("Q1[3] S(9) 下限", 0.48 - 1.96 * se9, 0.106, tol=6e-4)
check("Q1[3] S(9) 上限", 0.48 + 1.96 * se9, 0.854, tol=6e-4)
check("Q1[4] 打ち切りなしの確認 t=3", se3 ** 2, 0.8 * 0.2 / 10, tol=1e-12)
for trial in range(5):  # 打ち切りのない任意のデータで恒等式を確認
    n = int(rng.integers(5, 40))
    tt = rng.integers(1, 12, size=n).astype(float)
    rows = km_table(tt, np.ones(n, dtype=int))
    for (t, n_j, d_j, s, g) in rows[:-1]:
        check(f"Q1[4] 恒等式 trial{trial} t={t}", s * s * g, s * (1 - s) / n, tol=1e-12)
# [2] デルタ法の式: 独立二項の積で分散をシミュレーション確認（大標本）
qs = np.array([0.05, 0.08, 0.1])
ns = np.array([4000, 3500, 3000])
d = rng.binomial(ns, qs, size=(200_000, 3))
s_hat = np.prod(1 - d / ns, axis=1)
check("Q1[2] グリーンウッド近似（独立二項, 大標本）", s_hat.var(),
      np.prod(1 - qs) ** 2 * np.sum(qs / (ns * (1 - qs))), tol=2e-2, kind="rel")
# [5] log(-log) 変換
ln08_table = LN(0.8)
check("Q1[5] log0.8（付表）", ln08_table, math.log(0.8), tol=2e-4)
sig_true = math.sqrt(tab[1][4]) / abs(math.log(0.8))
check("Q1[5] sigma_h", math.sqrt(0.0250) / 0.2231, sig_true, tol=5e-4)
lo_true = 0.8 ** math.exp(1.96 * sig_true)
hi_true = 0.8 ** math.exp(-1.96 * sig_true)
check("Q1[5] 下限（真値）", lo_true, 0.409, tol=6e-4)
check("Q1[5] 上限（真値）", hi_true, 0.946, tol=6e-4)
e1389 = exp_table(1.389)
check("Q1[5] e^{1.389}（付表）", e1389, 4.011, tol=1e-3)
check("Q1[5] 下限（付表）", 1 / exp_table(4.011 * 0.2231), lo_true, tol=1e-3)
check("Q1[5] 上限（付表）", 1 / exp_table(0.2231 / 4.011), hi_true, tol=1e-3)
# 変換区間が log(-log S) の区間の逆変換であること
th = math.log(-math.log(0.8))
check("Q1[5] 逆変換の整合（下限）", math.exp(-math.exp(th + 1.96 * sig_true)), lo_true, tol=1e-12)
check("Q1[5] 逆変換の整合（上限）", math.exp(-math.exp(th - 1.96 * sig_true)), hi_true, tol=1e-12)

# ---------------------------------------------------------------- 問2
print("== 問2 分割表・調整済み残差・対数線形モデル")
tbl = np.array([[50, 30, 20], [30, 30, 40]], dtype=float)
m = tbl.sum(axis=1)
cj = tbl.sum(axis=0)
N = tbl.sum()
e = np.outer(m, cj) / N
chi2, pval, dof, e_sp = stats.chi2_contingency(tbl, correction=False)
check("Q2[1] X^2", chi2, 11.67, tol=5e-3)
check("Q2[1] 自由度", dof, 2)
check_true("Q2[1] 期待度数", np.allclose(e_sp, [[40, 30, 30], [40, 30, 30]]))
check("Q2[1] 5%点", stats.chi2.ppf(0.95, 2), 5.99, tol=5e-3)
adj = (tbl - e) / np.sqrt(e * (1 - m[:, None] / N) * (1 - cj[None, :] / N))
for j, ex in enumerate([2.89, 0.0, -3.09]):
    check(f"Q2[3] r_1{j+1}", adj[0, j], ex, tol=5e-3)
    p1, p2, pp = tbl[0, j] / m[0], tbl[1, j] / m[1], cj[j] / N
    z = (p1 - p2) / math.sqrt(pp * (1 - pp) * (1 / m[0] + 1 / m[1]))
    check(f"Q2[2] r_1{j+1} = z_{j+1}", adj[0, j], z, tol=1e-12)
    check(f"Q2[2] 等式 n-e=(m1m2/N)(p1-p2), j={j+1}", tbl[0, j] - e[0, j], m[0] * m[1] / N * (p1 - p2), tol=1e-12)
# 不等サイズの群での恒等式と分散（厳密計算）
m1, m2, pi_j = 30, 50, 0.3
k1 = np.arange(m1 + 1)[:, None]
k2 = np.arange(m2 + 1)[None, :]
pm = stats.binom.pmf(k1, m1, pi_j) * stats.binom.pmf(k2, m2, pi_j)
diff = k1 - m1 * (k1 + k2) / (m1 + m2)
var_exact = np.sum(pm * diff ** 2) - np.sum(pm * diff) ** 2
check("Q2[2] Var(n_1j - e_1j) 厳密計算", var_exact, m1 * m2 / (m1 + m2) * pi_j * (1 - pi_j), tol=1e-9)
# 対数線形モデルの最尤推定（数値最大化）
X = np.array([[1, i == 1, j == 1, j == 2] for i in range(2) for j in range(3)], dtype=float)
yv = tbl.ravel()
negll = lambda b: -np.sum(yv * (X @ b) - np.exp(X @ b))
fit = optimize.minimize(negll, np.zeros(4), method="BFGS", options={"gtol": 1e-10})
mu_hat = np.exp(X @ fit.x).reshape(2, 3)
check_true("Q2[4] 最尤推定値 = e_ij", np.allclose(mu_hat, e, atol=1e-4), str(np.round(mu_hat, 4).tolist()))
check("Q2[4] lambda^ = log e_11", fit.x[0], math.log(40), tol=1e-5)
check("Q2[4] alpha_2^ = log(m2/m1)", fit.x[1], 0.0, tol=1e-5)
check("Q2[4] beta_2^ = log(c2/c1)", fit.x[2], math.log(60 / 80), tol=1e-5)
g2_true = 2 * np.sum(tbl * np.log(tbl / e))
check("Q2[5] G^2（真値）", g2_true, 11.85, tol=5e-3)
check("Q2[5] G^2/2 = 50log5-60log2-30log3", g2_true / 2, 50 * math.log(5) - 60 * math.log(2) - 30 * math.log(3), tol=1e-10)
g2_table = 2 * (50 * LN(5) - 60 * LN(2) - 30 * LN(3))
check("Q2[5] G^2（付表）", g2_table, 11.86, tol=1.5e-2)
check_true("Q2[5] 棄却", g2_true > stats.chi2.ppf(0.95, 2))

# ---------------------------------------------------------------- 問3
print("== 問3 欠測データ")
N1, M1, A1, N0, M0, A0 = 80, 72, 63, 120, 60, 18
check("Q3[1a] 完全ケース", (A1 + A0) / (M1 + M0), 0.614, tol=5e-4)
check("Q3[1b] LOCF", (A1 + A0 + (N1 - M1)) / (N1 + N0), 0.445, tol=1e-12)
p1h, p0h = N1 / 200, N0 / 200
mu1h, mu0h = A1 / M1, A0 / M0
pi1h, pi0h = M1 / N1, M0 / N0
theta_s = p1h * mu1h + p0h * mu0h
check("Q3[3] theta_S", theta_s, 0.53, tol=1e-12)
check("Q3[3] IPW", (A1 / pi1h + A0 / pi0h) / 200, theta_s, tol=1e-12)
p1, p0, q1, q0, u1, u0 = sp.symbols("p1 p0 pi1 pi0 mu1 mu0", positive=True)
sub = {p0: 1 - p1}
theta = p1 * u1 + p0 * u0
cc = (p1 * q1 * u1 + p0 * q0 * u0) / (p1 * q1 + p0 * q0)
ident = sp.simplify((cc - theta - p1 * p0 * (q1 - q0) * (u1 - u0) / (p1 * q1 + p0 * q0)).subs(sub))
check_true("Q3[2] theta_CC - theta の恒等式（記号計算）", ident == 0, str(ident))
locf = p1 * q1 * u1 + p0 * q0 * u0 + p1 * (1 - q1)
ident2 = sp.simplify((locf - theta - (p1 * (1 - q1) * (1 - u1) - p0 * (1 - q0) * u0)).subs(sub))
check_true("Q3[4] theta_LOCF - theta の恒等式（記号計算）", ident2 == 0, str(ident2))
check("Q3[2] 偏りの数値", p1h * p0h * (pi1h - pi0h) * (mu1h - mu0h) / (p1h * pi1h + p0h * pi0h),
      (A1 + A0) / (M1 + M0) - theta_s, tol=1e-12)
check("Q3[4] LOCF の偏りの数値", p1h * (1 - pi1h) * (1 - mu1h) - p0h * (1 - pi0h) * mu0h, -0.085, tol=1e-12)
# MAR モデルのシミュレーション（真値を表1の割合に設定）
nsim = 2_000_000
y1 = rng.binomial(1, 0.4, nsim)
y2 = rng.binomial(1, np.where(y1 == 1, 0.875, 0.3))
r = rng.binomial(1, np.where(y1 == 1, 0.9, 0.5))
check("Q3[2] シミュ P(Y2=1|Y1=1,R=1)=mu1", y2[(y1 == 1) & (r == 1)].mean(), 0.875, tol=2e-3)
check("Q3[2] シミュ theta_CC", y2[r == 1].mean(), float(cc.subs({p1: 0.4, p0: 0.6, q1: 0.9, q0: 0.5, u1: 0.875, u0: 0.3})), tol=2e-3)
check("Q3[3] シミュ E[RY2/pi]", np.mean(r * y2 / np.where(y1 == 1, 0.9, 0.5)), 0.53, tol=2e-3)
check("Q3[4] シミュ theta_LOCF", np.mean(np.where(r == 1, y2, y1)), 0.445, tol=2e-3)
for k in (0.0, 0.4, 1.0):
    th_k = p1h * mu1h * (pi1h + (1 - pi1h) * k) + p0h * mu0h * (pi0h + (1 - pi0h) * k)
    check(f"Q3[5] theta(k) k={k}", th_k, 0.405 + 0.125 * k, tol=1e-12)
check("Q3[5] k=0 は 81/200", 0.405, 81 / 200, tol=1e-12)
# MNAR モデルのシミュレーション: 観測データの分布は同じで theta だけが k に依存
k = 0.5
m1v, m0v = 0.875, 0.3
r = rng.binomial(1, np.where(y1 == 1, 0.9, 0.5))
pr = np.where(y1 == 1, m1v, m0v) * np.where(r == 1, 1.0, k)
y2k = rng.binomial(1, pr)
check("Q3[5] シミュ MNAR(k=0.5) の theta", y2k.mean(), 0.405 + 0.125 * k, tol=2e-3)
check("Q3[5] シミュ MNAR でも完了者の割合は同じ", y2k[(y1 == 0) & (r == 1)].mean(), 0.3, tol=2e-3)

# ---------------------------------------------------------------- 問4
print("== 問4 効果指標・NNT・ケースコントロール")
x0, n0, x1, n1 = 40, 100, 25, 100
ph0, ph1 = x0 / n0, x1 / n1
check("Q4[1] リスク差", ph0 - ph1, 0.15, tol=1e-12)
check("Q4[1] リスク比", ph1 / ph0, 0.625, tol=1e-12)
check("Q4[1] オッズ比", (ph1 / (1 - ph1)) / (ph0 / (1 - ph0)), 0.5, tol=1e-12)
check("Q4[1] NNT", 1 / (ph0 - ph1), 6.67, tol=5e-3)
se_rd = math.sqrt(ph0 * (1 - ph0) / n0 + ph1 * (1 - ph1) / n1)
check("Q4[2] SE", se_rd, 0.0654, tol=5e-5)
check("Q4[2] 下限", 0.15 - 1.96 * se_rd, 0.022, tol=5e-4)
check("Q4[2] 上限", 0.15 + 1.96 * se_rd, 0.278, tol=5e-4)
check("Q4[2] NNT 下限", 1 / (0.15 + 1.96 * se_rd), 3.60, tol=5e-3)
check("Q4[2] NNT 上限", 1 / (0.15 - 1.96 * se_rd), 45.7, tol=1e-1)
var_lrr = (1 - ph1) / (n1 * ph1) + (1 - ph0) / (n0 * ph0)
check("Q4[3] Var(log RR)", var_lrr, 0.045, tol=1e-12)
check("Q4[3] SE", math.sqrt(var_lrr), 0.2121, tol=5e-5)
check("Q4[3] log0.625（付表）", LN(5) - 3 * LN(2), math.log(0.625), tol=5e-4)
lo = math.exp(math.log(0.625) - 1.96 * math.sqrt(var_lrr))
hi = math.exp(math.log(0.625) + 1.96 * math.sqrt(var_lrr))
check("Q4[3] RR 下限", lo, 0.412, tol=6e-4)
check("Q4[3] RR 上限", hi, 0.947, tol=6e-4)
check("Q4[3] 付表による下限", 1 / exp_table(0.886), lo, tol=1e-3)
check("Q4[3] 付表による上限", 1 / exp_table(0.054), hi, tol=1e-3)
# デルタ法の分散をシミュレーションで確認（大標本）
nn = 4000
a = rng.binomial(nn, 0.25, 400_000) / nn
b = rng.binomial(nn, 0.40, 400_000) / nn
check("Q4[3] デルタ法（シミュレーション, n=4000）", np.var(np.log(a / b)), 0.75 / (nn * 0.25) + 0.6 / (nn * 0.4), tol=2e-2, kind="rel")
# ケース・コントロール抽出
alpha, beta, f1, f0 = -1.2, -0.7, 0.9, 0.05
for xv in (0, 1):
    pd = 1 / (1 + math.exp(-(alpha + beta * xv)))
    psel = f1 * pd / (f1 * pd + f0 * (1 - pd))
    check(f"Q4[4] 抽出後のロジット x={xv}", math.log(psel / (1 - psel)), alpha + math.log(f1 / f0) + beta * xv, tol=1e-12)
npop = 3_000_000
xv = rng.binomial(1, 0.5, npop)
dv = rng.binomial(1, 1 / (1 + np.exp(-(alpha + beta * xv))))
sv = rng.binomial(1, np.where(dv == 1, f1, f0))
t = np.array([[np.sum((xv == i) & (dv == j) & (sv == 1)) for j in (1, 0)] for i in (1, 0)], dtype=float)
check("Q4[4] シミュ: 抽出標本のオッズ比", t[0, 0] * t[1, 1] / (t[0, 1] * t[1, 0]), math.exp(beta), tol=2e-2, kind="rel")
p1s = t[0, 0] / t[0].sum()
p0s = t[1, 0] / t[1].sum()
true_rr = (1 / (1 + math.exp(-(alpha + beta)))) / (1 / (1 + math.exp(-alpha)))
check_true("Q4[4] シミュ: 抽出標本のリスク比は母集団と異なる", abs(p1s / p0s - true_rr) > 0.1, f"{p1s/p0s:.3f} vs {true_rr:.3f}")
psi = 0.5
for p0v, ex in ((0.4, 6.67), (0.05, 41.05)):
    p1v = psi * p0v / (1 - p0v + psi * p0v)
    check(f"Q4[5] オッズ比の確認 p0={p0v}", (p1v / (1 - p1v)) / (p0v / (1 - p0v)), psi, tol=1e-12)
    check(f"Q4[5] NNT 式 p0={p0v}", 1 / (p0v - p1v), (2 - p0v) / (p0v * (1 - p0v)), tol=1e-9)
    check(f"Q4[5] NNT 値 p0={p0v}", 1 / (p0v - p1v), ex, tol=6e-3)

nnt = lambda p0v: (2 - p0v) / (p0v * (1 - p0v))
res = optimize.minimize_scalar(nnt, bounds=(1e-6, 1 - 1e-6), method="bounded", options={"xatol": 1e-12})
check("Q4[5] NNT 最小の p0 = 2-√2", res.x, 2 - math.sqrt(2), tol=1e-6)
check("Q4[5] NNT の最小値 3+2√2", res.fun, 3 + 2 * math.sqrt(2), tol=1e-9)
check("Q4[5] 数値 0.586", 2 - 1.4142, 0.586, tol=5e-4)
check("Q4[5] 数値 5.83", 3 + 2 * 1.4142, 5.83, tol=5e-3)
pp = sp.symbols("p0", positive=True)
dd = sp.simplify(sp.diff(pp * (1 - pp) / (2 - pp), pp) - (pp ** 2 - 4 * pp + 2) / (2 - pp) ** 2)
check_true("Q4[5] リスク差の導関数（記号計算）", dd == 0, str(dd))

# ---------------------------------------------------------------- 問5
print("== 問5 プール検査")
h = lambda k, p: 1 + 1 / k - (1 - p) ** k
check("Q5[2] 0.99^10", 0.99 ** 10, 0.904382, tol=1e-6)
check("Q5[2] h(10)", h(10, 0.01), 0.196, tol=5e-4)
p, k = 0.03, 8
tests = np.where(rng.binomial(k, p, 1_000_000) == 0, 1, k + 1)
check("Q5[1] E[T] シミュレーション", tests.mean(), 1 + k * (1 - (1 - p) ** k), tol=5e-3)
for p in (0.01, 0.0025):
    ks = np.linspace(1, 200, 200_000)
    approx = 1 / ks + ks * p
    check(f"Q5[2] 近似の最小点 p={p}", ks[np.argmin(approx)], 1 / math.sqrt(p), tol=2e-3, kind="rel")
    check(f"Q5[2] 近似の最小値 p={p}", approx.min(), 2 * math.sqrt(p), tol=1e-6)
# 最尤推定量（数値最大化）と分散
n, k, x = 50, 10, 5
negll = lambda pp: -(x * math.log(1 - (1 - pp) ** k) + (n - x) * k * math.log(1 - pp))
num = optimize.minimize_scalar(negll, bounds=(1e-8, 0.5), method="bounded", options={"xatol": 1e-12}).x
p_hat = 1 - (1 - x / n) ** (1 / k)
check("Q5[3] 最尤推定値（数値最大化）", num, p_hat, tol=1e-6)
check("Q5[4] p^（真値）", p_hat, 0.01048, tol=5e-6)
p_table = 1 - 1 / exp_table(-0.1 * LN(0.9))
check("Q5[4] p^（付表）", p_table, 0.0105, tol=6e-5)
q_hat = 1 - p_hat
var_hat = (1 - q_hat ** k) * q_hat ** (2 - k) / (k * k * n)
check("Q5[4] 分散の式 = g'(θ)^2 θ(1-θ)/n", var_hat, ((1 / k) * q_hat / 0.9) ** 2 * 0.1 * 0.9 / n, tol=1e-15)
check("Q5[4] SE", math.sqrt(var_hat), 0.00466, tol=1e-5)
check("Q5[4] 下限", p_hat - 1.96 * math.sqrt(var_hat), 0.0014, tol=1.5e-4)
check("Q5[4] 上限", p_hat + 1.96 * math.sqrt(var_hat), 0.0197, tol=1.5e-4)
# デルタ法の分散をシミュレーションで確認（大標本）
p, k, n = 0.02, 10, 5000
q = 1 - p
xs = rng.binomial(n, 1 - q ** k, 400_000)
est = 1 - (1 - xs / n) ** (1 / k)
check("Q5[3] X の分布: E[X]/n", xs.mean() / n, 1 - q ** k, tol=1e-3)
check("Q5[3] デルタ法の分散（シミュレーション）", est.var(), (1 - q ** k) * q ** (2 - k) / (k * k * n), tol=2e-2, kind="rel")
ratio = lambda p, k: (1 - (1 - p) ** k) * (1 - p) ** (1 - k) / (k * k * p)
check("Q5[5] 分散比の式", ((1 - q ** k) * q ** (2 - k) / (k * k * n)) / (p * q / n), ratio(p, k), tol=1e-12)
check("Q5[5] p→0 で比は 1/k", ratio(1e-6, 10), 0.1, tol=1e-5)
check("Q5[5] p=0.01,k=10 の比", ratio(0.01, 10), 0.1047, tol=1e-4)
ratios = [ratio(0.01, kk) for kk in (10, 100, 200, 400, 800)]
check_true("Q5[5] k を大きくしすぎると分散比は再び増大", min(ratios) < ratios[0] and ratios[-1] > ratios[0] and ratios[-1] > ratios[-2],
           str([round(v, 4) for v in ratios]))
check("Q5[5] 全プール陽性の確率 (p=0.01,k=400,n=50)", (1 - 0.99 ** 400) ** 50, 0.406, tol=5e-3)
# [5](b) 分散は (e^u-1)/u^2 に比例し，(u-2)e^u+2=0 の正の解で最小
phi = lambda u: (u - 2) * math.exp(u) + 2
u_star = optimize.brentq(phi, 1.0, 3.0)
check_true("Q5[5b] 1.5 < u* < 1.6", 1.5 < u_star < 1.6, f"u*={u_star:.6f}")
check_true("Q5[5b] φ(1.5)<0<φ(1.6)", phi(1.5) < 0 < phi(1.6), f"{phi(1.5):.4f}, {phi(1.6):.4f}")
check("Q5[5b] e^1.5（付表: 2.7183×1.6487）", 2.7183 * 1.6487, math.exp(1.5), tol=5e-4)
check("Q5[5b] e^1.6（付表: 2.7183×1.8221）", 2.7183 * 1.8221, math.exp(1.6), tol=5e-4)
check("Q5[5b] φ(1.5)（付表）", -0.5 * 2.7183 * 1.6487 + 2, -0.241, tol=1e-3)
check("Q5[5b] φ(1.6)（付表）", -0.4 * 2.7183 * 1.8221 + 2, 0.019, tol=1e-3)
us = np.linspace(0.01, 1.0, 400)
check_true("Q5[5b] φ<0 on (0,1]", np.all([phi(v) < 0 for v in us]))
us = np.linspace(1.0, 12, 4000)
check_true("Q5[5b] φ は u>1 で単調増加", np.all(np.diff([phi(v) for v in us]) > 0))
for p in (0.01, 0.05, 0.2):
    q = 1 - p
    n = 50
    var_k = lambda k: (1 - q ** k) * q ** (2 - k) / (k * k * n)
    k_opt = optimize.minimize_scalar(var_k, bounds=(0.5, 5000), method="bounded", options={"xatol": 1e-9}).x
    check(f"Q5[5b] 分散最小の k は u*/(-log q) (p={p})", k_opt, u_star / (-math.log(q)), tol=1e-4, kind="rel")
    for k in (3.0, 10.0, 57.5):
        u = -k * math.log(q)
        check(f"Q5[5b] 比例式 (p={p},k={k})", var_k(k), q * q * math.log(q) ** 2 / n * (math.exp(u) - 1) / u ** 2, tol=1e-12, kind="rel")
check("Q5[5c] 最適な k での陰性確率 e^{-u*}", math.exp(-u_star), 0.2, tol=5e-3)

# ---------------------------------------------------------------- まとめ
n_fail = sum(1 for r in results if not r["ok"])
summary = {"seed": SEED, "checks": len(results), "failed": n_fail, "results": results}
Path(__file__).with_name("検算結果.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n{len(results)} checks, {n_fail} failed")
raise SystemExit(1 if n_fail else 0)
