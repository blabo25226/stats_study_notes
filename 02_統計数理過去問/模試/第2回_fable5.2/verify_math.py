"""第2回模試・統計数理の検算。

模範解答のTeXは読み込まず、問題文の設定（分布・データ）から独立に再計算して
解答の式・数値と照合する。結果は 検算結果.json に保存する。

Run: python verify_math.py
Requires: NumPy, SciPy, SymPy
"""
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
import sympy as sp
from scipy import integrate, optimize, special, stats

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


LOG10 = {0.8: -0.0969, 0.9: -0.0458, 1.2: 0.0792, 2: 0.3010, 3: 0.4771, 5: 0.6990}
LN = lambda x: 2.3026 * LOG10[x]  # 付表5（常用対数）による自然対数

# ---------------------------------------------------------------- 問1
print("== 問1 ロジスティック分布")
F = lambda x: 1 / (1 + np.exp(-x))
f = lambda x: np.exp(-x) / (1 + np.exp(-x)) ** 2
u = rng.uniform(size=400_000)
x_sim = np.log(u / (1 - u))
for x0 in (-2.0, -0.5, 0.0, 1.0, 2.5):
    check(f"Q1[1] F({x0}) 経験分布", np.mean(x_sim <= x0), F(x0), tol=4e-3)
xs = np.linspace(-8, 8, 41)
check_true("Q1[1] f=F(1-F)", np.allclose(f(xs), F(xs) * (1 - F(xs))))
check_true("Q1[1] f(-x)=f(x)", np.allclose(f(xs), f(-xs)))
check("Q1[1] 密度の全積分", integrate.quad(f, -60, 60)[0], 1.0, tol=1e-9)
check("Q1[2] 上側25%点", optimize.brentq(lambda q: F(q) - 0.75, 0, 5), math.log(3))
check("Q1[2] 付表による log3", LN(3), math.log(3), tol=5e-4)
check("Q1[2] E|X|", 2 * integrate.quad(lambda x: x * f(x), 0, 80)[0], 2 * math.log(2))
check("Q1[2] 付表による 2log2", 2 * LN(2), 1.386, tol=5e-4)
y1, y2 = rng.exponential(size=(2, 400_000))
w = np.log(y1 / y2)
check("Q1[3] W と X の分布（KS統計量）", stats.kstest(w, lambda t: F(t)).statistic, 0.0, tol=4e-3)
for t in (-0.7, -0.3, 0.2, 0.5, 0.8):
    mgf = integrate.quad(lambda uu: uu ** t * (1 - uu) ** (-t), 0, 1)[0]
    check(f"Q1[4] M({t}) = Γ(1+t)Γ(1-t)", mgf, special.gamma(1 + t) * special.gamma(1 - t), tol=1e-6)
    check(f"Q1[4] Γ(1+t)Γ(1-t) = πt/sin(πt), t={t}", special.gamma(1 + t) * special.gamma(1 - t),
          math.pi * t / math.sin(math.pi * t), tol=1e-10)
check("Q1[4] 分散", integrate.quad(lambda x: 2 * x * x * f(x), 0, 80)[0], math.pi ** 2 / 3)
ts = sp.symbols("t")
ser = sp.series(sp.pi * ts / sp.sin(sp.pi * ts), ts, 0, 4).removeO()
check("Q1[4] πt/sin(πt) の t^2 の係数", ser.coeff(ts, 2), math.pi ** 2 / 6)
for x0 in (-1.0, 0.0, 1.5):
    n_big = 10 ** 7
    check(f"Q1[5a] 極限 x={x0}", (1 + math.exp(-x0) / n_big) ** (-n_big), math.exp(-math.exp(-x0)), tol=1e-6)
    n_s = 200
    m_sim = np.log(rng.uniform(size=(20000, n_s)))
    m_sim = np.max(m_sim - np.log1p(-np.exp(m_sim)), axis=1) - math.log(n_s)
    check(f"Q1[5a] シミュレーション n=200, x={x0}", np.mean(m_sim <= x0),
          (1 + math.exp(-x0) / n_s) ** (-n_s), tol=1.2e-2)
