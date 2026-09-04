---
description: アプリ用README.mdを自動生成・更新する。shields.ioバッジ、スクリーンショット、技術スタック情報を含む。
---

# README.md 自動生成

**目的:** プロジェクトの永続ドキュメント（PRD、機能設計書、アーキテクチャ）と実装状況から、アプリ用の README.md を自動生成する。

**引数:** なし（プロジェクト内の情報から自動生成）

---

## ステップ1: 情報収集

以下のファイルを読み込み、README に必要な情報を収集する。

### 必須ファイル
1. `CLAUDE.md` — プロジェクトの全体像
2. `docs/product-requirements.md` — プロダクトの目的・スコープ（存在する場合）

### 任意ファイル（存在する場合のみ読み込み）
3. `docs/functional-design.md` — 主要機能の一覧
4. `docs/architecture.md` — 技術スタック・アーキテクチャ
5. `.claude/docs/guidelines/tech-stack-guidelines.md` — 技術スタックガイドライン
6. `package.json` — Node.js依存関係・スクリプト
7. `requirements.txt` / `pyproject.toml` — Python依存関係
8. `LICENSE` — ライセンス情報
9. `docs/screenshots/` — スクリーンショット画像

## ステップ1.5: 変更履歴の収集

前回の README 生成以降の変更履歴を git log から収集し、機能単位で要約する。

### 1.5-A: 前回生成日時の取得

1. `README.md` が存在する場合、ファイル末尾付近の `<!-- readme-generated: YYYY-MM-DDTHH:MM:SS -->` コメントを検索する。
2. コメントが見つかった場合: その日時を「前回生成日時」として記録する。
3. コメントが見つからない場合（初回実行）: 前回生成日時を「なし」とする。

### 1.5-B: git リポジトリの確認

```bash
Bash('git rev-parse --is-inside-work-tree 2>/dev/null')
```

- **git リポジトリでない場合**: このステップの残りをスキップし、変更履歴を空（プレースホルダのみ）とする。
- **git リポジトリの場合**: 1.5-C へ進む。

### 1.5-C: git log の取得

前回生成日時の有無に応じてコマンドを切り替える:

- **前回生成日時がある場合**:
  ```bash
  Bash('git log --since="<前回生成日時>" --oneline --no-merges -50')
  ```
- **前回生成日時がない場合（初回）**:
  既存の git 履歴全体から変更履歴を生成する。直近 50 件のコミットを取得する:
  ```bash
  Bash('git log --oneline --no-merges -50')
  ```
  初回は履歴が多くなる可能性があるため、ステップ 1.5-D の要約で積極的にグルーピングし、エントリ数を絞ること。
  また、最初のコミットの日付を取得して「初期リリース」エントリとする:
  ```bash
  Bash('git log --reverse --format="%ai" | head -1')
  ```

### 1.5-D: 変更履歴の要約

取得したコミットログを以下のルールで機能単位にグルーピング・要約する:

1. **分類**: コミットメッセージのプレフィックスで分類する
   - `feat:` → 機能追加
   - `fix:` → バグ修正
   - `refactor:` / `chore:` / `docs:` → その他の改善
   - プレフィックスなし → コミットメッセージをそのまま使用
2. **グルーピング**: 同一機能に関する複数のコミット（同じキーワードを含む）は1行にまとめる
3. **参考情報**: `.steering/` 配下の各 `requirements.md` が存在する場合、機能名の参考として活用する
4. **出力形式**: 各エントリを「日付（YYYY-MM-DD） + 変更内容の1行要約」の形式にまとめる

### 1.5-E: 既存の変更履歴の抽出

README.md に既に「変更履歴」セクションが存在する場合、既存のエントリを抽出して保持しておく。
実際の統合（新旧エントリのマージ・重複除去）はステップ5 で行う。

## ステップ2: スクリーンショット撮影の確認

`AskUserQuestion` で以下を確認する:

- 「スクリーンショットを撮影しますか？（アプリが起動可能な状態である必要があります）」
  - **はい**: `Agent` ツールで `screenshot-capture` サブエージェントを起動する
    - `subagent_type`: "screenshot-capture"
    - `description`: "App screenshot capture"
    - `prompt`: "アプリケーションのスクリーンショットを撮影してください。docs/functional-design.md があればその主要画面を、なければトップページを撮影してください。"
  - **いいえ**: スキップして次のステップへ

## ステップ3: バッジの生成

以下のルールで shields.io バッジを生成する:

### ライセンスバッジ
- `LICENSE` ファイルが存在する場合、内容からライセンス種別を検出:
  - MIT → `![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)`
  - Apache 2.0 → `![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)`
  - GPL → `![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)`
- 存在しない場合はバッジなし

### 技術スタックバッジ
`package.json` の dependencies、または `requirements.txt` / `pyproject.toml` から主要技術を検出:

