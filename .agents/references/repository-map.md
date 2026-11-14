# Repository Map

リポジトリ `stats_study_notes`（ローカル: `C:\Document\数理統計学勉強`）の構成。
教材処理のパスの詳細は `canonical-paths.md` を参照する。

## 1. トップレベル

| パス | 内容 | Git |
|---|---|---|
| `00_学習管理/` | Home、MOC、Bases、Daily Note、Templates（Vault管理用） | 管理 |
| `01_現代数理統計学の基礎/` | 教科書の章末問題ノート（第2〜7章、`第n章/問b.md`） | 管理 |
| `02_統計数理過去問/` | 統計検定1級 統計数理 過去問 | 管理 |
| `03_統計応用医薬生物学過去問/` | 統計検定1級 統計応用（医薬生物学）過去問 | 管理 |
| `04_統計応用理工学過去問/` | 統計検定1級 統計応用（理工学）過去問 | 管理 |
| `05_院試過去問/` | 大学院入試問題 | 管理 |
| `06_数学/` | 一般数学（ガンマ・ベータ・ディガンマ関数、二項定理、確率不等式、ヤコビアン、極座標変換、射影行列と二次形式など。サブフォルダなし） | 管理 |
| `07_計算機統計学/` | 計算機統計学 | 管理 |
| `08_数理統計学/` | 数理統計学の概念ノート（分野別サブフォルダ: 確率・期待値、確率分布、多次元確率変数、標本分布・漸近論、推定、検定、分散分析、生存解析、ノンパラメトリック統計、一般化線形回帰、ベイズ統計、多変量解析） | 管理 |
| `09_統計検定準1級/` | 準1級関連 | 管理 |
| `10_医療統計学/` | 医療・生物統計 | 管理 |
| `11_研究関連/` | 研究関連 | 管理 |
| `12_データ分析/` | データ分析 | 管理 |
| `13_測度論・ルベーグ積分/` | 測度論・積分論 | 管理 |
| `14_確率論・確率過程論/` | 測度論的確率論・確率過程 | 管理 |
| `15_確率微分方程式・フォッカープランク方程式/` | SDE・Itô解析・Fokker–Planck | 管理 |
| `90_data/` | 生成データ・画像 | 除外 |
| `91_docs/` | ローカル教材（スクショ、TeX、答案写真、公式解答） | 除外 |
| `92_src/` | ローカルのコード置き場（`create_graphs/` など。置き場所は見直し中） | 除外 |
| `93_scratch/` | 一時作業用 | 除外 |
| `94_presentation/` | 発表資料 | — |
| `AGENTS.md` | AI向けルールの入口（Codex・Claude・Gemini共通） | 管理 |
| `.agents/` | 教材処理・採点・Vault管理の共通ルールとスキル | 管理 |
| `.obsidian/` | Obsidian設定 | 管理 |
| `daily_report.md` | AI作業ログ | 除外 |
| `README.md` | リポジトリの目的 | 管理 |
| `source.md` | 外部リンク集 | 管理 |

## 2. 『現代数理統計学の基礎』の構造

```text
01_現代数理統計学の基礎/
└── 第n章/
    └── 問b.md                      ← 公開ノート（問題の要約・答案）  ※第2〜7章のみ

91_docs/materials/現代数理統計学の基礎/
├── 解答/MathStat_Answers.pdf       ← 公式解答（全章）
└── 第n章/
    ├── スクリーンショット/pAA.png   ← 教科書本文の画像
    ├── latex/chaptern.tex          ← 教科書本文のTeX（1章1ファイル）
    ├── 回答/問b_c.jpg              ← ユーザーの手書き答案
    └── 答え/answers.tex            ← 公式解答のTeX（章別）
```

## 3. 処理の流れ

```text
教科書スクショ  → textbook-screenshot-to-tex   → 第n章/latex/chaptern.tex
公式解答PDF     → official-answer-to-tex       → 第n章/答え/answers.tex
手書き答案写真  → answer-photo-to-markdown     → 01_.../第n章/問b.md（採点はstatusのみ）
作業終了        → update-daily-report          → daily_report.md
```

## 4. 指示ファイルの解説

以下の一覧で `.agents/` 内の全ファイルを扱う。各Ruleは守る基準、Referenceは判断に使う資料、Skillは該当作業の手順である。すべてを毎回読むのではなく、`AGENTS.md` の必読ルールと作業に該当するファイルを参照する。

### 入口

| ファイル | 役割 | 参照する場面 |
|---|---|---|
| [AGENTS.md](../../AGENTS.md) | 共通の担当範囲、重要ルール、Rule・Skillへの入口。 | 作業開始時に最初に読む。 |
| [.agents/README.md](../README.md) | 共通ルールの概要と、パス・属性・分類・採点の正本の案内。 | ルールの優先関係や参照先を確認するとき。 |

### ルール

パスは `.agents/` からの相対パス。