check("Q1[5b] E[M_2]", integrate.quad(lambda x: x * 2 * F(x) * f(x), -80, 80)[0], 1.0, tol=1e-8)
check("Q1[5b] ∫u log u", integrate.quad(lambda v: v * math.log(v), 0, 1)[0], -0.25)
check("Q1[5b] ∫u log(1-u)", integrate.quad(lambda v: v * math.log(1 - v), 0, 1)[0], -0.75)
for n in (2, 3, 4, 6, 11):
    val = integrate.quad(lambda x: x * n * F(x) ** (n - 1) * f(x), -80, 80)[0]
    check(f"Q1[5c] E[M_{n}]=H_(n-1)", val, sum(1 / k for k in range(1, n)), tol=1e-7)
    check(f"Q1[5c] n∫u^(n-1)log u = -1/n (n={n})",
          n * integrate.quad(lambda v: v ** (n - 1) * math.log(v), 0, 1)[0], -1 / n, tol=1e-9)
    check(f"Q1[5c] n∫u^(n-1)log(1-u) = -H_n (n={n})",
          n * integrate.quad(lambda v: v ** (n - 1) * math.log(1 - v), 0, 1)[0], -sum(1 / k for k in range(1, n + 1)), tol=1e-8)
m_sim5 = rng.uniform(size=(400_000, 5))
m_sim5 = np.max(np.log(m_sim5 / (1 - m_sim5)), axis=1)
check("Q1[5c] シミュレーション E[M_5]=25/12", m_sim5.mean(), 25 / 12, tol=8e-3)

# ---------------------------------------------------------------- 問2
print("== 問2 変動係数既知の正規分布")
a_n = lambda n: math.sqrt(2 / (n - 1)) * math.exp(special.gammaln(n / 2) - special.gammaln((n - 1) / 2))
for (mu, c, n) in [(2.0, 0.5, 8), (1.3, 1.2, 15), (5.0, 0.2, 5)]:
    x = rng.normal(mu, c * mu, size=n)
    xbar, t = x.mean(), np.mean(x ** 2)
    negll = lambda m: n * math.log(m) + np.sum((x - m) ** 2) / (2 * c * c * m * m)
    num = optimize.minimize_scalar(negll, bounds=(1e-6, 50), method="bounded", options={"xatol": 1e-12}).x
    mle = (-xbar + math.sqrt(xbar ** 2 + 4 * c * c * t)) / (2 * c * c)
    check(f"Q2[2] 最尤推定値 (mu={mu},c={c},n={n})", num, mle, tol=1e-5)
    check(f"Q2[2] 尤度方程式 (mu={mu},c={c},n={n})", c * c * mle ** 2 + xbar * mle - t, 0.0, tol=1e-9)
    # フィッシャー情報量: スコアの2乗の期待値を数値積分
    score = lambda xx: -1 / mu + (xx - mu) / (c * c * mu * mu) + (xx - mu) ** 2 / (c * c * mu ** 3)
    dens = lambda xx: stats.norm.pdf(xx, mu, c * mu)
    info = integrate.quad(lambda xx: score(xx) ** 2 * dens(xx), mu - 12 * c * mu, mu + 12 * c * mu)[0]
    check(f"Q2[3] I(mu) (mu={mu},c={c})", info, (1 + 2 * c * c) / (c * c * mu * mu), tol=1e-7, kind="rel")
    check(f"Q2[3] スコアの期待値0 (mu={mu},c={c})",
          integrate.quad(lambda xx: score(xx) * dens(xx), mu - 12 * c * mu, mu + 12 * c * mu)[0], 0.0, tol=1e-8)
    # [4] E[S]=a_n c mu, Var, 最良線形結合（シミュレーション）
    an = a_n(n)
    sims = rng.normal(mu, c * mu, size=(400_000, n))
    xb = sims.mean(axis=1)
    s = sims.std(axis=1, ddof=1)
    check(f"Q2[4] E[S]=a_n c mu (n={n})", s.mean(), an * c * mu, tol=4e-3, kind="rel")
    v1 = c * c * mu * mu / n
    v2 = (1 - an * an) * mu * mu / (an * an)
    mt = s / (an * c)
    check(f"Q2[4] E[mu~]=mu (n={n})", mt.mean(), mu, tol=4e-3, kind="rel")
    check(f"Q2[4] Var(mu~) (n={n})", mt.var(), v2, tol=2e-2, kind="rel")
    check(f"Q2[4] Cov(Xbar,S)=0 (n={n})", np.corrcoef(xb, s)[0, 1], 0.0, tol=6e-3)
    wstar = n * (1 - an * an) / (c * c * an * an + n * (1 - an * an))
    vstar = c * c * (1 - an * an) * mu * mu / (c * c * an * an + n * (1 - an * an))
    check(f"Q2[4] w*=V2/(V1+V2) (n={n})", wstar, v2 / (v1 + v2))
    check(f"Q2[4] V*=V1V2/(V1+V2) (n={n})", vstar, v1 * v2 / (v1 + v2))
    check(f"Q2[4] Var(mu_w*) シミュレーション (n={n})", (wstar * xb + (1 - wstar) * mt).var(), vstar, tol=2e-2, kind="rel")
    grid = np.linspace(0, 1, 2001)
    check(f"Q2[4] w* が最小点 (n={n})", grid[np.argmin(grid ** 2 * v1 + (1 - grid) ** 2 * v2)], wstar, tol=6e-4)
    check(f"Q2[5] E[h]=0 (n={n})", (xb - mt).mean(), 0.0, tol=6e-3 * mu)
    check_true(f"Q2[5] Vの大小: CR下限 <= V* <= Var(Xbar) (n={n})",
               c * c * mu * mu / (n * (1 + 2 * c * c)) <= vstar <= v1)
