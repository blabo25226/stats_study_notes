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
updated: 2026-10-29
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

**二成分正規混合** $\pi\phi(x;\mu_1,\sigma_1^2)+(1-\pi)\phi(x;\mu_2,\sigma_2^2)$。確率モデルは $X_1,\dots,X_n$ が独立にこの混合密度に従う（未知母数 $\theta=(\pi,\mu_1,\mu_2,\sigma_1^2,\sigma_2^2)$、$0<\pi<1$）。最大化したい観測尤度は
$$
L(\theta)=\prod_{i=1}^n\bigl\{\pi\phi(x_i;\mu_1,\sigma_1^2)+(1-\pi)\phi(x_i;\mu_2,\sigma_2^2)\bigr\}
$$
で、対数をとっても和の対数が残るため陽に最大化できない（さらに $\mu_k=x_i,\ \sigma_k^2\downarrow0$ で非有界になるので、内部の局所最大を求める）。潜在変数 $z_i\in\{1,2\}$ は成分ラベルで、$P(z_i=1)=\pi$、$X_i\mid z_i=k\sim N(\mu_k,\sigma_k^2)$。完全データ尤度は $\prod_i\{\pi\phi(x_i;\mu_1,\sigma_1^2)\}^{\mathbf 1\{z_i=1\}}\{(1-\pi)\phi(x_i;\mu_2,\sigma_2^2)\}^{\mathbf 1\{z_i=2\}}$。
- E-step（責任度）: $\gamma_i=\dfrac{\pi\phi_1(x_i)}{\pi\phi_1(x_i)+(1-\pi)\phi_2(x_i)}$（$\phi_k$ は現在の $\theta_t$ で評価）。
- M-step:
$$
\pi=\frac1n\sum\gamma_i,\quad
\mu_1=\frac{\sum\gamma_ix_i}{\sum\gamma_i},\quad
\sigma_1^2=\frac{\sum\gamma_i(x_i-\mu_1)^2}{\sum\gamma_i},
$$
$\mu_2,\sigma_2^2$ は重み $1-\gamma_i$ で同様。完全データ対数尤度が $\gamma_i$ で重み付けした正規分布の対数尤度になるため。

**指数分布の打ち切りデータ**: 確率モデルは $X_1,\dots,X_n\overset{\rm iid}{\sim}\text{Ex}(\lambda)$（密度 $\lambda e^{-\lambda x}$、$x>0$、未知母数 $\lambda>0$、打ち切り時点 $c$ は既知）。$n$ 個のうち $m$ 個が時点 $c$ で打ち切られ（$X_i>c$ とのみ分かる）、残り $r=n-m$ 個の観測値の和を $s$ とする。観測尤度は、観測された個体の寄与が密度 $\lambda e^{-\lambda x_i}$、打ち切られた個体の寄与が生存確率 $P(X_i>c)=e^{-\lambda c}$ なので
$$
L(\lambda)=\prod_{\text{観測}}\lambda e^{-\lambda x_i}\prod_{\text{打ち切り}}e^{-\lambda c}=\lambda^re^{-\lambda(s+mc)},\qquad \ell(\lambda)=r\log\lambda-\lambda(s+mc).
$$
$\ell''=-r/\lambda^2<0$ なので、直接最大化すれば $r\ge1$ のとき $\hat\lambda=r/(s+mc)$。これをEMでも求めてみる。完全データ（打ち切られた $X_i$ の値も分かった場合）の尤度は $\lambda^ne^{-\lambda\sum X_i}$、対数尤度は $n\log\lambda-\lambda\sum X_i$。メモリレス性より $X-c\mid X>c\sim\text{Ex}(\lambda)$ なので
$$
E[X\mid X>c]=c+\frac1\lambda.
$$
- E-step: 打ち切り分を $c+1/\lambda_t$ で置き換える。
- M-step: $\lambda_{t+1}=\dfrac{n}{s+m(c+1/\lambda_t)}$。
- 不動点では $n/\lambda=s+mc+m/\lambda$ より $\hat\lambda=r/(s+mc)$ となり、[[打ち切りと尤度]]から直接求めた最尤推定量と一致する。

検算（$n=5$、$m=2$、$c=3$、$s=6$）: $\hat\lambda=3/(6+6)=0.25$。$\lambda_0=0.5$ から $\lambda_1=5/16=0.3125$、$\lambda_2=5/18.4\approx0.272$ と $0.25$ に近づく。$u=1/\lambda$ で書くと $u_{t+1}=(12+2u_t)/5$ で、不動点 $u=4$、収束率 $m/n=0.4$（線形収束で、率は欠測の割合）。

## 遺伝子計数法：ABO血液型の対立遺伝子頻度

2019医薬 問5 の型。対立遺伝子 A, B, O の頻度を $p,q,r$（$p+q+r=1$、未知母数）、ハーディ・ワインベルグ平衡を仮定すると遺伝子型の確率は AA $p^2$、AO $2pr$、BB $q^2$、BO $2qr$、AB $2pq$、OO $r^2$。観測できるのは表現型の度数 $n_A,n_B,n_{AB},n_O$（計 $n$）だけで、A型の中の AA と AO の内訳が潜在変数。

