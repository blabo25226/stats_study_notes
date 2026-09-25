# Skill: Update Daily Report

## Purpose

その日のAI作業を `daily_report.md` に追記し、
後から「何を学習・処理し、どこで躓いたか」を確認できる状態にする。

## Trigger

- まとまった学習ノート処理の終了時
- 答案のMarkdown化・採点の終了時
- 教材/公式解答のTeX化の終了時
- ユーザーが `daily_report.md` の更新を指示したとき

## Procedure

### 1. 今日の日付を確認する

既存 `daily_report.md` を読み、今日の日付のセクションがあるか確認する。

### 2. 作業内容を収集する

今回の作業から次を整理する。

- 学習した内容
- 新規作成ファイル
- 更新ファイル
- 採点結果
- 躓いたポイント
- 次回確認事項

### 3. 追記する

推奨形式:

```markdown
## YYYY-MM-DD

### 学習・作業内容

- ...

### 作成・更新ファイル

- `path/to/file.md`

### 採点

- `問3.md`: 正解
- `問4.md`: 部分的なミスあり — 符号ミス

### 躓いたポイント

- ...

### 次回

- ...
```

空の節は無理に残さなくてよい。

### 4. 既存内容を守る

- 過去日の記録を削除しない。
- 同日の内容がある場合は統合する。
- 同じファイル変更を重複記録しない。

### 5. 保存後

Git commit / pushは行わない。

## Important

Obsidian Daily Noteの

```text
00_学習管理/Daily/YYYY-MM-DD.md
```

をこのSkillで更新してはならない。
こちらは `.claude/skills/daily-study/` の担当である。
