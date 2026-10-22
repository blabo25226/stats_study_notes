---
test-category: 統計数理
stats-category: 計算機統計学
tags:
  - ニュートン法
  - フィッシャー・スコアリング
  - 尤度方程式
  - IRLS
created: 2026-10-22
updated: 2026-10-22
---

# ニュートン法とFisher_scoring

## 定義

**ニュートン・ラフソン法**は $f(x)=0$ の根を、接線の零点で更新して求める。
$$
x_{t+1}=x_t-\frac{f(x_t)}{f'(x_t)}.
$$
最尤推定では $f$ をスコア $S(\theta)=\ell'(\theta)$ にとる。
$$
\theta_{t+1}=\theta_t+\frac{S(\theta_t)}{-\ell''(\theta_t)}\quad\Bigl(\text{多次元: }\ \theta_{t+1}=\theta_t+\{-\nabla^2\ell(\theta_t)\}^{-1}\nabla\ell(\theta_t)\Bigr).
$$
**フィッシャー・スコアリング**は観測情報 $-\ell''(\theta)$ を期待情報 $I(\theta)$（標本全体の[[フィッシャー情報量]]）に置き換える。
$$
\theta_{t+1}=\theta_t+\frac{S(\theta_t)}{I(\theta_t)}.
$$

## 要点

- **2次収束**: 根 $x^*$ のまわりのテイラー展開 $0=f(x_t)+f'(x_t)(x^*-x_t)+\tfrac12f''(\xi)(x^*-x_t)^2$ を $f'(x_t)$ で割ると
  $x^*-x_{t+1}=-\dfrac{f''(\xi)}{2f'(x_t)}(x^*-x_t)^2$。誤差が $e_{t+1}\approx Ce_t^2$ となり、桁数が反復ごとにおよそ倍になる（$f'(x^*)\ne0$ が条件）。
- 初期値依存: 局所収束のみ保証され、初期値が遠いと発散・振動・別の根への収束が起こる。$f'\approx0$ の点では更新幅が爆発する。
- 観測情報は $\hat\theta$ の近くでは $nI(\theta)$ に近い（[[最尤推定量]]の漸近分散）。適切な正則性の下で情報行列 $I(\theta)$ は非負定値となり、可逆なら更新に利用できる。観測情報の符号変化による不安定さを避けられる場合もあるが、初期値への頑健性や収束速度はモデルと更新幅に依存する。
- **正準リンク**: [[指数型分布族]]で正準パラメータを使うと $\ell''$ が $y$ に依存しないため、観測情報と期待情報が一致し、両者は同じ反復になる。
- **ロジスティック回帰のIRLS**: $\mu_i=\text{logit}^{-1}(x_i^\top\beta)$、$W=\text{diag}\{\mu_i(1-\mu_i)\}$ として
  $\beta_{t+1}=\beta_t+(X^\top WX)^{-1}X^\top(y-\mu)$。これは作業応答 $z=X\beta_t+W^{-1}(y-\mu)$ への重み付き最小二乗で、毎回 $W,z$ を更新するので反復重み付き最小二乗法（IRLS）と呼ばれる。→ [[ロジスティック回帰]]

## 例

**ポアソン分布の平均**（$\ell=\sum x_i\log\lambda-n\lambda+\text{定数}$）: $S=n\bar x/\lambda-n$、$-\ell''=n\bar x/\lambda^2$、$I=n/\lambda$。
- ニュートン法: $\lambda_{t+1}=\lambda+\lambda-\lambda^2/\bar x=2\lambda-\lambda^2/\bar x$。
- スコアリング: $\lambda_{t+1}=\lambda+(n\bar x/\lambda-n)/(n/\lambda)=\bar x$。**1回で最尤推定値**に到達。

検算（$\bar x=2$、$\lambda_0=1$）: ニュートン法は $1\to1.5\to1.875\to1.992$。誤差は $1,\,0.5,\,0.125,\,0.0078$ で、$e_{t+1}=e_t^2/\bar x$（$0.5=1/2,\ 0.125=0.25/2,\ 0.0078\approx0.0156/2$）と一致し、2次収束している。ポアソンの対数尤度では $\bar x>0$ のとき $\lambda_0>2\bar x$ だと $\lambda_1<0$ となり破綻する（初期値依存の例）。

**コーシー分布の位置母数** $f(x;\theta)=1/\{\pi(1+(x-\theta)^2)\}$: $S(\theta)=\sum 2(x_i-\theta)/\{1+(x_i-\theta)^2\}$。尤度方程式は**多根**（極大が複数）になりうる。1個あたりの情報量は $1/2$ なので、スコアリングは
$$
\theta_{t+1}=\theta_t+\frac{4}{n}\sum_i\frac{x_i-\theta_t}{1+(x_i-\theta_t)^2}.
$$
ニュートン法は $-\ell''$ が負になる点で更新方向が逆転するが、$I=n/2>0$ のスコアリングは安全。初期値には標本中央値などの頑健な推定値を使う。

## 関連

- [[最尤推定量]]
- [[フィッシャー情報量]]
- [[指数型分布族]]
- [[非線形方程式の数値解法]]
- [[ポアソン分布]]

## 使われる問題

![[概念別問題一覧.base]]

## 過去問の計算形式に対応するオリジナル演習

> [!note] 出題との関係
> **2024年 統計数理 問1** のようなスコア・情報量の導出が前提になる。以下の反復アルゴリズム自体は発展問題として作成したもの。

**問題** $X_1,\dots,X_n\overset{\mathrm{iid}}{\sim}\operatorname{Po}(\lambda)$、観測標本平均 $\bar x=2$ とする。$\lambda_0=1$ から始め、(1) ニュートン–ラフソン法、(2) Fisher scoring法を1回適用して比較せよ。

> [!success]- 解答・導出
>
> 対数尤度を $\ell(\lambda)=n\bar x\log\lambda-n\lambda+\mathrm{const}$ とすれば
>
> $$
> S(\lambda)=\frac{n\bar x}{\lambda}-n,\quad
> J(\lambda)=-\ell''(\lambda)=\frac{n\bar x}{\lambda^2},\quad
> I(\lambda)=\frac n\lambda.
> $$
>
> $\lambda_0=1,\bar x=2$ なので
>
> $$
> \lambda_1^{\rm NR}=1+\frac{2n-n}{2n}=\frac32,\qquad
> \lambda_1^{\rm FS}=1+\frac{2n-n}{n}=2.
> $$
>
> 最尤推定値 $\hat\lambda=\bar x=2$ なので、この場合はFisher scoringが1回で到達する。NRをもう1回行えば
>
> $$
> \lambda_2^{\rm NR}=2\cdot\frac32-\frac{(3/2)^2}{2}=\frac{15}{8}.
> $$
>
> **理由**：$I(\lambda)=E[J(\lambda)]$ であるが、観測された $\bar x$ を $E[\bar X]=\lambda$ に置き換えるために更新が異なる。

**注意**：ここで $I(\lambda)$ は標本全体の情報量。1観測あたりの情報量 $1/\lambda$ と混同しない。
