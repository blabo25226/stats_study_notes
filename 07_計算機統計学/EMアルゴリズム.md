---
test-category: 統計数理
stats-category: 計算機統計学
tags:
  - EMアルゴリズム
  - 潜在変数
  - 混合分布
  - 打ち切りデータ
  - ジェンセンの不等式
created: 2026-10-22
updated: 2026-10-22
---

# EMアルゴリズム

## 定義

観測 $x$、潜在変数（欠測）$z$ があり、観測尤度 $f(x|\theta)=\int f(x,z|\theta)\,dz$ の最大化が難しいとき、完全データ $(x,z)$ の対数尤度を使って反復で[[最尤推定量]]を求める。
$$
Q(\theta|\theta_t)=E\bigl[\log f(x,Z|\theta)\,\big|\,x,\theta_t\bigr].
$$
- **E-step**: $Q(\theta|\theta_t)$ を計算する（$Z$ の条件付き分布 $f(z|x,\theta_t)$ のもとでの[[条件付き期待値]]）。
- **M-step**: $\theta_{t+1}=\arg\max_\theta Q(\theta|\theta_t)$。

## 要点

- **尤度は減らない**: $\log f(x|\theta)=Q(\theta|\theta_t)+H(\theta|\theta_t)$、$H(\theta|\theta_t)=-E[\log f(Z|x,\theta)\,|\,x,\theta_t]$ と分解する。ジェンセンの不等式（$-\log$ は凸）より $H(\theta|\theta_t)-H(\theta_t|\theta_t)=E\bigl[-\log\tfrac{f(Z|x,\theta)}{f(Z|x,\theta_t)}\bigr]\ge-\log E\bigl[\tfrac{f(Z|x,\theta)}{f(Z|x,\theta_t)}\bigr]=-\log1=0$。M-step で $Q(\theta_{t+1}|\theta_t)\ge Q(\theta_t|\theta_t)$ なので
  $\log f(x|\theta_{t+1})\ge\log f(x|\theta_t)$。
- 収束は**線形**で、速度は欠測情報の割合が大きいほど遅い。到達点は局所解・鞍点になりうるので、複数の初期値を試す。
- 各M-stepが閉形式になる問題（混合分布、打ち切り、指数型分布族）で特に有効。

## 例

**二成分正規混合** $\pi\phi(x;\mu_1,\sigma_1^2)+(1-\pi)\phi(x;\mu_2,\sigma_2^2)$。潜在変数 $z_i\in\{1,2\}$ は成分ラベル。
- E-step（責任度）: $\gamma_i=\dfrac{\pi\phi_1(x_i)}{\pi\phi_1(x_i)+(1-\pi)\phi_2(x_i)}$（$\phi_k$ は現在の $\theta_t$ で評価）。
- M-step:
$$
\pi=\frac1n\sum\gamma_i,\quad
\mu_1=\frac{\sum\gamma_ix_i}{\sum\gamma_i},\quad
\sigma_1^2=\frac{\sum\gamma_i(x_i-\mu_1)^2}{\sum\gamma_i},
$$
$\mu_2,\sigma_2^2$ は重み $1-\gamma_i$ で同様。完全データ対数尤度が $\gamma_i$ で重み付けした正規分布の対数尤度になるため。

**指数分布の打ち切りデータ**: $X_i\sim\text{Ex}(\lambda)$、$n$ 個のうち $m$ 個が時点 $c$ で打ち切られ（$X_i>c$ とのみ分かる）、残り $r=n-m$ 個の観測値の和を $s$ とする。完全データの対数尤度は $n\log\lambda-\lambda\sum X_i$。メモリレス性より $X-c\mid X>c\sim\text{Ex}(\lambda)$ なので
$$
E[X\mid X>c]=c+\frac1\lambda.
$$
- E-step: 打ち切り分を $c+1/\lambda_t$ で置き換える。
- M-step: $\lambda_{t+1}=\dfrac{n}{s+m(c+1/\lambda_t)}$。
- 不動点では $n/\lambda=s+mc+m/\lambda$ より $\hat\lambda=r/(s+mc)$ となり、[[打ち切りと尤度]]から直接求めた最尤推定量と一致する。

検算（$n=5$、$m=2$、$c=3$、$s=6$）: $\hat\lambda=3/(6+6)=0.25$。$\lambda_0=0.5$ から $\lambda_1=5/16=0.3125$、$\lambda_2=5/18.4\approx0.272$ と $0.25$ に近づく。$u=1/\lambda$ で書くと $u_{t+1}=(12+2u_t)/5$ で、不動点 $u=4$、収束率 $m/n=0.4$（線形収束で、率は欠測の割合）。

## 関連

- [[最尤推定量]]
- [[条件付き期待値]]
- [[打ち切りと尤度]]
- [[指数分布]]
- [[ニュートン法とFisher_scoring]]

## 使われる問題

![[概念別問題一覧.base]]
