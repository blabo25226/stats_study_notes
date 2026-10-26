---
test-category: 統計数理
stats-category: 推定
tags:
  - 平均二乗誤差
  - バイアス分散分解
  - ミニマックス推定量
created: 2026-10-22
updated: 2026-10-26
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

## 分解の証明

$T$ は母数 $\theta$ の推定量とし、$b=E_\theta T-\theta$ とおく。

$
\begin{aligned}
E_\theta[(T-\theta)^2]
&=E_\theta[(T-E_\theta T+b)^2]\\
&=\operatorname{Var}_\theta(T)+b^2
\end{aligned}
$

となる。交差項は $E_\theta[T-E_\theta T]=0$ で消える。**不偏でも分散が大きければMSEは大きい**ので、推定量の選択には分散との比較が必要。

## 例題（過去問改題）

> [!note] 出典
> 2017年 統計数理 問2〔2〕〔3〕〔4〕の数値を変更（一般の $n$ を $n=4$ に固定）。最尤推定量そのものの MSE と、$cX_{\max}$ の MSE 最小化を追加。

$X_1,\dots,X_4$ は独立に $U(0,\theta)$ に従い、$X_{\max}$ を最大値とする。$\theta$ の推定量として $\theta'=2\bar X$、$\theta''=\frac54X_{\max}$、最尤推定量 $X_{\max}$ を考える。

(1) $\theta',\theta''$ が不偏であることを示し、分散を比べよ。
(2) $X_{\max}$ の MSE を求めよ。
(3) $cX_{\max}$ の形の推定量のうち MSE を最小にする $c$ と、そのときの MSE を求めよ。

> [!success]- 解答
>
> (1) $E[X]=\theta/2$ より $E[\theta']=\theta$。$P(X_{\max}\le x)=(x/\theta)^4$ から密度は $4x^3/\theta^4$（[[順序統計量]]）で
>
> $$
> E[X_{\max}]=\frac45\theta,\qquad E[X_{\max}^2]=\frac46\theta^2=\frac23\theta^2,\qquad
> \operatorname{Var}(X_{\max})=\frac23\theta^2-\frac{16}{25}\theta^2=\frac{2}{75}\theta^2.
> $$
>
> よって $E[\theta'']=\theta$。分散は $\operatorname{Var}(X)=\theta^2/12$ を使い
>
> $$
> \operatorname{Var}(\theta')=4\cdot\frac{\theta^2}{12\cdot4}=\frac{\theta^2}{12}=0.0833\,\theta^2,\qquad
> \operatorname{Var}(\theta'')=\frac{25}{16}\cdot\frac{2}{75}\theta^2=\frac{\theta^2}{24}=0.0417\,\theta^2.
> $$
>
> どちらも不偏なので MSE は分散に等しく、$\theta''$ のほうが良い。
>
> (2) バイアスは $-\theta/5$。分解 $\mathrm{MSE}=\operatorname{Var}+\mathrm{Bias}^2$ より
>
> $$
> \mathrm{MSE}(X_{\max})=\frac{2}{75}\theta^2+\frac{1}{25}\theta^2=\frac{5}{75}\theta^2=\boxed{\frac{\theta^2}{15}}=0.0667\,\theta^2.
> $$
>
> (3) $E[(cX_{\max}-\theta)^2]=\theta^2\left(\dfrac23c^2-\dfrac85c+1\right)$。$c$ で微分して $\dfrac43c-\dfrac85=0$ より $c=\boxed{6/5}$。最小値は
>
> $$
> \theta^2\left(\frac23\cdot\frac{36}{25}-\frac85\cdot\frac65+1\right)=\theta^2\left(\frac{24}{25}-\frac{48}{25}+1\right)=\boxed{\frac{\theta^2}{25}}=0.04\,\theta^2.
> $$
>
> 不偏な $\theta''=\frac54X_{\max}$（$0.0417\theta^2$）よりわずかに小さい。少し大きめに補正して偏りを残すほうが MSE は小さくなる（一般の $n$ では $c=(n+2)/(n+1)$、MSE $=\theta^2/(n+1)^2$）。

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
