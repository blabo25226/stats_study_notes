---
paths:
  - "**/*.base"
  - "00_学習管理/**/*.md"
---

# Bases rules

`.base` はObsidian BasesのYAMLとして扱う。

## Principle

- Baseはノートを複製しない。
- データ本体は各MarkdownのPropertiesに保持する。
- Baseはfilter / view / orderを定義するだけにする。
- `.base` を編集するときは既存ビューを不用意に削除しない。

## Main bases

`00_学習管理/Bases/` に以下を置く。

- `問題一覧.base`
- `今日の復習.base`
- `概念別教科書問題一覧.base`（概念ノートに埋め込み、`concepts` でそのノートを指す `01_` の教科書問題を一覧）
- `概念別過去問一覧.base`（概念ノートに埋め込み、`concepts` でそのノートを指す `02_`〜`04_` の統計検定1級過去問を一覧）
- `不正解.base`
- `統計検定1級.base`
- `確率解析.base`

## Review properties

復習Baseで使用するProperties:

```yaml
review-count: 0
last-reviewed: 2026-09-25
next-review: 2026-09-28
```

`status` と復習Propertiesは分離する。
