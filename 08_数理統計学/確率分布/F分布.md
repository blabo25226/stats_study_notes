---
test-category: 統計数理
stats-category: 確率分布
tags:
  - F分布
  - カイ2乗分布の比
  - 分散分析
created: 2026-10-19
updated: 2026-10-19
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

## 関連

- [[t分布]]
- [[一元配置分散分析]]
- [[コクランの定理]]
- [[ベータ分布]]

## 使われる問題

![[概念別問題一覧.base]]
