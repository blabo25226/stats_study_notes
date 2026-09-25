---
name: update-review
description: 採点済み問題の復習Propertiesを更新し、次回復習日を設定する。復習計画や復習完了の記録を求められたときに使用する。
---

# Update Review

## Properties

```yaml
review-count: 0
last-reviewed:
next-review:
```

## Default intervals

ユーザーが別の間隔を指定していない場合の初期目安:

- `不正解`: 2日後
- `部分的なミスあり`: 4日後
- `正解`: 10日後
- `回答なし`: 次回日を自動設定しない

これは固定的な学習理論ではなく、Vault運用上の初期値。
ユーザーが復習頻度を指定した場合はその指示を優先する。

## When reviewed again

- `review-count` を1増やす。
- `last-reviewed` を当日にする。
- 最新の採点結果に応じて `next-review` を更新する。
- 数学的採点そのものは `.agents/` のgrading rubricに従う。