確率モデルは、$n$ 人の表現型が独立に確率 $(p^2+2pr,\ q^2+2qr,\ 2pq,\ r^2)$ で A, B, AB, O をとる、すなわち $(n_A,n_B,n_{AB},n_O)$ がこの確率の多項分布に従うというもの。最大化したい観測尤度は
$$
L(p,q,r)=\frac{n!}{n_A!\,n_B!\,n_{AB}!\,n_O!}(p^2+2pr)^{n_A}(q^2+2qr)^{n_B}(2pq)^{n_{AB}}(r^2)^{n_O}
$$
で、$p^2+2pr$ のような和を含むため、制約 $p+q+r=1$ の下のスコア方程式は陽に解けない。そこで遺伝子型の度数を完全データとして EM を使う。

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
- [[欠測]]

## 使われる問題

### 教科書（現代数理統計学の基礎）

![[概念別教科書問題一覧.base]]

### 統計検定1級 過去問

![[概念別過去問一覧.base]]

## 例題（過去問改題）

### 例題1：ゼロ切断二項分布の反復解法をEMとして読む

> [!note] 出典
> 2018年 統計数理 問3〔3〕〔5〕の数値を変更（$n$ を一般から $n=4$、$\bar y=2$ に固定）。原問は反復スキームの構成までで、EMとしての解釈と数値反復は追加した設問。

$X\sim\operatorname{Bin}(4,\theta)$ のうち $X\ge1$ のときだけ記録される（ゼロ切断）。記録された $m$ 個の観測値の平均が $\bar y=2$ だった。

1. 尤度方程式が $4\hat\theta=\bar y\{1-(1-\hat\theta)^4\}$ となることを示せ。
2. 記録されなかった「$X=0$ の試行」の個数を潜在変数とみなすと、反復 $\theta^{(t+1)}=\bar y\{1-(1-\theta^{(t)})^4\}/4$ が EM アルゴリズムになることを説明せよ。
3. 初期値 $\theta^{(0)}=\bar y/4=0.5$ から2回更新せよ。

> [!success]- 解答
>
> 1. 確率モデルは、記録値 $Y_1,\dots,Y_m$ が独立にゼロ切断二項分布に従う（未知母数 $0<\theta<1$）というもの。1個あたりの確率関数は $h(y;\theta)=\binom4y\theta^y(1-\theta)^{4-y}/\{1-(1-\theta)^4\}$（$y=1,\dots,4$）なので、観測値を代入した尤度関数は $L(\theta)=\prod_{j=1}^mh(y_j;\theta)$ で
>
> $$
> \ell(\theta)=\log L(\theta)=m\bar y\log\theta+m(4-\bar y)\log(1-\theta)-m\log\{1-(1-\theta)^4\}+\text{const}.
> $$
>
> $\ell'(\theta)=0$ は $\dfrac{\bar y}{\theta}-\dfrac{4-\bar y}{1-\theta}-\dfrac{4(1-\theta)^3}{1-(1-\theta)^4}=0$ で、両辺に $\theta(1-\theta)\{1-(1-\theta)^4\}$ を掛けて整理すると $4\hat\theta=\bar y\{1-(1-\hat\theta)^4\}$。この分布は自然母数 $\log\{\theta/(1-\theta)\}$ の指数型分布族なので $\ell$ は自然母数について狭義凹で、$1<\bar y<4$ なら $(0,1)$ 内の解は1つでそれが最大点。陽には解けないので反復で求める（2., 3.）。
>
> 2. 完全データは「記録された $m$ 個」と「記録されなかった $X=0$ の試行 $K$ 個」。完全データ対数尤度は $m\bar y\log\theta+\{4(m+K)-m\bar y\}\log(1-\theta)$ で $K$ について1次式。
>
> - **E-step**：1回の記録の前に失われる $X=0$ の個数は幾何分布型で、$E[K\mid\theta^{(t)}]=m\dfrac{(1-\theta^{(t)})^4}{1-(1-\theta^{(t)})^4}$。よって $m+E[K]=\dfrac{m}{1-(1-\theta^{(t)})^4}$。
> - **M-step**：成功数 $m\bar y$ を試行総数 $4(m+E[K])$ で割る：
>
> $$
> \theta^{(t+1)}=\frac{m\bar y}{4m/\{1-(1-\theta^{(t)})^4\}}=\frac{\bar y\{1-(1-\theta^{(t)})^4\}}{4}.
> $$
>
> 不動点は 1. の尤度方程式そのもの。
>
> 3. $\bar y=2$ なので $\theta^{(t+1)}=0.5\{1-(1-\theta^{(t)})^4\}$。
>
> - $\theta^{(1)}=0.5(1-0.5^4)=0.5(1-0.0625)=0.46875$
> - $1-\theta^{(1)}=0.53125$、$0.53125^2=0.28223$、$0.28223^2=0.07965$ より $\theta^{(2)}=0.5(1-0.07965)=0.4602$
>
> 反復を続けると $\hat\theta=0.4563$ に収束する（$4\times0.4563/\{1-0.5437^4\}=2.00$ で検算できる）。

**補足**：通常のEMでは観測対数尤度は非減少だが、一般に「常に線形速度で収束する」「必ず大域最大に収束する」という保証はない。局所挙動はモデルの正則性と初期値に依存する。
