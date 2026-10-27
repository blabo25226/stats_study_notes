---
test-category: 統計応用
stats-category: 分散分析
tags:
  - 線形対比
  - Dunnett検定
  - 多変量t分布
  - 用量反応
created: 2026-10-19
updated: 2026-10-26
---

# 線形対比とDunnett検定

## 定義

群平均 $\mu_1,\dots,\mu_a$ に対する線形対比は
$$
\psi=\sum_{i=1}^a c_i\mu_i,\quad \sum_i c_i=0
$$
推定量 $\hat\psi=\sum c_i\bar y_{i\cdot}$、$\operatorname{Var}(\hat\psi)=\sigma^2\sum c_i^2/n_i$。$H_0:\psi=0$ は
$$
t=\frac{\hat\psi}{\sqrt{MS_E\sum c_i^2/n_i}}\sim t(N-a)
$$
で検定する（[[t分布]]）。

## 要点

- 係数和が $0$ なので全群共通のレベルの違いが打ち消され、群間の差だけを表す。
- 直交性: 対比 $c,c'$ が $\sum c_ic'_i/n_i=0$ のとき $\hat\psi,\hat\psi'$ は無相関（正規なら独立）。平衡なら $\sum c_ic_i'=0$。互いに直交する $a-1$ 個の対比の平方和は群間平方和 $S_A$ を分解する。
- 線形用量反応: 4用量・等間隔・各群同数のとき対比係数は $(-3,-1,1,3)$（線形トレンド）。$\sum c_i=0$、$\sum c_i^2=20$。
- Dunnett検定: 対照群（$0$）と各処理群 $j=1,\dots,k$ の差を同時に比較する。統計量 $T_j=(\bar y_j-\bar y_0)/\sqrt{MS_E(1/n_j+1/n_0)}$。共通の $\bar y_0$ を含むため相関する:
$$
\operatorname{Corr}(T_j,T_k)=\frac{1/n_0}{\sqrt{(1/n_j+1/n_0)(1/n_k+1/n_0)}}=\sqrt{\frac{n_jn_k}{(n_j+n_0)(n_k+n_0)}}
$$
  （分子は $\operatorname{Cov}(\bar y_j-\bar y_0,\bar y_k-\bar y_0)/\sigma^2=1/n_0$、分母は各分散 $1/n_j+1/n_0$ から。）等しい標本サイズでは $1/2$。
- $(T_1,\dots,T_k)$ は共通の $MS_E$ を分母に持つ多変量 $t$ 分布に従う。臨界値は $\max_j|T_j|$ の分布（多変量 $t$ の分位点）から決め、$k$ 個の比較全体の第1種の過誤確率（FWER）を $\alpha$ に保つ。Bonferroni 法より相関を利用する分だけ検出力が高い。
- 多重性の一般論は[[多重比較]]を参照。

## 対比の分散と例題（過去問改題）

独立な群平均 $\bar Y_i$ が分散 $\sigma^2/n_i$ を持つとき、$\hat\psi=\sum_ic_i\bar Y_i$ の分散は

$$
\operatorname{Var}(\hat\psi)=\sigma^2\sum_i\frac{c_i^2}{n_i}.
$$

> [!note] 出典
> 2024年 統計応用（医薬生物学）問4〔4〕〔5〕〔6〕の数値を変更（用量 $0,40,80,120$ mg（等間隔）$\to0,10,20,40$ mg（不等間隔）、群平均・$\sigma^2$・$n_j$ を与えて検定まで行う形にした）。

**問題** プラセボ（0mg）と3用量（10, 20, 40mg）の4群、各群 $n=10$ 人で、$Y_{ij}\sim N(\mu_j,\sigma^2)$、$\sigma^2=4$（既知）とする。群平均は $(\bar Y_0,\bar Y_1,\bar Y_2,\bar Y_3)=(5.0,\ 5.4,\ 6.0,\ 7.2)$ だった。

1. 用量に対して $\mu_j$ が直線的に増加するかを調べる対比ベクトルを作り、$Z=\sum c_j\bar Y_j/\sqrt{\sigma^2\sum c_j^2/n_j}$ で片側2.5%検定せよ。
2. 1.の対比と $(-3,1,1,1)$ の対比の検定統計量の、帰無仮説の下での相関係数を求めよ。
3. Dunnett型の統計量 $Z_j=(\bar Y_j-\bar Y_0)/\sqrt{\sigma^2(1/n_j+1/n_0)}$ の相関係数を、(a) 全群10人、(b) プラセボ20人・各用量群10人のときに求めよ。