for n in (50, 500, 5000):
    check(f"Q2[5] a_n^2 = 1-1/(2n)+O(n^-2), n={n}", (1 - a_n(n) ** 2) * 2 * n, 1.0, tol=2.0 / n)
mu, c = 2.0, 0.7
n = 10 ** 6
an2 = 1 - 1 / (2 * n)  # 極限の確認には漸近形を使用
check("Q2[5] nV* の極限", n * c * c * (1 - an2) * mu * mu / (c * c * an2 + n * (1 - an2)),
      c * c * mu * mu / (1 + 2 * c * c), tol=1e-5)

# ---------------------------------------------------------------- 問3
print("== 問3 スピアマンの順位相関係数")
for n in (2, 3, 4, 5, 6, 7):
    vals = []
    ok_formula = True
    base = np.arange(1, n + 1)
    for perm in itertools.permutations(range(1, n + 1)):
        q = np.array(perm)
        d = int(np.sum((base - q) ** 2))
        r_formula = 1 - 6 * d / (n * (n * n - 1))
        r_pearson = np.corrcoef(base, q)[0, 1]
        ok_formula &= abs(r_formula - r_pearson) < 1e-12
        vals.append(r_formula)
    check_true(f"Q3[1] 公式とピアソン相関の一致 (n={n}, 全順列)", ok_formula)
    check(f"Q3[2] E[r_S]=0 (n={n})", np.mean(vals), 0.0, tol=1e-12)
    check(f"Q3[2] Var(r_S)=1/(n-1) (n={n})", np.var(vals), 1 / (n - 1), tol=1e-12)
n = 6
perms = np.array(list(itertools.permutations(range(1, n + 1))))
check("Q3[2] Var(Q_i) (n=6)", perms[:, 0].var(), (n * n - 1) / 12)
check("Q3[2] Cov(Q_i,Q_j) (n=6)", np.cov(perms[:, 0], perms[:, 1], bias=True)[0, 1], -(n + 1) / 12)
xd = np.array([5.2, 3.1, 8.0, 4.5, 6.8])
yd = np.array([21, 12, 30, 15, 19])
R = stats.rankdata(xd)
Q = stats.rankdata(yd)
check_true("Q3[3] 順位", list(R) == [3, 1, 5, 2, 4] and list(Q) == [4, 1, 5, 2, 3], f"R={list(R)} Q={list(Q)}")
D_obs = int(np.sum((R - Q) ** 2))
check("Q3[3] D", D_obs, 2)
check("Q3[3] r_S", stats.spearmanr(xd, yd)[0], 0.9)
cnt = sum(1 for p in itertools.permutations(range(1, 6))
          if sum((i + 1 - p[i]) ** 2 for i in range(5)) <= D_obs)
