---
test-category: 統計数理
stats-category: 確率分布
tags:
  - F分布
  - カイ二乗分布の比
  - 分散分析
created: 2026-10-19
updated: 2026-10-26
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

## 例題（過去問改題）

> [!note] 出典
> 2017年 統計数理 問5〔2〕の数値を変更（$X,Y$ の自由度を $1\to2$。確率と期待値の小問を追加）。

**問題** $X,Y$ は独立にそれぞれ自由度2のカイ二乗分布に従うとする。(1) $S=X/Y$ の密度を変数変換で求めよ。(2) $P(S>3)$ を求めよ。(3) $E[S]$ は存在するか。

> [!success]- 解答
>
> (1) $\chi^2_2$ の密度は $\frac12e^{-x/2}$（$x>0$）なので、同時密度は $\frac14e^{-(x+y)/2}$。$s=x/y,\ u=y$ とおくと $x=su,\ y=u$ で、ヤコビアンは
>
> $$
> \frac{\partial(x,y)}{\partial(s,u)}=\begin{vmatrix}u&s\\0&1\end{vmatrix}=u.
> $$
>
> $x+y=(1+s)u$ と $\int_0^\infty ue^{-bu}du=1/b^2$ より、$s>0$ で
>
> $$
> g(s)=\int_0^\infty\frac14e^{-(1+s)u/2}\,u\,du
> =\frac14\cdot\frac{4}{(1+s)^2}
> =\boxed{\frac1{(1+s)^2}}.
> $$
>
> $S=(X/2)/(Y/2)$ なので、これは $F(2,2)$ の密度である。
>
> (2)
>
> $$
> P(S>3)=\int_3^\infty\frac{ds}{(1+s)^2}=\left[-\frac1{1+s}\right]_3^\infty=\boxed{\frac14}.
> $$
>
> (3) $s\to\infty$ で $s\,g(s)\approx1/s$ なので $\int_0^\infty s\,g(s)\,ds=\infty$。分母の自由度 $n=2$ は $E[F]=n/(n-2)$ の条件 $n>2$ を満たさず、$E[S]$ は**存在しない**。

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

## 十分統計量・最尤推定量の導出（F）

$X_1,\ldots,X_n\overset{\rm iid}{\sim}F(u,v)$。通常、自由度$u,v$は**実験計画により既知**だが、ここでは両者を推定する仮想的な問題として$u,v>0$を**連続母数**とする。整数自由度に制限する場合も区別する。

### 十分統計量（因子分解と情報の縮約）

F分布の密度を直接書くと

$$
f(x;u,v)=
\frac{\Gamma((u+v)/2)}{\Gamma(u/2)\Gamma(v/2)}
\left(\frac uv\right)^{u/2}
x^{u/2-1}\left(1+\frac{ux}{v}\right)^{-(u+v)/2},
\quad x>0.
$$

尤度はこの密度の積であり、母数の比$u/v$が変わるたび$\sum_i\log(1+ux_i/v)$が変わる。**全順序統計量$(X_{(1)},\ldots,X_{(n)})$は$(u,v)$の十分統計量**。一般に$\sum X_i$や$\sum\log X_i$だけへの固定次元の縮約はできない。実際、全ての$r>0$で$\prod_i(1+rx_i)$が一致すれば多項式の根から標本の多重集合が復元される。

### 最尤推定量（自由度2つの連立スコアと大域比較）

$L=\sum_i\log x_i$、$A=\sum_i\log(1+ux_i/v)$、$B=\sum_i x_i/(v+ux_i)$、$\psi=\Gamma'/\Gamma$と定義する。

$$
\ell(u,v)=n\left[
\log\Gamma\left(\frac{u+v}{2}\right)
-\log\Gamma\left(\frac u2\right)
-\log\Gamma\left(\frac v2\right)
+\frac u2\log\frac uv\right]
+\left(\frac u2-1\right)L-\frac{u+v}{2}A.
$$

内点スコアは

$$
\begin{aligned}
\partial_u\ell
=&\frac n2\left[\psi\left(\frac{u+v}{2}\right)-\psi\left(\frac u2\right)
+\log\frac uv+1\right]\\
&+\frac L2-\frac A2-\frac{u+v}{2}B,\\
\partial_v\ell
=&\frac n2\left[\psi\left(\frac{u+v}{2}\right)-\psi\left(\frac v2\right)
-\frac uv\right]-\frac A2
+\frac{u(u+v)}{2v}B.
\end{aligned}
$$

正の領域で$\partial_u\ell=\partial_v\ell=0$を数値的に解き、**局所解同士と$u\to\infty,v\to\infty$等の境界極限**での尤度も比較する。形の一般的な閉形式解や、常に有限MLEが存在する保証はない。整数自由度なら離散的な尤度の比較が必要。

**確認問題**：任意の標本では、自由度が既知なら推定すべき未知母数はない。未知として推定するモデルでは、例えば$X=(1,2)$の順序統計量$(1,2)$が十分統計量で、上記$\ell(u,v)$を最大化する。

## 関連

- [[t分布]]
- [[一元配置分散分析]]
- [[コクランの定理]]
- [[ベータ分布]]

## 使われる問題

### 教科書（現代数理統計学の基礎）

![[概念別教科書問題一覧.base]]

### 統計検定1級 過去問

![[概念別過去問一覧.base]]