> [!success]- 解答
>
> **1.** 係数は用量の中心化 $d_j-\bar d$ に比例させる。$\bar d=70/4=17.5$ なので $(-17.5,-7.5,2.5,22.5)\propto c=(-7,-3,1,9)$（和0、$\sum c_j^2=140$）。等間隔でないので $(-3,-1,1,3)$ ではない。
>
> $$
> \hat\psi=-35-16.2+6.0+64.8=19.6,\qquad
> \sqrt{4\times140/10}=\sqrt{56}=7.483,\qquad
> Z=\frac{19.6}{7.483}=\boxed{2.62}>1.96.
> $$
>
> 直線的な用量反応があると判断する。
>
> **2.** 各群同数なので $\operatorname{Corr}=\dfrac{\sum c_jd_j}{\sqrt{\sum c_j^2\sum d_j^2}}$。$\sum c_jd_j=21-3+1+9=28$、$\sum d_j^2=12$ より
>
> $$
> \operatorname{Corr}=\frac{28}{\sqrt{140\times12}}=\frac{28}{\sqrt{1680}}=\frac{28}{40.99}=\boxed{0.683}.
> $$
>
> **3.** $\operatorname{Corr}(Z_j,Z_k)=\sqrt{\dfrac{n_jn_k}{(n_j+n_0)(n_k+n_0)}}$ より、(a) $\dfrac{10}{20}=\boxed{\dfrac12}$、(b) $\dfrac{10}{30}=\boxed{\dfrac13}$。プラセボ群を大きくすると共通の $\bar Y_0$ の寄与が減り、相関が下がる。

## 線形対比t検定とDunnett同時検定の帰無分布

独立な$k$群の観測がそれぞれ$N(\mu_i,\sigma^2)$、群$n_i\ge1$、総数$N>k$とする。$\sum_ic_i=0$の対比$L=\sum_i c_i\bar Y_i$は正規和なので

$$
L\sim N\!\left(\sum_ic_i\mu_i,\ \sigma^2\sum_i\frac{c_i^2}{n_i}\right).
$$

群内残差から得る$MSE$は、正規の直交分解より $(N-k)MSE/\sigma^2\sim\chi^2_{N-k}$。$L$と残差平方和は独立。帰無仮説$\sum_ic_i\mu_i=0$の下で

$$
\boxed{T_L=\frac{L}{\sqrt{MSE\sum_ic_i^2/n_i}}\sim t_{N-k}}.
$$

**Dunnett法**では対照0と各処置群$j$との差$D_j=\bar Y_j-\bar Y_0$を**同時**に検定する。各差は共通の$\bar Y_0$を持つため

$$
\operatorname{Cov}(D_j,D_\ell)=\sigma^2/n_0\quad(j\ne\ell).
$$

従って標準化$t$値は**相関する多変量t分布**で、最大絶対値の帰無分布を用いて閾値を決める。各差を独立な$t$検定として処理してはいけない。

## Dunnett統計量の**同時**帰無分布の証明

独立な正規群$Y_{ij}\sim N(\mu_j,\sigma^2)$、対照群$j=0$と処置群$j=1,\ldots,k$。$N=\sum_{j=0}^kn_j$、$\nu=N-(k+1)>0$、$MS_E$は群内残差平均平方とする。差$D_j=\bar Y_j-\bar Y_0$について、帰無仮説$H_0:\mu_j=\mu_0$（全$j$）では

$$
\operatorname{Var}(D_j)=\sigma^2\left(\frac1{n_j}+\frac1{n_0}\right),\qquad
\operatorname{Cov}(D_j,D_\ell)=\frac{\sigma^2}{n_0}\quad(j\ne\ell).
$$

各差は同じ対照平均$\bar Y_0$を共有するため、**相関係数**は

$$
\boxed{R_{j\ell}=
\frac{1/n_0}{\sqrt{(1/n_j+1/n_0)(1/n_\ell+1/n_0)}}\quad(j\ne\ell)}.
$$

差のベクトルを標準化して$Z=(Z_1,\ldots,Z_k)^\top\sim N_k(0,R)$。Cochranの定理で

$$
V=\frac{\nu\,MS_E}{\sigma^2}\sim\chi_\nu^2,\qquad Z\perp V.
$$

従って全ての対照比較のt統計量は**同じ分母**を共有し

$$
\boxed{(T_1,\ldots,T_k)^\top
=\frac{Z}{\sqrt{V/\nu}}\sim t_{k,\nu}(0,R)}
$$

（相関行列$R$、自由度$\nu$の多変量Student t）。各成分だけを見れば$t_\nu$だが**成分同士は独立ではない**。

両側のDunnett同時検定では$P(\max_j|T_j|\le c_\alpha)=1-\alpha$を満たす臨界値$c_\alpha$を**上記同時分布から**求め、各$|T_j|>c_\alpha$を棄却する。この仕組みで完全帰無下のFWERが$\alpha$になり、部分帰無下も真の比較だけの周辺同時分布が維持されるため**強いFWER制御**を得る。個別の$t$分布の臨界値を使うだけでは多重性を調整できない。

**問題** 対照・2処置群がすべて$n_j=5$なら、2本の比較の相関と残差自由度を求めよ。

> [!success]- 解答
>
> $\nu=15-3=\boxed{12}$、$R_{12}=(1/5)/\sqrt{(2/5)(2/5)}=\boxed{1/2}$。二変量t分布の自由度は12、潜在正規相関行列の非対角成分は1/2。

## 関連

- [[多重比較]]
- [[一元配置分散分析]]
- [[t分布]]
- [[閉手順]]

## 使われる問題

### 教科書（現代数理統計学の基礎）

![[概念別教科書問題一覧.base]]

### 統計検定1級 過去問

![[概念別過去問一覧.base]]
