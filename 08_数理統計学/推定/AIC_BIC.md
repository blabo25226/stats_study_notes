---
test-category: 統計応用
stats-category: 推定
tags:
  - AIC
  - BIC
  - モデル選択
  - 情報量規準
  - 予測誤差
created: 2026-10-19
updated: 2026-10-26
---

# AIC_BIC

## 定義

最大対数尤度 $\ell(\hat\theta)=\log L(\hat\theta)$、自由パラメータ数 $k$、標本サイズ $n$ に対し
$$
\mathrm{AIC}=-2\ell(\hat\theta)+2k,\qquad \mathrm{BIC}=-2\ell(\hat\theta)+k\log n
$$
値が小さいモデルを選ぶ。

## 要点

- 第1項はあてはまりの悪さ、第2項はパラメータ数に対する罰則。入れ子（nested）のモデルでは、パラメータを増やした大きいモデルの最大対数尤度 $\ell(\hat\theta)$ は小さいモデルより悪くならない（等しいか大きい）。そのため罰則なしでは、入れ子の列の中で最大のモデルが選ばれてしまう。構造の異なるモデル同士では、パラメータ数が多いほど最大対数尤度が大きいとは限らない。
- **AICの意味**：真の分布 $g$ とモデル $f_\theta$ の[[カルバック・ライブラー情報量]] $D(g\Vert f_{\hat\theta})$ の期待値を最小にしたい。$D$ のうち $\theta$ に依存する部分は $-E_g[\log f_{\hat\theta}(X^{\ast})]$（$X^{\ast}$ は新しい観測）。同じデータで評価した $\ell(\hat\theta)/n$ はこれを過大評価し、そのバイアスが（正則条件のもとで）漸近的に $k/n$ になる。これを補正して $2n$ 倍したものが AIC である。
- **BICの意味**：[[ベイズ推定の基本]]における周辺尤度 $\int L(\theta)\pi(\theta)\,d\theta$ のラプラス近似から $-2\log(\text{周辺尤度})\approx-2\ell(\hat\theta)+k\log n$ が出る。事前分布の項は $O(1)$ として落とす。
- **違い**：$\log n>2$（$n\ge8$）なら BIC の罰則のほうが重く、より小さいモデルを選びやすい。BIC は真のモデルが候補に含まれるとき一致性（真のモデルを選ぶ確率が1に収束）をもつ。AIC は予測の良さ（KL最小化）を目的とし、一致性は一般にもたない。
- 比較は同一データ・同一の尤度（定数項の扱いも同じ）で行う。AIC の差が小さい（目安 2 以内）なら優劣はほぼ付けられない。
- 入れ子のモデルでは[[尤度比検定]]と併用される。AIC差 $=$ 検定統計量 $-2\Delta k$ なので、「$\chi^2_{\Delta k}$ 統計量が $2\Delta k$ を超えたら大きいモデルを採用」と同値。

## パラメータ数の数え方

$k$ は平均構造のパラメータ数と分散共分散構造のパラメータ数の和（最尤法の場合）。反復測定データで $p$ 時点、共通の分散共分散構造を仮定するとき、共分散部分の個数は次のとおり。

| 構造 | 共分散のパラメータ数 |
|---|---|
| 複合対称（CS）：$\sigma^2,\ \rho$ | $2$ |
| AR(1) | $2$ |
| Toeplitz（ラグごとに共分散が異なる） | $p$ |
| 無構造（UN）：$p$ 個の分散と $p(p-1)/2$ 個の共分散 | $p(p+1)/2$ |

例：$p=4$ のとき CS は $2$、Toeplitz は $4$、無構造は $10$。平均構造のパラメータ数が $m$ なら、AIC の $k$ はそれぞれ $m+2,\ m+4,\ m+10$。無構造は最もよくあてはまるが罰則も最大で、CS や Toeplitz のほうが AIC が小さくなることがある。

## 自由パラメータの数え方

$k$ はモデルの**自由パラメータ数**であり、確率が1に足し合わさる等の制約を加味する。同じ標本・同じ確率密度の基準で最大対数尤度を比べる。

## 例題（過去問改題）

### 例題1：ヒストグラム密度のビン数選択

> [!note] 出典
> 2025年 統計数理 問1〔3〕〔4〕〔5〕の数値を変更（観測値を $n=6$ 個から $n=8$ 個の別データに変更）。

