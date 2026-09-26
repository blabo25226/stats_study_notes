# Git Rules

## 1. 基本

- AIは `git commit` / `git push` をユーザーの明示指示なしに行わない。
- 「コミットして」「pushして」など明示的な指示があった場合のみ実行する。
- `git reset --hard`, `git push --force`, `git clean` など破壊的な操作は、
  指示があっても対象を確認してから行う。

## 2. Git管理対象外

`.gitignore` で以下を除外している。これを変更しない。

- `91_docs/`（教材・答案写真・公式解答）
- `90_data/`（生成データ）
- `daily_report.md`（AI作業ログ）

## 3. コミットする場合

- メッセージは変更内容が分かる短い英語または日本語にする。
  - 例: `add chapter7 answers`, `normalize frontmatter`
- 1コミットに無関係な変更を混ぜない。
- `.obsidian/workspace.json` など個人のUI状態の変更は、指示がない限りコミットに含めない。

## 4. 改行コード

- Windows環境で `core.autocrlf` の警告が出ることがある。
- 既存ファイルの改行コードを勝手に一括変換しない。
