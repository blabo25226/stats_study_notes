---
test-category: 統計数理
stats-category: 標本分布
tags:
  - t分布
created: 2026-09-30
updated: 2026-09-30
---

# t分布

## 定義

$X_1,\dots,X_n,\ i.i.d.\sim\mathcal N(\mu,\sigma^2)$ とし、標本平均 $\overline X$、不偏分散 $V^2=(n-1)^{-1}\sum_{i=1}^n(X_i-\overline X)^2$ に対して
$$
T=\frac{\sqrt n(\overline X-\mu)}{V}=\frac{Z}{\sqrt{U/(n-1)}},\quad Z=\frac{\sqrt n(\overline X-\mu)}{\sigma}\sim\mathcal N(0,1),\ U=\frac{(n-1)V^2}{\sigma^2}\sim\chi^2_{n-1}
$$
の分布を自由度 $n-1$ の $t$ 分布 $t_{n-1}$ という。一般に、$Z\sim\mathcal N(0,1)$ と $U\sim\chi^2_k$ が独立なら $Z/\sqrt{U/k}\sim t_k$。

## 要点

- $\overline X$ と $V^2$ は独立（[[標本平均]]）。
- 0を中心に対称で、[[正規分布]]より裾が厚い。自由度が大きいと標準正規分布に近づく。自由度 $1$ はコーシー分布。
- $T^2\sim F_{1,k}$（[[F分布]]）。

## 関連

- [[正規分布]]
- [[カイ二乗分布]]
- [[F分布]]
- [[標本平均]]

## 使われる問題

![[概念別問題一覧.base]]
