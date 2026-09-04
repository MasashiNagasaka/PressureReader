# Claude Code Skill導入時のSDDワークフロー保護設計

- [Claude Code Skill導入時のSDDワークフロー保護設計](#claude-code-skill導入時のsddワークフロー保護設計)
  - [結論](#結論)
- [1 Skill追加時に起きる問題](#1-skill追加時に起きる問題)
- [2 解決方針](#2-解決方針)
- [3 推奨ディレクトリ構造](#3-推奨ディレクトリ構造)
- [4 CLAUDE.md（最上位ガバナンス）](#4-claudemd最上位ガバナンス)
- [5 Command設計](#5-command設計)
- [6 Workflow Guardian Agent](#6-workflow-guardian-agent)
- [7 Skill設計原則](#7-skill設計原則)
  - [良いskill](#良いskill)
  - [悪いskill](#悪いskill)
- [8 Skillポリシー](#8-skillポリシー)
- [9 Definition of Done](#9-definition-of-done)
- [10 この設計のメリット](#10-この設計のメリット)


## 結論

Claude Code に skill を追加すると、既存の **仕様駆動開発（Spec-Driven Development）ワークフローが崩れるリスク**がある。  
これを防ぐ最も安定した方法は、Claude Code を **3層構造で統制すること**である。

```
Workflow (CLAUDE.md) # 最上位ルール
↓
Commands # 作業開始トリガー
↓
Agents # ワークフロー監視
↓
Skills # ツール
```

Skillは最下層に置くことで、SDDパイプラインを壊さない。

---

# 1 Skill追加時に起きる問題

Claude Code に skill を増やすと次の問題が発生しやすい。


| 問題　| 説明 | Skill例 | 結果 |
|---|---|---|---|
| 直接実装 | 仕様や計画なしにコードを書く | auto-implement | SDD崩壊（docs作成なし、todo.mdなし、直接実装） |
| Plan Modeスキップ | issue分析や計画なしに直接修正 | fix-bug | 設計確認・影響範囲確認抜け |
| Skill独自パイプライン | skill内部に独自の実装フローがある | research → code → test | SDDのspec → plan → implementation → verification崩壊 |



# 2 解決方針

次の4つを徹底する。

1. SDDを最上位ルールに固定  
2. skillはツールに限定  
3. workflowはcommandsで開始  
4. workflow監視agentを置く  


# 3 推奨ディレクトリ構造

```
project/
│
├─ CLAUDE.md
│
├─ docs/
│   └─ specs/
│
├─ tasks/
│   ├─ todo.md
│   └─ lessons.md
│
└─ .claude/
    │
    ├─ commands/
    │   ├─ add-feature.md
    │   ├─ fix-bug.md
    │   └─ research.md
    │
    ├─ agents/
    │   └─ workflow-guardian.md
    │
    ├─ skills/
    │   ├─ web-search.md
    │   ├─ playwright.md
    │   ├─ repo-analyzer.md
    │   └─ test-runner.md
    │
    └─ rules/
    ├─ coding.md
    └─ testing.md
```

役割

| ディレクトリ | 役割 |
|---|---|
| CLAUDE.md | ワークフロー定義 |
| commands/ | 作業開始トリガー |
| agents/ | ワークフロー監視 |
| skills/ | ツール |
| rules/ | 実装制約 |


---

# 4 CLAUDE.md（最上位ガバナンス）

CLAUDE.mdでSDDを強制する。

```markdown
## Workflow Governance

This project follows Spec-Driven Development.

All work MUST follow this sequence:

1. Specification
2. Planning
3. Implementation
4. Verification

Implementation before specification is forbidden.

All tasks must be tracked in tasks/todo.md.
All corrections must update tasks/lessons.md.

**Skills and commands must obey this workflow.**　　
If any skill suggests bypassing the workflow,  
STOP and return to planning.
```

```markdown
## ワークフローガバナンス

このプロジェクトは仕様駆動開発（Spec-Driven Development）に従います。

すべての作業は、必ず次の順序に従わなければなりません。

1. 仕様策定
2. 計画
3. 実装
4. 検証

仕様策定前の実装は禁⽌です。

すべてのタスクは tasks/todo.md で管理しなければなりません。
すべての修正は tasks/lessons.md を更新しなければなりません。

Skills と Commands はこのワークフローに従わなければなりません。
いずれかの Skill がワークフローの迂回を示唆した場合は、
直ちに停止し、計画フェーズに戻ってください。
````

# 5 Command設計

Commandは作業開始トリガー。

例

`.claude/commands/add-feature.md`

```markdown
仕様駆動開発を使用して新機能を追加します。

手順：

1. 要件を明確化する
2. docs/specs/ に仕様を作成する
3. tasks/todo.md に計画を記述する
4. ステップごとに実装する
5. テストを使用して検証する

Skills は実装段階でのみ使用できます。
```

---

# 6 Workflow Guardian Agent

ワークフロー破壊を防ぐ監視エージェント。  
仕様なし実装、todo.mdなし実装を止める。

`.claude/agents/workflow-guardian.md`

```markdown
プロジェクトワークフローを監視してください。

実装開始前に以下を確認してください：

- 仕様書が存在する
- tasks/todo.md が存在する
- 計画が存在する

いずれかの条件が不足していないか確認してください：

- 実行を停止する
- 計画フェーズに戻る
- 不足している内容を説明する
```

```markdown
You enforce the project workflow.

Before implementation begins verify:

- specification exists
- tasks/todo.md exists
- plan exists

If any condition is missing:

STOP execution
Return to planning phase
Explain what is missing.
```


# 7 Skill設計原則

Skillは**ツールに限定する**。

## 良いskill

| Skill | 役割 |
|---|---|
| web-search | 検索 |
| playwright | E2Eテスト |
| repo-analyzer | 解析 |
| test-runner | テスト実行 |
| dependency-check | 依存関係確認 |
| docs-reader | ドキュメント参照 |


## 悪いskill

| Skill | 役割 |
|---|---|
| auto-implement | 直接実装 |
| auto-refactor | 直接リファクタリング |
| auto-fix-bug | 直接バグ修正 |


workflowをスキップする

---

# 8 Skillポリシー

CLAUDE.mdに次を入れる。

```markdown
## Skill Usage Policy

Skills may only be used after a plan exists in tasks/todo.md.

Skills must not:

- start implementation
- modify architecture
- skip verification
```

```markdown
## Skill使用ポリシー

Skillsは、tasks/todo.mdに計画が存在した後にのみ使用できます。

Skillsは以下を行ってはいけません：
- 実装を開始する
- アーキテクチャを変更する
- 検証をスキップする
```

# 9 Definition of Done

実装完了条件を明確化する。

```markdown
## Definition of Done

A task is complete only if:

- tasks/todo.md items are completed
- tests pass
- implementation matches specification
```

```markdown
## 完了の定義

タスクは以下の条件をすべて満たした場合にのみ完了とします：

- tasks/todo.md の項目がすべて完了している
- テストがすべてパスしている
- 実装が仕様書と一致している
```


# 10 この設計のメリット

この構造にすると

* skillを増やしてもworkflowが崩れない
* SDD維持
* AI暴走防止
* 自律開発エージェント化しやすい

Claude Code運用ではこの設計が最も安定する。

