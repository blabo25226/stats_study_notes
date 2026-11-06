"""ミニ版の例題の数値を検算する（python check_mini.py）。"""
import math

from scipy import stats
from scipy.optimize import brentq, minimize_scalar
from scipy.stats import multivariate_normal


def km(times, ev):
    """ev: 1=イベント 0=打ち切り。同時刻はイベント先（打ち切りはリスク集合に残す）。"""
    out, S = [], 1.0
    for t in sorted(set(t for t, e in zip(times, ev) if e)):
        n = sum(1 for x in times if x >= t)
        d = sum(1 for x, e in zip(times, ev) if x == t and e)
        S *= 1 - d / n
        out.append((t, n, d, S))
    return out


print("== 例題1 打ち切り尤度")
t = [3, 6, 8, 12, 15, 16]
dl = [1, 0, 1, 1, 0, 1]
d, W = sum(dl), sum(t)
lam = d / W
print(" d,W,lam", d, W, lam, "SE", lam / math.sqrt(d))
print(" CI log", math.log(lam) - 1.96 / math.sqrt(d), math.log(lam) + 1.96 / math.sqrt(d))
print(" CI lam", math.exp(math.log(lam) - 1.96 / math.sqrt(d)), math.exp(math.log(lam) + 1.96 / math.sqrt(d)))
print(" median", math.log(2) / lam)
d1, W1, d2, W2 = 30, 600, 45, 500
l1, l2 = d1 / W1, d2 / W2
lhr = math.log(l1 / l2)
se = math.sqrt(1 / d1 + 1 / d2)
print(" l1,l2,HR,logHR,se,Z,p", l1, l2, l1 / l2, lhr, se, lhr / se, 2 * stats.norm.sf(abs(lhr / se)))
print(" CI", math.exp(lhr - 1.96 * se), math.exp(lhr + 1.96 * se), lhr - 1.96 * se, lhr + 1.96 * se)
r = 2 * (1.96 + 0.84) ** 2 / math.log(0.7) ** 2
print(" r", r, "log0.7", math.log(0.7))

print("== 例題2 ログランク")
g1 = [(3, 0), (6, 1), (8, 0), (10, 1), (12, 1)]
g2 = [(1, 1), (2, 1), (4, 1), (5, 0), (7, 1)]
allv = [(x, e, 1) for x, e in g1] + [(x, e, 2) for x, e in g2]
U = V = E = 0
for tt in sorted(set(x for x, e, g in allv if e)):
    n1 = sum(1 for x, e, g in allv if g == 1 and x >= tt)
    n2 = sum(1 for x, e, g in allv if g == 2 and x >= tt)
    n = n1 + n2
    dj = sum(1 for x, e, g in allv if x == tt and e)
    d1j = sum(1 for x, e, g in allv if x == tt and e and g == 1)
    Ej = dj * n1 / n
    Vj = dj * n1 * n2 * (n - dj) / (n ** 2 * (n - 1)) if n > 1 else 0
    print("  ", tt, n1, n2, n, d1j, dj, round(Ej, 4), round(Vj, 4))
    U += d1j - Ej
    V += Vj
    E += Ej
print(" O1=3 E1", E, "U", U, "V", V, "chi2", U * U / V, "sqrt", math.sqrt(U * U / V), "p", stats.chi2.sf(U * U / V, 1))
print(" Q(2.09)", stats.norm.sf(2.09))


print("== 例題3 Cox")
def logL(b):
    eb = math.exp(b)
    return ((b - math.log(5 + 5 * eb)) + (b - math.log(5 + 4 * eb)) + (b - math.log(4 + 3 * eb))
            - math.log(4 + eb) + (b - math.log(3 + eb)) - math.log(2))


res = minimize_scalar(lambda b: -logL(b), bounds=(-5, 10), method="bounded")
print(" bhat", res.x, "HR", math.exp(res.x))
b, se = -0.35, 0.15
print(" HR", math.exp(b), "CI", math.exp(b - 1.96 * se), math.exp(b + 1.96 * se), b - 1.96 * se, b + 1.96 * se, "Z", b / se)

