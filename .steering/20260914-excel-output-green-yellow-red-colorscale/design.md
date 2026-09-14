# Design: Excel出力セルの緑・黄・赤カラースケール

## 対象
- `src/PressureReader.py`
  - `save_brightness_to_xlsx`

## 設計方針
- `openpyxl.formatting.rule.ColorScaleRule` を使って3色スケールを定義する。
- 対象範囲は `A1` から最終セル（`{最終列}{最終行}`）までとする。
- `row_count > 0` かつ `col_count > 0` のときだけ適用する。

## 変更内容
- `ColorScaleRule` の import を追加する。
- Excel出力処理内に条件付き書式適用を追加する。
  - 開始点: `min` / `00B050`（緑）
  - 中央点: `percentile=50` / `FFFF00`（黄）
  - 終了点: `max` / `FF0000`（赤）

## 互換性
- 出力値（`None` 空欄含む）には手を加えない。
- セル寸法設定、ズーム自動調整、保存メッセージ表示は既存のまま維持する。
