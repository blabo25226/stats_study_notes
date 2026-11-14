# 作業環境と指示の読み方

確認日: 2026-11-14（Asia/Tokyo）。実行時の環境情報が異なる場合はそちらを優先する。

- OS・シェル: Windows / PowerShell。
- リポジトリ: `C:\Document\数理統計学勉強`。Obsidian Vault兼Gitリポジトリ。
- 利用AI: Codex・Claude・Gemini。指示の正本はルートの `AGENTS.md`、詳細は `.agents/`。
- 指示ファイルを自動で読むかは利用クライアント・起動方法による。自動読込を保証せず、未読の場合は `AGENTS.md` と該当Rule・Skillを明示して読む。
- `.agents/skills/` の自動検出も前提にせず、`AGENTS.md` の一覧から必要な `SKILL.md` を開く。
- UTF-8で日本語ファイルを扱い、既存の改行コードを不用意に変えない。
- 日付はAsia/Tokyoを使用する。端末・API・ネットワークの利用可否や承認設定はセッションの実際の権限に従い、ここで権限を付与しない。
- 教材・中間生成物・作業ログのGit除外は `.agents/rules/git.md` に従う。

## Obsidian管理の考え方

フォルダは教材・分野、Propertiesは構造化属性、内部リンクは数学的関係を表す。
BasesはPropertiesを参照する一覧、MOCは学習ロードマップ、Daily Noteは学習日誌である。
数学的本文やユーザー答案を整理目的で書き換えない。新規概念ノートは既存ノートを検索してから作る。
Vault全体の整理では `.agents/skills/organize-vault/SKILL.md` に従う。
