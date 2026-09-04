---
name: main-py-launcher
description: FastAPI バックエンドを持つアプリで、プロジェクトルートの main.py 起動ランチャーを作成・更新するためのスキル。/add-feature または /add-feature-ui で FastAPI アプリを構築し、uv run main.py を標準の起動入口にする必要がある場合に使用。バニラ JavaScript + FastAPI と Next.js + FastAPI の両方を扱う。
---

# main.py 統合ランチャースキル

## Overview

FastAPI バックエンドを持つ構成向けに、プロジェクトルートの `main.py` 起動ランチャーを作成・更新する。

このスキルは開発ワークフローを置き換えない。必ず `/add-feature` または `/add-feature-ui` のステアリングファイル作成後、実装タスクの一部として使用する。

## 使用条件

以下をすべて満たす場合に使う。

- FastAPI バックエンドを採用している
- ルート `main.py` からアプリを起動したい
- `uv run main.py` と `uv run main.py --kill` を標準の起動・停止入口にしたい

フロントエンド構成は問わない。バニラ JavaScript を FastAPI が静的配信する構成でも、Next.js を別プロセスで起動する構成でも使う。

## 作業手順

1. `docs/architecture.md` または作業中の `.steering/*/design.md` で、FastAPI バックエンドの配置とフロントエンド構成を確認する。
2. フロントエンドが FastAPI 静的配信か、Next.js などの別プロセス起動かを判定する。
3. `src/backend` と、存在する場合は `src/frontend` の実際の配置を確認する。
4. ルート `main.py` が存在しない場合は `templates/main.py` をベースに作成する。
5. FastAPI 静的配信構成では、フロントエンド別プロセス起動部分を省き、FastAPI / uvicorn の起動入口として調整する。
6. Next.js + FastAPI 構成では、FastAPI / uvicorn と Next.js dev server を同時起動する統合ランチャーとして調整する。
7. 既存 `main.py` がある場合は、既存のプロジェクト固有処理を残しながら不足要件だけを取り込む。
8. プロジェクト名、バックエンド ASGI パス、フロントエンド起動コマンドが標準と違う場合は調整する。
9. `.env` の例または既存設定で、必要なポートと CORS / API URL の整合性を確認する。
10. 構文チェックと起動確認を行う。

## テンプレート

`templates/main.py` を参照する。テンプレートは Next.js + FastAPI の別プロセス起動を含む完全版を前提にしている。

- バックエンド: `src/backend` で `uvicorn app.main:app` を起動
- フロントエンド: `src/frontend` で `npm run dev` を起動
- デフォルトポート: `BACKEND_PORT=8080`, `FRONTEND_PORT=3030`
- 子プロセスは `0.0.0.0` に bind
- LAN IP 取得時は `NO_PROXY`, `CORS_ORIGINS`, `NEXT_PUBLIC_API_BASE_URL` を補完

FastAPI 静的配信構成では、テンプレートから `start_frontend()` と `FRONTEND_PORT` 依存の処理を省き、`BACKEND_PORT` の FastAPI URL だけを表示する形に調整する。

標準構成と異なる場合は、テンプレートをそのまま使わず次を調整する。

- `start_backend()` の `--directory` と ASGI import path
- `start_frontend()` の `cwd` と npm script
- デフォルトポート
- 起動時に表示するアプリ名や URL

## 必須要件

作成・更新後の `main.py` は次を満たすこと。

- `.env` から `BACKEND_PORT` を読み込む
- フロントエンド別プロセス構成では `.env` から `FRONTEND_PORT` も読み込む
- `uv run main.py --kill` で関連ポートのプロセスを終了してから終了する
- 通常起動時は起動前に関連ポートの既存プロセスを終了する
- FastAPI 静的配信構成では FastAPI / uvicorn を起動する
- Next.js + FastAPI 構成では FastAPI と Next.js を同時起動する
- 起動するサーバープロセスを `0.0.0.0` に bind する
- LAN IP を取得できる場合は LAN URL を表示する
- 子プロセスに `NO_PROXY` / `no_proxy` を注入する
- フロントエンド別プロセス構成では `NEXT_PUBLIC_API_BASE_URL` を注入する
- フロントエンド別オリジン構成ではバックエンドに LAN IP の `CORS_ORIGINS` を追加する
- Ctrl+C または SIGTERM で両プロセスを終了する

## 検証

最低限、以下を確認する。

- `python -m py_compile main.py`
- `uv run main.py --kill` が対象ポートで失敗せず完了する
- `uv run main.py` でアプリのアクセス URL が表示される
- ブラウザからフロントエンドにアクセスできる
- フロントエンドからバックエンド API へアクセスできる
- Ctrl+C で起動したプロセスが終了する

## 注意点

- `.env` の secret 実値はドキュメントやテンプレートに書かない。
- `kill_port()` は開発用ランチャーとして対象ポートのプロセスを終了する。実行前にポート設定が正しいことを確認する。
- Windows では `netstat -ano` と `taskkill`、Unix 系では `lsof` を使う。
- 既存 `main.py` がある場合、アプリ固有の処理を消さず差分として取り込む。