| ファイル | 役割 | 参照する場面 |
|---|---|---|
| [rules/bases.md](../rules/bases.md) | Obsidian Basesの作成・編集方針、主要な一覧と復習Properties。 | `.base` や学習一覧を編集するとき。 |
| [rules/copyright.md](../rules/copyright.md) | 教材・過去問の転載範囲と公開ノートでの要約方針。 | 教材からノートや公開資料を作るとき。 |
| [rules/core.md](../rules/core.md) | 作業全体の基本姿勢と優先事項。 | 作業開始時。 |
| [rules/daily-notes.md](../rules/daily-notes.md) | Obsidian Daily Noteの保存先と記録内容。 | 学習日誌を作成・更新するとき。 |
| [rules/files-and-paths.md](../rules/files-and-paths.md) | ファイル配置・命名・パスの扱い。 | ファイルを作成・配置するとき。 |
| [rules/frontmatter.md](../rules/frontmatter.md) | 問題ノートの必須Properties、キー順、値の表記の正本。 | 問題ノートのメタデータを作成・編集するとき。 |
| [rules/git.md](../rules/git.md) | commit・pushの明示指示、Git除外対象、改行コードの扱い。 | Git操作や管理対象の判断をするとき。 |
| [rules/internal-links.md](../rules/internal-links.md) | 内部リンクの付け方、既存概念の検索、conceptsとBasesの使い分け。 | リンクや概念ノートとの関連を整理するとき。 |
| [rules/markdown-obsidian.md](../rules/markdown-obsidian.md) | Obsidian互換Markdown・LaTeXの書式。 | Markdownや数式を書くとき。 |
| [rules/math.md](../rules/math.md) | 数学的正確性、付表による数値計算、最尤推定の導出手順。 | 証明・計算・解答例・解説を扱うとき。 |
| [rules/note-routing.md](../rules/note-routing.md) | 教材・分野ごとの保存先、概念ノートの分類、MOC・索引との対応。 | ノートの配置・移動・分類を決めるとき。 |
| [rules/obsidian.md](../rules/obsidian.md) | Vaultの構成と、本文・数式・リンクを扱う基本方針。 | Obsidian Vaultを編集するとき。 |
| [rules/problem-note.md](../rules/problem-note.md) | 問題ノートの対象章、本文構成、答案の保持、書かない内容。 | 問題ノートを作成・編集するとき。 |
| [rules/properties.md](../rules/properties.md) | Propertiesの運用、採点結果と復習状態の区別、概念ノートの属性。 | 既存メタデータを整理するとき。標準形はfrontmatter.mdを優先する。 |
| [rules/safe-editing.md](../rules/safe-editing.md) | 移動・改名・一括変更前の確認と、数学的本文・個人設定の保護。 | Vault整理や複数ファイルの変更をするとき。 |

### 参照資料

パスは `.agents/` からの相対パス。

| ファイル | 役割 | 参照する場面 |
|---|---|---|
| [references/canonical-paths.md](../references/canonical-paths.md) | 教材画像・手書き答案・公式解答・生成物の入出力パスの正本。 | 入力元・出力先・命名を確定するとき。 |
| [references/environment.md](../references/environment.md) | Windows・PowerShell・UTF-8・時刻などの環境と、指示の読み込み方。 | 環境を確認するときや、別のAI・クライアントで作業を始めるとき。 |
| [references/grading-rubric.md](../references/grading-rubric.md) | statusの4値、採点判定、公式解答未確認時と再採点の扱い。 | 答案を採点・再採点するとき。 |
| [references/repository-map.md](../references/repository-map.md) | リポジトリ全体の配置、教材処理の流れ、このファイル解説一覧。 | 必要なルール・資料・保存先を探すとき。 |
| [references/taxonomy.md](../references/taxonomy.md) | test-category・stats-category・difficulty・tagsの分類語彙。 | 分類やタグを付けるとき。 |

### スキル

パスは `.agents/` からの相対パス。

| ファイル | 役割 | 参照する場面 |
|---|---|---|
| [skills/answer-photo-to-markdown/SKILL.md](../skills/answer-photo-to-markdown/SKILL.md) | 手書き答案を論理展開を保って問題ノートへ転記する手順。 | 答案写真をMarkdown化するとき。 |
| [skills/build-dashboard/SKILL.md](../skills/build-dashboard/SKILL.md) | Home・MOC・Basesで学習ダッシュボードを作る手順。 | 一覧や学習の入口を整えるとき。 |
| [skills/create-concept-note/SKILL.md](../skills/create-concept-note/SKILL.md) | 既存ノートの重複確認、配置、概念ノートの構成。 | 数学・統計の概念ノートを新規作成するとき。 |
| [skills/daily-study/SKILL.md](../skills/daily-study/SKILL.md) | 復習対象の確認と、Daily Noteへの学習計画・実績の記録。 | 今日の学習計画や学習日誌を作るとき。 |
| [skills/link-related-notes/SKILL.md](../skills/link-related-notes/SKILL.md) | 関連する既存概念を探し、本文やconceptsのリンクを整える手順。 | ノート間の関連付けを依頼されたとき。 |
| [skills/official-answer-to-tex/SKILL.md](../skills/official-answer-to-tex/SKILL.md) | 公式解答PDFを章別に読み分け、所定の場所へTeX化する手順。 | 公式解答PDFを章別TeXにするとき。 |
| [skills/organize-vault/SKILL.md](../skills/organize-vault/SKILL.md) | 重複・孤立ノート、Properties、MOCなどの棚卸しと整理。 | Vault全体の整理を依頼されたとき。 |
| [skills/textbook-screenshot-to-tex/SKILL.md](../skills/textbook-screenshot-to-tex/SKILL.md) | 教科書画像をページ順に読み、章単位のTeXへまとめる手順。 | 教科書スクリーンショットをTeX化するとき。 |
| [skills/update-daily-report/SKILL.md](../skills/update-daily-report/SKILL.md) | AI作業ログへの追記形式、日付の階層、記録上の注意。 | 作業終了時、または日報更新を依頼されたとき。 |
| [skills/update-review/SKILL.md](../skills/update-review/SKILL.md) | 復習回数・最終復習日・次回復習日の更新と初期の間隔目安。 | 復習計画・復習完了の記録を依頼されたとき。 |
