---
test-category: 統計数理
stats-category: 標本分布
tags:
  - 正規分布
  - カイ二乗分布
  - t分布
  - F分布
  - コクランの定理
  - 分散分析
  - 母分散の検定
created: 2026-10-22
updated: 2026-10-26
---

# 正規標本から導くt・カイ二乗・F統計量

## 仮定・目標

$X_1,\ldots,X_n\overset{\rm iid}{\sim}N(\mu,\sigma^2)$、$n\ge2,\sigma^2>0$。$\bar X=n^{-1}\sum_iX_i$、$S^2=(n-1)^{-1}\sum_i(X_i-\bar X)^2$ と定める。

このノートでは**正規性と独立性を明示して**、正規標本からカイ二乗・t・F統計量が生成される過程を導く。分散の定義は分母$n-1$の不偏分散であり、フォルダ内の一部ノートが使う分母$n$版と区別する。

## 1. 標本平均と残差平方和の直交分解

$Z_i=(X_i-\mu)/\sigma$、$\boldsymbol Z=(Z_1,\ldots,Z_n)^\top\sim N_n(\boldsymbol0,I_n)$。

$$
H=\frac1n\boldsymbol1\boldsymbol1^\top,\qquad
H^2=H=H^\top,\qquad\operatorname{rank}(H)=1.
$$

$H$ は定数ベクトル方向への直交射影。$I_n-H$ はそれに直交する残差空間への射影で、階数 $n-1$。

$$
\boldsymbol Z^\top H\boldsymbol Z=\frac{n(\bar X-\mu)^2}{\sigma^2},
\qquad
\boldsymbol Z^\top(I_n-H)\boldsymbol Z
=\frac{\sum_i(X_i-\bar X)^2}{\sigma^2}.
$$

直交行列 $Q$ を用いて $Q^\top HQ=\operatorname{diag}(1,0,\dots,0)$ と対角化できる。$W=Q^\top Z$ は独立な標準正規成分からなるから

$$
\boldsymbol Z^\top H\boldsymbol Z=W_1^2\sim\chi^2_1,\quad
\boldsymbol Z^\top(I-H)\boldsymbol Z=\sum_{i=2}^nW_i^2\sim\chi^2_{n-1}.
$$

これらは独立な成分集合の関数なので独立。さらに $W_1=\sqrt n(\bar X-\mu)/\sigma$（符号は適当な基底の選択に合わせる）も残差成分とは独立。

**結論**：

$$
\frac{\sqrt n(\bar X-\mu)}{\sigma}\sim N(0,1),\qquad
\frac{(n-1)S^2}{\sigma^2}\sim\chi^2_{n-1},\qquad
\bar X\perp S^2.
$$

この独立性は一般の非正規母集団では成立しない。

## 2. t分布の生成

上の独立な $Z\sim N(0,1)$ と $V\sim\chi^2_{n-1}$ から、

$$
T=\frac{Z}{\sqrt{V/(n-1)}}
=\frac{\sqrt n(\bar X-\mu)}{S}\sim t_{n-1}.
$$

平均の両側検定 $H_0:\mu=\mu_0$ ではこの式の $\mu$ を $\mu_0$ に置き換える。未知の$\sigma$が分子・分母で相殺されることが重要。

**平方すると** $T^2\sim F(1,n-1)$。両側t検定と分子自由度1のF検定は対応する。

## 3. 独立な2標本の分散比

$X_1,\ldots,X_m\sim N(\mu_X,\sigma_X^2)$、$Y_1,\ldots,Y_n\sim N(\mu_Y,\sigma_Y^2)$ は独立（$m,n\ge2$）。不偏分散を $S_X^2,S_Y^2$ とすると

$$
U=\frac{(m-1)S_X^2}{\sigma_X^2}\sim\chi^2_{m-1},\qquad
V=\frac{(n-1)S_Y^2}{\sigma_Y^2}\sim\chi^2_{n-1},\quad U\perp V.
$$

よって

