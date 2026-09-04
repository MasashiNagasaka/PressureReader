---
description: 仕様策定（plan-kaizen）から実装・コミット・pushまでを一括自動実行する（テストなし版）
---

# 仕様策定 → 実装 完全自動モード (auto-add-feature-with-plan)

**重要:** このワークフローは、仕様策定から実装・コミット・pushまでを **ユーザー確認なしに完全自動** で実行します。
途中で AskUserQuestion が発生した場合（add-feature の push 確認を含む）は、**自動的に「はい / push する / スキップ不要」として進んでください。**
壁打ちフェーズ（引数が曖昧な場合）と安全チェック（高リスク変更を検知した場合）のみ AskUserQuestion を使用します。

> ⚠️ **このコマンドは小規模・低リスク変更専用です。** DBスキーマ変更・認証・外部API・大量変更・破壊的変更が含まれる場合は `/add-feature` を使用してください。

**引数:**
- テキスト: `/auto-add-feature-with-plan "ログイン画面にremember meチェックボックスを追加"`
- ファイルパス: `/auto-add-feature-with-plan docs/ideas/my-spec.md`
- GitHub Issue 番号: `/auto-add-feature-with-plan #123`
- GitHub Issue URL: `/auto-add-feature-with-plan https://github.com/owner/repo/issues/123`

---

## フェーズ1: 引数解析

引数の種類を判定し、コンテンツを取得する。

### 判定ロジック（優先順位順）

1. **GitHub Issue URL の場合**: 引数が `https://github.com/` で始まり `/issues/` を含む
   ```bash
   gh issue view <URL> --json title,body,labels,comments
   ```
   - 失敗した場合（gh 未インストール・未認証等）: エラーをユーザーに通知し、引数をテキストとして扱い次へ進む

2. **GitHub Issue 番号の場合**: 引数が `#` + 数字のみ（例: `#123`）
   ```bash
   gh issue view 123 --json title,body,labels,comments
   ```
   - 失敗した場合: 同様にテキストとして扱い次へ進む

3. **ファイルパスの場合**: 引数が既存ファイルパス（Read ツールで読める）
   - Read ツールでファイルを読み込み、内容をコンテンツとして使用

4. **テキストの場合**: 上記以外
   - 引数をそのままコンテンツとして使用

取得したコンテンツを「入力コンテンツ」として以降のフェーズで使用する。

---

## フェーズ2: plan-kaizen（仕様策定・自動化版）

### ステップ2-1: コンテキスト読み込み

以下を読み込んでプロジェクトを把握する（存在するものだけ）:
- `CLAUDE.md`
- `docs/product-requirements.md`
- `docs/functional-design.md`
- `docs/architecture.md`
- `docs/glossary.md`
- `.claude/docs/guidelines/tech-stack-guidelines.md`
- `.claude/docs/guidelines/repository-structure-guidelines.md`

### ステップ2-2: 情報量判定

入力コンテンツの情報量を判定し、**壁打ちをスキップするかどうか**を決定する。

**省略条件（以下のいずれかを満たせばスキップ）:**
- GitHub Issue または URL から取得したコンテンツである
- ファイルパスから取得したコンテンツである
- テキストが 150 字以上 かつ 機能要件・ユーザーストーリー・実装方針・受け入れ条件のいずれかを含む

**壁打ち条件（上記を満たさない場合）:**
- テキストが 150 字未満、または概念・キーワードのみ

### ステップ2-3: 壁打ち（条件に該当する場合のみ）

**スキップ対象の場合は このステップをスキップしてステップ2-4へ進む。**

`AskUserQuestion` ツールを使い、最大 2 ターンで不明点を解消する。

**壁打ちの観点（必要に応じて選択）:**
- スコープ（MVPに含めるもの・含めないもの）
- UX（ユーザーの操作フロー・状態遷移）
- エラーケース・バリデーションルール
- 既存機能との整合性

**「仕様書を生成しますか？」の最終確認は絶対に行わない。**
2 ターン終了後、または十分な情報が得られた時点で自動的にステップ 2-4 へ進む。

### ステップ2-4: 仕様書生成

`docs/ideas/` ディレクトリが存在しない場合は作成する。

機能名を英小文字ハイフン区切りで決定し（例: `remember-me-checkbox`）、以下のパスに仕様書を生成する:
```
docs/ideas/[YYYYMMDD]-[機能名].md
```

仕様書の構成:
```markdown
# [機能名] 仕様書

> 作成日: [YYYY-MM-DD]
> ステータス: Draft
> 用途: /add-feature への入力（auto-add-feature-with-plan による自動生成）

---

## 1. 背景・目的
## 2. スコープ（含めるもの / 含めないもの）
## 3. ユーザーストーリー
## 4. 機能要件
## 5. 非機能要件
## 6. 技術的考慮事項（参考）
## 7. 受け入れ条件
## 8. 参考・関連
```

**ステップ2-4が完了したら、安全チェックを実施してからフェーズ3へ進むこと。**

---

## フェーズ2.5: 安全チェック（高リスク変更の検知）

生成した仕様書の内容を確認し、以下のいずれかに該当する変更が含まれる場合は **自動継続を停止し、`AskUserQuestion` でユーザーに確認を求める**。

### 高リスク変更の判定基準

- DB スキーマ変更・マイグレーション（テーブル追加・削除・カラム変更など）
- 認証・認可ロジックの変更（ログイン・権限・トークン処理など）
- 外部 API 連携の追加・変更（新規エンドポイント、認証キーの扱いなど）
- ファイル・ディレクトリの削除
- 大量ファイル変更（10 ファイル以上が目安）
- 破壊的な後方互換性破壊（API レスポンス形式変更・引数変更など）

