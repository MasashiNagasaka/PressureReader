- [SDD Template](#sdd-template)
  - [事前準備](#事前準備)
  - [開発ワークフロー](#開発ワークフロー)
    - [1. アプリの仕様を固める](#1-アプリの仕様を固める)
    - [2. アプリの仕様書を作る](#2-アプリの仕様書を作る)
    - [3. アプリを実装する](#3-アプリを実装する)
    - [4. アプリの機能追加・バグ修正をする](#4-アプリの機能追加バグ修正をする)
  - [主要なコマンド](#主要なコマンド)
  - [ディレクトリ構成](#ディレクトリ構成)
  - [tests/ ディレクトリについて](#tests-ディレクトリについて)
    - [品質ゲートとの関係](#品質ゲートとの関係)
  - [参考ドキュメント](#参考ドキュメント)
- [Playwright CLI / MCP セットアップガイド](#playwright-cli--mcp-セットアップガイド)
  - [Playwrightとは](#playwrightとは)
  - [Playwright CLI と Playwright MCP について](#playwright-cli-と-playwright-mcp-について)
  - [セットアップ方法](#セットアップ方法)
    - [Playwright CLI のセットアップ](#playwright-cli-のセットアップ)
    - [Playwright MCPのセットアップ](#playwright-mcpのセットアップ)
  - [動作確認例](#動作確認例)
    - [Playwright CLI 動作確認例](#playwright-cli-動作確認例)
    - [Playwright MCP 動作確認例](#playwright-mcp-動作確認例)


# SDD Template

**Spec Driven Development (SDD)** のプロジェクトテンプレートです。
「仕様を先に書き、仕様に従って実装する」ワークフローを Claude Code で自動化します。

## 事前準備

1. このリポジトリをテンプレートとしてプロジェクトフォルダを作る。
   * プロジェクトフォルダに `.claude`フォルダと`CLAUDE.md`をコピーしても良いです。

2. アプリテストに使う Playwright CLI と Playwright MCP をインストールする。
   * インストール方法は[Playwright CLI / MCP セットアップガイド](#playwright-cli--mcp-セットアップガイド) を参照してください。


## 開発ワークフロー

[SDD-workflow.md](SDD-workflow.md) にフローチャートでまとめました。

### 1. アプリの仕様を固める

* アプリ構想を `docs/ideas/initial-requirements.md` に記述する。
* プロジェクトフォルダで Claude Code を起動する。
* `/plan-kaizen` コマンドを使って、Claude Codeとの対話を通じて内容をブラッシュアップする。
  * プロダクトの基本的なアイデア、解決したい課題、ターゲットユーザーの概要、実装したい主要機能、MVPの範囲 などを整理する。
  * このコマンドは`.claude/docs/guidelines`フォルダにあるガイドラインを参照します。アプリにつかう技術スタックを指定したい場合は、`tech-stack-guidelines.md`を編集してください。

### 2. アプリの仕様書を作る

* `/setup-project`コマンドを実行して、初回セットアップをおこなう。
  * 永続的ドキュメントが`docs/`に生成される。

### 3. アプリを実装する

* `/add-feature`コマンドあるいは`/add-feature-ui`コマンドでアプリ実装をする。
  * 例: `/add-feature-ui アプリMVPを作って`
  * `src/`にソースコードが、`tests/`にテストコードが生成される。

### 4. アプリの機能追加・バグ修正をする

* 簡単なものであれば、`/add-feature [依頼コメント]` で実装できます。
  * 例: `/add-feature ユーザープロフィール編集を追加して`
* 複雑な依頼の場合は、アイデアノートを`docs/ideas/`に作成し、その内容をClaude Codeと壁打ちして固める。
  * 例: `/plan-kaizen docs/ideas/memo1.md をブラッシュアップして`
  * 壁打ち結果は、`docs/ideas/[YYYYMMDD]-[機能名].md`として保存される。
  * 仕様が固まったら、`/add-feature`あるいは`/add-feature-ui`コマンドで実装する。
    * 例: `/add-feature [ファイル名]を実装して`


## 主要なコマンド

| コマンド | 用途 |
|---------|------|
| `/setup-project` | 初回のみ。6種のドキュメントを作成してプロジェクト基盤を確立する |
| `/plan-kaizen <アイデア>` | 既存コード・ドキュメントを踏まえて壁打ちし、仕様 MD を `docs/ideas/` に生成する |
| `/add-feature <機能名>` | 機能追加（計画→実装→検証→振り返りを自動実行） |
| `/add-feature-ui <機能名>` | 機能追加（E2Eテストを含む） |
| `/resume-work` | 中断した作業をチェックポイントから再開する |
| `/review-docs <パス>` | ドキュメントをサブエージェントで精査する |

## ディレクトリ構成

/add-feature および /add-feature-ui コマンドの実行により、以下のディレクトリ構成が自動生成される:

```
.claude/commands/   # /add-feature などのコマンド定義
.claude/agents/     # サブエージェント定義
.claude/skills/     # スキル定義
.claude/rules/      # 常時有効なガードレール（全会話に自動注入）
docs/               # プロジェクト永続ドキュメント（/setup-project で生成）
.steering/          # 作業単位のタスク管理（/add-feature で生成）
src/                # ソースコード（/add-feature で生成）
tests/              # テストコード（下記参照）
```

## tests/ ディレクトリについて

`tests/` 配下の `example.spec.ts` は**テンプレート参照用のサンプル**です。

実際のテストファイルは `/add-feature-ui` の実行時に自動生成されます。手動でファイルを削除・書き換える必要はありません。

### 品質ゲートとの関係

各ゲートは以下のファイル・ディレクトリの存在によって自動的に発動します。

| ディレクトリ / ファイル | 発動する Gate | 備考 |
|----------------------|-------------|------|
| `tests/a11y/` が存在する | Gate 4（a11y）が発動 | `/add-feature-ui` 実行時に実テストファイルが生成される |
| `tests/vrt/__screenshots__/` が存在する | Gate 3（VRT）が発動 | このディレクトリはテンプレートに含まれないため初期状態では発動しない |
| `playwright.config.ts` が存在する | Gate 2（E2E）が発動 | このファイルはテンプレートに含まれないため初期状態では発動しない |

<!-- > **Gate 4 を使用しない場合**: `tests/a11y/` ディレクトリごと削除してください（Gate 4 が不要なプロジェクトの場合のみ）。 -->

## 参考ドキュメント

- [SDD-workflow.md](SDD-workflow.md) — 全体ワークフロー図
- [.claude/docs/guidelines/definition-of-done.md](.claude/docs/guidelines/definition-of-done.md) — 品質ゲートの定義
- [.claude/docs/guidelines/repository-structure-guidelines.md](.claude/docs/guidelines/repository-structure-guidelines.md) — ディレクトリ構造
- [.claude/docs/guidelines/tech-stack-guidelines.md](.claude/docs/guidelines/tech-stack-guidelines.md) — 技術スタック選定ガイドライン


--------------

# Playwright CLI / MCP セットアップガイド

## Playwrightとは

[Playwright](https://github.com/microsoft/playwright) は、Microsoftが開発しているブラウザ自動化エンジンです。

プログラムから以下のようなブラウザを操作できます。

* URLを開く
* クリックする
* 文字を入力する
* スクリーンショットを撮る

通常はテスト自動化やWeb操作自動化に使われます。

## Playwright CLI と Playwright MCP について

| | [Playwright CLI](https://github.com/microsoft/playwright-cli) | [Playwright MCP](https://github.com/microsoft/playwright-mcp) |
| :---: | :---: | :---: |
|　概要 | コマンドライン経由でPlaywrightを操作するツール | MCPサーバー |
| 利用方法 | Claude Codeからはskills経由で利用可能 | Claude CodeからはMCP経由で利用可能 |
| 特徴 | 軽量で高速 | 柔軟で高度な操作が可能 |
| トークン消費 | 少ない | 多い |
| 自然言語の解釈 | 限定的 | 逐次推論で高度な解釈が可能 |
| 使い分けの目安 | * コーディングエージェントと組み合わせる<br>* 定型的な操作を自動化したい<br>* CIや自動化パイプラインで使いたい<br>* トークンコストを抑えたい | * 未知のUIを探索したい<br>* 要素構造を読みながら操作したい<br>* ログイン済みブラウザを使いたい<br>* 自然言語で柔軟に試行錯誤したい |

コーディングAIと組みあわせるならば、Playwright CLIが第一選択肢になります。


## セットアップ方法

### Playwright CLI のセットアップ

```bash
# グローバルインストール
npm install -g @playwright/cli@latest
```

```bash
# インストール確認
playwright-cli --version
```

```bash
# ブラウザのインストール
playwright-cli install
```

```bash
# Claude Codeにスキルとして登録
# プロジェクトディレクトリ直下で実行
playwright-cli install --skills
```

これでClaude Code から `/playwright-cli`スキルが使用可能になります。


### Playwright MCPのセットアップ

```bash
# Playwright MCPをユーザースコープでインストール
claude mcp add --scope user playwright -- npx @playwright/mcp@latest
```
```bash
# インストール確認
claude mcp list
```
```bash
# ブラウザのインストール（初回のみ）
npx playwright install
```

---

## 動作確認例

### Playwright CLI 動作確認例

Claude Code を起動して以下コマンドを実行：
```
/playwright-cli https://www.yahoo.co.jp にアクセスして、ページ全体のスクリーンショットを artifacts/yahoo.png に保存して
```
### Playwright MCP 動作確認例

Claude Codeを起動して以下プロンプトを入力：
```
playwright mcpでhttps://www.yahoo.co.jp にアクセスして、検索ボックスに「トヨタ 自動車」と入力し、検索実行して、
検索結果ページのスクリーンショットを yahoo_search.png として保存して。
```
