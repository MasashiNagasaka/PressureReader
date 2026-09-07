# 0003: 解析条件をPNGメタデータ `press{...}` で保持

- Status: Accepted
- Date: 2026-09-07
- Decision Makers: AI Agent (setup-project)

## Context
解析条件を画像と一緒に持ち運べることが現場運用上重要。既存では`press{...}`形式でPNGメタに保存・復元している。

## Options
1. PNGメタデータ保持（現行）
2. 別JSON/CSVで条件管理
3. 外部DB管理

## Decision
現行のPNGメタデータ方式を継続する。単一ファイル運用と再現性確保に有利。

## Consequences
- Positive:
  - 画像単体で解析条件を再現できる
  - ファイル受け渡しが簡便
- Negative:
  - メタ形式の後方互換を維持する責務が続く
  - 画像編集ツールによりメタが失われるリスクがある

