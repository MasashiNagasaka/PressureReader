# Design: Excel出力時の自動ズーム調整（16x56実測基準）

## 対象
- `src/PressureReader.py`
  - `save_brightness_to_xlsx`

## 設計方針
- 実機確認で得た基準値「ズーム100%で 16行 x 56列 が表示可能」を採用する。
- 出力範囲（行数・列数）に対して、縦横がともに収まるズームを `min` で決定する。
- 表示余裕を持たせるため `fit_margin = 0.95` を掛ける。
- 最終ズームは `10`〜`400` にクランプする。

## 変更内容
- Excel保存前のズーム算出を、実測基準方式へ置き換える。
- 計算式:
  - `zoom_h = 100 * 16 / row_count`
  - `zoom_w = 100 * 56 / col_count`
  - `zoom = floor(min(zoom_w, zoom_h) * 0.95)`
  - `zoom = clamp(zoom, 10, 400)`
- 設定:
  - `ws.sheet_view.zoomScale = zoom`

## 互換性
- セル値出力・空欄処理・列幅/行高さ設定・ファイル保存は変更しない。
