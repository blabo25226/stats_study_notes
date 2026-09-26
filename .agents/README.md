# .agents

AIアシスタント向けの、教材処理・採点のルールとスキル。入口は `AGENTS.md`。

ClaudeとGeminiの両方がこのディレクトリのルールに従う。
Obsidian Vaultの管理（内部リンク・MOC・Bases・Daily Note・復習管理）はClaudeのみの担当で、ルールは `.claude/` にある。
担当範囲の詳細は `AGENTS.md` の「AI roles」を参照する。

## 基準となるファイル

| 対象 | 唯一の基準 |
|---|---|
| パス・命名・入出力先 | `references/canonical-paths.md` |
| frontmatter | `rules/frontmatter.md` |
| 分類の語彙 | `references/taxonomy.md` |
| 採点 | `references/grading-rubric.md` |

各SkillやRuleにパスやfrontmatterが書かれている場合も、上のファイルと一致させる。
矛盾がある場合はユーザーの最新指示を最優先し、次に上のファイルを優先する。

## 構成

構成の一覧は `references/repository-map.md` §4 を参照する。
