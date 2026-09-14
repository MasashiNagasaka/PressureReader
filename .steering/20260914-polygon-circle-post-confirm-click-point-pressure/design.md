# Design: 多角形/円形モードの確定後クリック点圧表示

## 対象
- `src/PressureReader.py`
  - `on_mouse_down`
  - `on_mouse_drag`
  - `on_mouse_up`
  - `set_mode_rect`
  - `set_mode_polygon`
  - `set_mode_circle`
  - `clear_selectarea`
  - `reset_to_startup_state`

## 設計方針
- 多角形確定後クリック:
  - 既存の「新規頂点追加しない」を維持しつつ、クリック点の点圧表示を追加する。
- 円形確定後クリック:
  - 既存の「新規円作成しない」を維持する。
  - クリック時は点圧表示、ドラッグ編集時は既存どおり範囲再計算を行う。
  - クリックとドラッグを分離するために、最小限の状態変数を追加する。

## 変更内容
- 追加状態:
  - `polygon_click_point`: 多角形確定後クリック点（クリック時の点圧表示用）
  - `polygon_dragged`: 多角形操作がドラッグだったかの判定フラグ
  - `circle_click_point`: 円形確定後クリック点（クリック時の点圧表示用）
  - `circle_dragged`: 円形操作がドラッグだったかの判定フラグ
- `on_mouse_down`:
  - polygon: `polygon_id` 存在時はクリック点を保持して return（点圧表示は `on_mouse_up` でクリック確定時のみ）
  - circle: `circle_id` 存在時の円外クリックで点圧表示して return
  - circle: 円内クリック時は移動候補として `circle_click_point` を保持
- `on_mouse_drag`:
  - polygon の頂点移動/全体移動で `polygon_dragged=True` を設定
  - circle の移動/リサイズ/新規描画で `circle_dragged=True` を設定
- `on_mouse_up`:
  - polygon の確定済み操作で
    - ドラッグあり: 既存どおり範囲再計算
    - ドラッグなしクリック: 点圧表示
  - circle の確定済み操作で
    - ドラッグあり: 既存どおり範囲再計算
    - ドラッグなしクリック: 点圧表示
- 各種リセット関数:
  - 新規状態変数を初期化

## 互換性
- 既存の計算ロジック (`calculate_brightness3`, `mark_lowest_brightness_points`) は変更しない。
- クリック時点圧表示は既存関数 (`calculate_point_pressure`, `show_point_pressure_text`) を再利用する。