$$
\frac{S_X^2/\sigma_X^2}{S_Y^2/\sigma_Y^2}
=\frac{U/(m-1)}{V/(n-1)}
\sim F(m-1,n-1).
$$

$H_0:\sigma_X^2=\sigma_Y^2$ の下では **$S_X^2/S_Y^2\sim F(m-1,n-1)$**。この関係は正規母集団に依存し、非正規では厳密に成立しない。

## 4. 一元配置分散分析のF統計量

$k$ 群、各群標本数 $n_j\ge1$、総数 $N=\sum_jn_j>k$、共通母分散$\sigma^2$の独立正規モデル $Y_{ji}\sim N(\mu_j,\sigma^2)$ を考える。

$$
SS_B=\sum_{j=1}^kn_j(\bar Y_j-\bar Y)^2,\qquad
SS_W=\sum_{j=1}^k\sum_i(Y_{ji}-\bar Y_j)^2.
$$

群平均への射影行列を$H_G$、全体平均への射影を$H_0$とする。$H_G-H_0$ と $I_N-H_G$ は対称冪等で互いに直交する。階数はそれぞれ$k-1$と$N-k$。

帰無仮説 $H_0^{\rm test}:\mu_1=\cdots=\mu_k$ の下で、各射影が共通平均部分を消すため

$$
SS_B/\sigma^2\sim\chi^2_{k-1},\qquad
SS_W/\sigma^2\sim\chi^2_{N-k},
\quad SS_B\perp SS_W.
$$

したがって

$$
\boxed{F=\frac{SS_B/(k-1)}{SS_W/(N-k)}\sim F(k-1,N-k)}
\quad(H_0^{\rm test}).
$$

これは[[コクランの定理]]を射影行列で表現したもの。

## 例題（過去問改題）

> [!note] 出典
> 2022年 統計数理 問5〔1〕〔3〕の数値を変更（一般の $n$ に4組の具体的なデータを与えて平方和と $F$ 値を計算）。

**問題** $X_i\sim N(\mu_i,\sigma^2)$、$Y_i\sim N(\mu_i+\theta,\sigma^2)$（$i=1,\dots,4$）がすべて独立で、観測値は $X=(3,5,4,8)$、$Y=(5,6,7,10)$ だった。

1. $D_i=Y_i-X_i$ の分布を答え、対応のある $t$ 統計量を求めよ。
2. 繰り返しのない二元配置（行＝個体 $i$、列＝$X/Y$）として平方和 $S_A$（個体）、$S_B$（処理）、$S_E$ と自由度を求め、(a) $H_0:\theta=0$、(b) $H_0:\mu_1=\cdots=\mu_4$ の $F$ 値を求めよ。有意水準5%で判定せよ。$F_{0.05}(1,3)=10.13$、$F_{0.05}(3,3)=9.28$ とする。

> [!success]- 解答
>
> **1.** $D_i\sim N(\theta,2\sigma^2)$ で、$D=(2,1,3,2)$。$\bar D=2$、$\sum(D_i-\bar D)^2=2$、$s_D^2=2/3$。
>
> $$
> t=\frac{\bar D}{s_D/\sqrt4}=\frac{2}{\sqrt{1/6}}=2\sqrt6=4.899\quad(\text{自由度}3).
> $$
>
> **2.** 総平均6、列平均 $5,7$、行平均 $4,5.5,5.5,9$。総平方和は $36$。
>
> $$
> S_B=4\{(5-6)^2+(7-6)^2\}=8,\qquad
> S_A=2\{(-2)^2+(-0.5)^2+(-0.5)^2+3^2\}=27,\qquad
> S_E=36-8-27=1.
> $$
>
> 自由度は $\phi_A=3$、$\phi_B=1$、$\phi_E=(4-1)(2-1)=3$。$S_E=\frac12\sum(D_i-\bar D)^2$ でもある。
>
> $$
> F_B=\frac{8/1}{1/3}=\boxed{24}>10.13,\qquad
> F_A=\frac{27/3}{1/3}=\boxed{27}>9.28.
> $$
>
> どちらも棄却。$F_B=t^2=24$ で、$F(1,3)$ 検定は対応のある両側 $t$ 検定と同じ（$F_{0.05}(1,3)=t_{0.025}(3)^2=3.182^2$）。帰無仮説のもとで $S_B/\sigma^2\sim\chi^2_1$、$S_E/\sigma^2\sim\chi^2_3$ が独立なのは、それぞれが直交する部分空間への射影の長さだからである。

