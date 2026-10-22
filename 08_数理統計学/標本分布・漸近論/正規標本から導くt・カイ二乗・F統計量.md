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
created: 2026-10-22
updated: 2026-10-22
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

## 過去問型のオリジナル演習

> [!note] 出題型
> 統計数理に頻出する正規モデルの平方和・自由度・独立性の計算を、3群の独自データで練習する。

**問題** 3群に各2個の観測 $(1,2)$、$(2,3)$、$(3,4)$ がある。等分散の独立正規モデルを仮定し、共通平均の帰無仮説を検定する一元配置分散分析の群間平方和・群内平方和、$F$ 値、自由度を求めよ。

> [!success]- 解答・導出
>
> 各群平均は $3/2,5/2,7/2$、全体平均は $5/2$。群間平方和は
>
> $$
> SS_B=2\left\{(-1)^2+0^2+1^2\right\}=4.
> $$
>
> 各群の群内平方和は $(1/2)^2+(1/2)^2=1/2$ なので
>
> $$
> SS_W=3\cdot\frac12=\frac32.
> $$
>
> $k=3,N=6$。よって
>
> $$
> MS_B=\frac4{3-1}=2,\qquad
> MS_W=\frac{3/2}{6-3}=\frac12.
> $$
>
> $$
> \boxed{F=\frac2{1/2}=4},\qquad
> (df_1,df_2)=(2,3).
> $$
>
> 棄却判定では $F(2,3)$ の指定上側確率点を付表から読み比較する。自由度の差は群数と観測総数から決める。

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
