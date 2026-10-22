---
test-category: 統計数理
stats-category: 推定
tags:
  - バイアス
  - 偏り
  - 不偏性
created: 2026-10-22
updated: 2026-10-22
---

# bias

## 定義

推定量 $\hat\theta$ のバイアス（偏り）を
$$
\mathrm{Bias}_\theta(\hat\theta)=E_\theta[\hat\theta]-\theta
$$
と定める。すべての $\theta$ でバイアスが $0$ のとき[[不偏推定量]]。$n\to\infty$ でバイアスが $0$ に近づくとき漸近不偏という。

## 要点

- 推定量の誤差は、系統的なずれ（バイアス）と、ばらつき（分散）に分けて考える。[[MSE]] $=\mathrm{Var}(\hat\theta)+\mathrm{Bias}(\hat\theta)^2$。
- バイアスが小さくても、分散が大きければ推定は悪い。逆に、少しバイアスを許して分散を大きく減らすほうが MSE が小さくなることがある（[[MSE]]の例）。
- 不偏性は非線形変換で保たれない。$g(\hat\theta)$ のバイアスは、2次のテイラー展開
$$
E[g(\hat\theta)]\approx g(\theta)+\tfrac12g''(\theta)\mathrm{Var}(\hat\theta)
$$
で評価できる（[[デルタ法]]の2次の項）。$\hat\theta$ が不偏でも $\mathrm{Var}(\hat\theta)=O(1/n)$ なので、バイアスは $O(1/n)$。
- [[最尤推定量]]は一般にバイアスをもつが、$O(1/n)$ で、標準偏差 $O(1/\sqrt n)$ より速く $0$ に近づく。

## 例

- 正規母集団の分散：$\hat\sigma^2=\dfrac1n\sum(X_i-\bar X)^2$ は $E[\hat\sigma^2]=\dfrac{n-1}{n}\sigma^2$ なのでバイアスは $-\sigma^2/n$。不偏分散 $S^2$ は $\dfrac{n}{n-1}$ 倍して不偏にしたもの。
- $U(0,\theta)$ の最大値 $X_{(n)}$：$E[X_{(n)}]=\dfrac{n}{n+1}\theta$ なのでバイアスは $-\dfrac{\theta}{n+1}$（常に過小）。$\dfrac{n+1}{n}X_{(n)}$ にすると不偏（[[一様分布]]、[[順序統計量]]）。
- 指数分布 $\mathrm{Ex}(\lambda)$ の最尤推定量 $\hat\lambda=n/\sum X_i$：$\sum X_i\sim\mathrm{Ga}(n,1/\lambda)$ で $E[1/\sum X_i]=\lambda/(n-1)$（$n\ge2$）なので $E[\hat\lambda]=\dfrac{n}{n-1}\lambda$、バイアスは $\dfrac{\lambda}{n-1}$。$\dfrac{n-1}{n}\hat\lambda=\dfrac{n-1}{\sum X_i}$ が不偏（[[指数分布]]、[[ガンマ分布]]）。

## 関連

- [[不偏推定量]]
- [[MSE]]
- [[点推定]]
- [[最尤推定量]]
- [[デルタ法]]

## 使われる問題

![[概念別問題一覧.base]]