check("Q3[3] D<=2 の順列の数", cnt, 5)
check("Q3[3] 正確な片側p値", cnt / 120, 1 / 24)
check("Q3[3] 正規近似 Q(1.80)", stats.norm.sf(1.8), 0.0359, tol=5e-5)
for th in (-1.0, -0.4, 0.3, 0.9):
    h = lambda y, x: 1 + th * (1 - 2 * x) * (1 - 2 * y)
    check(f"Q3[4] 周辺密度 h_X(0.3)=1 (theta={th})", integrate.quad(lambda y: h(y, 0.3), 0, 1)[0], 1.0)
    exy = integrate.dblquad(lambda y, x: x * y * h(y, x), 0, 1, 0, 1)[0]
    check(f"Q3[4] 相関係数 theta/3 (theta={th})", (exy - 0.25) / (1 / 12), th / 3, tol=1e-9)
    H = lambda x, y: x * y + th * x * (1 - x) * y * (1 - y)
    eH = integrate.dblquad(lambda y, x: H(x, y) * h(y, x), 0, 1, 0, 1)[0]
    check(f"Q3[5] E[H(X,Y)] (theta={th})", eH, 0.25 + th / 18, tol=1e-9)
    check(f"Q3[5] E[r_S]=2theta/9 (theta={th})", 2 * (2 * eH) - 1, 2 * th / 9, tol=1e-9)
    # シミュレーション: 条件付き分布関数の逆関数で (X,Y) を生成
    m = 400_000
    xx = rng.uniform(size=(m, 2))
    vv = rng.uniform(size=(m, 2))
    a = th * (1 - 2 * xx)
    with np.errstate(divide="ignore", invalid="ignore"):
        yy = np.where(np.abs(a) < 1e-12, vv, ((1 + a) - np.sqrt((1 + a) ** 2 - 4 * a * vv)) / (2 * a))
    conc = np.sign((xx[:, 0] - xx[:, 1]) * (yy[:, 0] - yy[:, 1]))
    check(f"Q3[5] シミュレーション E[r_S] (theta={th})", conc.mean(), 2 * th / 9, tol=6e-3)
    check(f"Q3[4] シミュレーション 相関 (theta={th})", np.corrcoef(xx[:, 0], yy[:, 0])[0, 1], th / 3, tol=6e-3)

# ---------------------------------------------------------------- 問4
print("== 問4 AIC・BIC・ベイズファクター")
n, x = 100, 60
lam_true = 2 * (x * math.log(x / n) + (n - x) * math.log(1 - x / n) + n * math.log(2))
l1 = stats.binom.logpmf(x, n, x / n)
l0 = stats.binom.logpmf(x, n, 0.5)
check("Q4[1] Λ の式", 2 * (l1 - l0), lam_true, tol=1e-9)
lam_table = 2 * (60 * LN(1.2) + 40 * LN(0.8))
check("Q4[2] Λ（付表）", lam_table, 4.034, tol=1e-3)
check("Q4[2] Λ（真値）と付表の差", lam_table, lam_true, tol=1e-2)
check_true("Q4[2] AIC は M1", lam_true > 2)
check_true("Q4[2] BIC は M0", lam_true < math.log(100), f"log100={math.log(100):.4f}")
check("Q4[2] log100（付表）", 2 * 2.3026, math.log(100), tol=1e-4)
check_true("Q4[2] 尤度比検定で棄却", lam_true > stats.chi2.ppf(0.95, 1), f"3.84 vs {stats.chi2.ppf(0.95, 1):.4f}")
check("Q4[3] P(chi2_1>2)", stats.chi2.sf(2, 1), 2 * stats.norm.sf(math.sqrt(2)))
check("Q4[3] 付表補間 2Q(1.414)", 2 * (0.0793 - 0.4 * 0.0015), stats.chi2.sf(2, 1), tol=5e-4)


def select_prob(nn, thr):
    ks = np.arange(0, nn + 1)
    with np.errstate(divide="ignore", invalid="ignore"):
        lam = 2 * (special.xlogy(ks, ks / nn) + special.xlogy(nn - ks, 1 - ks / nn) + nn * math.log(2))
    return float(np.sum(stats.binom.pmf(ks, nn, 0.5)[lam > thr]))


for nn in (10_000, 100_000):
    check(f"Q4[3] AIC の誤選択確率 n={nn}", select_prob(nn, 2.0), stats.chi2.sf(2, 1), tol=6e-3)
