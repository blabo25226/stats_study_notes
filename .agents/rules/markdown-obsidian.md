# Markdown / Obsidian Rules

このリポジトリはObsidian Vaultとして閲覧される。

## 1. 数式

- インライン数式は `$...$`、ディスプレイ数式は `$$...$$` を使う。
- `$$` は単独行に置く。

  ```markdown
  $$
  E[X] = \int_{-\infty}^{\infty} x f(x)\,dx
  $$
  ```

- `\[...\]`, `\(...\)` は使わない（Obsidianで表示されないため）。
- 複数行の式は `$$` の中で `\begin{align*} ... \end{align*}` を使う。
- `\mathbb`, `\mathrm`, `\boldsymbol` などMathJaxで使えるコマンドのみ使う。
  `\newcommand` やパッケージ依存のマクロは使わない。
- 表のセル内で `|` を使う場合は `\mid` や `\vert` にする。

## 2. 見出し

- H1（`#`）はノートに1つだけ置く。問題ノートでは `# 第n章 問b`。
- 問題ノートのH2は `## 問題の要約` と `## 答案` のみ（`problem-note.md`）。
- 小問は `###` で `(1)`, `(2)` のように分ける。

## 3. 内部リンク

- 問題ノートの内部リンクは、frontmatterの `concepts` Property（`frontmatter.md` §2, §4）でのみ表す。
  本文には `[[...]]` を書かず、`## 関連` 節も作らない。
- 内部リンクの整備はClaudeの担当（`AGENTS.md` の「AI roles」）。Geminiは内部リンクを追加しない。

## 4. frontmatter

`.agents/rules/frontmatter.md` に従う。

## 5. 画像

- 答案写真・教科書画像は `91_docs/`（Git管理外）にあるため、公開ノートに埋め込まない。
- ノート用の図は `90_data/` に置き、`92_src/create_graphs/` のコードで生成する。

## 6. その他

- 強調は `**太字**` を使う。
- コールアウトは `> [!note]`, `> [!warning]` などObsidian標準のものを使う。
- 改行コードは既存ファイルに合わせる。