$[0,1)$ を $m$ 等分した小区間 $I_j$ 上で一定値 $\theta_j$ をとる密度 $f_m(x;\boldsymbol\theta)$ をモデルとする（$\theta_j\ge0$、$\sum_j\theta_j/m=1$）。$I_j$ に入る観測数を $N_j$ とする。

(1) $\theta_j$ の最尤推定量と AIC を求めよ。
(2) $n=8$、観測値 $0.03,\ 0.10,\ 0.16,\ 0.22,\ 0.52,\ 0.61,\ 0.83,\ 0.97$ のとき、$m\in\{2,3,4\}$ のうち AIC 最小のものを選べ。$\log2=0.693$、$\log3=1.099$ を用いてよい。

> [!success]- 解答
>
> (1) 尤度は $L=\prod_j\theta_j^{N_j}$。制約 $\sum_j\theta_j=m$ のもとでラグランジュ未定乗数法を使うと $N_j/\theta_j=\text{一定}$ なので
>
> $$
> \hat\theta_j=\frac{mN_j}{n},\qquad
> \mathrm{AIC}=-2\sum_{j:N_j>0}N_j\log\frac{mN_j}{n}+2(m-1).
> $$
>
> 制約が1本あるので自由パラメータ数は $m-1$。
>
> (2) 各 $m$ の度数と推定値は次のとおり。
>
> | $m$ | $(N_j)$ | $(\hat\theta_j)$ | 最大対数尤度 | AIC |
> |---|---|---|---|---|
> | 2 | $(4,4)$ | $(1,1)$ | $0$ | $0+2=2$ |
> | 3 | $(4,2,2)$ | $(3/2,\ 3/4,\ 3/4)$ | $8\log3-12\log2=0.476$ | $-0.952+4=3.048$ |
> | 4 | $(4,0,2,2)$ | $(2,\ 0,\ 1,\ 1)$ | $4\log2=2.772$ | $-5.544+6=0.456$ |
>
> $m=3$ の対数尤度は $4\log\frac32+2\log\frac34+2\log\frac34=4(\log3-\log2)+4(\log3-2\log2)$ と分解した。AIC 最小は $\boxed{m=4}$。空のビン（$N_2=0$）を作れる細かい分割が、観測の偏りを捉えて罰則の増加を上回っている。

### 例題2：反復測定の共分散構造（AIC と BIC）

> [!note] 出典
> 2023年 統計応用（医薬生物学） 問4〔2〕の数値を変更（最大対数尤度 $-206.42,\ -204.87\to-150.30,\ -146.10$）。BIC による比較を追加。

3時点の反復測定（$N=40$ 人、3変量正規）で、平均ベクトル3個のほかに共分散を Toeplitz 構造（$\sigma_0,\sigma_1,\sigma_2$）とした場合の最大対数尤度が $-150.30$、無構造とした場合が $-146.10$ であった。AIC と BIC でそれぞれどちらの構造を選ぶか。$\log40=3.689$ を用いてよい。

> [!success]- 解答
>
> パラメータ数は Toeplitz が $3+3=6$、無構造が $3+6=9$（分散3個と共分散3個）。
>
> $$
> \mathrm{AIC}_{\rm T}=300.60+12=312.60,\qquad
> \mathrm{AIC}_{\rm U}=292.20+18=\boxed{310.20}
> $$
>
> なので AIC は無構造を選ぶ。BIC は
>
> $$
> \mathrm{BIC}_{\rm T}=300.60+6\times3.689=\boxed{322.73},\qquad
> \mathrm{BIC}_{\rm U}=292.20+9\times3.689=325.40
> $$
>
> で Toeplitz を選ぶ。$\log40>2$ なので BIC の罰則のほうが重く、小さいモデルが選ばれた。尤度比で見ると $2\times4.20=8.40$ が AIC の境界 $2\Delta k=6$ は超えるが、BIC の境界 $3\times3.689=11.07$ は超えない。AIC と BIC は目的が異なるので、結果が一致するとは限らない。

## 正規線形回帰での罰則項の厳密な導出

AICの罰則 $2k$ が「同じデータで評価した当てはまりの過大評価」から生じることを、正規線形回帰で**厳密に**確かめる（2023数理 問4 の題材）。

