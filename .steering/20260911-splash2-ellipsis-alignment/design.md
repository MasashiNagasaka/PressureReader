# Design: スプラッシュ2 各行の「…」位置揃え

## 対象
- `src/PressureReader.py` の `show_startup_info_window()`

## 設計方針
- 各行を `bullet / left-column / separator / right-column` の4要素で構成する。
- `left-column` の幅を固定して、`separator` の列位置を統一する。

## 変更内容
- `add_segmented_labels()` を追加し、キーワード強調付きラベル生成を共通化。
- `add_aligned_item()` を追加し、2カラムレイアウトで行描画する。
- `row_frame.grid_columnconfigure(1, minsize=250)` により `…` の位置を固定。

## 影響範囲
- スプラッシュ2表示レイアウトのみ。
- メイン画面機能ロジックには影響しない。
