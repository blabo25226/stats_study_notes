# Skill: Answer Photo to Markdown

## Purpose

『現代数理統計学の基礎』第2〜7章の章末問題について、ユーザーの手書き答案写真から問題ノートを作り、
公式解答と照合して `status` を付ける。

ノートの構成は `.agents/rules/problem-note.md` に従い、**frontmatter・問題の要約・答案のみ**とする。
採点理由・解説はノートに書かない。

## Trigger

```text
91_docs/materials/現代数理統計学の基礎/第n章/回答/   (n = 2〜7)
```

に答案写真が入ったとき、またはユーザーから答案の書き起こし・採点を指示されたとき。

## References

処理前に以下を読む。

- `.agents/rules/problem-note.md`（本文構成・対象章）
- `.agents/rules/frontmatter.md`（frontmatter）
- `.agents/references/taxonomy.md`（分類の語彙・難易度）
- `.agents/references/grading-rubric.md`（採点）
- `.agents/references/canonical-paths.md`（パス）

## Input

答案写真:

```text
91_docs/materials/現代数理統計学の基礎/第n章/回答/問b_c.jpg
```

- `b`: 問題番号
- `c`: その問題の答案の何枚目か（1から）

問題文（要約の元）:

```text
91_docs/materials/現代数理統計学の基礎/第n章/latex/chaptern.tex
91_docs/materials/現代数理統計学の基礎/第n章/スクリーンショット/pAA.png
```

`chaptern.tex` の演習問題の節がスクリーンショットと食い違うことがある。
食い違う場合はスクリーンショットを正とする。

公式解答（採点用）:

```text
91_docs/materials/現代数理統計学の基礎/第n章/答え/answers.tex
```

## Output

```text
01_現代数理統計学の基礎/第n章/問b.md
```

1問題1ファイル。第1章・第8章以降は作らない。

## Procedure

### Step 1: 画像を整理する

- 画像の向きを確認し、倒れていれば回転補正する。
- ファイル名が `問b_c.jpg` 形式でなければ、画像内容から問題番号・枚数を確認してリネームする。
- 問題番号が判別できない画像は推測で命名せず、ユーザーに確認する。

### Step 2: 答案をTeXに書き起こす

- 答案の論理展開・途中式・記法をそのまま再現する。誤りがあっても直さない。
- 判読できない箇所は `【判読不能】` と書き、推測で補わない。
- 答案中の疑問符・メモ（「?」など）も残す。
- 小問ごとに `### (1)` のように見出しを付ける。
- ユーザーがGemini等で書き起こし済みのTeXを渡した場合は、それを `## 答案` にそのまま使う。

### Step 3: 問題の要約を書く

- 教科書の問題文から、設定と求めるものを短くまとめる（`problem-note.md` §3）。

### Step 4: 採点する

- `grading-rubric.md` に従って `status` を決める。
- 判定理由はノートに書かず、ユーザーに報告し `daily_report.md` に記録する。

### Step 5: frontmatterを付ける

- `stats-category` は章から決める（`taxonomy.md` §2）。
- `difficulty` は問題内容から `易/中/難` を判断する（`taxonomy.md` §3）。
- `tags` は数学的トピックを2〜8個。

### Step 6: ノートを書く

```markdown
---
test-category: 統計数理
stats-category: 標本分布
difficulty: 中
status: 部分的なミスあり
tags:
  - マルコフの不等式
  - 積率母関数
source: 現代数理統計学の基礎 第5章
created: 2026-09-26
updated: 2026-09-26
---

# 第5章 問6

## 問題の要約

（問題文の要約）

## 答案

### (1)

（答案）

### (2)

（答案）
```

- 回答なしの場合、`## 答案` の本文は `答案未提出` の1行。
- 目次・採点・解説・関連知識・`## 関連` は書かない。

### Step 7: 既存ノートがある場合

- 無条件に上書きしない。
- 解き直しの答案であれば、`## 答案` の中に `### 解き直し（YYYY-MM-DD）` を追加し、
  採点が変われば `status` と `updated` を更新する。

### Step 8: 完了確認

- [ ] 出力先が `01_現代数理統計学の基礎/第n章/問b.md`（n = 2〜7）
- [ ] frontmatterが `frontmatter.md` の標準形
- [ ] 本文が `## 問題の要約` と `## 答案` のみ
- [ ] 答案を書き換えていない
- [ ] 判読不能箇所を捏造していない
- [ ] `status` が公式解答との照合に基づいている
- [ ] 数式がObsidianで表示できる
- [ ] Git commit / pushをしていない

作業後は `update-daily-report` スキルで `daily_report.md` に採点結果と判定理由を記録する。
