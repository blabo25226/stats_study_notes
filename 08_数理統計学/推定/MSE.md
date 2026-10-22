---
test-category: 統計数理
stats-category: 推定
tags:
  - 平均二乗誤差
  - バイアス分散分解
  - ミニマックス推定量
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

## リスク一定の推定量とミニマックス性

推定量 $T$ のリスク（ここでは MSE）$R(\theta,T)$ の**最大値** $\sup_\theta R(\theta,T)$ を最小にする推定量をミニマックス推定量という。

**ミニマックスの十分条件** ある事前分布に対するベイズ推定量 $T_\pi$ のリスクが $\theta$ によらず一定 $r$ なら、$T_\pi$ はミニマックス。任意の $T$ について
$$
\sup_\theta R(\theta,T)\ \ge\ \int R(\theta,T)\pi(\theta)d\theta\ \ge\ \int R(\theta,T_\pi)\pi(\theta)d\theta=r=\sup_\theta R(\theta,T_\pi)
$$
（2番目の不等号はベイズ推定量がベイズリスクを最小にすることによる。[[ベイズ推定と損失関数]]）。

**ベルヌーイでの構成**（2024数理 問3 の題材） $X_i\overset{\rm iid}{\sim}\operatorname{Bern}(\theta)$、$S=\sum X_i$、$T=aS+b$ とする。
$$
\mathrm{MSE}=a^2n\theta(1-\theta)+(an\theta+b-\theta)^2
=\{(an-1)^2-a^2n\}\theta^2+\{a^2n+2b(an-1)\}\theta+b^2.
$$
$\theta$ によらないためには $\theta^2,\theta$ の係数が0。$(an-1)^2=a^2n$ で縮小側（$an<1$）をとると $1-an=a\sqrt n$、よって
$$
a=\frac1{n+\sqrt n},\qquad b=\frac{a^2n}{2(1-an)}=\frac{\sqrt n}{2(n+\sqrt n)},\qquad
\boxed{T^*=\frac{S+\sqrt n/2}{n+\sqrt n}},\qquad \mathrm{MSE}=b^2=\frac1{4(1+\sqrt n)^2}.
$$
$T^*$ は事前分布 $\operatorname{Beta}(\sqrt n/2,\sqrt n/2)$ の事後平均でもあるので、上の十分条件からミニマックス。

**MLEとの比較** $\hat\theta=S/n$ の MSE は $\theta(1-\theta)/n=\{1/4-(\theta-1/2)^2\}/n$。$T^*$ の方が小さいのは
$$
\left|\theta-\tfrac12\right|<\frac{\sqrt{1+2\sqrt n}}{2(1+\sqrt n)}
$$
のとき（$1/4-(\theta-1/2)^2>n/\{4(1+\sqrt n)^2\}$ を整理）。$\theta$ が $0,1$ に近いと MLE の方が良い。最大リスクで比べればミニマックス推定量が勝つが、すべての $\theta$ で勝つわけではない。

**問題1** $n=16$ のとき、$T^*$ の MSE、MLE の最大 MSE、$T^*$ の方が MSE の小さい $\theta$ の範囲を求めよ。

> [!success]- 解答
>
> $\sqrt n=4$。$T^*=(S+2)/20$、MSE $=1/(4\cdot25)=0.01$。MLE の MSE の最大は $\theta=1/2$ で $1/64=0.0156$。範囲は $|\theta-1/2|<\sqrt9/(2\cdot5)=0.3$、すなわち $0.2<\theta<0.8$。

**問題2（尺度推定量の定数）** $X_1,\dots,X_n$ が独立に平均 $\theta$ の指数分布に従う。損失 $L(d,\theta)=d/\theta+\theta/d-2$ のもとで、$d=c\bar X$ のリスクを最小にする $c$ を $n=5$ で求めよ（2019数理 問2 と同型）。

> [!success]- 解答
>
> $n\bar X/\theta\sim\operatorname{Ga}(n,1)$ より $E[\bar X/\theta]=1$、$E[\theta/\bar X]=n/(n-1)$（[[ガンマ関数]]の逆数モーメント）。リスクは
>
> $
> R(c)=c+\frac{n}{(n-1)c}-2,
> $
>
> で $\theta$ によらない。$R'(c)=0$ より $c=\sqrt{n/(n-1)}$。$n=5$ では $c=\sqrt5/2=1.118$、最小リスク $2c-2=\sqrt5-2=0.236$。損失が $d/\theta$ と $\theta/d$ について対称なので、不偏推定量（$c=1$、リスク $0.25$）は最適でない。

## 関連

- [[bias]]
- [[点推定]]
- [[不偏推定量]]
- [[一致性]]
- [[クラメール・ラオの不等式]]

## 使われる問題

![[概念別問題一覧.base]]
