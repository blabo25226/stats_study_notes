"""第2版で引用する過去問の数値の検算（公式解答・初版の記述との照合用）．"""
import math
import numpy as np
from scipy import optimize, stats

def hdr(s): print("\n=== " + s)

hdr("2017 医薬 問4：層別 2x2 表（曝露 OR）")
# 各層: a=発症あり・多い, b=発症あり・少ない, c=発症なし・多い, d=発症なし・少ない
T = [(5, 5, 35, 270), (67, 55, 56, 277), (24, 44, 18, 119)]
num = den = 0.0; sOE = sV = 0.0
for a, b, c, d in T:
    n = a + b + c + d
    E = (a + b) * (a + c) / n
    V = (a + b) * (c + d) * (a + c) * (b + d) / (n**2 * (n - 1))
    print(f"OR={a*d/(b*c):.3f} E={E:.4f} V={V:.4f} Peto層OR={math.exp((a-E)/V):.2f}")
    num += a * d / n; den += b * c / n; sOE += a - E; sV += V
peto = sOE / sV
print(f"Peto型 log OR={peto:.4f}, OR={math.exp(peto):.3f}, Var={1/sV:.5f}, "
      f"CI=({math.exp(peto-1.96/math.sqrt(sV)):.2f},{math.exp(peto+1.96/math.sqrt(sV)):.2f})")
print(f"MH OR={num/den:.3f}")
A = np.array(T).sum(0); print("粗 OR=", A[0]*A[3]/(A[1]*A[2]))

hdr("2021 医薬 問4：変量効果メタ")
y = np.array([-0.480, 0.032, 0.221, -0.085]); s2 = np.array([0.095, 0.092, 0.014, 0.013])
for t2 in (0.013, 0.014):
    w = 1 / (s2 + t2); mu = (w * y).sum() / w.sum(); se = 1 / math.sqrt(w.sum())
    print(f"tau2={t2}: mu={mu:.4f} se={se:.4f} CI=({mu-1.96*se:.3f},{mu+1.96*se:.3f})")
w = 1 / s2; th = (w * y).sum() / w.sum(); Q = (w * (y - th)**2).sum()
c = w.sum() - (w**2).sum() / w.sum()
print(f"FE theta={th:.4f} Q={Q:.3f} DL tau2={(Q-3)/c:.4f}")
def nll(p):
    mu, t2 = p
    v = s2 + t2
    return 0.5 * (np.log(v) + (y - mu)**2 / v).sum()
r = optimize.minimize(nll, [0, 0.01], bounds=[(-1, 1), (0, 1)])
print("ML (mu,tau2)=", r.x)

hdr("2023 医薬 問3：固定効果と Q")
tab = [(26, 1526, 20, 1520), (21, 1991, 15, 1985), (26, 1406, 20, 1400), (15, 1215, 30, 1230)]
Y = []; V = []
for x1, n1, x0, n0 in tab:
    a, b, c, d = x1, n1 - x1, x0, n0 - x0
    Y.append(math.log(a * d / (b * c))); V.append(1/a + 1/b + 1/c + 1/d)
Y = np.array(Y); V = np.array(V); w = 1 / V
th = (w * Y).sum() / w.sum(); Q = (w * (Y - th)**2).sum()
print("Y=", Y.round(3), "V=", V.round(4), f"theta={th:.4f} Q={Q:.3f} I2={(Q-3)/Q:.3f}")
print("I2 at Q=7.15:", (7.15 - 3) / 7.15)

hdr("2022 医薬 問2：マッチドペア")
a11, a12, a21, a22 = 442, 662, 2632, 1477399   # 行=運転者(死亡,生存) 列=同乗者(死亡,生存)
N = a11 + a12 + a21 + a22
pd = (a11 + a12) / N; pp = (a11 + a21) / N
print(f"risk 運転者={pd:.6f} 同乗者={pp:.6f} RR={pp/pd:.3f} OR={pp/(1-pp)/(pd/(1-pd)):.3f}")
# MH: 各ペア n=m=1, N=2. RR_MH = sum A/2 / sum B/2 = (#同乗者死亡)/(#運転者死亡)
print("RR_MH=", (a11 + a21) / (a11 + a12), "OR_MH=", a21 / a12)

hdr("2024 医薬 問3：Rubin のルール")
obs = [(28, 22, .06), (30, 23, .07), (29, 21, .08)]
vs = []
for t, c_, d in obs:
    p1, p0 = t / 100, c_ / 100
    v = p1 * (1 - p1) / 100 + p0 * (1 - p0) / 100; vs.append(v)
    print(f"diff={p1-p0:.2f} (表は {d}) var={v:.6f}")
th = np.array([(t - c_) / 100 for t, c_, _ in obs])
W = np.mean(vs); B = th.var(ddof=1); print(f"W={W:.6f} B={B:.6f} T={W+(1+1/3)*B:.6f}")
tbl = np.array([[30, 70], [10, 90]]); chi2 = stats.chi2_contingency(tbl, correction=False)[0]
print("欠測と群の chi2 =", chi2)

hdr("2025 医薬 問2：ポアソン率と Gamma-Poisson")
yA, yB, TA, TB = 4, 14, 2, 8
th = (yA + yB) / (TA + TB); print("MLE=", th)
z = (yA / TA - yB / TB) / math.sqrt(yA / TA**2 + yB / TB**2); print("Z=", z)
a, b = 1 + yA + yB, 1 + TA + TB; print(f"事後 Ga(shape={a}, rate={b}), 平均={a/b:.4f}")
TC = 5; p = b / (b + TC); print(f"事後予測 NB(r={a}, p={p:.4f}) 平均={a*(1-p)/p:.4f} vs MLE予測={TC*th}")
# 数値積分で NB を確認
from scipy.special import gammaln
for k in range(3):
    lp = gammaln(a + k) - gammaln(a) - gammaln(k + 1) + a * math.log(p) + k * math.log(1 - p)
    f = lambda t: stats.poisson.pmf(k, TC * t) * stats.gamma.pdf(t, a, scale=1 / b)
    from scipy.integrate import quad
    print(k, math.exp(lp), quad(f, 0, 50)[0])

hdr("2019 医薬 問1：KM・NA・RMST")
t = [10, 13, 18, 19, 23]; cens = [0, 0, 1, 0, 1]
lam = 3 / sum(t); print("lambda hat=", lam)
tau = 20
rmst = (1 - math.exp(-lam * tau)) / lam
EX2 = 2 * (1 - math.exp(-lam * tau) * (1 + lam * tau)) / lam**2
print(f"RMST={rmst:.4f}, Var X(tau)={EX2 - rmst**2:.4f}")
