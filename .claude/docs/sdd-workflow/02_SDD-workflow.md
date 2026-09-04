# SDD (Spec Driven Development) ワークフロー

SDD は「仕様を先に書き、仕様に従って実装する」開発手法です。
ドキュメントを正とし、Claude が自律的に計画・実装・検証までを担います。

---

## 目次

1. [全体フロー](#全体フロー)
2. [コマンド一覧](#コマンド一覧)
3. [/setup-project](#setup-project) — 初回セットアップ（6ドキュメント作成）
4. [/add-feature](#add-feature) — 機能追加（標準）
5. [/add-feature-ui](#add-feature-ui) — 機能追加（E2Eテストあり）
6. [/resume-work](#resume-work) — 中断作業の再開
7. [/review-docs](#review-docs) — ドキュメントレビュー
8. [品質ゲート一覧](#品質ゲート一覧)
9. [スキル・サブエージェント 参照マップ](#スキルサブエージェント-参照マップ)

---

## 全体フロー

```mermaid
flowchart TD
    Start([プロジェクト開始]) --> SetupQ{初回セットアップ済?}
    SetupQ -->|No| Setup["/setup-project"]
    SetupQ -->|Yes| DevCycle

    Setup --> Docs[("docs/<br/>6ドキュメント完成")]
    Docs --> DevCycle

    subgraph DevCycle ["🔄 開発サイクル"]
        direction LR
        AddFeature["/add-feature 機能名"]
        AddFeatureUI["/add-feature-ui 機能名<br/>(E2Eテストあり)"]
        ResumeWork["/resume-work<br/>(中断作業の再開)"]
        ReviewDocs["/review-docs パス"]
        AddFeature -->|ドキュメント更新が必要な場合| ReviewDocs
        AddFeatureUI -->|ドキュメント更新が必要な場合| ReviewDocs
        AddFeature -->|中断した場合| ResumeWork
        AddFeatureUI -->|中断した場合| ResumeWork
    end
```

---

## コマンド一覧

| コマンド | 用途 | タイミング |
|---------|------|-----------|
| `/setup-project` | 6種のドキュメントを順番に作成し、プロジェクト基盤を確立する | プロジェクト初回のみ |
| `/add-feature <機能名>` | 計画→実装→検証→振り返りを一貫して実行する | 通常の機能追加時 |
| `/add-feature-ui <機能名>` | `/add-feature` に加え E2E テスト（Gate 2）を必須実行する | UI を伴う機能追加時 |
| `/resume-work [ディレクトリ名]` | 中断したタスクを `tasklist.md` のチェックポイントから再開する | 作業が途中で止まった場合 |
| `/review-docs <パス>` | サブエージェントがドキュメントを独立コンテキストで精査し改善点を報告する | ドキュメント品質を上げたい時 |

---

## /setup-project

プロジェクト開始時に **1回だけ** 実行します。
`docs/ideas/` 配下のブレインストーミングメモを起点に、6種の永続ドキュメントを順番に生成します。
**Step 1（PRD）のみユーザー承認が必須**で、承認後に後続ステップへ進みます。

```mermaid
flowchart TD
    SP_Start(["▶ /setup-project"]) --> SP_Ideas

    SP_Ideas["docs/ideas/ 読み込み<br/>(ブレインストーミング・要件メモ)"]
    SP_Ideas --> SP1_skill

    subgraph SP1 ["Step 1: プロダクト要求定義書　⚠️ 承認必須"]
        SP1_skill["skill: prd-writing"] --> SP1_doc["docs/product-requirements.md"]
    end

    SP1 --> SP1_gate{"ユーザー承認"}
    SP1_gate -->|"修正依頼"| SP1
    SP1_gate -->|"承認"| SP2_skill

    subgraph SP2 ["Step 2: 機能設計書"]
        SP2_skill["skill: functional-design"] --> SP2_doc["docs/functional-design.md"]
    end
    SP2 --> SP3_skill

    subgraph SP3 ["Step 3: アーキテクチャ設計書"]
        SP3_skill["skill: architecture-design"] --> SP3_doc["docs/architecture.md"]
    end
    SP3 --> SP4_skill

    subgraph SP4 ["Step 4: リポジトリ構造定義書"]
        SP4_skill["skill: repository-structure"] --> SP4_doc["docs/repository-structure.md"]
    end
    SP4 --> SP5_skill

    subgraph SP5 ["Step 5: 開発ガイドライン"]
        SP5_skill["skill: development-guidelines"] --> SP5_doc["docs/development-guidelines.md"]
    end
    SP5 --> SP6_skill

    subgraph SP6 ["Step 6: 用語集"]
        SP6_skill["skill: glossary-creation"] --> SP6_doc["docs/glossary.md"]
    end

    SP6 --> SP_End(["✅ セットアップ完了"])
```

---

## /add-feature

機能追加の標準コマンドです。
「計画 → 実装 → 検証 → 品質ゲート → 動作確認 → 振り返り」の8フェーズを自動で実行します。

> **実装ループのルール**
> - **Rule A**: タスクが大きすぎる場合、サブタスクに分割して継続
> - **Rule B**: 技術的理由で不要なタスクは `[x] ~~タスク名~~ (理由)` として記録しスキップ

```mermaid
flowchart TD
    AF_Start(["▶ /add-feature 機能名"]) --> AF1

    AF1["① ステアリングディレクトリ作成<br/>.steering/YYYYMMDD-機能名/<br/>requirements.md / design.md / tasklist.md"]
    AF1 --> AF1_init_check{"src/ 存在?"}
    AF1_init_check -->|"No — 初回実行"| AF1_init["docs/repository-structure.md を読み込み<br/>ディレクトリ構造をすべて作成"]
    AF1_init_check -->|"Yes"| AF2
    AF1_init --> AF2

    AF2["② コンテキスト読み込み<br/>CLAUDE.md + docs/ + Grep検索(src/)"]
    AF2 --> AF3_skill

    subgraph AF3 ["③ 計画フェーズ"]
        AF3_skill["skill: steering（計画モード）"] --> AF3_docs["requirements.md / design.md / tasklist.md を生成"]
    end
    AF3 --> AF4_check

    subgraph AF4 ["④ 実装ループ（tasklist.md を全消化）"]
        AF4_check{"未完了タスク [ ] あり?"}
        AF4_check -->|Yes| AF4_exec

        subgraph AF4_exec ["タスク実行"]
            AF4_s1["skill: steering（実装モード）"]
            AF4_s2["skill: development-guidelines（コーディング規約遵守）"]
        end

        AF4_exec --> AF4_update["tasklist.md 更新　[ ] → [x]"]
        AF4_update --> AF4_check
        AF4_check -->|No| AF4_done["全タスク完了"]

        AF4_exec -->|"Rule A: タスクが大きすぎる"| AF4_split["サブタスクに分割して継続"]
        AF4_split --> AF4_check
        AF4_exec -->|"Rule B: 技術的理由で不要"| AF4_skip["[x] ~~タスク~~（理由記載）として継続"]
        AF4_skip --> AF4_check
    end

    AF4_done --> AF5_agent

    subgraph AF5 ["⑤ 実装検証"]
        AF5_agent["sub-agent: implementation-validator"] --> AF5_result["検証レポート<br/>（規約 / エラーハンドリング / 既存パターン整合性）"]
    end
    AF5 --> AF6_prep

    subgraph AF6 ["⑥ 品質ゲート検証（DoD 準拠）"]
        AF6_prep["definition-of-done.md 読み込み<br/>反復カウンター = 0（最大 3 回）"]
        AF6_prep --> AF6_g1

        AF6_g1["Gate 1 ✅ 必須<br/>npm run lint / typecheck / test"]
        AF6_g1 --> AF6_g3_check{"tests/vrt/__screenshots__/ 存在?"}
        AF6_g3_check -->|Yes| AF6_g3["Gate 3 — VRT<br/>npm run test:vrt"]
        AF6_g3_check -->|No| AF6_g4_check
        AF6_g3 --> AF6_g4_check{"tests/a11y/ 存在?"}
        AF6_g4_check -->|Yes| AF6_g4["Gate 4 — a11y<br/>npm run test:a11y"]
        AF6_g4_check -->|No| AF6_g5_check
        AF6_g4 --> AF6_g5_check{".claude/agents/ui-ux-validator.md 存在?"}
        AF6_g5_check -->|Yes| AF6_g5["Gate 5 — UI/UX<br/>sub-agent: ui-ux-validator"]
        AF6_g5_check -->|No| AF6_result
        AF6_g5 --> AF6_result{"全ゲート合格?"}

        AF6_result -->|"✅ 全パス"| AF6_done["CP-FINAL Evidence 記録"]
        AF6_result -->|"❌ 失敗"| AF6_count{"反復カウンター ≤ 3?"}
        AF6_count -->|"Yes（カウンター++）"| AF6_fix["原因分析・修正"]
        AF6_fix --> AF6_g1
        AF6_count -->|"No — エスカレーション"| AF6_escalate["failure-report.md 作成<br/>.steering/タスク名/<br/>→ ユーザーに報告・作業停止"]
    end

    AF6_done --> AF7_skill

    subgraph AF7 ["⑦ 動作確認・リグレッションチェック"]
        AF7_skill["skill: testing<br/>（実装機能の動作確認 / 既存機能のリグレッション確認）"]
    end

    AF7 --> AF8_skill

    subgraph AF8 ["⑧ 振り返り・ドキュメント更新"]
        AF8_skill["skill: steering（振り返りモード）"] --> AF8_notes["tasklist.md に申し送り記入<br/>（完了日 / 差分 / 学び / 改善提案）"]
        AF8_notes --> AF8_gate{"docs/ 更新が必要?"}
        AF8_gate -->|Yes| AF8_docs["docs/ 内の関連永続ドキュメントを更新"]
        AF8_gate -->|No| AF8_done
        AF8_docs --> AF8_done["完了"]
    end

    AF8_done --> AF_End(["✅ 機能追加完了"])
```

---

## /add-feature-ui

`/add-feature` と同一フローですが、**Gate 2（E2E テスト）が必須**で追加されます。
UI コンポーネントや画面遷移を含む機能追加時に使用してください。

> **Gate 2 失敗時**: `test-results/trace.zip` を Playwright Trace Viewer で確認してください。

```mermaid
flowchart TD
    AFU_Start(["▶ /add-feature-ui 機能名"]) --> AFU1

    AFU1["① ステアリングディレクトリ作成<br/>.steering/YYYYMMDD-機能名/<br/>requirements.md / design.md / tasklist.md"]
    AFU1 --> AFU1_init_check{"src/ 存在?"}
    AFU1_init_check -->|"No — 初回実行"| AFU1_init["docs/repository-structure.md を読み込み<br/>ディレクトリ構造をすべて作成"]
    AFU1_init_check -->|"Yes"| AFU2
    AFU1_init --> AFU2

    AFU2["② コンテキスト読み込み<br/>CLAUDE.md + docs/ + Grep検索(src/)"]
    AFU2 --> AFU3_skill

    subgraph AFU3 ["③ 計画フェーズ"]
        AFU3_skill["skill: steering（計画モード）"] --> AFU3_docs["requirements.md / design.md / tasklist.md を生成"]
    end
    AFU3 --> AFU4_check

    subgraph AFU4 ["④ 実装ループ（tasklist.md を全消化）"]
        AFU4_check{"未完了タスク [ ] あり?"}
        AFU4_check -->|Yes| AFU4_exec

        subgraph AFU4_exec ["タスク実行"]
            AFU4_s1["skill: steering（実装モード）"]
            AFU4_s2["skill: development-guidelines（コーディング規約遵守）"]
        end

        AFU4_exec --> AFU4_update["tasklist.md 更新　[ ] → [x]"]
        AFU4_update --> AFU4_check
        AFU4_check -->|No| AFU4_done["全タスク完了"]

        AFU4_exec -->|"Rule A: タスクが大きすぎる"| AFU4_split["サブタスクに分割して継続"]
        AFU4_split --> AFU4_check
        AFU4_exec -->|"Rule B: 技術的理由で不要"| AFU4_skip["[x] ~~タスク~~（理由記載）として継続"]
        AFU4_skip --> AFU4_check
    end

    AFU4_done --> AFU5_agent

    subgraph AFU5 ["⑤ 実装検証"]
        AFU5_agent["sub-agent: implementation-validator"] --> AFU5_result["検証レポート<br/>（規約 / エラーハンドリング / 既存パターン整合性）"]
    end
    AFU5 --> AFU6_prep

    subgraph AFU6 ["⑥ 品質ゲート検証（DoD 準拠）"]
        AFU6_prep["definition-of-done.md 読み込み<br/>反復カウンター = 0（最大 3 回）"]
        AFU6_prep --> AFU6_g1

        AFU6_g1["Gate 1 ✅ 必須<br/>npm run lint / typecheck / test"]
        AFU6_g1 --> AFU6_g2["Gate 2 ✅ 必須（E2E）<br/>npm run test:e2e<br/>失敗時 → test-results/trace.zip 確認"]
        AFU6_g2 --> AFU6_g3_check{"tests/vrt/__screenshots__/ 存在?"}
        AFU6_g3_check -->|Yes| AFU6_g3["Gate 3 — VRT<br/>npm run test:vrt"]
        AFU6_g3_check -->|No| AFU6_g4_check
        AFU6_g3 --> AFU6_g4_check{"tests/a11y/ 存在?"}
        AFU6_g4_check -->|Yes| AFU6_g4["Gate 4 — a11y<br/>npm run test:a11y"]
        AFU6_g4_check -->|No| AFU6_g5_check
        AFU6_g4 --> AFU6_g5_check{".claude/agents/ui-ux-validator.md 存在?"}
        AFU6_g5_check -->|Yes| AFU6_g5["Gate 5 — UI/UX<br/>sub-agent: ui-ux-validator"]
        AFU6_g5_check -->|No| AFU6_result
        AFU6_g5 --> AFU6_result{"全ゲート合格?"}

        AFU6_result -->|"✅ 全パス"| AFU6_done["CP-FINAL Evidence 記録"]
        AFU6_result -->|"❌ 失敗"| AFU6_count{"反復カウンター ≤ 3?"}
        AFU6_count -->|"Yes（カウンター++）"| AFU6_fix["原因分析・修正"]
        AFU6_fix --> AFU6_g1
        AFU6_count -->|"No — エスカレーション"| AFU6_escalate["failure-report.md 作成<br/>.steering/タスク名/<br/>→ ユーザーに報告・作業停止"]
    end

    AFU6_done --> AFU7_skill

    subgraph AFU7 ["⑦ 動作確認・リグレッションチェック"]
        AFU7_skill["skill: testing<br/>（実装機能の動作確認 / 既存機能のリグレッション確認）"]
    end

    AFU7 --> AFU8_skill

    subgraph AFU8 ["⑧ 振り返り・ドキュメント更新"]
        AFU8_skill["skill: steering（振り返りモード）"] --> AFU8_notes["tasklist.md に申し送り記入<br/>（完了日 / 差分 / 学び / 改善提案）"]
        AFU8_notes --> AFU8_gate{"docs/ 更新が必要?"}
        AFU8_gate -->|Yes| AFU8_docs["docs/ 内の関連永続ドキュメントを更新"]
        AFU8_gate -->|No| AFU8_done
        AFU8_docs --> AFU8_done["完了"]
    end

    AFU8_done --> AFU_End(["✅ 機能追加完了"])
```

---

## /resume-work

`/add-feature` または `/add-feature-ui` で開始した作業が中断した場合に、
`tasklist.md` のチェックポイントから作業を再開します。

引数を省略すると `.steering/` 内の**最新ディレクトリを自動選択**します。

```mermaid
flowchart TD
    RW_Start(["▶ /resume-work [ディレクトリ名]"]) --> RW1

    RW1{"引数あり?"}
    RW1 -->|"Yes"| RW1_specified[".steering/[引数]/ を対象とする"]
    RW1 -->|"No — 省略"| RW1_auto[".steering/ 内の最新ディレクトリを自動選択"]
    RW1_specified --> RW2
    RW1_auto --> RW2

    RW2["① チェックポイント読み込み<br/>tasklist.md / requirements.md / design.md"]
    RW2 --> RW3

    RW3["② 再開ポイントの特定<br/>・完了済みフェーズ: CP完了日時が記録済み<br/>・再開フェーズ: 未完了タスク [ ] が最初に現れるフェーズ<br/>・再開状況をユーザーに報告"]
    RW3 --> RW4

    RW4["③ コンテキスト復元<br/>CLAUDE.md + docs/ + design.md<br/>直前の CP Evidence で実装状況を把握"]
    RW4 --> RW5_check

    subgraph RW5 ["④ 実装の再開（再開ポイントから）"]
        RW5_check{"未完了タスク [ ] あり?"}
        RW5_check -->|Yes| RW5_exec["タスク実行<br/>skill: steering（実装モード）"]
        RW5_exec --> RW5_update["tasklist.md 更新　[ ] → [x]"]
        RW5_update --> RW5_check
        RW5_check -->|"No — 全タスク完了"| RW5_gate_check{"品質ゲートは完了済み?"}
        RW5_gate_check -->|No| RW6
        RW5_gate_check -->|Yes| RW7
    end

    RW6["⑤ 品質ゲート検証<br/>/add-feature の⑥と同じ手順<br/>（Gate 1〜5 / 最大 3 回ループ / エスカレーション）"]
    RW6 --> RW7

    RW7["⑥ 振り返り・ドキュメント更新<br/>/add-feature の⑧と同じ手順<br/>skill: steering（振り返りモード）"]
    RW7 --> RW_End(["✅ 作業再開・完了"])
```

---

## /review-docs

指定したドキュメントをサブエージェントが**独立したコンテキスト**で精査します。
メインの会話コンテキストを汚染せずに、客観的な品質チェックが行えます。

```mermaid
flowchart TD
    RD_Start(["▶ /review-docs パス"]) --> RD1

    RD1{"ドキュメント存在確認"}
    RD1 -->|"❌ 存在しない"| RD_Error["エラー: パスを確認してください"]
    RD1 -->|"✅ 存在する"| RD2_agent

    subgraph RD2 ["レビュー実行"]
        RD2_agent["sub-agent: doc-reviewer<br/>（独立コンテキストで実行）"] --> RD2_report["詳細レビューレポート作成<br/><br/>レビュー観点:<br/>・完全性 — 必要項目の網羅<br/>・具体性 — 曖昧表現の排除<br/>・一貫性 — 他ドキュメントとの整合<br/>・測定可能性 — 成功指標の定量性"]
    end

    RD2 --> RD3["改善点を優先度付きでユーザーに報告"]
    RD3 --> RD_End(["✅ レビュー完了"])
```

---

## 品質ゲート一覧

| Gate | 必須 / 条件付き | コマンド | 発動条件 |
|------|---------------|---------|---------|
| **Gate 1** — lint / typecheck / test | ✅ 必須 | `npm run lint`<br/>`npm run typecheck`<br/>`npm test` | 常に実行 |
| **Gate 2** — E2E テスト | ✅ 必須（`/add-feature-ui` のみ） | `npm run test:e2e` | `/add-feature-ui` 使用時 |
| **Gate 3** — ビジュアルリグレッション | 条件付き | `npm run test:vrt` | `tests/vrt/__screenshots__/` が存在する場合 |
| **Gate 4** — アクセシビリティ | 条件付き | `npm run test:a11y` | `tests/a11y/` が存在する場合 |
| **Gate 5** — UI/UX 検証 | 条件付き | sub-agent: `ui-ux-validator` | `.claude/agents/ui-ux-validator.md` が存在する場合 |

> **失敗時のルール**: 最大 3 回まで原因分析・修正を繰り返します。3 回を超えた場合は `failure-report.md` を作成してユーザーに報告し、作業を停止します。

---

## スキル・サブエージェント 参照マップ

| コマンド | フェーズ | 呼び出し先 | 種別 | 役割 |
|---------|---------|-----------|------|------|
| `/setup-project` | Step 1 | `prd-writing` | skill | PRD 作成ガイド |
| `/setup-project` | Step 2 | `functional-design` | skill | 機能設計書テンプレート |
| `/setup-project` | Step 3 | `architecture-design` | skill | アーキテクチャ設計テンプレート |
| `/setup-project` | Step 4 | `repository-structure` | skill | リポジトリ構造テンプレート |
| `/setup-project` | Step 5 | `development-guidelines` | skill | 開発ガイドラインテンプレート |
| `/setup-project` | Step 6 | `glossary-creation` | skill | 用語集テンプレート |
| `/add-feature` | ③ 計画 | `steering`（計画モード） | skill | ステアリングファイル自動生成 |
| `/add-feature` | ④ 実装 | `steering`（実装モード） | skill | `tasklist.md` 更新管理 |
| `/add-feature` | ④ 実装 | `development-guidelines` | skill | コーディング規約の適用 |
| `/add-feature` | ⑤ 検証 | `implementation-validator` | sub-agent | 実装品質の独立検証 |
| `/add-feature` | ⑥ Gate 5 | `ui-ux-validator` | sub-agent | UI/UX 品質の検証（条件付き） |
| `/add-feature` | ⑦ 確認 | `testing` | skill | 動作確認・リグレッションチェック |
| `/add-feature` | ⑧ 振り返り | `steering`（振り返りモード） | skill | 申し送り記入 |
| `/add-feature-ui` | 全フェーズ | `/add-feature` と同じ | — | Gate 2（E2E）が必須で追加 |
| `/resume-work` | ④ 実装 | `steering`（実装モード） | skill | 中断箇所からの実装再開 |
| `/resume-work` | ⑥ 振り返り | `steering`（振り返りモード） | skill | 申し送り記入 |
| `/review-docs` | レビュー | `doc-reviewer` | sub-agent | ドキュメントの詳細レビュー |
