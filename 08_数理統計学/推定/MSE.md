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

## 分解の証明とオリジナル演習

$T$ は母数 $\theta$ の推定量とし、$b=E_\theta T-\theta$ とおく。

$
\begin{aligned}
E_\theta[(T-\theta)^2]
&=E_\theta[(T-E_\theta T+b)^2]\\
&=\operatorname{Var}_\theta(T)+b^2
\end{aligned}
$

となる。交差項は $E_\theta[T-E_\theta T]=0$ で消える。**不偏でも分散が大きければMSEは大きい**ので、推定量の選択には分散との比較が必要。

**問題** $X_1,\ldots,X_n\sim N(\mu,\sigma^2)$、$\mu$ は既知とし、$\hat v_a=a n^{-1}\sum_i(X_i-\mu)^2$ で $\sigma^2$ を推定する（$a$ は定数）。$\hat v_a$ のMSEを求め、最小化する $a$ を示せ。

> [!success]- 解答
>
> $\sum_i(X_i-\mu)^2/\sigma^2\sim\chi_n^2$ より $E[\hat v_a]=a\sigma^2$、$\operatorname{Var}(\hat v_a)=2a^2\sigma^4/n$。
>
> $
> \mathrm{MSE}(\hat v_a)=\sigma^4\left[\frac{2a^2}{n}+(a-1)^2\right].
> $
>
> $a$ で微分して $4a/n+2(a-1)=0$ より $a^*=n/(n+2)$。このMSE最小推定量はバイアスがあり、不偏推定量とは一致しない。

## 関連

- [[bias]]
- [[点推定]]
- [[不偏推定量]]
- [[一致性]]
- [[クラメール・ラオの不等式]]

## 使われる問題

![[概念別問題一覧.base]]
