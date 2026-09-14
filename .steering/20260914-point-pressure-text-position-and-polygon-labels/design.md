# Design: 点圧表示の文言/位置/多角形個別表示

## 対象
- `src/PressureReader.py`
  - `show_point_pressure_text`
  - `show_polygon_point_pressure_text`
  - `on_mouse_down`
  - 範囲確定/モード切替/クリア処理

## 設計方針
- 点圧表示文言は固定語を除去し、値のみ（`xx.xxxMPa`）を表示する。
- 点圧表示位置はクリック点の上側へ統一する。
- 多角形モードでは点ごとの表示タグを持たせ、各頂点に個別表示する。
- 範囲確定時やモード切替時は既存運用を維持し、`point_pressure` 系タグをクリアする。

## 変更内容
- 更新:
  - `show_point_pressure_text` の表示テキストを `点圧` なしに統一
  - `show_point_pressure_text` / `show_polygon_point_pressure_text` の描画位置を点の上側に統一
  - `show_polygon_point_pressure_text` を点インデックスごとのタグ管理にして個別表示
- 既存維持:
  - `on_mouse_up` / `right_click` / `set_mode_*` / `clear_selectarea` / `reset_to_startup_state` での点圧表示クリア
