---
test-category: 統計数理
stats-category: 推定
tags:
  - バイアス
  - 偏り
  - 不偏性
  - 標本標準偏差
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

## 変換による偏りとオリジナル演習

$E[\hat\theta]=\theta$ でも一般に $E[g(\hat\theta)]\ne g(\theta)$。$g$ が凸なら Jensen の不等式から $E[g(\hat\theta)]\ge g(E[\hat\theta])$ である。

**問題** $X_i\sim\operatorname{Bern}(p)$ 独立、$\hat p=\bar X$ とする。$p^2$ の推定量 $\hat p^2$ のバイアスを求め、不偏に直せ（$n\ge2$）。

> [!success]- 解答
>
> $E[\hat p]=p$、$\operatorname{Var}(\hat p)=p(1-p)/n$ より
>
> $
> E[\hat p^2]=p^2+\frac{p(1-p)}n
> =\frac{n-1}{n}p^2+\frac pn.
> $
>
> 従って $\operatorname{Bias}(\hat p^2)=p(1-p)/n$。この式から
>
> $
> \boxed{\tilde q=\frac{n\hat p^2-\hat p}{n-1}}
> $
>
> とすれば $E[\tilde q]=p^2$。また $\tilde q=\sum_{i\ne j}X_iX_j/\{n(n-1)\}$ であり、異なる標本間の独立性からも不偏性を確認できる。

## 標本標準偏差の偏り：2次近似と厳密式

$S^2$ は $\sigma^2$ の不偏推定量だが、$S=\sqrt{S^2}$ は $\sigma$ の不偏推定量ではない（2018数理 問1 の題材）。$X_i\overset{\rm iid}{\sim}N(\mu,\sigma^2)$、$S^2$ は除数 $n-1$ とする。

**1. 2次近似** $g(v)=\sqrt v$ は凹で $g''(v)=-\frac14v^{-3/2}$。$\operatorname{Var}(S^2)=2\sigma^4/(n-1)$ を上の2次展開に入れると
$$
E[S]\approx\sigma-\frac18\sigma^{-3}\cdot\frac{2\sigma^4}{n-1}=\sigma\left(1-\frac1{4(n-1)}\right),
\qquad \operatorname{Bias}(S)\approx-\frac{\sigma}{4n}.
$$

**2. 厳密式** $Y\sim\chi^2_\nu$ のとき
$$
E[\sqrt Y]=\int_0^\infty\frac{y^{1/2}y^{\nu/2-1}e^{-y/2}}{2^{\nu/2}\Gamma(\nu/2)}dy=\frac{\sqrt2\,\Gamma\!\left(\frac{\nu+1}2\right)}{\Gamma\!\left(\frac\nu2\right)}
$$
（[[ガンマ関数]]による規格化）。$(n-1)S^2/\sigma^2\sim\chi^2_{n-1}$ に $\nu=n-1$ を入れて
$$
E[S]=c_4\sigma,\qquad c_4=\sqrt{\frac2{n-1}}\,\frac{\Gamma(n/2)}{\Gamma((n-1)/2)}.
$$
$S/c_4$ は $\sigma$ の不偏推定量。

**3. 二つの経路の一致** [[スターリングの公式]]を1項先まで展開すると
$$
\frac{\Gamma(z+1/2)}{\Gamma(z)}=\sqrt z\left(1-\frac1{8z}+O(z^{-2})\right).
$$
$z=(n-1)/2$ とすれば $c_4=1-\dfrac1{4(n-1)}+O(n^{-2})$ となり、2次近似と一致する。

**問題** $n=9$ のとき $c_4$ を厳密に計算し、2次近似と比べよ。$\sqrt\pi=1.7725$ を用いてよい。

> [!success]- 解答
>
> $c_4=\sqrt{2/8}\,\Gamma(4.5)/\Gamma(4)$。$\Gamma(4.5)=3.5\times2.5\times1.5\times0.5\times\sqrt\pi=6.5625\times1.7725=11.632$、$\Gamma(4)=6$ より
>
> $
> c_4=0.5\times\frac{11.632}{6}=0.9693.
> $
>
> 2次近似は $1-1/32=0.96875$。差は $0.0006$ 程度で、$O(n^{-2})$ の項に相当する。

## 関連

- [[不偏推定量]]
- [[MSE]]
- [[点推定]]
- [[最尤推定量]]
- [[デルタ法]]

## 使われる問題

![[概念別問題一覧.base]]
