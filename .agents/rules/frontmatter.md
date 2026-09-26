# Frontmatter Rules

問題ノート（`01_`〜`05_`）のYAML frontmatterは、以下のキー・順序・表記に統一する。
新規作成時も既存ノート更新時も、このファイルを唯一の基準とする。

## 1. 標準形

```yaml
---
test-category: 統計数理
stats-category: 確率分布
difficulty: 中
status: 正解
tags:
  - 指数分布
  - 積率母関数
source: 現代数理統計学の基礎 第3章
created: 2026-09-25
updated: 2026-09-25
---
```

## 2. キーの順序

以下の順で並べる。存在しない任意キーは省略し、順序は崩さない。

| 順 | キー | 必須 | 内容 |
|---|---|---|---|
| 1 | `test-category` | 必須 | `統計数理` / `統計応用` など試験区分 |
| 2 | `stats-category` | 必須 | 分野（§5） |
| 3 | `difficulty` | 必須（値は空可） | `易` / `中` / `難` |
| 4 | `status` | 必須（公式解答未確認の間のみ空可） | 採点結果（§3） |
| 5 | `tags` | 必須 | 数学的トピック（§4） |
| 6 | `source` | 必須 | 出典。例: `現代数理統計学の基礎 第n章` |
| 7 | `section` | 任意 | 教科書の節番号。`"4.7"` のように引用符付き |
| 8 | `created` | 必須 | 作成日 `YYYY-MM-DD` |
| 9 | `updated` | 必須 | 最終更新日 `YYYY-MM-DD` |
| 10 | `review-count` | 任意 | 復習回数（復習運用を開始した問題のみ） |
| 11 | `last-reviewed` | 任意 | 前回復習日 |
| 12 | `next-review` | 任意 | 次回復習日 |

## 3. 値の表記

- 文字列値はダブルクォートで囲まない。
  - 正: `status: 正解`
  - 誤: `status: "正解"`
  - 例外: `section` は数値と誤認されないよう `"4.7"` と引用符を付ける。
- `status` は次の4値のみ（採点結果専用。理解度・復習状態ではない）。
  - `正解` / `部分的なミスあり` / `不正解` / `回答なし`
- `difficulty` は `易` / `中` / `難` のみ。`easy` / `normal` / `hard` などの英語表記は使わない。
  - 未判定の場合は `difficulty:` と値を空にする。問題内容を確認せずに埋めない（基準は `taxonomy.md` §3）。
- 日付は引用符なしの `YYYY-MM-DD`。

## 4. tags

- その問題の中心となる数学的トピックを2〜8個程度付ける。
  - 例: `指数分布`, `変数変換`, `最尤推定量`, `十分統計量`
- 次のような汎用タグは付けない（フォルダ・Propertiesで表現済みのため）。
  - `数理統計学`, `現代数理統計学の基礎`, `統計学`, `演習問題`, `統計検定1級`
- 同義語は1つに寄せる。既存タグを検索してから付ける。表記の統一表は `.agents/references/taxonomy.md` §4。

- 回答なしの問題でも、問題文・公式解答の内容からtagsを付ける。

## 5. 分類の語彙

`test-category`, `stats-category`, `difficulty` の値と判断基準は `.agents/references/taxonomy.md` に従う。

## 6. 使わないキー

以下は使わない。既存ノートにあれば標準形へ移すか削除する。

| 旧キー | 扱い |
|---|---|
| `title`, `id`, `chapter`, `allpaths`, `draft` | 削除（ファイルパスとH1見出しで表現済み） |
| `source_book` | `source` に統合 |
| `created-date`, `created_at`, `date` | `created` に統合 |
| `updated-date`, `updated_at`, `last-modified` | `updated` に統合 |

## 7. 理論・概念ノート

採点対象でない理論・概念ノートには `status` を付けない。
`test-category`, `stats-category`, `tags`, `created`, `updated` など必要なキーのみを同じ順序で使う。

## 8. 禁止事項

- 既存の `status` を推測で書き換えない（採点照合後のみ変更する）。
- frontmatter整理のために本文・数式を書き換えない。
- `status` に理解度・復習状態（「要復習」など）を入れない。
