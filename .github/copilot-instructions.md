# GitHub Copilot Instructions

このリポジトリは Claude Code 向けの設定を基準にして開発している。

作業時は、まず以下を確認すること。

1. `CLAUDE.md`
2. `.claude/commands/`
3. `.claude/skills/`

`CLAUDE.md` は、このリポジトリの開発方針・設計思想・技術スタック・作業ルールの一次情報として扱うこと。

`.claude/commands/` に定義された Markdown ファイルは、定型作業の手順書として扱うこと。ユーザーが `/run`、`/verify`、`/plan-kaizen` などの Claude Code コマンド名を指定した場合は、対応する `.claude/commands/*.md` を読んで、その意図に従うこと。

`.claude/skills/` に定義された `SKILL.md` は、特定タスク用の手順・制約・ベストプラクティスとして扱うこと。ユーザーの依頼内容に該当する skill がある場合は、その `SKILL.md` を読んでから作業すること。

新しいルールや手順を追加する場合は、まず既存の `CLAUDE.md`、`.claude/commands/`、`.claude/skills/` の構造に合わせること。安易に Copilot 専用の別ルールを増やさないこと。