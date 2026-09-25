---
paths:
  - "**/*.md"
---

# Properties rules

## 問題ノート

問題演習ノートでは基本的に以下を用いる。

```yaml
---
test-category: 統計数理
stats-category: 確率
difficulty: 中
status: 正解
review-count: 0
last-reviewed:
next-review:
---
```

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
