# Canonical Paths

このファイルは `stats_study_notes` における教材処理パスの唯一の基準である。

パスに関して `.agents/skills/` や `.agents/rules/` の記述と矛盾がある場合、
ユーザーの最新指示を最優先し、その次にこのファイルを優先する。

Windows上のリポジトリルート:

```text
C:\Document\数理統計学勉強
```

## 1. 教科書本文スクリーンショット

### Input

```text
91_docs/materials/現代数理統計学の基礎/第n章/スクリーンショット/
```

Windows上:

```text
C:\Document\数理統計学勉強\91_docs\materials\現代数理統計学の基礎\第n章\スクリーンショット
```

画像は教科書上の実ページ番号を確認して

```text
pAA.png
```

とする。

例:

```text
p37.png
p38.png
p39.png
```

ページ番号を推測で付けない。

### Output

第n章の全スクリーンショットをページ順にまとめ、
**各章の `latex/` に1章につき1つのTeXファイル**として保存する。

```text
91_docs/materials/現代数理統計学の基礎/第n章/latex/chaptern.tex
```

例:

```text
第2章/latex/chapter2.tex
第3章/latex/chapter3.tex
第4章/latex/chapter4.tex
```

以下は誤り。

```text
第n章/latex/pAA.tex (1ページ1TeXは禁止)
91_docs/materials/現代数理統計学の基礎/latex/chaptern.tex (ルート直下の共通latexに置かない)
```

**1ページ1TeXにはしない。1章につき1つのTeXファイル `chaptern.tex` を各章の `第n章/latex/` に置く。**

正しい処理:

```text
第n章/スクリーンショット/*.png
        ↓
ページ順に読み取る
        ↓
第n章/latex/chaptern.tex
```

## 2. ユーザーの手書き答案

Input:

```text
91_docs/materials/現代数理統計学の基礎/第n章/回答/
```

答案写真:

```text
問b_c.jpg
```

- `b`: 問題番号
- `c`: その問題の答案写真のページ番号（1から開始）

Output:

```text
01_現代数理統計学の基礎/第n章/問b.md
```

1問題につき1Markdownファイル。

## 3. 公式解答

Source:

```text
91_docs/materials/現代数理統計学の基礎/解答/MathStat_Answers.pdf
```

Windows上:

```text
C:\Document\数理統計学勉強\91_docs\materials\現代数理統計学の基礎\解答\MathStat_Answers.pdf
```

PDF全体を章ごとに読み分けて、各章の対応範囲を

```text
91_docs/materials/現代数理統計学の基礎/第n章/答え/answers.tex
```

へ保存する。

以下は誤り。

```text
第n章/latex/answers.tex
```

## 4. グラフ生成

コード:

```text
92_src/create_graphs/
```

生成データ・画像:

```text
90_data/
```

`src/create_graphs/` や `data/` には変更しない。

## 5. 3系統のまとめ

```text
【教科書本文】

91_docs/materials/現代数理統計学の基礎/第n章/スクリーンショット/*.png
        ↓
91_docs/materials/現代数理統計学の基礎/第n章/latex/chaptern.tex
```

```text
【ユーザー答案】

91_docs/materials/現代数理統計学の基礎/第n章/回答/問b_c.jpg
        ↓
01_現代数理統計学の基礎/第n章/問b.md
```

```text
【公式解答】

91_docs/materials/現代数理統計学の基礎/解答/MathStat_Answers.pdf
        ↓
91_docs/materials/現代数理統計学の基礎/第n章/答え/answers.tex
```

この3系統を混同しない。
