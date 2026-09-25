# Git Rules

## 禁止事項

AIはユーザーから明示的な指示がない限り、以下を実行しない。

- `git commit`
- `git push`
- ブランチの削除
- 履歴のrewrite
- force push

## 許可される支援

- `git status` の確認
- `git diff` の確認
- 変更内容の要約
- コミットメッセージ案の作成
- `.gitkeep` の整理
- `.gitignore` の確認

## 重要

現在のリポジトリでルート `AGENTS.md` をGit管理したい場合は、
`.gitignore` に `AGENTS.md` が記載されていないことを確認する。

`.agents/` はAI設定そのものなので、可能ならGit管理する。
