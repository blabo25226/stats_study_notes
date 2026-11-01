"""例題9-4（NA・RMST）と例題10-5（累積発生関数）の検算．"""
import math

# 例題9-2 のデータ（+ は打ち切り）
data = [(3, 1), (5, 0), (6, 1), (6, 1), (8, 0), (10, 1), (12, 0), (15, 1)]
times = sorted({t for t, e in data if e})
S_km, H, rows = 1.0, 0.0, []
for t in times:
    n = sum(1 for u, _ in data if u >= t); d = sum(1 for u, e in data if u == t and e)
    S_km *= 1 - d / n; H += d / n
    rows.append((t, n, d, S_km, H, math.exp(-H)))
    print(f"t={t} n={n} d={d} KM={S_km:.4f} H_NA={H:.4f} S_NA={math.exp(-H):.4f}")
var_H = sum(d / n**2 for t, n, d, *_ in rows if t <= 10)
print("Var H_NA(10)=", var_H)


def rmst_km(tau):
    area, prev_t, prev_s = 0.0, 0.0, 1.0
    for t, n, d, s, *_ in rows:
        if t > tau:
            break
        area += prev_s * (t - prev_t); prev_t, prev_s = t, s
    return area + prev_s * (tau - prev_t)


print("RMST_KM(12)=", rmst_km(12))
d = sum(e for _, e in data); W = sum(t for t, _ in data); lam = d / W
print("lambda=", lam, "lam*12=", lam * 12, "RMST_exp(12)=", (1 - math.exp(-lam * 12)) / lam)

# 例題10-5：競合リスク（cause 1, 2, 0=打ち切り）
cr = [(2, 1), (3, 2), (4, 0), (5, 1), (6, 2), (7, 1), (8, 0), (9, 1), (10, 2), (12, 0)]
S, F1, F2, S1km = 1.0, 0.0, 0.0, 1.0
for t in sorted({t for t, c in cr if c}):
    n = sum(1 for u, _ in cr if u >= t)
    d1 = sum(1 for u, c in cr if u == t and c == 1); d2 = sum(1 for u, c in cr if u == t and c == 2)
    F1 += S * d1 / n; F2 += S * d2 / n
    S *= 1 - (d1 + d2) / n; S1km *= 1 - d1 / n
    print(f"t={t} n={n} d1={d1} d2={d2} S={S:.4f} F1={F1:.4f} F2={F2:.4f} sum={S+F1+F2:.4f} 1-KM1={1-S1km:.4f}")
