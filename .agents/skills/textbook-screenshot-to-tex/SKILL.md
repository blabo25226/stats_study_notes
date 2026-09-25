# Skill: Textbook Screenshot to Chapter TeX

## Purpose

『現代数理統計学の基礎』の各章のスクリーンショットをページ順に読み取り、
**1章につき1つのTeXファイル**へまとめる。

パスの基準は必ず以下を参照する。

```text
.agents/references/canonical-paths.md
```

## Trigger

```text
91_docs/materials/現代数理統計学の基礎/第n章/スクリーンショット/
```

に新しい教科書スクリーンショットが入ったときに使用する。

## Input image naming

画像内容から教科書上の実ページ番号を確認し、

```text
pAA.png
```

へ整理する。

例:

```text
p37.png
p38.png
p39.png
```

ページ番号が不明な画像を推測で命名しない。

JPEG等の場合は画像実体と拡張子を一致させる。
拡張子だけを書き換えて画像形式を偽装しない。

## Output

第n章の全スクリーンショットをページ順にまとめ、
各章の `latex/` に**1章につき1つのTeXファイル**として保存する。

```text
91_docs/materials/現代数理統計学の基礎/第n章/latex/chaptern.tex
```

例:

```text
91_docs/materials/現代数理統計学の基礎/第2章/latex/chapter2.tex
91_docs/materials/現代数理統計学の基礎/第3章/latex/chapter3.tex
91_docs/materials/現代数理統計学の基礎/第4章/latex/chapter4.tex
```

以下にはしない。

```text
第n章/latex/p37.tex (1ページ1TeXは禁止)
91_docs/materials/現代数理統計学の基礎/latex/chaptern.tex (ルート直下の共通latexには置かない)
```

**1ページ1TeXではなく、各章ごとの 1章1TeX (`第n章/latex/chaptern.tex`) である。**

## Procedure

### Step 1: 対象章を確認する

たとえば入力が

```text
第2章/スクリーンショット/
```

なら出力は

```text
第2章/latex/chapter2.tex
```

とする。

### Step 2: 全画像を確認する

対象章のスクリーンショットを一覧化し、

- 教科書上のページ番号
- ページの連続性
- 重複画像
- 欠落ページ
- 画像の向き
- 判読可能性

を確認する。

### Step 3: ファイル名を整理する

ページ番号が明確な画像を

```text
pAA.png
```

形式にする。

ページ番号が不明な画像を推測で割り当てない。

### Step 4: ページ順に並べる

文字列順ではなく、教科書上の実ページ番号順に処理する。

例:

```text
p98.png
p99.png
p100.png
p101.png
```

### Step 5: 各ページを正確にTeX化する

以下を可能な限り忠実に保持する。

- 見出し
- 本文
- 定義
- 定理
- 例
- 数式
- 式番号
- 問題番号
- 条件
- 注記

特に数式では以下を落とさない。

- 添字
- 上付き
- 積分範囲
- 総和範囲
- 絶対値
- 場合分け
- パラメータ条件

判読不能箇所を推測で補完しない。

### Step 6: 章全体を1つのTeXへ結合する

```text
91_docs/materials/現代数理統計学の基礎/第n章/latex/chaptern.tex
```

へ保存する。

推奨形式:

```tex
% 現代数理統計学の基礎 第2章
% Source images: 第2章/スクリーンショット/

% ---- p37 ----

...

% ---- p38 ----

...

% ---- p39 ----

...
```

ページ境界が追跡できるよう、各ページ開始位置にコメントを入れる。

### Step 7: 既存 chaptern.tex がある場合

無条件に全体を上書きしない。

- 新規ページだけ追加する
- 既存ページと重複しないか確認する
- ページ順を維持する
- 過去の手修正を不用意に失わない

必要に応じて該当ページ部分だけ更新する。

### Step 8: 完了確認

- 入力章が正しい
- 画像名のページ番号が正しい
- ページ順が正しい
- 1章1TeXになっている
- 出力先が各章の `第n章/latex/chaptern.tex` である
- 数式がLaTeXとして妥当
- 判読不能箇所を捏造していない
- Git commit / pushをしていない

## Important

正しい対応:

```text
第n章/スクリーンショット/*.png
        ↓
第n章/latex/chaptern.tex
```

ルート直下の `91_docs/materials/現代数理統計学の基礎/latex/` は出力先ではない。
必ず該当する章のフォルダ `第n章/latex/` 直下に配置する。