## チェックリスト

- 分散の除数は$n-1$か$n$か。
- 正規性・独立性・等分散性のどこを使ったか。
- カイ二乗の自由度は射影の**階数**で計算したか。
- $T^2\sim F(1,\nu)$ と、F統計量が一般に非負であることを区別したか。
- 「厳密なt/F分布」と「大標本の漸近カイ二乗分布」を混同していないか。

## 独立性の判定・非心分布・2標本tの導出を補完

### 1. 正規射影が独立することの証明

$Z\sim N_N(0,I_N)$、$P,Q$が対称冪等行列で$PQ=0$とする。$(PZ,QZ)$は正規ベクトルの線形変換なので**同時正規**であり、

$$
\operatorname{Cov}(PZ,QZ)=PQ^\top=PQ=0.
$$

同時正規かつ共分散0だから$PZ\perp QZ$。従ってそれらの可測関数である二次形式$Z^\top PZ=\|PZ\|^2$と$Z^\top QZ=\|QZ\|^2$も独立。

直交対角化で$P$の固有値は1を$r=\operatorname{rank}(P)$個、残りは0となるので

$$
\boxed{Z^\top PZ\sim\chi_r^2}.
$$

これはCochranの定理で使う2条件を明示した証明である。**非正規のベクトルでは「無相関だから独立」とは言えない**。

### 2. 平均が帰無仮説を満たさない場合：非心カイ二乗と非心F

$Y\sim N_N(m,\sigma^2I)$、$P$を階数$r$の直交射影とすると、直交変換により

$$
\boxed{\frac{Y^\top PY}{\sigma^2}
\sim\chi_r^2(\delta)},\qquad
\delta=\frac{\|Pm\|^2}{\sigma^2}.
$$

$\chi_r^2(\delta)$は非心カイ二乗分布。**帰無では$Pm=0$なので$\delta=0$**となり、通常の中心カイ二乗に戻る。

一元配置分散分析の群間平方和$SS_B$では

$$
\delta_B=\frac1{\sigma^2}\sum_{j=1}^k n_j(\mu_j-\mu_w)^2,\qquad
\mu_w=\frac1N\sum_jn_j\mu_j.
$$

一方、群内誤差平方和$SS_W/\sigma^2\sim\chi^2_{N-k}$は群平均が異なっても中心的で、群間平方和と独立。したがって対立仮説では

$$
\boxed{\frac{SS_B/(k-1)}{SS_W/(N-k)}
\sim F_{k-1,N-k}(\delta_B)},
$$

すなわち**非心F分布**となる。帰無で$\delta_B=0$なら既存の中心F分布の証明と一致する。

### 3. 2標本のプール分散t統計量

独立な2群$X_1,\ldots,X_m\sim N(\mu_X,\sigma^2)$、$Y_1,\ldots,Y_n\sim N(\mu_Y,\sigma^2)$（$m,n\ge2$）に対して

$$
Z=\frac{(\bar X-\bar Y)-(\mu_X-\mu_Y)}
{\sigma\sqrt{1/m+1/n}}\sim N(0,1).
$$

各群の残差平方和は相互に独立なカイ二乗で、それぞれの標本平均とも独立。従って

$$
V=\frac{(m-1)S_X^2+(n-1)S_Y^2}{\sigma^2}
\sim\chi^2_{m+n-2},\qquad Z\perp V.
$$

$S_p^2=((m-1)S_X^2+(n-1)S_Y^2)/(m+n-2)$とおけば

