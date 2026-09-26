---
paths:
  - "**/*.md"
---

# Properties rules

## 問題ノート

キー・順序・表記の基準は `.agents/rules/frontmatter.md`。以下はその要約。

```yaml
---
test-category: 統計数理
stats-category: 確率
difficulty: 中
status: 正解
tags:
  - 変数変換
source: 現代数理統計学の基礎 第2章
created: 2026-09-25
updated: 2026-09-25
review-count: 0
last-reviewed:
next-review:
---
```

- 値はダブルクォートで囲まない。
- `difficulty` は `易 / 中 / 難` のみ。
- 汎用タグ（`数理統計学` など）は付けない。

`review-count`, `last-reviewed`, `next-review` は復習運用を開始した問題だけ追加してよい。

## status

`status` は採点結果専用。

- 正解
- 部分的なミスあり
- 不正解
- 回答なし

理解度や「要復習」を `status` に入れない。

## 理論・概念ノート

採点対象ではない理論ノートでは、`status` を無理に付与しない。
必要な分類Propertiesのみを使う。

## Existing metadata

既存値を推測で一括変換しない。
特に `status: 一度解けた` を機械的に `正解` にしてはならない。
答案と公式解答の照合後に変更する。
