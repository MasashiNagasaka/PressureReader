# Design: 可視化しきい値の境界安定化

## 対象ファイル
- `src/PressureReader.py`

## 設計方針
- 色見本採色結果の `filtered` 統計を一貫利用する。
- 平均値は表示用に使用し、最小/最大は端点クランプ用に使用する。
- `region_values` 全画素の min/max は使わない。

## 実装ポイント
- `swatch_brightness_bounds` で `{value_key: (min, max)}` を保持する。
- `insert_to_visible_entries(avg_list, bounds_list=None)` で以下を反映する。
  - 表示値: `avg_list`（`filtered` 平均）
  - 境界値: `bounds_list`（`filtered` min/max）
- `apply_threshold` で以下を実施する。
  - `threshold_margin = 1`
  - `low_threshold = floor(bri_Max) - 1`
  - `high_threshold = ceil(bri_Min) + 1`
  - 先頭スロット（1.0側）の min で `low_threshold` をクランプ
  - 末尾スロット（0.1側）の max で `high_threshold` をクランプ
- デバッグ用に、しきい値と外れ画素数（`mask_low/mask_high`）をログ出力する。