print("== 例題4 KM")
tt = [8, 11, 11, 11, 17, 22]
ev = [1, 1, 1, 0, 1, 0]
H = 0
for (x, n, dd, S) in km(tt, ev):
    H += dd / n
    print("  ", x, n, dd, round(S, 4), "NA H", round(H, 4), "S~", round(math.exp(-H), 4))
print(" Greenwood(11)", 0.5 ** 2 * (1 / 30 + 2 / 15), math.sqrt(0.5 ** 2 * (1 / 30 + 2 / 15)))

print("== 例題5 競合リスク")
data = [(3, 2), (5, 1), (7, 0), (9, 1), (10, 2), (12, 1), (14, 0), (16, 1)]
S1 = 1
for x in sorted(set(x for x, j in data if j == 1)):
    n = sum(1 for y, j in data if y >= x)
    S1 *= 1 - 1 / n
    print("  1-KM", x, n, round(S1, 4), round(1 - S1, 4))
S = 1
F = {1: 0, 2: 0}
for x in sorted(set(x for x, j in data if j)):
    n = sum(1 for y, j in data if y >= x)
    jj = [j for y, j in data if y == x and j][0]
    F[jj] += S / n
    S *= 1 - 1 / n
    print("  AJ", x, n, jj, round(S, 4), round(F[1], 4), round(F[2], 4))
print(" const F1(10)", 0.03 / 0.1 * (1 - math.exp(-1)), "1-e^-0.3", 1 - math.exp(-0.3), "x=1", 0.03 / 0.2 * (1 - math.exp(-2)))

print("== 例題6 McNemar")
n11, n10, n01, n00 = 150, 34, 18, 48
N = n11 + n10 + n01 + n00
W_ = (n10 - n01) ** 2 / (n10 + n01)
dh = (n10 - n01) / N
v = (n10 + n01) / N ** 2 - (n10 - n01) ** 2 / N ** 3
G2 = 2 * (n10 * math.log(2 * n10 / (n10 + n01)) + n01 * math.log(2 * n01 / (n10 + n01)))
print(" N", N, "W", W_, "p", stats.chi2.sf(W_, 1), "dh", dh, "v", v, "se", math.sqrt(v), "CI", dh - 1.96 * math.sqrt(v), dh + 1.96 * math.sqrt(v))
print(" G2", G2, "logs", math.log(68 / 52), math.log(36 / 52), "z", (n10 - 26) / math.sqrt(52 / 4), "condOR", n10 / n01)
print(" pX", (n11 + n10) / N, "pY", (n11 + n01) / N)


print("== 例題7-1 Cochran")
def coch(a, b, c, d):
    n1, n2, m1, m0 = a + b, c + d, a + c, b + d
    Nn = n1 + n2
    return (n2 * a - n1 * c) / Nn, n1 * n2 * m1 * m0 / Nn ** 3, n1 * n2 * m1 * m0 / (Nn ** 2 * (Nn - 1))


y, vv, vh = coch(60, 70, 66, 64)
print(" crude Y,V,X", y, vv, y * y / vv, "OR", 60 * 64 / (70 * 66))
lor = math.log(60 * 64 / (70 * 66))
sv = 1 / 60 + 1 / 70 + 1 / 66 + 1 / 64
print(" logOR", lor, "var", sv, "se", math.sqrt(sv), "CI", math.exp(lor - 1.96 * math.sqrt(sv)), math.exp(lor + 1.96 * math.sqrt(sv)),
      lor - 1.96 * math.sqrt(sv), lor + 1.96 * math.sqrt(sv))
y1, v1, h1 = coch(24, 6, 60, 40)
y2, v2, h2 = coch(36, 64, 6, 24)
print(" strata", y1, v1, y2, v2, "XC", (y1 + y2) ** 2 / (v1 + v2), "CMH", (y1 + y2) ** 2 / (h1 + h2), "ORs", 24 * 40 / (6 * 60), 36 * 24 / (64 * 6))
print(" MH OR", (24 * 40 / 130 + 36 * 24 / 130) / (6 * 60 / 130 + 64 * 6 / 130))

