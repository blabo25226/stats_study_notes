---
test-category: 統計数理
stats-category: 確率分布
tags:
  - t分布
  - 自由度
  - 裾の重さ
created: 2026-10-19
updated: 2026-10-29
---

# t分布

## 定義

$Z\sim N(0,1)$ と $V\sim\chi^2(\nu)$ が独立のとき
$$
T=\frac{Z}{\sqrt{V/\nu}}\sim t(\nu)
$$
を自由度 $\nu$ の $t$ 分布という。密度は $f(t)\propto\left(1+t^2/\nu\right)^{-(\nu+1)/2}$。

## 要点

- 正規母集団の標本平均と標本分散は独立で（[[コクランの定理]]）、$\sqrt n(\bar X-\mu)/\sigma\sim N(0,1)$、$(n-1)S^2/\sigma^2\sim\chi^2(n-1)$ なので、$\sqrt n(\bar X-\mu)/S\sim t(n-1)$。母分散が未知のときの平均の検定・区間推定（[[t検定]]）の基礎。
- $T^2=Z^2/(V/\nu)$ で $Z^2\sim\chi^2(1)$ なので $T^2\sim F(1,\nu)$（[[F分布]]）。
- 原点について対称。$E[T]=0$（$\nu>1$）、$\operatorname{Var}(T)=\nu/(\nu-2)$（$\nu>2$）。$\nu=1$ はコーシー分布で期待値が存在しない。
- 自由度無限で正規: $V/\nu\to1$（大数の法則）より $\nu\to\infty$ で $t(\nu)\to N(0,1)$（[[正規分布]]）。
- 裾の重さ: 正規分布より裾が重く、$|T|>c$ の確率は同じ $c$ で正規より大きい。そのため同じ水準なら $t$ の臨界値のほうが大きい。
- 2標本（等分散）では、プールした分散 $S_p^2$（自由度 $n_1+n_2-2$）を用いて $t(n_1+n_2-2)$ に従う統計量を作る。

## 導出：平均・分散と正規分布への極限

$Z\sim N(0,1)$、$V\sim\chi_\nu^2$ は独立、$T=Z/\sqrt{V/\nu}$ とする。条件付きでは $T$ は $Z$ の正の尺度変換なので対称性より、$\nu>1$ で $E[T]=0$（絶対1次モーメントの存在条件）。

$\nu>2$ のとき独立性を用いれば

$$
\begin{aligned}
E[T^2]&=E[Z^2]\,\nu E[V^{-1}]\\
&=1\cdot\nu\frac1{\nu-2}
=\frac{\nu}{\nu-2}.
\end{aligned}
$$

従って $\operatorname{Var}(T)=\nu/(\nu-2)$。$\nu\le1$ では平均が存在せず、$1<\nu\le2$ では平均は存在するが分散は有限でない。

**正規極限**：$V_\nu=\sum_{i=1}^\nu Z_i^2$ とおけば $V_\nu/\nu\xrightarrow{P}1$（大数の法則）。独立な $Z\sim N(0,1)$ と組み合わせたスルツキーの定理により

$$
\frac{Z}{\sqrt{V_\nu/\nu}}\xrightarrow{d}N(0,1).
$$

また $T^2=Z^2/(V/\nu)\sim F(1,\nu)$。$\nu=1$ なら $T$ は標準コーシー分布（**2023年 統計数理 問2**）。

## 例題（過去問改題）

> [!note] 出典
> 2025年 統計数理 問3〔5〕の数値を変更（一般の $n$ → $n=6$、すなわち $t$ の自由度 $4$。確率の小問を追加）。

**問題** 単回帰 $Y_i=\alpha+\beta x_i+\varepsilon_i$（$\varepsilon_i\sim N(0,\sigma^2)$ 独立、$n=6$）で $\beta=0$ とする。標本相関係数 $r$ は、$T\sim t(4)$ を用いて $r=T/\sqrt{4+T^2}$ と表せる。(1) $E[T]$、$\operatorname{Var}(T)$ を求めよ。(2) $r$ の密度を求めよ。(3) $P(|r|>1/2)$ を求め、$T$ の両側確率で言い換えよ。

