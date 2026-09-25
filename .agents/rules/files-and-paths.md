# Files and Paths Rules

パスに関する唯一の基準は

```text
.agents/references/canonical-paths.md
```

である。

## 1. 問題ファイル

以下では原則として1問題につき1ファイルを作成する。

- `01_現代数理統計学の基礎`
- `02_統計数理過去問`
- `03_統計応用医薬生物学過去問`
- `04_統計応用理工学過去問`
- `05_院試過去問`

例:

```text
問1.md
問2.md
問12.md
```

不要な連番プレフィックスは追加しない。

## 2. 現代数理統計学の基礎

公開ノート:

```text
01_現代数理統計学の基礎/第n章/問b.md
```

ローカル教材の主要構造:

```text
91_docs/materials/現代数理統計学の基礎/
├── 解答/
│   └── MathStat_Answers.pdf
├── 第2章/
│   ├── latex/
│   │   └── chapter2.tex
│   ├── スクリーンショット/
│   ├── 回答/
│   └── 答え/
│       └── answers.tex
├── 第3章/
│   ├── latex/
│   │   └── chapter3.tex
│   ├── スクリーンショット/
│   ├── 回答/
│   └── 答え/
│       └── answers.tex
└── ...
```

### 教科書スクリーンショット

入力:

```text
第n章/スクリーンショット/
```

画像名:

```text
pAA.png
```

第n章の画像をページ順にまとめて

```text
第n章/latex/chaptern.tex
```

へ保存する。

**1ページ1TeXにはしない。各章の `第n章/latex/` に1章につき1つのTeXファイル `chaptern.tex` を置く。**

### ユーザー答案

入力:

```text
第n章/回答/
```

画像名:

```text
問b_c.jpg
```

出力:

```text
01_現代数理統計学の基礎/第n章/問b.md
```

### 公式解答

原本:

```text
解答/MathStat_Answers.pdf
```

章別出力:

```text
第n章/答え/answers.tex
```

## 3. グラフ生成

コード:

```text
92_src/create_graphs/
```

生成データ・画像:

```text
90_data/
```

## 4. `.gitkeep`

Git管理対象の空ディレクトリに限り `.gitkeep` を使用する。

- ディレクトリが空なら必要に応じて置く。
- 実ファイルが入ったら不要な `.gitkeep` を削除する。
- `91_docs/` や `90_data/` などGit管理対象外では原則不要。
