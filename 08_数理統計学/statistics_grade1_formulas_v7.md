# 統計検定1級 SM・SA 暗記表

## 1. Cox部分尤度

$$
\lambda(t\mid\boldsymbol{x})=\lambda_0(t)e^{\boldsymbol\beta^\top\boldsymbol{x}},\qquad
L_p(\boldsymbol\beta)=\prod_{i:\delta_i=1}
\frac{e^{\boldsymbol\beta^\top\boldsymbol{x}_i}}
{\sum_{j\in R(t_i)}e^{\boldsymbol\beta^\top\boldsymbol{x}_j}}.
$$

$R(t_i)$：時刻$t_i$の直前のリスク集合（イベント時刻に同時イベントがない場合）。

## 2. Kaplan–Meier法（KM推定量）

$$
\hat S_{\mathrm{KM}}(t)=\prod_{t_j\le t}\left(1-\frac{d_j}{n_j}\right).
$$

$n_j$：イベント時刻$t_j$直前のリスク集合人数、$d_j$：その時刻のイベント数。

## 3. 感度・特異度

- **感度**：実際に疾患がある人のうち、検査で陽性と判定される人の割合。
- **特異度**：実際に疾患がない人のうち、検査で陰性と判定される人の割合。

## 4. ROC曲線・AUC

**ROC曲線**：横軸を $1-\text{特異度}$、縦軸を感度とする曲線。

**AUC**（$X$：陽性群のスコア、$Y$：陰性群のスコア、スコアが大きいほど陽性）：

$$
\mathrm{AUC}=P(X>Y)=\int_0^1\mathrm{ROC}(u)\,du
$$

**対数正規分布による近似**（$X,Y$ は独立で、$\log X\approx N(\mu_X,\sigma_X^2)$、$\log Y\approx N(\mu_Y,\sigma_Y^2)$）：

$$
\mathrm{AUC}\approx
\Phi\!\left(\frac{\mu_X-\mu_Y}{\sqrt{\sigma_X^2+\sigma_Y^2}}\right)
$$

## 5. Bonferroni法・FWER

$$
\mathrm{FWER}=P(\text{真の帰無仮説を1つ以上誤って棄却}).
$$

$m$個の帰無仮説を検定するとき、各検定に割り当てる有意水準は

$$
\alpha_i=\frac{\alpha}{m}\qquad(i=1,\ldots,m).
$$

## 6. TOST・生物学的同等性の判定

$\delta=\mu_T-\mu_R$（試験製剤$T$と対照製剤$R$の母平均の差）、同等性マージン$\Delta>0$について、

$$
H_0:\delta\le-\Delta\ \text{または}\ \delta\ge\Delta,
\qquad H_1:-\Delta<\delta<\Delta.
$$

二つの片側検定の統計量（推定値$\hat\delta$、標準誤差$\widehat{\mathrm{SE}}(\hat\delta)$）は

$$
T_L=\frac{\hat\delta+\Delta}{\widehat{\mathrm{SE}}(\hat\delta)},\qquad
T_U=\frac{\hat\delta-\Delta}{\widehat{\mathrm{SE}}(\hat\delta)}.
$$

$t$分布による検定では、両方の片側帰無仮説を棄却するとき同等と判定する：

$$
T_L>t_{1-\alpha,\nu}\quad\text{かつ}\quad
T_U<-t_{1-\alpha,\nu}.
$$

$$
\text{同等性の判定}\iff
\text{両側 }100(1-2\alpha)\%\text{ 信頼区間}\subset(-\Delta,\Delta).
$$

比の同等域が$(L,U)$の場合は、対数比$\delta=\log(\text{比})$についてマージン$(\log L,\log U)$を使って検定する（通常は$L=1/U$）。

## 7. 層別Cochran検定

第$k$層の度数を$n_{11k},n_{12k},n_{21k},n_{22k}$、群ごとの合計を$n_{1+k}=n_{11k}+n_{12k}$、$n_{2+k}=n_{21k}+n_{22k}$、$N_k=n_{1+k}+n_{2+k}$とする。

$$
\hat\pi_k=\frac{n_{11k}+n_{21k}}{N_k},\qquad
\hat E[n_{11k}]=n_{1+k}\hat\pi_k,
$$

$$
\hat V\left[n_{11k}-\hat E[n_{11k}]\right]
=\frac{n_{1+k}n_{2+k}}{N_k}\hat\pi_k(1-\hat\pi_k).
$$

$$
\boxed{
X_C=
\frac{\left(\displaystyle\sum_{k=1}^{K}(n_{11k}-\hat E[n_{11k}])\right)^2}
{\displaystyle\sum_{k=1}^{K}\hat V\left[n_{11k}-\hat E[n_{11k}]\right]}
\overset{H_0}{\approx}\chi_1^2
}
$$

## 8. ログランク検定

時刻$t_j$のリスク人数を$n_j=n_{1j}+n_{2j}$、全イベント数を$d_j$、群1のイベント数を$d_{1j}$とすると、

$$
O_{1j}=d_{1j},\qquad E_{1j}=d_j\frac{n_{1j}}{n_j},
$$