bic_err = [select_prob(nn, math.log(nn)) for nn in (100, 1000, 10_000, 100_000)]
check_true("Q4[3] BIC の誤選択確率は減少して0へ", all(a > b for a, b in zip(bic_err, bic_err[1:])) and bic_err[-1] < 0.005,
           str([round(v, 5) for v in bic_err]))
p = sp.symbols("p")
for (nn, xx_) in [(4, 1), (7, 7), (10, 3), (12, 0)]:
    m1 = sp.integrate(sp.binomial(nn, xx_) * p ** xx_ * (1 - p) ** (nn - xx_), (p, 0, 1))
    check_true(f"Q4[4] m1(x)=1/(n+1) (n={nn},x={xx_})", sp.simplify(m1 - sp.Rational(1, nn + 1)) == 0)
B10 = Fraction(2 ** 100, 101 * math.comb(100, 60))
check("Q4[4][5] B10 の正確な値", float(B10), 0.9130, tol=5e-4)
approx = math.sqrt(2 * math.pi * n * 0.6 * 0.4) / (n + 1) * math.exp(lam_true / 2)
check("Q4[5] 近似式（真の Λ）", approx, float(B10), tol=5e-3)
e2017 = 2.7183 ** 2 * (1.0101 + 0.7 * (1.0202 - 1.0101))
check("Q4[5] e^{2.017}（付表）", e2017, math.exp(2.017), tol=2e-3)
approx_table = math.sqrt(2 * 3.1416 * 24) * e2017 / 101
check("Q4[5] B10（付表による手計算）", approx_table, 0.91, tol=6e-3)
check("Q4[5] 2logB10 ≈ Λ - log n + log(2πp(1-p))", 2 * math.log(float(B10)),
      lam_true - math.log(n) + math.log(2 * math.pi * 0.24), tol=3e-2)
# Λ を固定して n を増やすと B10 -> 0
vals = []
for nn in (100, 10_000, 1_000_000):
    xx_ = round(nn / 2 + math.sqrt(nn))  # z = 2 に相当
    logB = nn * math.log(2) - math.log(nn + 1) - (special.gammaln(nn + 1) - special.gammaln(xx_ + 1) - special.gammaln(nn - xx_ + 1))
    vals.append(math.exp(logB))
check_true("Q4[5] 同じ有意性で n を増やすと B10 は減少", vals[0] > vals[1] > vals[2], str([round(v, 4) for v in vals]))

# ---------------------------------------------------------------- 問5
print("== 問5 偏相関係数")


def partial_stuff(r12, r13, r23):
    S = np.array([[1, r12, r13], [r12, 1, r23], [r13, r23, 1.0]])
    assert np.all(np.linalg.eigvalsh(S) > 0)
    P = np.linalg.inv(S)
    pc = -P[0, 1] / math.sqrt(P[0, 0] * P[1, 1])
    cond = S[:2, :2] - np.outer(S[:2, 2], S[:2, 2]) / S[2, 2]
    beta = np.linalg.solve(S[1:, 1:], S[1:, 0])
    resid = 1 - S[1:, 0] @ beta
    return S, pc, cond, beta, resid


