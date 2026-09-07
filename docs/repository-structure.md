---
last_updated: 2026-09-07
git_commit: ""
status: draft
---

# リポジトリ構造定義書 (Repository Structure Document)

## プロジェクト構造
- 本リポジトリはSDD運用のための管理ドキュメント群と、実行ソースを同居させる。
- 実行コード本体は `src/` 配下を正とする。

## ディレクトリ詳細
### `src/`
- `PressReader_v3.5.0.py`（改名後の主実行ファイル）
- `pr_images/`（UI画像）
- `poppler/`（PDF変換依存バイナリ）

### `docs/`
- 永続ドキュメント（PRD, 設計, ガイド, 用語集）
- `ideas/`（仕様メモ・壁打ち結果）
- `adr/`（アーキテクチャ意思決定）

### `.claude/`, `.codex/`
- コマンド/スキル/ルール定義

### `.steering/`
- `/add-feature` 実行時の作業単位仕様

## ファイル配置規則
- 実行対象Pythonは `src/` 配下に配置
- 仕様書は `docs/ideas/` に配置
- 永続設計書は `docs/` 直下に配置

## 命名規則
- 仕様書: `YYYYMMDD-<topic>-spec.md`
- アイディア: `YYYYMMDD-<topic>-idea.md`
- ADR: `NNNN-<title>.md`

## 依存関係ルール
- UI画像は `src/pr_images/` を参照
- PDF変換は `src/poppler/` を前提
- 絶対パス依存を避け、可能な限り実行ファイル基準の相対解決を採用

## スケーリング戦略
- 単一ファイル維持しつつ、段階的に責務分離を進める
- 優先分割候補: `c2p`関連ロジック、I/O層、UIイベント層