> [!success]- 解答
>
> (1) 自由度4なので $E[T]=0$、$\operatorname{Var}(T)=4/(4-2)=2$。
>
> (2) $t(4)$ の密度は
>
> $$
> f_T(t)=\frac{\Gamma(5/2)}{\sqrt{4\pi}\,\Gamma(2)}\left(1+\frac{t^2}{4}\right)^{-5/2}.
> $$
>
> $r=t/\sqrt{4+t^2}$ は $(-\infty,\infty)$ から $(-1,1)$ への単調増加な全単射で、
>
> $$
> t=\frac{2r}{\sqrt{1-r^2}},\qquad \frac{dt}{dr}=\frac{2}{(1-r^2)^{3/2}},\qquad 1+\frac{t^2}{4}=\frac1{1-r^2}.
> $$
>
> $\Gamma(5/2)=\frac34\sqrt\pi$ を使うと、$-1<r<1$ で
>
> $$
> f(r)=\frac{\frac34\sqrt\pi}{2\sqrt\pi}(1-r^2)^{5/2}\cdot\frac{2}{(1-r^2)^{3/2}}=\boxed{\frac34(1-r^2)}.
> $$
>
> 検算：$\int_{-1}^1\frac34(1-r^2)\,dr=\frac34\cdot\frac43=1$。
>
> (3) 対称性から
>
> $$
> P(|r|>1/2)=2\int_{1/2}^1\frac34(1-r^2)\,dr=\frac32\left[r-\frac{r^3}3\right]_{1/2}^1=\frac32\left(\frac23-\frac{11}{24}\right)=\boxed{\frac5{16}}.
> $$
>
> $r=1/2$ に対応する $t$ は $2\cdot\frac12/\sqrt{3/4}=2/\sqrt3$ なので、$P(|T|>2/\sqrt3)=5/16$。$r$ による無相関の検定と、傾き $\beta=0$ の $t$ 検定は同じ棄却域を与える。

## 矢印の証明：t → コーシー／正規／F

### 1. $t_1=$ 標準コーシー（密度の厳密一致）

自由度$\nu$のt密度は

$$
f_\nu(t)=\frac{\Gamma((\nu+1)/2)}
{\sqrt{\nu\pi}\Gamma(\nu/2)}
\left(1+\frac{t^2}{\nu}\right)^{-(\nu+1)/2}.
$$

$\nu=1$を代入し$\Gamma(1)=1,\Gamma(1/2)=\sqrt\pi$を使えば

$$
\boxed{f_1(t)=\frac1{\pi(1+t^2)}},
$$

すなわち**$t_1$と標準コーシーは同じ分布**。$\nu\downarrow1$を考える必要はない（同一性である）。

### 2. $t_\nu\Rightarrow N(0,1)$（密度の極限も示す）

$\nu\to\infty$で独立な$Z\sim N(0,1),V_\nu\sim\chi_\nu^2$を考える。$V_\nu/\nu\xrightarrow P1$よりSlutskyで

$$
\frac{Z}{\sqrt{V_\nu/\nu}}\xrightarrow{d}N(0,1).
$$

**密度の各点収束**も、Gamma関数比の漸近公式$\Gamma(z+1/2)/\Gamma(z)\sim z^{1/2}$と

$$
\left(1+\frac{t^2}{\nu}\right)^{-(\nu+1)/2}\to e^{-t^2/2}
$$

から

$$
\boxed{f_\nu(t)\to \phi(t)=\frac{e^{-t^2/2}}{\sqrt{2\pi}}}
\quad(t\in\mathbb R\ \text{固定})
$$

と示せる。

### 3. $T_\nu^2\sim F(1,\nu)$（厳密な変換）

$T_\nu=Z/\sqrt{V_\nu/\nu}$（$Z\perp V_\nu$）なら$Z^2\sim\chi_1^2$で$Z^2\perp V_\nu$。従って