| 検出キーワード | バッジ |
|-------------|-------|
| `react` | `![React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB)` |
| `next` | `![Next.js](https://img.shields.io/badge/Next.js-000000?logo=nextdotjs&logoColor=white)` |
| `vue` | `![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?logo=vuedotjs&logoColor=white)` |
| `express` | `![Express](https://img.shields.io/badge/Express-000000?logo=express&logoColor=white)` |
| `fastapi` | `![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)` |
| `flask` | `![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white)` |
| `django` | `![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white)` |
| `typescript` | `![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)` |
| `python` | `![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)` |
| `tailwindcss` | `![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=white)` |
| `playwright` | `![Playwright](https://img.shields.io/badge/Playwright-2EAD33?logo=playwright&logoColor=white)` |

上記に該当しない技術でも、主要なものは `https://img.shields.io/badge/{名前}-{色}` 形式で生成する。

## ステップ4: README.md の生成

以下のテンプレートに沿って README.md を生成する。各セクションは収集した情報に基づいて埋める。情報が不足しているセクションはプレースホルダを残す。

```markdown
# {プロジェクト名}

{バッジ一覧（ライセンス + 技術スタック）}

## 概要

{product-requirements.md の「目的」「解決する課題」セクションから抽出。なければ CLAUDE.md から推定}

## スクリーンショット

{docs/screenshots/ 内の画像をテーブル形式で表示。なければ以下のプレースホルダ}
<!-- `/generate-readme` を実行してスクリーンショットを自動生成できます -->

## 主な機能

{functional-design.md から主要機能を箇条書き。なければ product-requirements.md から抽出}

- 機能1: 説明
- 機能2: 説明
- 機能3: 説明

## 技術スタック

{architecture.md または tech-stack-guidelines.md から抽出}

| カテゴリ | 技術 |
|---------|------|
| フロントエンド | {検出した技術} |
| バックエンド | {検出した技術} |
| データベース | {検出した技術} |
| テスト | {検出した技術} |

## セットアップ

### 前提条件

{package.json の engines や requirements.txt から推定}

### インストール

\`\`\`bash
# リポジトリのクローン
git clone {リポジトリURL}
cd {プロジェクト名}

# 依存関係のインストール
{npm install / pip install -r requirements.txt / uv sync 等}
\`\`\`

### 起動

\`\`\`bash
{npm run dev / python src/main.py 等}
\`\`\`

## 使い方

{基本的な使い方を記載。functional-design.md のユースケースから推定}

## 変更履歴

{ステップ1.5で収集した変更履歴を以下の形式で出力する}

{最新5件をテーブル形式で表示:}
| 日付 | 変更内容 |
|------|---------|
| YYYY-MM-DD | 変更内容の1行要約 |
| ... | ... |

{6件目以降が存在する場合、以下の折りたたみで表示:}
<details>
<summary>過去の変更履歴</summary>

| 日付 | 変更内容 |
|------|---------|
| YYYY-MM-DD | 変更内容の1行要約 |

</details>

{変更履歴がない場合、以下の条件に応じて出力を切り替える:}
{- git リポジトリでない場合:}
<!-- `/generate-readme` を再実行すると、git log から変更履歴が自動生成されます -->
{- 前回生成以降にコミットがない場合: 既存の変更履歴をそのまま維持（新規エントリなし）}

## ライセンス

{LICENSE ファイルから検出。なければプレースホルダ}

<!-- readme-generated: {現在日時を YYYY-MM-DDTHH:MM:SS 形式で埋め込む} -->
```

## ステップ5: 既存README.mdの処理

- README.md が存在しない場合: そのまま生成
- README.md が存在する場合:
  - `AskUserQuestion` で「既存の README.md を上書きしますか？」と確認
  - **上書き**: 新しい内容で置換（ステップ1.5 で生成した変更履歴をそのまま使用）
  - **マージ**: 既存の内容を参考にしつつ、テンプレートに沿って再構成

### 変更履歴の統合（マージ時）

マージを選択した場合、変更履歴セクションは以下のルールで統合する:

1. 既存 README の変更履歴セクションからエントリを抽出する
2. ステップ1.5 で生成した新しいエントリを既存エントリの先頭に追加する
3. 重複エントリ（同一日付かつ同一内容）を除去する
4. 統合後のエントリを最新5件（テーブル表示）と6件目以降（折りたたみ）に分割する

## ステップ6: 完了報告

```
README.md を生成しました。

含まれるセクション:
- [x] バッジ（{N}個）
- [x/  ] スクリーンショット
- [x/  ] 主な機能
- [x/  ] 技術スタック
- [x/  ] セットアップ手順
- [x/  ] 変更履歴（{N}件）
- [x/  ] ライセンス

変更履歴は git log から自動生成されます。再度 `/generate-readme` を実行すると、前回以降の差分が追加されます。
スクリーンショットを更新するには、アプリを起動可能な状態で再度 `/generate-readme` を実行してください。
```
