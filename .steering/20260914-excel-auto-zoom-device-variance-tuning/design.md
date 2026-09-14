# Design: Excel自動ズームの実機差調整しやすさ向上

## 対象
- `src/PressureReader.py`
  - `save_brightness_to_xlsx`

## 設計方針
- `zoomScale` 算出処理をローカル関数化して可読性を上げる。
- 実効表示領域・補正係数・最小/最大ズームを同一ブロックに集約し、今後の調整を容易にする。
- 振る舞いは従来仕様と同等を維持する（値は変更しない）。

## 変更内容
- `calculate_excel_zoom_scale(...)` を追加。
- 以下をパラメータとして関数内に明示:
  - `view_width_px`, `view_height_px`
  - `safety_margin`, `width_margin`, `zoom_bias`
  - `min_zoom`, `max_zoom`
- 呼び出し側は `ws.sheet_view.zoomScale = calculate_excel_zoom_scale(...)` のみに簡略化。
