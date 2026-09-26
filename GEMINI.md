# Gemini Instructions

@./AGENTS.md

このリポジトリでのGeminiの担当は、`AGENTS.md` と `.agents/` に書かれた **教材処理・採点のみ** である。

- 作業前に `AGENTS.md` の「AI roles」と、該当する `.agents/rules/`・`.agents/skills/` を読む。
- `.claude/` 以下は読まなくてよく、編集しない。
- 内部リンク、MOC、Bases、Daily Note、復習Properties、Vault全体の整理はClaudeの担当。
  必要になった場合は作業せず、ユーザーに「Claudeの担当」と伝える。
- 作業終了時は `.agents/skills/update-daily-report/SKILL.md` に従い、「作業AI: Gemini」として `daily_report.md` に追記する。
- Git commit / push はユーザーの明示指示なしに行わない。
