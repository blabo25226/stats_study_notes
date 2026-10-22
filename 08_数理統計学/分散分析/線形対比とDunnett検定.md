---
test-category: 統計応用
stats-category: 分散分析
tags:
  - 線形対比
  - Dunnett検定
  - 多変量t分布
  - 用量反応
created: 2026-10-19
updated: 2026-10-22
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

## 対比の分散とオリジナル演習

独立な群平均 $\bar Y_i$ が分散 $\sigma^2/n_i$ を持つとき、$\hat\psi=\sum_ic_i\bar Y_i$ の分散は

$
\operatorname{Var}(\hat\psi)=\sigma^2\sum_i\frac{c_i^2}{n_i}.
$

**問題** 3群（対照0・低用量1・高用量2）の各群標本数$n=5$。線形トレンド対比$c=(-1,0,1)$について、推定値と標準誤差を群平均$(2,3,5)$、共通残差平均平方$MS_E=2$から求めよ。

> [!success]- 解答
>
> $\hat\psi=-2+0\cdot3+5=\boxed{3}$。
>
> $
> \widehat{\operatorname{Var}}(\hat\psi)=2\left(\frac15+0+\frac15\right)=\frac45,\quad
> \widehat{\operatorname{SE}}(\hat\psi)=\sqrt{\frac45}.
> $
>
> $t=3/\sqrt{4/5}$（自由度は残差自由度）で検定。Dunnettは**対照との差を複数同時に検定する別の多重比較手順**なので、単一の線形トレンド対比と区別する。

## 関連

- [[多重比較]]
- [[一元配置分散分析]]
- [[t分布]]
- [[閉手順]]

## 使われる問題

![[概念別問題一覧.base]]
