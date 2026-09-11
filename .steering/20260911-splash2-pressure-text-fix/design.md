# Design: スプラッシュ2 文言修正（圧力計測時）

## 対象ファイル
- `src/PressureReader.py`

## 実装方針
- `show_startup_info_window()` 内の `add_aligned_item(...)`（温度/湿度行）の右側セグメントを更新する。
- 既存の強調制御（`True` でマゼンダ+bold）を利用するため、変更は文言とフラグのみとする。

## 変更点
- `("圧力計測時の設定値", False)` を `("圧力計測時の値", True)` に変更。
