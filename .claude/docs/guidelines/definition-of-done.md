# Definition of Done (DoD)

<!-- `.claude/commands/add-feature.md`から参照されています -->
<!-- `.claude/commands/add-feature-ui.md`から参照されています -->
<!-- `.claude/commands/resume-work.md`から参照されています -->

## 概要

このファイルは、`/add-feature` 、`/add-feature-ui`および `/resume-work` ワークフローにおける「完了」の定義を固定します。
tasklist.md のフェーズ3（品質ゲート）はこの定義を満たすまでクローズできません。

---

## ゲート設定の有無確認方法

Claude Code は以下のファイル・ディレクトリの存在で各ゲートの実行要否を判断する:

| ゲート | 判断根拠 | 不要なプロジェクトの例 |
|-------|---------|---------------------|
| E2E (Gate 2) | `playwright.config.ts` または `playwright.config.js` の存在 | バックエンド API のみ・CLI ツール・バッチ処理・ライブラリ |
| VRT (Gate 3) | `tests/vrt/__screenshots__/` ディレクトリの存在 | デザイン仕様が頻繁に変わる開発初期・バックエンドのみ |
| a11y (Gate 4) | `tests/a11y/` ディレクトリの存在 | 社内限定ツール（対象ユーザーが限定的）・バックエンド API・CLI ツール |
| UI/UX 批評 (Gate 5) | `.claude/agents/ui-ux-validator.md` の存在 | `ui-ux-validator.md` を作成・設定していないプロジェクト全般 |

> **⚠️ `/add-feature-ui` の場合**
> `/add-feature-ui` は UI 機能の追加が前提のため、Gate 2 は**必須**です。
> `playwright.config.ts` が存在しない場合は、実装ループ（ステップ5）の中で
> Playwright のセットアップと E2E テストコードの作成をタスクとして実施してから Gate 2 を実行してください。

---

## テスト層ゲート定義

### Gate 1: 静的解析（必須 / ブロッキング）

<!-- 目的: コードの構文エラー・型不整合・ユニットテストの失敗を機械的に検出し、最低限の品質基準を担保する。すべてのプロジェクトで必ず実行する。 -->

| コマンド | 合格条件 | 備考 |
|---------|---------|------|
| `npm run lint` | エラー 0 件 | Warning は許容 |
| `npm run typecheck` | エラー 0 件 | |
| `npm test` | 全テストパス | カバレッジ 80% 以上を目標 |

### Gate 2: E2E テスト（設定済みの場合のみ / ブロッキング）

<!-- 目的: ユーザー視点でのシナリオ（画面遷移・フォーム送信・API連携など）を自動実行し、エンドツーエンドのフロー破壊を検出する。UIを伴う機能に有効。 -->

| コマンド | 合格条件 | 備考 |
|---------|---------|------|
| `npm run test:e2e` | 全シナリオパス | `playwright.config.ts` が存在する場合のみ実行 |

失敗時は `test-results/` に trace.zip が保存されること。

### Gate 3: ビジュアル回帰テスト（VRT）（設定済みの場合のみ / ブロッキング）

<!-- 目的: 実装前後のスクリーンショットを比較し、意図しないレイアウト崩れ・スタイル変更を検出する。デザインの安定性が重要なプロジェクトに有効。 -->

| コマンド | 合格条件 | 備考 |
|---------|---------|------|
| `npm run test:vrt` | スクリーンショット差分 0 件 | `tests/vrt/__screenshots__/` が存在する場合のみ実行 |

- 基準画像は `tests/vrt/__screenshots__/` に格納する
- 意図した UI 変更の場合のみ `npm run test:vrt:update` で更新を許可する

### Gate 4: アクセシビリティ（a11y）（設定済みの場合のみ / ブロッキング）

<!-- 目的: 障害を持つユーザーが利用できるか WCAG AA 基準で自動検証する。スクリーンリーダー対応・キーボード操作・コントラスト比などを機械的にチェックする。 -->

| コマンド | 合格条件 | 備考 |
|---------|---------|------|
| `npm run test:a11y` | violations 0 件 (WCAG AA) | `tests/a11y/` が存在する場合のみ実行 |

- ゲート対象ルール: WCAG AA タグ（`wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`）
- 既知の例外は `axe.configure({ rules: [...] })` で明示的に除外し、理由をコードにコメントする

### Gate 5: UI/UX 批評（設定済みの場合のみ / ブロッキング）

<!-- 目的: 自動テストでは測れない「使いやすさ・デザイン品質・操作の一貫性」を AI サブエージェントが人間目線で批評する。重大な UX 問題（操作を妨げるもの）を出荷前に発見する。 -->

`ui-ux-validator` エージェントによるレビューを実施し、重大な指摘が 0 件であること。

- `.claude/agents/ui-ux-validator.md` が存在する場合のみ実行

---

## Done When（完了条件チェックリスト）

実装が「完了」とみなされるのは以下が全て満たされた時:

- [ ] Gate 1 が全てパスしている
- [ ] Gate 2〜5 は「設定済みの場合のみ」実行し、パスしている
- [ ] `tasklist.md` の全タスクが `[x]` になっている
- [ ] `tasklist.md` の Evidence フィールドにテスト結果が記録されている
- [ ] 実装した機能がデモ可能な状態（手順が tasklist.md に記載されている）
- [ ] 影響を受ける `docs/` ドキュメントが更新されている

---

## 最大反復回数（修正→再検証ループ）

Gate が失敗した場合、以下の規則に従う:

