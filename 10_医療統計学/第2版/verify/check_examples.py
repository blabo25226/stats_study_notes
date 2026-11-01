"""第2版で新設・改訂した例題の数値検算．"""
import math
import numpy as np

def hdr(s): print("\n=== " + s)

def meta(y, v, label):
    y = np.array(y, float); v = np.array(v, float); w = 1 / v
    th = (w * y).sum() / w.sum(); se = 1 / math.sqrt(w.sum())
    Q = (w * (y - th)**2).sum(); K = len(y)
    c = w.sum() - (w**2).sum() / w.sum(); t2 = max(0, (Q - (K - 1)) / c)
    ws = 1 / (v + t2); mu = (ws * y).sum() / ws.sum(); se2 = 1 / math.sqrt(ws.sum())
    print(f"[{label}] w={w.round(3)} sum w={w.sum():.3f} sum wy={(w*y).sum():.4f}")
    print(f"  FE={th:.4f} SE={se:.4f} CI=({th-1.96*se:.3f},{th+1.96*se:.3f}) OR CI=({math.exp(th-1.96*se):.3f},{math.exp(th+1.96*se):.3f})")
    print(f"  Q terms={(w*(y-th)**2).round(3)} Q={Q:.3f} I2={(Q-K+1)/Q:.3f} sum w2={(w**2).sum():.2f} c={c:.3f} tau2={t2:.4f}")
    print(f"  w*={ws.round(3)} sum={ws.sum():.3f} sum w*y={(ws*y).sum():.4f} RE={mu:.4f} SE={se2:.4f} CI=({mu-1.96*se2:.3f},{mu+1.96*se2:.3f})")
    return th, t2

hdr("例題18-1（固定効果・Q・DL・変量効果）")
meta([-0.40, -0.05, -0.60, 0.15], [0.04, 0.02, 0.09, 0.03], "18-1")

hdr("例題18-2（最適重み）")
v = np.array([0.01, 0.04, 0.04])
print("等重み Var=", v.sum() / 9, " 逆分散 Var=", 1 / (1 / v).sum(), " 比=", (1 / (1 / v).sum()) / (v.sum() / 9))
# 等分散 K=5, sigma2=0.05, Q=12
print("DL tau2=", 0.05 * (12 - 4) / 4, " I2=", (12 - 4) / 12)

hdr("例題07-2（層別 2x2：粗 OR・MH・Peto・CMH・Woolf・RBG 分散）")
def strat(T):
    R = S = PR = PS_QR = QS = 0.0; sOE = sV = 0.0; th = []; wv = []
    for a, b, c, d in T:
        n = a + b + c + d
        E = (a + b) * (a + c) / n; V = (a + b) * (c + d) * (a + c) * (b + d) / (n**2 * (n - 1))
        r, s_ = a * d / n, b * c / n; P, Qk = (a + d) / n, (b + c) / n
        R += r; S += s_; PR += P * r; PS_QR += P * s_ + Qk * r; QS += Qk * s_
        sOE += a - E; sV += V
        v = 1/a + 1/b + 1/c + 1/d; th.append(math.log(a * d / (b * c))); wv.append(1 / v)
        print(f"  n={n} OR={a*d/(b*c):.3f} ad/n={r:.4f} bc/n={s_:.4f} E={E:.3f} V={V:.4f} logOR={math.log(a*d/(b*c)):.4f} v={v:.4f}")
    mh = R / S
    var = PR / (2 * R**2) + PS_QR / (2 * R * S) + QS / (2 * S**2)
    A = np.array(T).sum(0)
    print(f"  粗OR={A[0]*A[3]/(A[1]*A[2]):.3f} MH={mh:.4f} logMH={math.log(mh):.4f} RBG var={var:.5f} se={math.sqrt(var):.4f}"
          f" CI=({mh*math.exp(-1.96*math.sqrt(var)):.3f},{mh*math.exp(1.96*math.sqrt(var)):.3f})")
    print(f"  sum(O-E)={sOE:.3f} sumV={sV:.4f} CMH={sOE**2/sV:.3f} Peto OR={math.exp(sOE/sV):.3f}")
    th = np.array(th); wv = np.array(wv); tw = (wv * th).sum() / wv.sum()
    print(f"  Woolf: w={wv.round(3)} theta_w={tw:.4f} OR={math.exp(tw):.3f} Q={(wv*(th-tw)**2).sum():.3f}")
    return mh, var
strat([(30, 70, 10, 70), (60, 60, 20, 40), (90, 30, 20, 10)])
hdr("2017 問4 の MH と RBG")
strat([(5, 35, 5, 270), (67, 56, 55, 277), (24, 18, 44, 119)])

hdr("RBG 分散のシミュレーション確認（層別、共通 OR=2）")
rng = np.random.default_rng(1)
ests = []; vars_ = []
n1 = [100, 120, 120]; n0 = [80, 60, 30]; p0 = [0.125, 0.33, 0.5]
for _ in range(20000):
    T = []
    for k in range(3):
        o0 = p0[k] / (1 - p0[k]); p1 = 2 * o0 / (1 + 2 * o0)
        a = rng.binomial(n1[k], p1); c = rng.binomial(n0[k], p0[k])
        T.append((a, n1[k] - a, c, n0[k] - c))
    R = S = PR = PSQR = QS = 0
    for a, b, c, d in T:
        n = a + b + c + d; r, s_ = a * d / n, b * c / n; P, Qk = (a + d) / n, (b + c) / n
        R += r; S += s_; PR += P * r; PSQR += P * s_ + Qk * r; QS += Qk * s_
    ests.append(math.log(R / S)); vars_.append(PR / (2 * R**2) + PSQR / (2 * R * S) + QS / (2 * S**2))
print("  sim mean logMH=", np.mean(ests), "(log2=", math.log(2), ") sim var=", np.var(ests), " mean RBG=", np.mean(vars_))
