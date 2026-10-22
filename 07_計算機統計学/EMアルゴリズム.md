---
test-category: 統計数理
stats-category: 計算機統計学
tags:
  - EMアルゴリズム
  - 潜在変数
  - 混合分布
  - 打ち切りデータ
  - ジェンセンの不等式
  - 遺伝子頻度
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
- 正則なモデルにおける局所収束は線形となることが多く、欠測情報の割合が大きいと一般に収束が遅くなる。到達点は局所解・鞍点になりうるので、複数の初期値を試す。
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

## 遺伝子計数法：ABO血液型の対立遺伝子頻度

2019医薬 問5 の型。対立遺伝子 A, B, O の頻度を $p,q,r$（$p+q+r=1$）、ハーディ・ワインベルグ平衡を仮定すると遺伝子型の確率は AA $p^2$、AO $2pr$、BB $q^2$、BO $2qr$、AB $2pq$、OO $r^2$。観測できるのは表現型の度数 $n_A,n_B,n_{AB},n_O$（計 $n$）だけで、A型の中の AA と AO の内訳が潜在変数。

**完全データ**（遺伝子型の度数）の対数尤度は[[多項分布]]から
$$
\log L_c=(2n_{AA}+n_{AO}+n_{AB})\log p+(2n_{BB}+n_{BO}+n_{AB})\log q+(n_{AO}+n_{BO}+2n_O)\log r+\text{const}.
$$
これを $N_A\log p+N_B\log q+N_O\log r$（$N$ は対立遺伝子の数、計 $2n$）と書く。

- **E-step**：A型の人が AA である条件付き確率は $p^2/(p^2+2pr)=p/(p+2r)$ なので
$$
n_{AA}^{(t)}=n_A\frac{p_t}{p_t+2r_t},\quad n_{AO}^{(t)}=n_A\frac{2r_t}{p_t+2r_t}
$$
（B型も同様）。$\log L_c$ は度数の1次式なので、度数を条件付き期待値で置き換えれば $Q$ になる。
- **M-step**：制約 $p+q+r=1$ の下で $N_A\log p+N_B\log q+N_O\log r$ を最大化する。ラグランジュ関数 $N_A\log p+\dots-\nu(p+q+r-1)$ を微分して $N_A/p=N_B/q=N_O/r=\nu$、総和から $\nu=2n$：
$$
p_{t+1}=\frac{N_A^{(t)}}{2n},\quad q_{t+1}=\frac{N_B^{(t)}}{2n},\quad r_{t+1}=\frac{N_O^{(t)}}{2n}
$$
（対立遺伝子を数えて割るだけ。これが「遺伝子計数法」の名前の由来）。

**問題** $n=100$ 人で A型40、B型12、AB型4、O型44。初期値 $p_0=q_0=r_0=1/3$ から1回更新せよ。

> [!success]- 解答
>
> E-step：$n_{AA}=40\times\frac{1/3}{1}=\frac{40}{3}$、$n_{AO}=\frac{80}{3}$、$n_{BB}=4$、$n_{BO}=8$。
>
> 対立遺伝子数：$N_A=2\cdot\frac{40}3+\frac{80}3+4=\frac{172}3$、$N_B=8+8+4=20$、$N_O=\frac{80}3+8+88=\frac{368}3$（計 $200$）。
>
> M-step：$p_1=\frac{172}{600}=\boxed{0.2867}$、$q_1=\frac{20}{200}=\boxed{0.1000}$、$r_1=\frac{368}{600}=\boxed{0.6133}$。
>
> 反復を続けると $(p,q,r)\to(0.2519,\ 0.0835,\ 0.6646)$ に収束し、観測尤度を直接最大化した値と一致する。

## 関連

- [[最尤推定量]]
- [[条件付き期待値]]
- [[打ち切りと尤度]]
- [[指数分布]]
- [[ニュートン法とFisher_scoring]]

## 使われる問題

![[概念別問題一覧.base]]

## 独自例題：潜在ラベルの事後確率と1回のEM更新

> [!note] 出題との関係
> **2018年 医薬生物学 問5（4分野共通問題）** では正規混合分布の性質が扱われる。以下は混合分布の潜在ラベル推定へ発展させたオリジナル問題であり、原問題にEMの指定はない。

**問題** 潜在ラベル $Z_i\in\{1,2\}$ について $P(Z_i=1)=\pi$、$X_i\mid Z_i=1\sim\operatorname{Bern}(1/4)$、$X_i\mid Z_i=2\sim\operatorname{Bern}(3/4)$ とする。観測値が $(x_1,x_2)=(1,0)$、現在の混合比が $\pi^{(0)}=1/4$ のとき、(1) E-stepで各観測が第1成分から来た責任度を求め、(2) M-stepで新しい $\pi^{(1)}$ を求めよ。

> [!success]- 解答・導出
>
> $x_1=1$ のときベイズ公式より
>
> $$
> \gamma_1=P(Z_1=1\mid X_1=1,\pi^{(0)})
> =\frac{(1/4)(1/4)}{(1/4)(1/4)+(3/4)(3/4)}=\frac1{10}.
> $$
>
> $x_2=0$ のときは
>
> $$
> \gamma_2=\frac{(1/4)(3/4)}{(1/4)(3/4)+(3/4)(1/4)}=\frac12.
> $$
>
> 完全データ対数尤度の混合比に関係する部分の条件付き期待値は
>
> $$
> Q(\pi\mid\pi^{(0)})=\sum_{i=1}^2\{\gamma_i\log\pi+(1-\gamma_i)\log(1-\pi)\}+\mathrm{const}.
> $$
>
> 微分して0と置くと $\pi^{(1)}=(\gamma_1+\gamma_2)/2$ なので
>
> $$
> \boxed{\pi^{(1)}=\frac{1/10+1/2}{2}=\frac3{10}}.
> $$
>
> 観測ラベルを決め打ちするのではなく、**条件付き確率で重み付け**するのがEMの要点。

**補足**：通常のEMでは観測対数尤度は非減少だが、一般に「常に線形速度で収束する」「必ず大域最大に収束する」という保証はない。局所挙動はモデルの正則性と初期値に依存する。
