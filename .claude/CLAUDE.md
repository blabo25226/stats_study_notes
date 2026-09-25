# Obsidian Vault Assistant

@../AGENTS.md

この `.claude/` は、`stats_study_notes` をObsidian Vaultとして育てるためのClaude Code専用設定である。

## Responsibility split

`.agents/` と `AGENTS.md`:
- 教材・答案ファイルの処理
- 手書き答案 → Markdown
- 教科書スクリーンショット → TeX
- 公式解答PDF → 章別TeX
- 数学的採点
- `daily_report.md`

`.claude/`:
- Obsidian内部リンク
- MOC
- Bases
- Propertiesの整理
- Daily Notes
- 復習管理
- Vaultの重複・孤立ノート整理

数学的内容や教材処理について `.claude/` が `AGENTS.md` と競合する場合、
`AGENTS.md` / `.agents/` の具体的ルールを優先する。

## Core Obsidian model

- フォルダ = 教材・分野
- Properties = 構造化された属性
- `[[内部リンク]]` = 数学的関係
- `.base` = 問題一覧・復習管理・検索UI
- MOC = 人間が読む学習ロードマップ
- Daily Note = 日々の学習記録

## Critical rules

- 数学的内容をVault整理のために勝手に書き換えない。
- ユーザー答案を要約・別解化して置換しない。
- 同じ概念ノートを重複作成しない。
- 新規概念ノート作成前に既存ノートを検索する。
- `status` は採点結果であり、復習状態ではない。
- `status` は `正解 / 部分的なミスあり / 不正解 / 回答なし` のみ。
- 復習状態は `last-reviewed`, `next-review`, `review-count` で管理する。
- `daily_report.md` と `00_学習管理/Daily/` を混同しない。
- Git commit / pushはユーザーの明示指示なしに行わない。