$$
V_{1j}=d_j\frac{n_{1j}}{n_j}\frac{n_{2j}}{n_j}\frac{n_j-d_j}{n_j-1}\quad(n_j>1),
$$

$$
Z=\frac{\sum_j(O_{1j}-E_{1j})}{\sqrt{\sum_jV_{1j}}},\qquad
Z^2\overset{H_0}{\approx}\chi_1^2.
$$

## 9. 超幾何分布の特性値

母集団$N$個中、成功$K$個。非復元で$n$個抽出した成功個数$X$について、$p=K/N$として、

$$
P(X=x)=\frac{\binom Kx\binom{N-K}{n-x}}{\binom Nn},
$$

$$
E[X]=np,\qquad
V(X)=np(1-p)\frac{N-n}{N-1}.
$$

成功指示変数$I_i,I_j$（$i\ne j$）では、

$$
\operatorname{Cov}(I_i,I_j)=-\frac{p(1-p)}{N-1}.
$$

## 10. ベータ関数

$$
B(a,b)=\int_0^1 t^{a-1}(1-t)^{b-1}\,dt
=\frac{\Gamma(a)\Gamma(b)}{\Gamma(a+b)}\qquad(a,b>0).
$$

正の整数 $a,b$ について、

$$
B(a,b)=\frac{(a-1)!(b-1)!}{(a+b-1)!}.
$$

## 11. 経験分布関数

$$
F_n(x)=\frac1n\sum_{i=1}^n\mathbf{1}\{X_i\le x\}.
$$

独立同分布標本では、

$$
nF_n(x)\sim\operatorname{Bin}(n,F(x)),\quad
E[F_n(x)]=F(x),\quad
\operatorname{Var}(F_n(x))=\frac{F(x)(1-F(x))}{n}.
$$

## 12. AIC・BIC

$$
\mathrm{AIC}=-2\ell(\hat\theta)+2k,\qquad
\mathrm{BIC}=-2\ell(\hat\theta)+k\log n.
$$

$\ell(\hat\theta)$：最大対数尤度、$k$：自由パラメータ数、$n$：標本サイズ。

## 13. KL情報量

$$
D_{\mathrm{KL}}(P\Vert Q)
=E_P\!\left[\log\frac{p(X)}{q(X)}\right].
$$

$$
D_{\mathrm{KL}}(P\Vert Q)\ge0,\qquad
D_{\mathrm{KL}}(\mathrm{Ber}(p)\Vert\mathrm{Ber}(q))
=p\log\frac pq+(1-p)\log\frac{1-p}{1-q}.
$$

## 14. 正規線形モデルの標本分布

$$
\boldsymbol Y=X\boldsymbol\beta+\boldsymbol\varepsilon,\qquad
\boldsymbol\varepsilon\sim N_n(\boldsymbol0,\sigma^2I_n),\quad
\operatorname{rank}(X)=p<n.
$$

$$
\hat{\boldsymbol\beta}=(X^\top X)^{-1}X^\top\boldsymbol Y
\sim N_p\!\left(\boldsymbol\beta,\sigma^2(X^\top X)^{-1}\right).
$$

$$
\mathrm{SSE}
=\sum_{i=1}^n\bigl(Y_i-\boldsymbol x_i^\top\hat{\boldsymbol\beta}\bigr)^2
=\|\boldsymbol Y-X\hat{\boldsymbol\beta}\|^2.
$$

$$
\frac{\mathrm{SSE}}{\sigma^2}\sim\chi^2_{n-p},\qquad
\hat{\boldsymbol\beta}\perp\!\!\!\perp\mathrm{SSE},\qquad
s^2=\frac{\mathrm{SSE}}{n-p}.
$$

$$
\frac{\boldsymbol c^\top\hat{\boldsymbol\beta}-\boldsymbol c^\top\boldsymbol\beta}
{s\sqrt{\boldsymbol c^\top(X^\top X)^{-1}\boldsymbol c}}
\sim t_{n-p}.
$$

## 15. 符号検定

差が0でない独立な対応差$D_1,\dots,D_n$について、

$$
T=\sum_{i=1}^n\mathbf1\{D_i>0\},\qquad
H_0:P(D_i>0)=\frac12,
$$

$$
T\sim\operatorname{Bin}\!\left(n,\frac12\right),\quad
E_0[T]=\frac n2,\quad V_0(T)=\frac n4,\quad
Z=\frac{T-n/2}{\sqrt{n/4}}\ \overset{\mathrm{approx}}\sim N(0,1).
$$

## 16. Wilcoxon符号付き順位検定

非ゼロの対応差の絶対値順位を$r_i$、符号が正のものの順位和を$W^+=\sum_{D_i>0}r_i$とする。同順位がなく、帰無仮説下で差の分布が0を中心に対称なら、

$$
E_0[W^+]=\frac{n(n+1)}4,\qquad
V_0(W^+)=\frac{n(n+1)(2n+1)}{24},
$$

$$
Z=\frac{W^+-E_0[W^+]}{\sqrt{V_0(W^+)}}
\ \overset{\mathrm{approx}}\sim N(0,1).
$$

## 17. Wilcoxon順位和検定・Mann–Whitney U検定

