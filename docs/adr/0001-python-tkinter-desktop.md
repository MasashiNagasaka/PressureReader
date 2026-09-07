# 0001: Python Tkinterベースのデスクトップ構成を採用

- Status: Accepted
- Date: 2026-09-07
- Decision Makers: AI Agent (setup-project)

## Context
現行のPressReaderはWindows運用の単体ツールで、既存実装資産はPython+Tkinterに集中している。短期間で安定運用を継続する必要がある。

## Options
1. Python + Tkinter（現行踏襲）
2. Web化（FastAPI + React/Next.js）
3. 別GUIフレームワーク（PyQt等）

## Decision
Python + Tkinterを継続採用する。既存資産の再利用性と改修コスト最小化を優先する。

## Consequences
- Positive:
  - 既存コードを活かして迅速に改善できる
  - 実行環境の変化が少なく運用リスクが低い
- Negative:
  - 単一ファイル化による保守性課題が残る
  - Web化に比べ配布/遠隔利用の柔軟性は低い