- **最大反復回数: 3 回**
- 各反復で必ず修正を施してから再検証を実行すること
- 3 回試みても合格しない場合は、失敗レポートを生成してユーザーにエスカレーションすること

### 失敗レポートの保存先

`.steering/[タスク名]/failure-report.md`

### 失敗レポートのフォーマット

```markdown
# 品質ゲート失敗レポート

## 機能名
[機能名]

## 失敗したゲート
[失敗したゲートと具体的なエラー内容]

## 試みた修正の履歴
- 反復1: [実施した修正の概要]
- 反復2: [実施した修正の概要]
- 反復3: [実施した修正の概要]

## 根本原因の仮説
[エラーから推定される根本原因]

## 推奨される次のアクション
[人間が対応すべきこと]

## 保存された証拠
- test-results/ (trace.zip)
- [その他の成果物パス]
```

---

## 必須成果物

機能追加完了時に以下が存在すること:

| 成果物 | パス | 必須/任意 |
|-------|-----|---------|
| ステアリングファイル | `.steering/[日付]-[機能名]/` | 必須 |
| テスト結果ログ | `tasklist.md` の Evidence フィールド | 必須 |
| E2E トレース | `test-results/` （失敗時のみ） | 失敗時必須 |
| 失敗レポート | `.steering/[タスク名]/failure-report.md` | 3回失敗時必須 |

---

## フィードバック速度の階層（提案E）

品質を決定するのはフィードバックの速さ。フィードバックが遅いほど修正コストが高くなる。

| 階層 | タイミング | 手段 | 目標速度 |
|------|----------|------|---------|
| **L0: 即時** | ツール実行前 | PreToolUse Hook（設定ファイル保護・機密ファイル保護・--no-verify禁止） | ミリ秒 |
| **L1: 最速** | ファイル編集直後 | PostToolUse Hook（リント・フォーマット自動実行） | ミリ秒〜秒 |
| **L2: 速** | コミット直前 | プリコミットフック（Lefthook / Husky） | 秒〜数十秒 |
| **L3: 遅** | PR作成後 | CI（GitHub Actions 等） | 分 |
| **L4: 最遅** | リリース前後 | 人間によるコードレビュー・QA | 時間〜日 |

### L0: PreToolUse Hook（Safety Gates）

`.claude/settings.json` の `hooks.PreToolUse` で危険な操作を事前にブロック:

- **設定ファイル保護**: リンター設定（`.eslintrc*`, `biome.json`, `tsconfig.json` 等）の編集をブロック。エージェントがリンターエラーを設定変更で回避することを防止
- **機密ファイル保護**: `.env*`, `credentials*`, `*.key` の編集をブロック
- **`--no-verify` 禁止**: `git commit --no-verify` をブロックし、プリコミットフックのバイパスを防止

### L1: PostToolUse Hook の設定

`.claude/hooks/post-lint.sh` がファイル編集後に自動実行される。言語を自動検出し、適切なリンターを実行:

- `.ts/.tsx/.js/.jsx` → `npm run lint`
- `.py` → `ruff check` + `ruff format`
- `.go` → `golangci-lint run`

フィードバックは `hookSpecificOutput.additionalContext` を含むJSON形式でエージェントのコンテキストに直接注入される。

設定: `.claude/settings.json` の `hooks.PostToolUse` → `.claude/hooks/post-lint.sh`

### L2: プリコミットフックの設定（Lefthook）

プロジェクトルートの `lefthook.yml` でコミット前にlint/typecheckを自動実行:

```yaml
# lefthook.yml
pre-commit:
  commands:
    lint:
      glob: "*.{ts,tsx,js,jsx}"
      run: npm run lint
      skip:
        - run: "[ ! -f package.json ]"
    typecheck:
      glob: "*.{ts,tsx}"
      run: npm run typecheck
      skip:
        - run: "[ ! -f package.json ]"
    ruff-check:
      glob: "*.py"
      run: ruff check {staged_files}
      skip:
        - run: "! command -v ruff >/dev/null 2>&1"
    ruff-format:
      glob: "*.py"
      run: ruff format --check {staged_files}
      skip:
        - run: "! command -v ruff >/dev/null 2>&1"
```

インストール:

```bash
npm install --save-dev lefthook
npx lefthook install
```

---

## Playwright テンプレートのセットアップ手順（参考）

プロジェクトで Playwright を有効化するには:

```bash
# Playwright インストール
npm install --save-dev @playwright/test @axe-core/playwright

# ブラウザインストール
npx playwright install chromium

# VRT 基準画像の初回生成
npm run test:vrt:update
```

設定ファイル: `playwright.config.ts`（プロジェクトルート）
テストテンプレート:

- `tests/e2e/example.spec.ts`
- `tests/vrt/example.spec.ts`
- `tests/a11y/example.spec.ts`

### `playwright.config.ts` 推奨設定（Python + FastAPI 向け）

> ⚠️ `reuseExistingServer: false` を必ず設定すること。デフォルトの `true` のままにすると、
> E2E テスト終了後もサーバーがバックグラウンドで生き続け、コード修正が反映されない問題が発生する。
> 詳細は `.claude/docs/sdd-workflow/setup-playwright.md` の「必須設定チェックリスト」を参照。

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  workers: 1,           // DB共有テストはシリアル実行で競合を防ぐ
  fullyParallel: false,
  webServer: {
    command: 'python main.py',  // --reload なし。毎回フレッシュ起動
    url: 'http://localhost:8000',
    reuseExistingServer: false, // 必須: 古いサーバーの占有を防ぐ
    timeout: 15000,
  },
  use: {
    baseURL: 'http://localhost:8000',
  },
});
```
