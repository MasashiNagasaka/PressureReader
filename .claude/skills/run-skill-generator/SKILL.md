---
name: run-skill-generator
description: プロジェクト固有の起動・テスト・確認手順を .claude/skills/run-<project>/ にレシピとして記録する。新規プロジェクト作成後、または起動方法・依存関係・環境変数が変わったときに実行する。
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob
---

# run-skill-generator

`/run` と `/verify` が参照するプロジェクト固有の「起動レシピ」を生成します。
一度実行しておくと、以降は `/run` や `/verify` が自動的にこのレシピを参照して正確に起動・検証できます。

**引数:** プロジェクト名（省略可。省略時は自動検出）

---

## ステップ1: プロジェクト名を特定する

以下の優先順位でプロジェクト名を自動検出する:

1. 引数 `$ARGUMENTS` が指定されている場合はそれを使用
2. `package.json` → `name` フィールド
3. `pyproject.toml` → `[project] name` フィールド
4. `Cargo.toml` → `[package] name` フィールド
5. `go.mod` → `module` 宣言の末尾セグメント
6. カレントディレクトリ名

検出したプロジェクト名を `<project-name>` として使用する。
スペース・スラッシュは `-` に置換し、小文字化する。

## ステップ2: 既存情報をスキャンする

以下のファイルを読んで、起動・テスト方法を自動収集する（存在するもののみ）:

```bash
# 読む対象（優先順）
package.json          # scripts.dev / scripts.start / scripts.test / scripts.build
Makefile              # dev / start / run / test / build ターゲット
pyproject.toml        # [tool.poetry.scripts] または [project.scripts]
README.md             # 起動手順・インストール手順セクション
docker-compose.yml    # services と ports
.env.example          # 環境変数名の一覧（値は読まない）
.env.sample           # 同上
```

読み取った内容から以下を抽出する:
- インストールコマンド（`npm install`, `pip install -r requirements.txt` など）
- 起動コマンド
- テスト・型チェックコマンド
- ビルドコマンド
- 使用ポート番号
- 環境変数名（**値は絶対に収集しない。名前だけ**）

## ステップ3: 不足情報を対話的に収集する

ステップ2で取得できなかった情報のみ `AskUserQuestion` で質問する。
すでに判明している項目は質問しない。

**質問カテゴリ（不足分のみ）:**

| 項目 | 例 |
|---|---|
| 起動コマンド | `npm run dev`, `python main.py`, `./gradlew bootRun` |
| テストコマンド | `npm test`, `pytest`, `go test ./...` |
| 確認 URL / ポート | `http://localhost:3000`, ポート 8080、CLI の場合は「なし」 |
| 必要な環境変数名 | `DATABASE_URL`, `API_KEY`（**名前のみ。値は不要**） |
| 注意事項 | 「Docker を先に起動」「Node 20 以上が必要」など |

## ステップ4: 動作確認（任意・推奨）

情報が揃ったら、実際に起動を試みて手順を検証する。

```bash
# 例: npm プロジェクトの場合
npm install
npm run dev &
DEV_PID=$!
# ポートが開くまで数秒待機
sleep 3
# 起動確認
curl -s -o /dev/null -w "%{http_code}" http://localhost:[PORT]
kill $DEV_PID 2>/dev/null
```

起動に成功した手順をそのままレシピに記録する。
失敗した場合は原因と回避策をレシピの「注意事項」に記録する。

## ステップ5: レシピファイルを生成する

収集した情報をもとに、テンプレートファイルを読み込んで生成する:

```
Read('.claude/skills/run-skill-generator/templates/run-skill.md')
```

テンプレートのプレースホルダーを置き換えて、以下のパスに保存する:

```
.claude/skills/run-<project-name>/SKILL.md
```

### ⚠️ 生成ルール（必ず守ること）

- `.env`, `credentials`, `*.key`, `*.secret` などの機密ファイルは一切読まない
- 環境変数の**値**は絶対に記録しない（名前のみ）
- `secrets`, `password`, `token`, `key` を含む文字列は値を書かない
- 生成ファイルは `.gitignore` 対象外（コミット対象）なので、機密情報は含めない

## ステップ6: 完了報告

```
✅ レシピを生成しました: .claude/skills/run-<project-name>/SKILL.md

これ以降、/run や /verify を実行するとこのレシピが自動的に参照されます。

📋 記録内容:
  - 起動コマンド: <起動コマンド>
  - テストコマンド: <テストコマンド>
  - 確認URL: <確認URL>
  - 環境変数（名前のみ）: <環境変数名リスト>

⚠️  以下のタイミングで再実行してください:
  - 起動コマンドが変わったとき
  - 依存関係・ランタイムバージョンが変わったとき
  - 環境変数の構成が変わったとき
  - 外部サービス接続（DB・キャッシュ等）が変わったとき

内容を確認し、必要であれば手動で編集してください。
```

---

詳細なテンプレート: [templates/run-skill.md](templates/run-skill.md)
