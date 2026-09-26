# Obsidian Vault Assistant

@../AGENTS.md

この `.claude/` はClaude Code専用設定である。

## Role

Claudeは、このリポジトリの **すべての作業** を担当する。

| 領域 | ルール | 担当AI |
|---|---|---|
| 教材・答案の処理、採点、`daily_report.md` | `AGENTS.md` と `.agents/` | Claude、Gemini |
| Obsidian Vaultの管理 | `.claude/` | Claudeのみ |

`.agents/` の担当:
- 手書き答案 → 問題ノート
- 教科書スクリーンショット → TeX
- 公式解答PDF → 章別TeX
- 数学的採点
- `daily_report.md`

`.claude/` の担当:
- Obsidian内部リンク
- MOC
- Bases
- Propertiesの整理
- Daily Notes
- 復習管理
- Vaultの重複・孤立ノート整理

`.agents/` のタスクでは、`.agents/` のRule・Skillを読んでから処理する（`AGENTS.md` の Skills 節）。
数学的内容や教材処理について `.claude/` が `AGENTS.md` と競合する場合、
`AGENTS.md` / `.agents/` の具体的ルールを優先する。

`.agents/` はGeminiと共有するルールである。Claudeが `.agents/` を変更するときは、
Geminiが読んでも単独で理解できるように書き、`.claude/` のファイルへの依存を持ち込まない。

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