for (r12, r13, r23) in [(0.48, 0.6, 0.8), (0.0, 0.6, 0.6), (0.3, -0.5, 0.2), (-0.2, 0.7, 0.4)]:
    S, pc, cond, beta, resid = partial_stuff(r12, r13, r23)
    formula = (r12 - r13 * r23) / math.sqrt((1 - r13 ** 2) * (1 - r23 ** 2))
    tag = f"({r12},{r13},{r23})"
    check(f"Q5[2] 偏相関の式 {tag}", formula, pc, tol=1e-12)
    check(f"Q5[2][3] 条件付き分散1 {tag}", cond[0, 0], 1 - r13 ** 2, tol=1e-12)
    check(f"Q5[2][3] 条件付き分散2 {tag}", cond[1, 1], 1 - r23 ** 2, tol=1e-12)
    check(f"Q5[2][3] 条件付き共分散 {tag}", cond[0, 1], r12 - r13 * r23, tol=1e-12)
    check(f"Q5[5] beta2 {tag}", beta[0], (r12 - r13 * r23) / (1 - r23 ** 2), tol=1e-12)
    check(f"Q5[5] beta3 = rho13 - beta2 rho23 {tag}", beta[1], r13 - beta[0] * r23, tol=1e-12)
    check(f"Q5[5] 最小値 {tag}", resid, (1 - r13 ** 2) * (1 - formula ** 2), tol=1e-12)
    check_true(f"Q5[5] 符号の一致 {tag}", np.sign(round(beta[0], 12)) == np.sign(round(formula, 12)))
    z = rng.multivariate_normal(np.zeros(3), S, size=400_000)
    e1 = z[:, 0] - r13 * z[:, 2]
    e2 = z[:, 1] - r23 * z[:, 2]
    check(f"Q5[1] Cov(e1,X3)=0 シミュレーション {tag}", np.cov(e1, z[:, 2])[0, 1], 0.0, tol=6e-3)
    check(f"Q5[2] Corr(e1,e2) シミュレーション {tag}", np.corrcoef(e1, e2)[0, 1], formula, tol=6e-3)
    sel = np.abs(z[:, 2] - 0.8) < 0.05
    check(f"Q5[3] X3≈0.8 での条件付き相関 {tag}", np.corrcoef(z[sel, 0], z[sel, 1])[0, 1], formula, tol=3e-2)
    check(f"Q5[3] X3≈0.8 での条件付き平均 {tag}", z[sel, 0].mean(), r13 * z[sel, 2].mean(), tol=2.5e-2)
check("Q5[4a] 値", partial_stuff(0.48, 0.6, 0.8)[1], 0.0, tol=1e-12)
check("Q5[4b] 値", partial_stuff(0.0, 0.6, 0.6)[1], -0.5625, tol=1e-12)
check("Q5[4a] 行列式", np.linalg.det(partial_stuff(0.48, 0.6, 0.8)[0]), 0.2304, tol=1e-12)
check("Q5[4b] 行列式", np.linalg.det(partial_stuff(0.0, 0.6, 0.6)[0]), 0.28, tol=1e-12)
# [6] rho13=0.6, rho23=0.8 のとき正定値となる rho12 の範囲
grid = np.round(np.arange(-0.999, 1.0, 0.001), 3)
pd = np.array([np.all(np.linalg.eigvalsh(np.array([[1, r, 0.6], [r, 1, 0.8], [0.6, 0.8, 1.0]])) > 1e-12) for r in grid])
check("Q5[6] 正定値となる rho12 の下限", grid[pd].min(), 0.001, tol=1e-9)
check("Q5[6] 正定値となる rho12 の上限", grid[pd].max(), 0.959, tol=1e-9)
check_true("Q5[6] 正定値の範囲は区間", np.all(np.diff(np.where(pd)[0]) == 1))
for r in (0.0, 0.96):
    check(f"Q5[6] 端点 rho12={r} で行列式0", np.linalg.det(np.array([[1, r, 0.6], [r, 1, 0.8], [0.6, 0.8, 1.0]])), 0.0, tol=1e-12)
for (r12, r13, r23) in [(0.3, -0.5, 0.2), (0.48, 0.6, 0.8), (-0.2, 0.7, 0.4)]:
    pc = (r12 - r13 * r23) / math.sqrt((1 - r13 ** 2) * (1 - r23 ** 2))
    check(f"Q5[6] det = (1-r13^2)(1-r23^2)(1-pc^2) ({r12},{r13},{r23})",
          np.linalg.det(np.array([[1, r12, r13], [r12, 1, r23], [r13, r23, 1.0]])),
          (1 - r13 ** 2) * (1 - r23 ** 2) * (1 - pc ** 2), tol=1e-12)
A = np.array([[1, 0, -0.6], [0, 1, -0.8], [0, 0, 1.0]])
S6 = np.array([[1, 0.3, 0.6], [0.3, 1, 0.8], [0.6, 0.8, 1.0]])
check_true("Q5[6] AΣA^T の形", np.allclose(A @ S6 @ A.T, [[0.64, 0.3 - 0.48, 0], [0.3 - 0.48, 0.36, 0], [0, 0, 1]]))

# ---------------------------------------------------------------- まとめ
n_fail = sum(1 for r in results if not r["ok"])
summary = {"seed": SEED, "checks": len(results), "failed": n_fail, "results": results}
Path(__file__).with_name("検算結果.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n{len(results)} checks, {n_fail} failed")
raise SystemExit(1 if n_fail else 0)
