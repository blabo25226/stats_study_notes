# AI Assistant Guidelines

## Project purpose

このリポジトリは、以下の目的のための学習ノートである。

- 2026年11月の統計検定1級合格
- 将来の大学院入試対策
- 数理統計学、測度論、確率論、確率過程論、確率微分方程式などの継続的な学習
- Obsidianで閲覧・整理し、Git/GitHubで管理する学習資産の構築

AIは学習アシスタントとして、数学的正確性を最優先する。

## AI roles

| AI | 担当範囲 | 読むルール |
|---|---|---|
| Claude（Claude Code） | すべての作業（教材処理・採点 + Obsidian Vault管理） | `AGENTS.md`、`.agents/`、`.claude/` |
| Gemini | 教材処理・採点のみ | `AGENTS.md`、`.agents/` |

Geminiの担当:
- 手書き答案 → 問題ノート（`answer-photo-to-markdown`）
- 教科書スクリーンショット → TeX（`textbook-screenshot-to-tex`）
- 公式解答PDF → 章別TeX（`official-answer-to-tex`）
- 数学的採点
- `daily_report.md` への追記（`update-daily-report`）

Geminiが行わないこと（Claudeの担当）:
- `.claude/` 以下の編集
- 内部リンク、MOC、Bases（`00_学習管理/`）、Daily Note（`00_学習管理/Daily/`）の作成・編集
- 復習Properties（`review-count`, `last-reviewed`, `next-review`）の更新
- Vault全体の整理（ノートの移動・改名、重複・孤立ノートの整理）

これらが必要になった場合、Geminiは作業せずユーザーに「Claudeの担当」と伝える。

## Instruction structure

詳細なルールは `.agents/` 以下に分割している。

作業時は、まず以下を参照すること。

- `.agents/rules/core.md`
- `.agents/rules/math.md`
- `.agents/rules/markdown-obsidian.md`
- `.agents/rules/frontmatter.md`
- `.agents/rules/problem-note.md`
- `.agents/rules/files-and-paths.md`
- `.agents/rules/copyright.md`
- `.agents/rules/git.md`

リポジトリ構成については以下を参照する。

- `.agents/references/canonical-paths.md`（パスの唯一の基準）
- `.agents/references/repository-map.md`
- `.agents/references/taxonomy.md`
- `.agents/references/grading-rubric.md`

## Skills

タスクが該当する場合、対応する `SKILL.md` を必ず読んでから処理する。

### 手書き答案 → Markdown

`91_docs/materials/現代数理統計学の基礎/第n章/回答/`（n = 2〜7）
に答案写真が入った場合:

- `.agents/skills/answer-photo-to-markdown/SKILL.md`

### 教科書スクリーンショット → TeX

`91_docs/materials/現代数理統計学の基礎/第n章/スクリーンショット/`
に画像が入った場合:

- `.agents/skills/textbook-screenshot-to-tex/SKILL.md`

### Daily Report

作業終了時、またはユーザーから日報更新の指示があった場合:

- `.agents/skills/update-daily-report/SKILL.md`

### 公式解答PDF → 章別TeX

『現代数理統計学の基礎』全体の公式解答PDF

`91_docs/materials/現代数理統計学の基礎/解答/MathStat_Answers.pdf`

を章ごとに読み分け、各章の `答え/` にTeX化する場合:

- `.agents/skills/official-answer-to-tex/SKILL.md`

## Critical rules

1. AIはGit commit / pushを勝手に行わない。
2. 数学的正確性を文章の見栄えより優先する。
3. 手書き答案のMarkdown化では、ユーザーの論理展開を勝手に修正・別解化しない。
4. `status` は理解度ではなく採点結果を表す。
5. `status` の確定値は `正解`、`部分的なミスあり`、`不正解`、`回答なし` の4種類とする。
6. 公式解答と異なる解法でも数学的に正しければ `正解` とする。
7. 公式解答を確認できない場合、推測で採点しない。
8. Obsidian互換Markdown/LaTeXを使用する。
9. `現代数理統計学の基礎`、統計数理過去問、統計応用過去問では原則1問題1Markdownファイルとする。
10. 公開ノート側に教科書や過去問の問題文を丸ごと転載しない。問題ノートの「問題の要約」は要約であり転載に当たらないものとする。
11. `daily_report.md` はAI作業ログとして、作業終了時またはユーザー指示時に既存内容を消さず追記する。
12. `00_学習管理/Daily/` のObsidian Daily Noteとルートの `daily_report.md` を混同しない。
13. 問題ノートのfrontmatterは `.agents/rules/frontmatter.md` の標準形に従う。
    - キー順は `test-category` → `stats-category` → `difficulty` → `status` → `tags` → `source` → (`section`) → `created` → `updated` → (復習Properties)。
    - 値はダブルクォートで囲まない（例: `status: 正解`）。
    - `difficulty` は `易` / `中` / `難` のみ。
    - `tags` は必須。汎用タグ（`数理統計学` など）は付けず、数学的トピックを付ける。
14. 『現代数理統計学の基礎』で問題を解くのは第2章〜第7章のみ。
15. 問題ノートの本文は `.agents/rules/problem-note.md` に従い、`## 問題の要約` と `## 答案` のみとする。
    - 目次、採点・判定理由、解説・模範解答、講評、関連知識・発展事項は書かない。
    - 採点結果はfrontmatterの `status` のみ。判定理由はユーザーへの報告と `daily_report.md` に書く。
    - 回答なしの答案は `答案未提出` の1行とする。
16. 内部リンク `[[...]]` の運用は保留中。問題ノートに `## 関連` 節や内部リンクを追加しない。
