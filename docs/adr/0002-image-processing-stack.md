# 0002: Pillow + OpenCV + NumPy + SciPy を画像解析スタックとして採用

- Status: Accepted
- Date: 2026-09-07
- Decision Makers: AI Agent (setup-project)

## Context
PressReaderはPNG画像解析、輝度計算、補間、可視化、メタデータ保存を一体で扱う。既存実装は当該スタックに依存している。

## Options
1. 既存スタックを維持（Pillow/OpenCV/NumPy/SciPy）
2. Pillow中心に統一しOpenCV/SciPy依存を削減
3. 画像処理基盤を全面刷新

## Decision
既存スタックを維持する。機能回帰リスクを抑え、v3.5.0の目的（安定改修）に集中する。

## Consequences
- Positive:
  - 換算ロジックの互換性を維持しやすい
  - 既存の検証済み処理を再利用できる
- Negative:
  - 依存ライブラリが多く、配布サイズや環境管理コストが増える

