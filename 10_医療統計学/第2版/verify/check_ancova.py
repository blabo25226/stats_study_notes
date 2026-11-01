"""例題8-3・ANCOVA 節の検算：3推定量の分散と，傾き推定時の分散の補正係数 (2n-3)/(2n-4)．"""
import numpy as np

rng = np.random.default_rng(2)
sigma, rho, n, reps = 10.0, 0.6, 20, 100000
cov = sigma**2 * np.array([[1, rho], [rho, 1]])
d, c, a, a_est = [], [], [], []
for _ in range(reps):
    T = rng.multivariate_normal([50, 50], cov, n)
    C = rng.multivariate_normal([50, 50], cov, n)
    yT, xT, yC, xC = T[:, 1].mean(), T[:, 0].mean(), C[:, 1].mean(), C[:, 0].mean()
    d.append(yT - yC)
    c.append((yT - xT) - (yC - xC))
    a.append((yT - yC) - rho * (xT - xC))
    # 群内でプールした傾き
    sxy = ((T[:, 0] - xT) * (T[:, 1] - yT)).sum() + ((C[:, 0] - xC) * (C[:, 1] - yC)).sum()
    sxx = ((T[:, 0] - xT) ** 2).sum() + ((C[:, 0] - xC) ** 2).sum()
    a_est.append((yT - yC) - sxy / sxx * (xT - xC))
v = 2 * sigma**2 / n
print("Var d  sim/theory:", np.var(d), v)
print("Var c  sim/theory:", np.var(c), v * 2 * (1 - rho))
print("Var a  sim/theory:", np.var(a), v * (1 - rho**2))
print("Var a(傾き推定) sim/theory:", np.var(a_est), v * (1 - rho**2) * (2 * n - 3) / (2 * n - 4))

# 例題8-3
s2, r, n = 100, 0.6, 50
print("例題8-3 分散:", 2 * s2 / n, 4 * s2 * (1 - r) / n, 2 * s2 * (1 - r**2) / n)
print("推定値:", 45 - 48, (45 - 52) - (48 - 50), (45 - 48) - r * (52 - 50))
