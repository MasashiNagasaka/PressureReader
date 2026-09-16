# Design: 標準色見本処理ボタン トグル化

## 実装方針
- `swatch_toggle_on`（`tk.BooleanVar`）を導入し、標準色見本モードのON/OFF状態を保持する。
- ボタンコマンドを `toggle_swatch_mode()` に変更し、状態に応じて `set_mode_rect(\"14\")` / `set_mode_rect(\"99\")` を呼び分ける。
- 見た目更新は `update_iromihon_button_visual()` に集約し、ON/OFFとホバーを一元管理する。

## 変更点
1. `標準色見本処理` ボタン文言を状態付き（`：ON` / `：OFF`）表示にする。
2. `on_enter_iromihon` / `on_leave_iromihon` は直接画像差し替えではなく、統一関数で更新する。
3. `set_mode_rect()` 内で `current_value` に応じてトグル状態を同期する。
4. 色見本矩形確定後（`current_value != \"99\"`）は自動OFF処理を入れる。

## 影響範囲
- `src/PressureReader.py` のみ。
