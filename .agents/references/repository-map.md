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
| `06_数学/` | 一般数学 | 管理 |
| `07_計算機統計学/` | 計算機統計学 | 管理 |
| `08_数理統計学用語深堀/` | 数理統計学の概念ノート | 管理 |
| `09_統計検定準1級/` | 準1級関連 | 管理 |
| `10_医療統計学/` | 医療・生物統計 | 管理 |
| `11_研究関連/` | 研究関連 | 管理 |
| `12_データ分析/` | データ分析 | 管理 |
| `13_測度論・ルベーグ積分/` | 測度論・積分論 | 管理 |
| `14_確率論・確率過程論/` | 測度論的確率論・確率過程 | 管理 |
| `15_確率微分方程式/` | SDE・Itô解析 | 管理 |
| `90_data/` | 生成データ・画像 | 除外 |
| `91_docs/` | ローカル教材（スクショ、TeX、答案写真、公式解答） | 除外 |
| `92_src/` | コード（`create_graphs/` など） | 管理 |
| `scratch/` | 一時作業用 | — |
| `AGENTS.md` | AI向けルールの入口（Claude・Gemini共通） | 管理 |
| `.agents/` | 教材処理・採点のルールとスキル | 管理 |
| `.claude/` | Claude専用の設定（Vault管理）。Geminiは編集しない | 管理 |
| `GEMINI.md` | Gemini向けの入口（`AGENTS.md` を参照させる） | 管理 |
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

## 4. `.agents/` の構成

```text
.agents/
├── README.md
├── rules/
│   ├── core.md               全体の基本ルール
│   ├── math.md               数学的内容のルール
│   ├── markdown-obsidian.md  Markdown・数式の書式
│   ├── frontmatter.md        frontmatterの標準形
│   ├── problem-note.md       問題ノートの本文構成・対象章
│   ├── files-and-paths.md    ファイル配置
│   ├── copyright.md          著作権
│   └── git.md                Git操作
├── references/
│   ├── canonical-paths.md    パスの唯一の基準
│   ├── repository-map.md     このファイル
│   ├── taxonomy.md           分類の語彙
│   └── grading-rubric.md     採点基準
└── skills/
    ├── answer-photo-to-markdown/SKILL.md
    ├── textbook-screenshot-to-tex/SKILL.md
    ├── official-answer-to-tex/SKILL.md
    └── update-daily-report/SKILL.md
```
