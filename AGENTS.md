# AI Assistant Guidelines

## Project purpose

このリポジトリは、以下の目的のための学習ノートである。

- 2026年11月の統計検定1級合格
- 将来の大学院入試対策
- 数理統計学、測度論、確率論、確率過程論、確率微分方程式などの継続的な学習
- Obsidianで閲覧・整理し、Git/GitHubで管理する学習資産の構築

AIは学習アシスタントとして、数学的正確性を最優先する。

## Instruction structure

詳細なルールは `.agents/` 以下に分割している。

作業時は、まず以下を参照すること。

- `.agents/rules/core.md`
- `.agents/rules/math.md`
- `.agents/rules/markdown-obsidian.md`
- `.agents/rules/frontmatter.md`
- `.agents/rules/files-and-paths.md`
- `.agents/rules/copyright.md`
- `.agents/rules/git.md`

リポジトリ構成については以下を参照する。

- `.agents/references/repository-map.md`
- `.agents/references/taxonomy.md`
- `.agents/references/grading-rubric.md`

## Skills

タスクが該当する場合、対応する `SKILL.md` を必ず読んでから処理する。

### 手書き答案 → Markdown

`91_docs/materials/現代数理統計学の基礎/第n章/回答/`
に答案写真が入った場合:

- `.agents/skills/answer-photo-to-markdown/SKILL.md`

### 教科書スクリーンショット → TeX

`91_docs/materials/現代数理統計学の基礎/第n章/スクリーンショット/`
に画像が入った場合:

- `.agents/skills/textbook-screenshot-to-tex/SKILL.md`

### 公式解答 → TeX

`91_docs/materials/現代数理統計学の基礎/第n章/答え/`
に公式解答の画像・PDF等が入った場合:

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
10. 公開ノート側に教科書や過去問の問題文を丸ごと転載しない。