print("== 例題7-2 Peto")
tabs = [(6, 4, 30, 160), (40, 50, 60, 250), (20, 30, 15, 85)]
sO = sV = num = den = 0
for a, b_, c, d_ in tabs:
    Nk = a + b_ + c + d_
    Ek = (a + b_) * (a + c) / Nk
    Vk = (a + b_) * (c + d_) * (a + c) * (b_ + d_) / (Nk ** 2 * (Nk - 1))
    print("   N,E,V,(O-E)/V,exp,OR", Nk, round(Ek, 4), round(Vk, 4), round((a - Ek) / Vk, 4), round(math.exp((a - Ek) / Vk), 3), round(a * d_ / (b_ * c), 3))
    sO += a - Ek
    sV += Vk
    num += a * d_ / Nk
    den += b_ * c / Nk
bb = sO / sV
print(" sum O-E", sO, "sumV", sV, "beta", bb, "psi", math.exp(bb), "se", 1 / math.sqrt(sV))
print(" CI", bb - 1.96 / math.sqrt(sV), bb + 1.96 / math.sqrt(sV), math.exp(bb - 1.96 / math.sqrt(sV)), math.exp(bb + 1.96 / math.sqrt(sV)), "MH", num / den)

print("== 例題7-3 マッチドペア")
A11, A12, A21, A22 = 300, 500, 1800, 997400
Np = A11 + A12 + A21 + A22
dd_, pd_ = A11 + A12, A11 + A21
print(" N", Np, "risk drv", dd_ / Np, "pas", pd_ / Np, "RRc", pd_ / dd_, "ORc", pd_ * (Np - dd_) / (dd_ * (Np - pd_)), "ORmh", A21 / A12)
B11, B12, B21 = 4000, 8000, 8200
rrb = (B11 + B21) / (B11 + B12)
print(" RRb", rrb, "ratio", (pd_ / dd_) / rrb)

print("== 例題8 FWER")
print(" m3 indep", 1 - 0.95 ** 3, "bonf", 1 - (1 - 0.05 / 3) ** 3, "sidak", 1 - 0.95 ** (1 / 3))
za = stats.norm.isf(0.025)
rho = 0.5
phi = multivariate_normal(mean=[0, 0], cov=[[1, rho], [rho, 1]]).cdf([-za, -za])
print(" rho", rho, "phi", phi, "FWER", 2 * 0.025 - phi, "FWER0", 1 - 0.975 ** 2)
print(" dunnett n0=40 nj=20", math.sqrt(20 * 20 / (60 * 60)), "equal", 0.5)

print("== 例題9 alpha spending")
a = lambda t: 0.025 * t ** 2  # noqa: E731
z1 = stats.norm.isf(a(0.5))
print(" a(.5)", a(0.5), "z1", z1, "final", 0.025 - a(0.5), "a(.8)-a(.5)", a(0.8) - a(0.5), "final2", 0.025 - a(0.8))
rho = math.sqrt(0.5)
mvn = multivariate_normal(mean=[0, 0], cov=[[1, rho], [rho, 1]])
f = lambda c: (stats.norm.cdf(z1) - mvn.cdf([z1, c])) - (0.025 - a(0.5))  # noqa: E731
print(" c2", brentq(f, 1.0, 3.0), "nominal", stats.norm.isf(0.025))
print(" naive 2 looks at 1.96", 1 - mvn.cdf([1.96, 1.96]))
print(" Q(2.50)", stats.norm.sf(2.50), "Q(2.49)", stats.norm.sf(2.49))

print("== 例題10 BE")
for nm, n, m, s in [("A", 16, 0.08, 0.20), ("B", 12, -0.12, 0.30)]:
    tq = stats.t.isf(0.05, n - 1)
    h = tq * s / math.sqrt(n)
    print("  ", nm, "t", tq, "half", h, "CI", m - h, m + h, "exp", math.exp(m - h), math.exp(m + h),
          "T1", (m + math.log(1.25)) / (s / math.sqrt(n)), "T2", (m - math.log(1.25)) / (s / math.sqrt(n)))
print(" CV0.5 sigma2", math.log(1.25))
