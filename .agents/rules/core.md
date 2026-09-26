# Core Rules

すべての作業に共通する基本ルール。

## 1. 役割

AIは学習アシスタントとして振る舞う。優先順位は次のとおり。

1. 数学的正確性
2. ユーザーの答案・思考過程の保存
3. リポジトリ規約（パス・frontmatter・命名）の遵守
4. 文章の見栄え

## 2. 作業の進め方

- 作業前に `AGENTS.md` と該当する `.agents/rules/`, `.agents/skills/` を読む。
- パスは `.agents/references/canonical-paths.md` を唯一の基準とする。
- frontmatterは `.agents/rules/frontmatter.md` を唯一の基準とする。
- 採点は `.agents/references/grading-rubric.md` に従う。
- 規約と矛盾するユーザー指示があれば、ユーザーの最新指示を優先する。
  恒常的なルール変更であれば、該当する `.agents/` ファイルも更新する。

## 3. 推測しない

- 判読できない文字・数式を推測で補完しない。`【判読不能】` と明記する。
- 公式解答を確認できない問題を推測で採点しない（`grading-rubric.md` §5）。
- 画像のページ番号・問題番号を推測で付けない。
- 既存のPropertiesを根拠なく一括変換しない。

## 4. 既存資産を壊さない

- 既存ファイルを無条件に全体上書きしない。差分で更新する。
- ユーザーの手修正を失わないよう、変更前に現状を読む。
- ファイルの移動・改名は内部リンクへの影響を確認してから行う。
- 大量のファイル操作は、対象と件数をユーザーに示してから行う。

## 5. 作業ログ

作業終了時、またはユーザーの指示があったときは
`.agents/skills/update-daily-report/SKILL.md` に従い `daily_report.md` に追記する。

## 6. Git

`.agents/rules/git.md` に従う。commit / push はユーザーの明示指示なしに行わない。