**設定** $\boldsymbol Y=X\boldsymbol\beta+\boldsymbol\varepsilon$、$\boldsymbol\varepsilon\sim N_n(\boldsymbol 0,\sigma^2I)$、$X$ は $n\times p$ で階数 $p$。射影行列 $H=X(X^\top X)^{-1}X^\top$ とし、

$$
\Delta(\boldsymbol Y)=\|\boldsymbol Y-H\boldsymbol Y\|^2,\qquad \hat\sigma^2=\Delta(\boldsymbol Y)/n\ \ (\text{MLE、除数 }n).
$$

$\boldsymbol Z=X\boldsymbol\beta+\boldsymbol\varepsilon'$ は $\boldsymbol Y$ と独立な「将来のデータ」で、$\Delta(\boldsymbol Z)=\|\boldsymbol Z-H\boldsymbol Y\|^2$ とする。

**1. 二つの平方和の分布**（[[射影行列と二次形式]]）
$$
W_1=\frac{\Delta(\boldsymbol Y)}{\sigma^2}=\frac{\boldsymbol\varepsilon^\top(I-H)\boldsymbol\varepsilon}{\sigma^2}\sim\chi^2_{n-p},\qquad
W_2=\frac{\|H\boldsymbol Y-X\boldsymbol\beta\|^2}{\sigma^2}=\frac{\boldsymbol\varepsilon^\top H\boldsymbol\varepsilon}{\sigma^2}\sim\chi^2_p,
$$
$H(I-H)=O$ なので $W_1$ と $W_2$ は独立。

**2. 将来データでの残差平方和** $\boldsymbol Z-H\boldsymbol Y=\boldsymbol\varepsilon'+(X\boldsymbol\beta-H\boldsymbol Y)$ で、$\boldsymbol\varepsilon'$ は $\boldsymbol Y$ と独立・平均0なので交差項が消え
$$
E[\Delta(\boldsymbol Z)\mid\boldsymbol Y]=n\sigma^2+\|H\boldsymbol Y-X\boldsymbol\beta\|^2=\sigma^2(n+W_2).
$$

**3. 過大評価の期待値** $\Delta(\boldsymbol Y)/\hat\sigma^2=n$ を使うと
$$
E\!\left[\frac{\Delta(\boldsymbol Z)-\Delta(\boldsymbol Y)}{\hat\sigma^2}\right]
=E\!\left[\frac{n(n+W_2)}{W_1}\right]-n
=n(n+p)\,E\!\left[\frac1{W_1}\right]-n
=\boxed{\frac{2n(p+1)}{n-p-2}}.
$$
ここで独立性と $E[1/\chi^2_\nu]=1/(\nu-2)$（$\nu>2$、[[カイ二乗分布]]）を使った。$n\to\infty$ で $\boxed{2(p+1)}$。

**4. AICとの対応** 推定値を代入した $-2\log f(\cdot\,;\hat{\boldsymbol\beta},\hat\sigma^2)$ は $n\log(2\pi\hat\sigma^2)+\Delta(\cdot)/\hat\sigma^2$ なので、上の量は「将来データの $-2\times$対数尤度」と「手元データの $-2\times$最大対数尤度」の差の期待値そのもの。自由パラメータは $\boldsymbol\beta$ の $p$ 個と $\sigma^2$ の1個で $k=p+1$ だから、極限 $2(p+1)=2k$ が AIC の罰則に一致する。有限 $n$ の厳密値 $2kn/(n-k-1)$ を罰則に使うのが小標本補正版 AICc。

**問題** $n=20$、$p=3$ のとき、過大評価の厳密な期待値と AIC の罰則を比べよ。

> [!success]- 解答
>
> $k=p+1=4$。厳密値は
>
> $
> \frac{2\cdot20\cdot4}{20-3-2}=\frac{160}{15}=10.67,
> $
>
> AIC の罰則は $2k=8$。小標本では AIC の罰則が過大評価を補いきれず、パラメータの多いモデルを選びやすい。$n=200$ なら $1600/195=8.21$ で、ほぼ8に近づく。

## 関連

- [[カルバック・ライブラー情報量]]
- [[最尤推定量]]
- [[尤度比検定]]
- [[ベイズ推定の基本]]

## 使われる問題

![[概念別問題一覧.base]]
