"""第2版の本文・例題で使った残りの数値の検算（例題16-4，17-3，18-1〜18-3 の補足，付録G）．"""
import math
from scipy import stats

def hdr(s): print("\n=== " + s)

hdr("例題18-1 補足")
print("e^-0.119 =", math.exp(-0.119), " 重み比 FE:", 11.111 / 119.444, " RE:", 7.114 / 44.736)
print("2021問4 RR の CI:", math.exp(-0.198), math.exp(0.212))
hdr("例題18-2(2) 1/SE 重み")
c = [0.5, 0.25, 0.25]; v = [0.01, 0.04, 0.04]
print("Var =", sum(ci**2 * vi for ci, vi in zip(c, v)))
hdr("例題18-3")
t1 = (10, 90, 20, 80); t2 = (15, 185, 25, 175); t3 = (0, 20, 2, 18)
def lor(a, b, c_, d): return math.log(a * d / (b * c_)), 1/a + 1/b + 1/c_ + 1/d
(y1, v1), (y2, v2) = lor(*t1), lor(*t2)
w1, w2 = 1 / v1, 1 / v2; th = (w1 * y1 + w2 * y2) / (w1 + w2)
print(f"logOR {y1:.4f} {y2:.4f} v {v1:.4f} {v2:.4f} IV={math.exp(th):.4f}")
R = sum(a * d / (a + b + c_ + d) for a, b, c_, d in (t1, t2)); S = sum(b * c_ / (a + b + c_ + d) for a, b, c_, d in (t1, t2))
print("MH(2試験)=", R / S, " MH(3試験)=", R / (S + t3[1] * t3[2] / sum(t3)))

hdr("例題16-4")
th = [1.2, 1.0, 1.4, 1.1, 1.3]; V = [0.04, 0.05, 0.04, 0.06, 0.06]; m = 5
tb = sum(th) / m; W = sum(V) / m; B = sum((x - tb)**2 for x in th) / (m - 1); T = W + (1 + 1/m) * B
r = (1 + 1/m) * B / W; nu = (m - 1) * (1 + 1/r)**2
print(f"theta={tb} W={W} B={B} T={T} r={r} nu={nu:.2f} t={stats.t.ppf(0.975, nu):.4f} lambda={(1+1/m)*B/T}")
print("CI:", tb - stats.t.ppf(0.975, 28) * math.sqrt(T), tb + stats.t.ppf(0.975, 28) * math.sqrt(T))
p, N, M = 0.5, 80, 20
print("improper Var=", M * p * (1 - p) / (N + M)**2, " proper Var=", p * (1 - p) * (M + M**2 / N) / (N + M)**2,
      " obs var=", p * (1 - p) / N)

hdr("例題17-3")
a, b = 2 + 10, 4 + 16; Tp = 5; pp = b / (b + Tp)
print("事後平均", a / b, " 予測平均", Tp * a / b, " 予測分散", Tp * a / b + Tp**2 * a / b**2)
print("P0", pp**a, " P1", a * pp**a * (1 - pp), " NB 検算:", stats.nbinom.pmf([0, 1], a, pp))
print("尺度取り違え:", 12 / (0.25 + 16))
print("2025問2 H0 共通率で分散:", 0.25 / math.sqrt(1.8 / 2 + 1.8 / 8))

hdr("付録G")
print("P0(X>=9)", stats.binom.sf(8, 10, 0.5), " P0(X>=8)", stats.binom.sf(7, 10, 0.5), " power", stats.binom.sf(8, 10, 0.8))
ry1, ry2, r12 = 0.5, 0.1, 0.6
b1 = (ry1 - r12 * ry2) / (1 - r12**2); b2 = (ry2 - r12 * ry1) / (1 - r12**2)
print("b1,b2,R2:", b1, b2, b1 * ry1 + b2 * ry2)
