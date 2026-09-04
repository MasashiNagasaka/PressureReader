---
name: setup-project
description: 初回セットアップ: 6つの永続ドキュメントを対話的に作成する
allowed-tools: Read, Write, Edit, Bash
caller: migrated-from-claude-command
---

# setup-project skill

> Source: .claude/commands/setup-project.md
> Original command: /setup-project

# 初回プロジェクトセットアップ

このコマンドは、プロジェクトの6つの永続ドキュメントを対話的に作成します。

## 実行方法

```bash
claude
> /setup-project
```

## 実行前の確認

`docs/ideas/` ディレクトリ内のファイルを確認します。
```bash
# 確認
ls docs/ideas/

# ファイルが存在する場合
✅ docs/ideas/initial-requirements.md が見つかりました
   この内容を元にPRDを作成します

# ファイルが存在しない場合
⚠️  docs/ideas/ にファイルがありません
   対話形式でPRDを作成します
```

## 手順

### ステップ0: インプットの読み込み

1. `docs/ideas/` 内のマークダウンファイルを全て読む
2. 内容を理解し、PRD作成の参考にする

### ステップ1: プロダクト要求定義書の作成

1. **prd-writingスキル**をロード
2. `docs/ideas/`の内容を元に`docs/product-requirements.md`を作成
3. 壁打ちで出たアイデアを具体化：
   - 詳細なユーザーストーリー
   - 受け入れ条件
   - 非機能要件
   - 成功指標
4. ユーザーに確認を求め、**承認されるまで待機**

**以降のステップはプロダクト要求定義書の内容を元にするため、自動的に作成する**

### ステップ2: 機能設計書の作成

1. **functional-designスキル**をロード
1. `docs/product-requirements.md`を読む
3. スキルのテンプレートとガイドに従って`docs/functional-design.md`を作成

### ステップ3: アーキテクチャ設計書の作成

1. **architecture-designスキル**をロード
2. 既存のドキュメントを読む
3. スキルのテンプレートとガイドに従って`docs/architecture.md`を作成

### ステップ3.5: ADRの自動生成

1. `docs/architecture.md` を読み、主要なアーキテクチャ意思決定を抽出する。
   - 技術スタック選定（フロントエンド、バックエンド、データベース等）
   - 設計パターン選択（状態管理方式、CSS/スタイリング方式等）
   - インフラ・デプロイ方針
2. 各決定について `docs/adr/_template.md` の形式でADRを生成する:
   - `docs/adr/` 内の既存ADRファイル（`_template.md`、`README.md`を除く）を確認し、最大番号の次の番号を採番する（初回は`0001`から開始）
   - ファイル名: `NNNN-[決定の英語要約].md`（例: `0001-react-nextjs-frontend.md`）
   - ステータス: `Accepted`
   - 日付: 現在の日付
   - 決定者: `AI Agent (setup-project)`
   - コンテキスト: architecture.md から該当箇所を要約
   - 検討した選択肢: architecture.md に記載があれば抽出、なければ代表的な選択肢を補完
   - 決定内容: 選択した技術・パターンとその理由
   - 結果・トレードオフ: 採用による利点と受け入れたトレードオフ
3. 生成されるADRは architecture.md に記載された決定事項の数に応じて動的に決まる。

### ステップ4: リポジトリ構造定義書の作成

1. **repository-structureスキル**をロード
2. 既存のドキュメントを読む
3. スキルのテンプレートに従って`docs/repository-structure.md`を作成

### ステップ5: 開発ガイドラインの作成

1. **development-guidelinesスキル**をロード
2. 既存のドキュメントを読む
3. スキルのテンプレートに従って`docs/development-guidelines.md`を作成

### ステップ6: 用語集の作成

1. **glossary-creationスキル**をロード
2. 既存のドキュメントを読む
3. スキルのテンプレートに従って`docs/glossary.md`を作成

### ステップ7: README.md の雛形生成

1. ステップ1〜6で作成した永続ドキュメントを元に、アプリ用の README.md の雛形を生成する。
2. `/generate-readme` コマンドと同等の処理を実行する:
   - `docs/product-requirements.md` から概要を抽出
   - `docs/architecture.md` から技術スタックを抽出
   - `docs/functional-design.md` から主要機能を抽出
   - shields.io バッジを生成
   - スクリーンショットセクションはプレースホルダとする（この時点ではアプリ未実装のため）
3. README.md をプロジェクトルートに保存する。


### ステップ7.5: Pythonホワイトリストの更新

1. 全体公開用ホワイトリストを GitHub リポジトリから `git clone --depth 1` で取得して更新する。
   - デフォルトリポジトリURL（必要に応じて差し替え）:
     - `https://github.com/tmc-ccoe/python-package-whitelist.git`
   - 固定相対パス:
     - `whitelist_python_packages.txt`
   - 実行例:
     - `powershell -ExecutionPolicy Bypass -File .claude/scripts/update-whitelist-from-git.ps1 -RepoUrl <固定リポジトリURL> -RelativeFilePath whitelist_python_packages.txt -TargetPath .python_packages_list/whitelist_python_packages.txt`
2. `/setup-project` の最後に、以下を**毎回必ず**ユーザーへ確認する。
   - 「チーム限定ホワイトリストがあれば GitHub リポジトリURLを教えてください。追加でホワイトリストを更新します。」
3. リポジトリURLが入力された場合:
   - 固定相対パス `approved_python_packages.txt` を `git clone --depth 1` で取得して更新する。
   - 実行例:
     - `powershell -ExecutionPolicy Bypass -File .claude/scripts/update-whitelist-from-git.ps1 -RepoUrl <入力リポジトリURL> -RelativeFilePath approved_python_packages.txt -TargetPath .python_packages_list/approved_python_packages.txt`
4. URL未入力の場合:
   - スキップしたことを明示して処理を完了する。
5. いずれの場合も、更新結果（成功/失敗/スキップ）をユーザーへ表示する。
## 完了条件

- 6つの永続ドキュメントが全て作成されていること
- README.md の雛形が生成されていること
- `docs/adr/` にアーキテクチャ意思決定のADRが生成されていること

完了時のメッセージ:
```
「初回セットアップが完了しました!

作成したドキュメント:
✅ docs/product-requirements.md
✅ docs/functional-design.md
✅ docs/architecture.md
✅ docs/repository-structure.md
✅ docs/development-guidelines.md
✅ docs/glossary.md
✅ docs/adr/NNNN-*.md（ADR）
✅ README.md（雛形）

これで開発を開始する準備が整いました。

今後の使い方:
- ドキュメントの編集: 普通に会話で依頼してください
  例: 「PRDに新機能を追加して」「architecture.mdを見直して」

- 機能の追加: /add-feature [機能名] を実行してください
  例: /add-feature ユーザー認証

- README更新: /generate-readme を実行してください
  スクリーンショット撮影やバッジ更新が自動で行われます

- ドキュメントレビュー: /review-docs [パス] を実行してください
  例: /review-docs docs/product-requirements.md
」
```


## Pythonホワイトリスト参照ルール（最優先）
- Python依存関係の追加・更新・検証を伴う場合は、必ず .python_packages_list/ ディレクトリを確認すること。
- **ファイル名を固定決め打ちしてはならない。** .python_packages_list/ 配下の実在ファイルを列挙し、参照対象を決定すること。
- .python_packages_list/ フォルダ、または参照すべきホワイトリストファイルが存在しない場合は、**そのまま処理を進めることを厳禁**とする。
- 上記不足がある場合は処理を停止し、**必ずユーザーに確認を取ってから**再開すること。
- 本節は、ホワイトリスト名の固定例示より優先して適用する。
