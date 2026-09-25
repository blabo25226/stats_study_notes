# `.agents/` ガイド

このディレクトリは、学習ノートをAIエージェントが一貫した方法で扱うためのルール・スキル・テンプレート・参照情報を管理する。

## 構成

```text
.agents/
├── README.md
├── rules/
│   ├── core.md
│   ├── math.md
│   ├── markdown-obsidian.md
│   ├── frontmatter.md
│   ├── files-and-paths.md
│   ├── copyright.md
│   └── git.md
├── skills/
│   ├── answer-photo-to-markdown/
│   │   └── SKILL.md
│   ├── textbook-screenshot-to-tex/
│   │   └── SKILL.md
│   └── official-answer-to-tex/
│       └── SKILL.md
├── templates/
│   ├── exercise-note.md
│   └── theory-note.md
└── references/
    ├── repository-map.md
    ├── taxonomy.md
    └── grading-rubric.md
```

## 優先順位

矛盾がある場合は、原則として以下の順に優先する。

1. ユーザーがその場で明示した指示
2. ルート `AGENTS.md` の Critical rules
3. 該当する `.agents/skills/*/SKILL.md`
4. `.agents/rules/*.md`
5. `.agents/templates/*.md`
6. 既存ノートの慣例

既存ノートの形式を尊重するが、既存ファイルに明らかな誤りや古いルールがある場合は、新しいルールを優先する。

## Skill の考え方

Skillは「特定の入力が置かれたときに何をするか」を定義する。

- 答案写真が入る → `answer-photo-to-markdown`
- 教科書ページが入る → `textbook-screenshot-to-tex`
- 公式解答が入る → `official-answer-to-tex`

同一タスクで複数Skillが関係する場合は、依存関係に従って必要なSkillを組み合わせる。
