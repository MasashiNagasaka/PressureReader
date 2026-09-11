# Design: スプラッシュ2「…」位置の完全揃え（再修正）

## 対象
- `src/PressureReader.py` の `show_startup_info_window()`

## 設計方針
- 本文3行を共通の `table_frame` に集約する。
- `table_frame` 上で `bullet / left / separator / right` の4列を共有し、`separator` 列を固定する。

## 変更内容
- 既存の `add_aligned_item(parent, ...)` を、共通 `table_frame` を使う `add_aligned_item(row_index, ...)` に変更。
- `table_frame.grid_columnconfigure(1, minsize=250)` を1回だけ設定して全行で共有。
- 各行は `row_index`（0,1,2）で同一列へ配置し、`…` の位置を一致させる。

## 影響範囲
- スプラッシュ2の本文レイアウトのみ。
- 解析処理、メイン画面機能、起動シーケンスには影響しない。
