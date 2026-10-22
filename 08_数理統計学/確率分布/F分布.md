---
test-category: 統計数理
stats-category: 確率分布
tags:
  - F分布
  - カイ2乗分布の比
  - 分散分析
created: 2026-10-19
updated: 2026-10-22
---

# F分布

## 定義

$U\sim\chi^2(m)$、$V\sim\chi^2(n)$ が独立のとき
$$
F=\frac{U/m}{V/n}\sim F(m,n)
$$
を自由度 $(m,n)$ の $F$ 分布という。

## 要点

- 逆数性: $1/F\sim F(n,m)$。したがって下側点と上側点の関係 $F_{1-\alpha}(m,n)=1/F_\alpha(n,m)$（$F_\alpha(m,n)$ は上側 $\alpha$ 点）。片側の付表しかなくても両側が得られる。
- 期待値: $E[F]=\dfrac{n}{n-2}$（$n>2$）。導出の要点: $U,V$ が独立なので $E[F]=\dfrac{n}{m}E[U]\,E[1/V]=\dfrac{n}{m}\cdot m\cdot\dfrac{1}{n-2}$（$E[1/V]=1/(n-2)$、$V\sim\chi^2(n)$）。
- $t$ との関係: $T\sim t(\nu)$ なら $T^2\sim F(1,\nu)$（[[t分布]]）。
- 正規母集団の分散比: $X_1,\dots,X_m\sim N(\mu_1,\sigma_1^2)$ と $Y_1,\dots,Y_n\sim N(\mu_2,\sigma_2^2)$ が独立なら $\dfrac{S_X^2/\sigma_1^2}{S_Y^2/\sigma_2^2}\sim F(m-1,n-1)$（等分散性の検定）。
- 分散分析との関係: 群間平方和と群内平方和が独立な $\sigma^2\chi^2$ で、その自由度当たりの比が $F$ 分布になる（[[一元配置分散分析]]、独立性は[[コクランの定理]]）。
- $n\to\infty$ のとき $mF\to\chi^2(m)$（分母が $1$ に収束する）。
- ベータ分布との関係: $F\sim F(m,n)$ なら $\dfrac{mF/n}{1+mF/n}\sim\mathrm{Beta}(m/2,n/2)$（[[ベータ分布]]）。

## 導出：期待値・分散とカイ二乗分布との関係

$U\sim\chi_m^2$、$V\sim\chi_n^2$ は独立として $F=(U/m)/(V/n)$ とする。$n>2$ なら独立性から

$$
E[F]=\frac nmE[U]E[V^{-1}]
=\frac nm\cdot m\cdot\frac1{n-2}=\frac n{n-2}.
$$

$n>4$ では

$$
\begin{aligned}
E[F^2]&=\left(\frac nm\right)^2E[U^2]E[V^{-2}]\\
&=\frac{n^2}{m^2}\frac{m(m+2)}{(n-2)(n-4)}.
\end{aligned}
$$

従って

$$
\boxed{\operatorname{Var}(F)=\frac{2n^2(m+n-2)}{m(n-2)^2(n-4)}}\qquad(n>4).
$$

$n\le2$ では平均が存在せず、$2<n\le4$ では分散が有限でない。

**極限**：$m$ を固定し $n\to\infty$ とすると $V/n\xrightarrow{P}1$ なので、スルツキーの定理より $mF\Rightarrow\chi_m^2$。さらに $T\sim t_n$ なら $T^2\sim F(1,n)$。

この形が正規母集団の分散比較や[[一元配置分散分析]]の F 統計量を支える（独立な平方和を各自由度で割る）。

## 過去問型のオリジナル例題

> [!note] 参考
> **2017年 統計数理 問5**（カイ二乗分布の比）、**2021年 統計数理 問5**（正規二次形式）。

**問題** $F\sim F(4,8)$ の $E[F]$、$\operatorname{Var}(F)$ を求め、存在条件を確認せよ。

> [!success]- 解答
>
> $n=8>4$ なので期待値・分散はともに有限。
>
> $$
> E[F]=\frac8{8-2}=\frac43,
> \quad
> E[F^2]=\frac{8^2}{4^2}
> \frac{4(4+2)}{(8-2)(8-4)}=4.
> $$
>
> $$
> \operatorname{Var}(F)=4-\left(\frac43\right)^2
> =\boxed{\frac{20}{9}}.
> $$
>
> $F$ は正に歪んだ分布なので、期待値が自由度の比から自明に1となるわけではない。

## F分布 → カイ二乗：分布収束と密度の収束

分子自由度$m>0$を固定し、分母自由度$n\to\infty$とする。独立な$U\sim\chi_m^2,V_n\sim\chi_n^2$について

$$
F_{m,n}=\frac{U/m}{V_n/n}.
$$

$E[V_n/n]=1,\operatorname{Var}(V_n/n)=2/n\to0$より$V_n/n\xrightarrow P1$。Slutskyの定理で

$$
\boxed{mF_{m,n}=\frac U{V_n/n}\xrightarrow{d}\chi_m^2}.
$$

つまり**$F_{m,n}$自体は$\chi_m^2/m$に収束**し、$\chi_m^2$へ収束するのは$mF_{m,n}$である。

**密度関数の点ごとの収束**も示す。$Y_n=mF_{m,n}$の密度は、$y>0$で

$$
f_{Y_n}(y)=
\frac{\Gamma((m+n)/2)}{\Gamma(m/2)\Gamma(n/2)}
n^{-m/2}y^{m/2-1}\left(1+\frac yn\right)^{-(m+n)/2}.
$$

Gamma関数比$\Gamma(z+a)/\Gamma(z)\sim z^a$と$(1+y/n)^{-(m+n)/2}\to e^{-y/2}$から

$$
\boxed{f_{Y_n}(y)\to
\frac{y^{m/2-1}e^{-y/2}}{2^{m/2}\Gamma(m/2)}}.
$$

右辺は$\chi_m^2$の**密度**。分母自由度が大きいという条件と、**倍率$m$**を必ず明示する。

**確認例題**：$m=2$を固定して$n\to\infty$なら$2F_{2,n}\Rightarrow\chi_2^2$。$F_{2,n}$単独なら$\chi_2^2/2$。

## 関連

- [[t分布]]
- [[一元配置分散分析]]
- [[コクランの定理]]
- [[ベータ分布]]

## 使われる問題

![[概念別問題一覧.base]]