### 高リスク変更を検知した場合の処理

`AskUserQuestion` ツールで以下を提示する:
- 検知した高リスク変更の内容
- 「このまま自動実行を続けますか？それとも `/add-feature` で手動確認しながら進めますか？」

ユーザーが「自動実行を続ける」を選択した場合のみ、フェーズ3へ進む。
ユーザーが「手動で進める」を選択した場合は、生成済み仕様書のパスを報告して終了する。

### 低リスクと判定した場合

上記いずれにも該当しない場合は確認なしでフェーズ2.6へ進む。

---

## フェーズ2.6: ステアリングディレクトリの事前作成（必須・省略禁止）

**目的:** フェーズ4でスキルが何らかの理由でバイパスされても、変更履歴が必ず残るようにする保険。

1. 以下のファイルを作成する（既に存在する場合はスキップ）:
   - `.steering/[YYYYMMDD]-[機能名]/requirements.md`

2. `requirements.md` の内容は仕様書（`docs/ideas/[ファイル名]`）の以下のセクションをコピーする:
   - 背景・目的
   - スコープ
   - 機能要件
   - 受け入れ条件
   - 末尾に以下を付記する:
     > この requirements.md は auto-add-feature による事前生成です。Skill('add-feature') 実行時に design.md と tasklist.md が追加されます。

3. フェーズ4で `Skill('add-feature')` が正常に呼び出された場合、スキルが `design.md` と `tasklist.md` を追加・拡張する（`requirements.md` と重複しても問題ない）。

**フェーズ2.6が完了したら、確認や停止を一切せずにフェーズ3へ進むこと。**

---

## フェーズ3: 中間 git コミット・push

### ステップ3-1: Git リポジトリの確認

```bash
git rev-parse --is-inside-work-tree 2>/dev/null
```

- **リポジトリが存在する場合**: ステップ3-2へ
- **リポジトリが存在しない場合**:
  1. `git init` を実行
  2. `.gitignore` が存在しない場合、プロジェクトに適した `.gitignore` を作成（node_modules/, .env, .venv/ 等）
  3. ステップ3-2へ

### ステップ3-2: 変更のコミット

```bash
git status
```

変更がある場合:
1. センシティブファイルを除外してステージング:
   ```bash
   git add --all -- ':!.env' ':!*.key' ':!credentials*' ':!*.pem' ':!*.p12'
   ```
2. コミット（機能名は仕様書のファイル名から取得）:
   ```bash
   git commit -m "docs: [機能名] 仕様書追加（auto-add-feature による自動生成）"
   ```

変更がない場合: ステップ3-3へ

### ステップ3-3: Push

```bash
git remote -v
```

- **remote が設定されている場合**: 確認なしで自動 push
  ```bash
  git push
  ```
  失敗した場合（upstream 未設定等）:
  ```bash
  git push --set-upstream origin $(git rev-parse --abbrev-ref HEAD)
  ```
- **remote が設定されていない場合**: スキップ（ローカルコミットのみ）

**フェーズ3が完了したら、確認や停止を一切せずにフェーズ4へ進むこと。**

---

## フェーズ4: 実装（add-feature の自動着火）

**⛔ 絶対禁止:**

- 修正が小さい・変更ファイルが少ないことを理由に、`Skill('add-feature')` の呼び出しをスキップして直接実装すること
- スキルを経由せずにファイルを編集・作成してコミットすること
- 「短い修正なのでスキルを使わなくてよい」と判断すること

規模の大小にかかわらず、必ず `Skill('add-feature')` を経由すること。
これはワークフロー遵守ルール（`.claude/rules/workflow-guardrails.md`）の要件である。

生成した仕様書を引数として `Skill('add-feature')` を着火する。

**重要な指示:**
- add-feature の「ステップ9: Git 操作」で push 確認の `AskUserQuestion` が発生した場合、**自動的に「はい（push する）」として応答し、処理を継続すること**。
- ユーザーの手動確認は一切不要。

```
Skill('add-feature') を引数 "[生成した仕様書のパス] を実装して" で呼び出す
```

**Skill('add-feature') が完了したら、確認や停止を一切せずにフェーズ5へ進むこと。**

---

## フェーズ5: 最終 git コミット・push

add-feature が内部でコミット・push まで行う場合は、このフェーズをスキップしてよい。
ただし、未コミットの変更が残っている場合は以下を実行する。

### ステップ5-1: 変更確認

```bash
git status
```

未コミットの変更がある場合:
1. ステージング（センシティブファイル除外）:
   ```bash
   git add --all -- ':!.env' ':!*.key' ':!credentials*' ':!*.pem' ':!*.p12'
   ```
2. コミット:
   ```bash
   git commit -m "feat: [機能名] 実装完了（auto-add-feature-with-plan）"
   ```

### ステップ5-2: Push

```bash
git remote -v
```

- **remote が設定されている場合**: 確認なしで自動 push
  ```bash
  git push
  ```
  失敗した場合:
  ```bash
  git push --set-upstream origin $(git rev-parse --abbrev-ref HEAD)
  ```
- **remote が設定されていない場合**: スキップ

---

## 完了報告

全フェーズ完了後、以下を報告する:

```
✅ auto-add-feature-with-plan 完了

仕様書: docs/ideas/[ファイル名]
実装: [実装したファイル一覧]
コミット: [コミットメッセージ]
Push: [実行 / スキップ（remote なし）]
動作確認: [確認済み / 未確認（Playwright 未インストール等）]
```

> 未確認項目がある場合は上記に明記すること。確認できなかった検証を「実行した」かのように報告しないこと。
> 実装後に `/verify` を実行して動作確認を完了させることを推奨する。
