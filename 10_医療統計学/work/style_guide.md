# 執筆スタイルガイド（医療統計学参考書）

## ファイル構成
- parts/00_preamble.tex … プリアンブル（マクロ・環境定義）
- parts/01_front.tex … \begin{document}, 表紙, 前付, 目次
- parts/chNN.tex … 各章（\chapter から）
- parts/90_appendix.tex … \appendix 付録A–E
- parts/99_bib.tex … 参考文献（thebibliography）
- build.py で連結 → ../医療統計学参考書.tex, `python build.py compile` で work/build にPDF

## 環境（プリアンブル定義済み）
- 定理型: teigi(定義) teiri(定理) meidai(命題) reidai(例題)。ラベル: def:, thm:, prop:, reidai:chNN-x
- \begin{kaitou}{reidai:...} … \end{kaitou}（例題の解答。タイトル自動「例題x.yの解答」）
- ボックス: goalbox, exambox, pointbox[タイトル], warnbox[タイトル], linkbox[タイトル], supbox[補足（出典：…）], summarybox
- \flowline{データ}{推定対象}{手法}{仮定}{計算}{解釈}
- 重要度: \Hissu \Hinshutsu \Youchui \Hatten
- 過去問参照: \kakomon{2022}{2} → 「2022年 医薬 問2」, \kakomonSM{2016}{2} → 「2016年 数理 問2」
- 数式マクロ: \E \V \Var \Cov \Corr \Prob \SE \dd \RR \RD \OR \HR \logit \indep \iid \Normal \Bin \Po \Ga \Be \Ex \NB \Unif \transp \ind \hatS
- 参照は \cref{...}。章ラベル ch:NN, 節ラベル sec:NN-xxx, 式 eq:NN-xxx, 表 tab:NN-xxx, 図 fig:NN-xxx
- 文献 \cite{key}（99_bib.tex の \bibitem key）

## 記法の約束（本書全体）
- z_α：標準正規の上側100α%点。t_ν(α), χ²_ν(α) も上側点。
- β：第2種の過誤確率、検出力 1-β（医療統計の慣習）。※教科書『現代数理統計学の基礎』の β(θ) は検出力関数そのもの。
- 不偏分散 s² は n-1 で割る（試験と同じ）。※教科書は S²=除数n, V²=除数n-1。
- 指数分布 Ex(λ)：率λ（ハザード）, 平均1/λ。
- ガンマ分布：本書は Ga(a, b) = 形状a・**率**b, 密度 b^a θ^{a-1} e^{-bθ}/Γ(a), 平均a/b, 分散a/b²（試験2025医薬問2, 数理2022問3と同じ）。
  ※教科書は Ga(α,β) を形状・**尺度**で定義（平均αβ）→ 必ず注意書き。
- 負の二項：失敗回数 k=0,1,...。
- Normal N(μ,σ²)：第2引数は分散。
- Fisher情報：I_n(θ) 標本全体, I_1 1個あたり。
- 対数は自然対数 log。

## 各章の構成
goalbox → exambox → 問題設定 → 基本概念 → 数理 → 推定・検定 → 仮定 → 解釈 → 手法選択 → よくある誤り(warnbox) → 数理統計との接続(linkbox) → 例題 → 解答 → 章末まとめ(summarybox)
過去問本文は転載しない。「2022年 医薬 問2」形式で参照。例題はオリジナル（数値も独自）。
Web由来は supbox[補足（出典：…）] か [発展] で区別。