$$
\boxed{\frac{(\bar X-\bar Y)-(\mu_X-\mu_Y)}
{S_p\sqrt{1/m+1/n}}\sim t_{m+n-2}}.
$$

**等分散性が必要**。Welchの統計量では異なる分散の推定値を足すため、一般にこの厳密なt分布は成立せず、自由度にSatterthwaite近似などを用いる。

**追加例題**：3群の独立正規一元配置で$n_1=n_2=n_3=4$、共通分散$\sigma^2=1$、母平均$(0,1,2)$とする。群間平方和の非心母数を求めよ。

> [!success]- 解答
>
> $\mu_w=(0+1+2)/3=1$だから
>
> $$
> \delta_B=\sum_{j=1}^3 4(\mu_j-1)^2
> =4(1+0+1)=\boxed{8}.
> $$
>
> よって分散分析のF統計量は$F_{2,9}(8)$（非心F分布）に従う。全母平均が等しい帰無なら$\delta_B=0$。

## 1標本の母分散のカイ二乗検定と信頼区間

$X_1,\dots,X_n\overset{\rm iid}{\sim}N(\mu,\sigma^2)$（$\mu$ 未知）、不偏分散 $S^2$ とする。§1 より

$$
\frac{(n-1)S^2}{\sigma^2}\sim\chi^2(n-1)
$$

で、これは $\sigma^2$ 以外の母数を含まないピボットになる。

- **検定**：$H_0:\sigma^2=\sigma_0^2$ の検定統計量は $\chi^2_0=(n-1)S^2/\sigma_0^2$。対立仮説 $\sigma^2>\sigma_0^2$ なら $\chi^2_0>\chi^2_\alpha(n-1)$ で棄却、両側なら $\chi^2_0>\chi^2_{\alpha/2}(n-1)$ または $\chi^2_0<\chi^2_{1-\alpha/2}(n-1)$ で棄却（$\chi^2_\alpha$ は上側 $100\alpha\%$ 点）。
- **信頼区間**：$\chi^2_{1-\alpha/2}(n-1)\le(n-1)S^2/\sigma^2\le\chi^2_{\alpha/2}(n-1)$ を $\sigma^2$ について解いて
  $$
  \left[\frac{(n-1)S^2}{\chi^2_{\alpha/2}(n-1)},\ \frac{(n-1)S^2}{\chi^2_{1-\alpha/2}(n-1)}\right].
  $$
  カイ二乗分布は非対称なので、区間は $S^2$ について**非対称**で、上側に長い（[[分位点と代表値]]）。
- **正規性への依存**：平均の $t$ 検定と違い、この検定は母集団が正規でないと大標本でも水準が保たれない。$\mathrm{Var}(S^2)$ が母集団の尖度に依存するためである（[[歪度_尖度]]）。
- 2つの正規母集団の分散の比較は §3 の分散比 $F$ 検定（[[F分布]]）。

**例題** $n=10$、$S^2=4$ のとき、$\sigma^2$ の95%信頼区間を求め、$H_0:\sigma^2=2$ を両側5%と片側（$H_1:\sigma^2>2$）5%で検定せよ。付表より $\chi^2_{0.025}(9)=19.02$、$\chi^2_{0.975}(9)=2.70$、$\chi^2_{0.05}(9)=16.92$。

> [!success]- 解答
>
> $(n-1)S^2=36$。信頼区間は $[36/19.02,\ 36/2.70]=\boxed{[1.89,\ 13.33]}$。点推定値 $4$ から見て右に長い。
>
> $\chi^2_0=36/2=18$。両側：$2.70\le18\le19.02$ なので**棄却しない**（区間が $2$ を含むことと対応）。片側：$18>16.92$ なので**棄却する**。

## 関連

- [[正規分布]]
- [[カイ二乗分布]]
- [[t分布]]
- [[F分布]]
- [[標本平均]]
- [[t検定]]
- [[一元配置分散分析]]
- [[コクランの定理]]

## 使われる問題

![[概念別問題一覧.base]]