独立2群の標本数$m,n$、X群の順位和$R_X$とする。帰無仮説下で分布が等しく、同順位がない場合、

$$
E_0[R_X]=\frac{m(m+n+1)}2,\qquad
V_0(R_X)=\frac{mn(m+n+1)}{12}.
$$

$$
U=R_X-\frac{m(m+1)}2
=\sum_{i=1}^m\sum_{j=1}^n\mathbf1\{X_i>Y_j\}.
$$

$$
E_0[U]=\frac{mn}{2},\qquad
V_0(U)=\frac{mn(m+n+1)}{12},\qquad
E[U]=mnP(X>Y).
$$

## 18. McNemar検定

対応2値データの不一致セル数を$b=n_{10},\ c=n_{01}$とすると、

$$
X^2=\frac{(b-c)^2}{b+c}\ \overset{H_0}{\approx}\ \chi_1^2\qquad(b+c>0).
$$

$$
B\mid(B+C=s)\sim\operatorname{Bin}(s,1/2)\qquad(H_0).
$$

## 19. 多項分布の共分散・正規近似

$$
(N_1,\dots,N_k)\sim\operatorname{Multinomial}(n;p_1,\dots,p_k),
\qquad\sum_i p_i=1.
$$

$$
E[N_i]=np_i,\quad V(N_i)=np_i(1-p_i),\quad
\operatorname{Cov}(N_i,N_j)=-np_ip_j\quad(i\ne j).
$$

$\hat p_i=N_i/n$として、$H_0:p_i=p_j$（$i\ne j$）の検定統計量は

$$
Z=\frac{\hat p_i-\hat p_j}{\sqrt{(\hat p_i+\hat p_j)/n}}
=\frac{N_i-N_j}{\sqrt{N_i+N_j}}
\ \overset{H_0}{\approx}\ N(0,1),
$$

$$
Z^2=\frac{(N_i-N_j)^2}{N_i+N_j}
\ \overset{H_0}{\approx}\ \chi_1^2.
$$

## 20. 対数正規分布の特性値

$\log X\sim N(\mu,\sigma^2)$のとき、

$$
\begin{aligned}
\operatorname{median}(X)&=e^\mu,\\
E[X]&=e^{\mu+\sigma^2/2},\\
V(X)&=(e^{\sigma^2}-1)e^{2\mu+\sigma^2},\\
\operatorname{CV}(X)&=\sqrt{e^{\sigma^2}-1},\\
E[X^r]&=e^{r\mu+r^2\sigma^2/2}.
\end{aligned}
$$

## 21. 完備統計量・UMVU

十分統計量（因子分解定理）：

$$
f_\theta(\boldsymbol x)=g_\theta(T(\boldsymbol x))h(\boldsymbol x).
$$

完備統計量：

$$
\forall\theta,\ E_\theta[g(T)]=0
\quad\Longrightarrow\quad
\forall\theta,\ P_\theta(g(T)=0)=1
$$

（$E_\theta|g(T)|<\infty$を仮定）。

Lehmann–Schefféの定理：$T$が完備十分統計量で、$E_\theta[a(T)]=\tau(\theta)$なら、$a(T)$は$\tau(\theta)$のUMVU推定量。

## 22. Rao–Blackwellの定理

$T$が十分統計量、$\delta(\boldsymbol X)$が$\tau(\theta)$の不偏推定量で有限分散をもつとき、

$$
\delta^*(T)=E_\theta[\delta(\boldsymbol X)\mid T],
\qquad E_\theta[\delta^*(T)]=\tau(\theta),
$$

$$
V_\theta(\delta^*(T))\le V_\theta(\delta(\boldsymbol X)).
$$

$$
V(\delta)=E[V(\delta\mid T)]+V(E[\delta\mid T]).
$$

## 23. クロスバリデーション

$\{I_1,\dots,I_K\}$を標本の分割、$\hat f^{(-k)}$を第$k$fold以外のデータで学習したモデルとして、

$$
\mathrm{CV}_K=\frac1n\sum_{k=1}^K\sum_{i\in I_k}
L\bigl(y_i,\hat f^{(-k)}(x_i)\bigr).
$$

$$
\mathrm{LOOCV}=\frac1n\sum_{i=1}^n
L\bigl(y_i,\hat f^{(-i)}(x_i)\bigr).
$$

## 24. ブートストラップ

観測標本$x_1,\dots,x_n$の経験分布$F_n$から復元抽出：

$$
X_1^*,\dots,X_n^*\overset{\mathrm{iid}}\sim F_n,\qquad
\bar X^*=\frac1n\sum_{j=1}^nX_j^*.
$$

$$
E_*[\bar X^*]=\bar x,\qquad
V_*(\bar X^*)=\frac1{n^2}\sum_{i=1}^n(x_i-\bar x)^2.
$$

$B$回の再標本統計量$T_1^*,\dots,T_B^*$による標準誤差の推定：

$$
\widehat{\mathrm{SE}}_{\mathrm{boot}}(T)
=\sqrt{\frac1{B-1}\sum_{b=1}^B(T_b^*-\bar T^*)^2}.
$$