$$
T_\nu^2=\frac{Z^2/1}{V_\nu/\nu}\sim F(1,\nu).
$$

これは**極限ではなく厳密な分布関係**。密度の変数変換でも$y>0$について$f_{T^2}(y)=[f_T(\sqrt y)+f_T(-\sqrt y)]/(2\sqrt y)$から同じF密度を得る。

**確認例題**：$\nu=1$では$t_1$がコーシーで$T_1^2\sim F(1,1)$。コーシーの期待値は存在しない。

## 十分統計量・最尤推定量の導出（Student t）

**確率モデル。** $X_1,\dots,X_n\overset{\rm iid}{\sim}t_\nu$は**位置0・尺度1を固定**した標準t分布とし、自由度$\nu>0$だけを未知母数とする（連続母数）。位置・尺度まで未知にする場合は**別モデル**であり、以下の十分統計量は変わる。

**確率密度関数。**

$$
f(x;\nu)=\frac{\Gamma((\nu+1)/2)}{\sqrt{\nu\pi}\,\Gamma(\nu/2)}\left(1+\frac{x^2}{\nu}\right)^{-(\nu+1)/2},\qquad x\in\mathbb R.
$$

### 十分統計量（対称性と因子分解）

**尤度関数。** 独立なので、観測値を代入した同時密度を $\nu$ の関数とみて

$$
L(\nu;\boldsymbol x)=\prod_{i=1}^nf(x_i;\nu)
=\left[
\frac{\Gamma((\nu+1)/2)}
{\sqrt{\nu\pi}\Gamma(\nu/2)}
\right]^n
\prod_i\left(1+\frac{x_i^2}{\nu}\right)^{-(\nu+1)/2}.
$$

符号と標本順序に依存しないため

$$
\boxed{T=\operatorname{sort}(X_1^2,\ldots,X_n^2)}
$$

が$\nu$の十分統計量。一般に**$\sum_iX_i^2$だけでは十分でない**。全順序統計量$(X_{(1)},\ldots,X_{(n)})$も十分だが、標準tでは絶対値の情報だけに縮約できる。

### 最尤推定量（自由度のスコア・境界）

**対数尤度とスコア。** $C(\nu)=\log\Gamma((\nu+1)/2)-\log\Gamma(\nu/2)-\tfrac12\log(\nu\pi)$とおけば

$$
\ell(\nu)=nC(\nu)-\frac{\nu+1}{2}
\sum_i\log\left(1+\frac{x_i^2}{\nu}\right).
$$

ディガンマ関数$\psi$を使って微分すると

$$
\begin{aligned}
\ell'(\nu)
=&\frac n2\left[\psi\left(\frac{\nu+1}{2}\right)
-\psi\left(\frac\nu2\right)-\frac1\nu\right]\\
&-\frac12\sum_i\log\left(1+\frac{x_i^2}{\nu}\right)
+\frac{\nu+1}{2\nu}\sum_i\frac{x_i^2}{\nu+x_i^2}.
\end{aligned}
$$

**最大化。** スコア方程式は陽に解けず数値計算になり、$\ell$ の凹性も一般には保証されない。**$\ell'(\hat\nu)=0$の正の根は候補にすぎない**。$\nu\downarrow0$や$\nu\to\infty$（標準正規への極限）の尤度とも比較して全域最大を選ぶ。有限のMLEが存在しない場合もある。整数自由度を仮定する教材では候補整数の尤度を比較する。スコアを単純に0にする方法だけで済まない例である。

**確認問題**：標本$(1,-1)$では十分統計量$\operatorname{sort}(1,1)$。自由度のMLEは上の1変数尤度を最大化して決め、標本平均0を自由度推定量として使わない。

## 関連

- [[F分布]]
- [[t検定]]
- [[正規分布]]
- [[コクランの定理]]

## 使われる問題

### 教科書（現代数理統計学の基礎）

![[概念別教科書問題一覧.base]]

### 統計検定1級 過去問

![[概念別過去問一覧.base]]
