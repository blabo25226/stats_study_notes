---
test-category: 統計数理
stats-category: 推定
tags:
  - 平均二乗誤差
  - バイアス分散分解
created: 2026-10-22
updated: 2026-10-22
---

# MSE

## 定義

推定量 $\hat\theta$ の平均二乗誤差（mean squared error）を
$$
\mathrm{MSE}_\theta(\hat\theta)=E_\theta\bigl[(\hat\theta-\theta)^2\bigr]
$$
と定める。

## 要点

- バイアス・分散分解：
$$
\mathrm{MSE}=\mathrm{Var}(\hat\theta)+\bigl\{\mathrm{Bias}(\hat\theta)\bigr\}^2
$$
導出：$\hat\theta-\theta=(\hat\theta-E\hat\theta)+(E\hat\theta-\theta)$ を二乗して期待値をとると、交差項は $2(E\hat\theta-\theta)\,E[\hat\theta-E\hat\theta]=0$。
- 不偏推定量では $\mathrm{MSE}=\mathrm{Var}(\hat\theta)$。
- $\mathrm{MSE}\to0$（平均二乗収束）なら $\hat\theta\to\theta$ が確率収束するので[[一致性]]をもつ（チェビシェフの不等式 $P(|\hat\theta-\theta|>\varepsilon)\le\mathrm{MSE}/\varepsilon^2$、[[チェビシェフの不等式]]）。
- 不偏推定量の分散の下限は[[クラメール・ラオの不等式]]。バイアス $b(\theta)$ をもつ推定量では $\mathrm{Var}(\hat\theta)\ge\dfrac{\{1+b'(\theta)\}^2}{nI(\theta)}$（[[フィッシャー情報量]]）。
- すべての $\theta$ で MSE を最小にする推定量は一般に存在しない。不偏推定量に限れば一様最小分散不偏推定量（UMVUE）を考える（[[完備十分統計量]]）。

## 例：正規分布の分散推定

$X_i\sim N(\mu,\sigma^2)$ i.i.d. で $W=\sum(X_i-\bar X)^2/\sigma^2\sim\chi^2_{n-1}$（[[カイ二乗分布]]）。$E[W]=n-1$、$\mathrm{Var}(W)=2(n-1)$。$\hat\sigma_c^2=c\sum(X_i-\bar X)^2$ の MSE は
$$
\sigma^4E[(cW-1)^2]=\sigma^4\bigl\{c^2(n-1)(n+1)-2c(n-1)+1\bigr\}
$$
（$E[W^2]=2(n-1)+(n-1)^2=(n-1)(n+1)$）。

| $c$ | 推定量 | MSE |
|---|---|---|
| $1/(n-1)$ | 不偏分散 $S^2$ | $2\sigma^4/(n-1)$ |
| $1/n$ | 最尤推定量 | $(2n-1)\sigma^4/n^2$ |
| $1/(n+1)$ | MSE 最小 | $2\sigma^4/(n+1)$ |

$c$ について二次式を最小化すると $c=1/(n+1)$。分散の小さい $2\sigma^4/(n+1)$ のほうが、バイアスがあっても不偏推定量より MSE は小さい。$n=5$ で比べると、不偏が $2/4=0.5$、最尤が $9/25=0.36$、最小が $2/6\approx0.33$（単位 $\sigma^4$）。

## 関連

- [[bias]]
- [[点推定]]
- [[不偏推定量]]
- [[一致性]]
- [[クラメール・ラオの不等式]]

## 使われる問題

![[概念別問題一覧.base]]
