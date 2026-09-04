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

---

## ⚠️ 必須設定チェックリスト（`playwright.config.ts` 作成時）

> **背景**: `reuseExistingServer: true`（Playwright のデフォルト）を使うと、E2E テスト終了後もサーバーがバックグラウンドで生き続ける。その後いくらコードを修正してもブラウザは古いサーバーに接続し続けるため、「修正が反映されない」という錯覚が発生する。この問題はデフォルト値を変えるだけで防止できる。

### 必須設定

```typescript
webServer: {
  command: 'python main.py',  // 下記「起動スクリプト」参照
  url: 'http://localhost:8000',
  reuseExistingServer: false, // 必須: テスト終了後にサーバーを必ず停止する
  timeout: 15000,
},
```

**`reuseExistingServer: false` を必ず設定すること。** これを省略するとデフォルトの `true` が適用され、古いサーバーが占有し続ける問題が発生する。

### 推奨設定（DB 共有テスト向け）

```typescript
workers: 1,          // DB を共有するテストはシリアル実行で競合を防ぐ
fullyParallel: false,
```

SQLite などの単一ファイル DB を複数テストが同時に操作すると競合エラーが発生する。
DB を使うテストは必ず `workers: 1` を設定すること。

### `webServer.command` に `--reload` を使わないこと

```typescript
// ❌ 非推奨
command: 'uvicorn src.backend.app:app --port 8000 --reload',

// ✅ 推奨（毎回フレッシュ起動）
command: 'python main.py',
```

`--reload` は watchfiles でファイル変更を監視するが、Windows 環境では検知漏れが起きやすく
「変更したのに反映されない」錯覚を生む。E2E テスト用サーバーは毎回フレッシュに起動する方が信頼できる。

### Python (FastAPI + uvicorn) 向け起動スクリプト

`main.py`（`webServer.command` から呼び出すエントリーポイント）に以下のパターンを実装すること。

```python
import os
import shutil
import signal
import subprocess

PORT = 8000


def kill_port(port: int) -> None:
    """指定ポートを占有しているプロセスを全て強制終了する"""
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"], capture_output=True, text=True
        )
        for pid in result.stdout.strip().split("\n"):
            if pid:
                os.kill(int(pid), signal.SIGKILL)
    except Exception:
        pass


def clear_pycache() -> None:
    """古い .pyc を削除して最新コードを確実にロードする"""
    for root, dirs, _ in os.walk("."):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)


def main() -> None:
    kill_port(PORT)      # 既存プロセスを全て kill
    clear_pycache()      # 古い .pyc を削除して確実に最新コードをロード
    os.execvp("uvicorn", ["uvicorn", "src.backend.app:app", "--port", str(PORT)])


if __name__ == "__main__":
    main()
```

### まとめ：`playwright.config.ts` の推奨テンプレート（Python + FastAPI 向け）

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  workers: 1,           // DB共有テストはシリアル実行
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
