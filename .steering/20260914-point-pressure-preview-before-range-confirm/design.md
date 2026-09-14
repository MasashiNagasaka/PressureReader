# Design: 範囲確定前の点圧表示（クリック1点）

## 対象
- `src/PressureReader.py`
  - `on_mouse_down`
  - `on_mouse_up`
  - `right_click`
  - モード切替/クリア処理

## 設計方針
- クリック点の圧力値算出を `calculate_point_pressure` に分離する。
- キャンバステキスト表示を `show_point_pressure_text` に分離し、タグ `point_pressure` で管理する。
- 範囲確定時（ドラッグ確定・右クリック確定）に `point_pressure` を消して従来表示へ遷移する。

## 変更内容
- 追加:
  - `calculate_point_pressure(canvas_x, canvas_y)`
  - `show_point_pressure_text(canvas_x, canvas_y, pressure_value)`
- 更新:
  - `on_mouse_down`（rect/circle/polygon で点圧表示）
  - `on_mouse_up`（クリックのみ時は点圧維持、範囲確定時は点圧削除）
  - `right_click`（polygon/circle確定時に点圧削除）
  - `set_mode_*`, `clear_selectarea`, `reset_to_startup_state` 等で `point_pressure` のクリアを追加
