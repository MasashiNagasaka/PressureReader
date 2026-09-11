# design

## 変更点
- `SHEET_TYPE_PLACEHOLDER_DISPLAY` / `SHEET_TYPE_PLACEHOLDER_VALUE` を追加。
- `is_sheet_type_unselected()` と `set_sheet_type_unselected()` を追加。
- `selected_var` の初期値を未選択値に変更。
- `options` に未選択項目（`感圧紙を選択`）を末尾追加。
- `update_entries_and_buttons()` で未選択時の解析条件ウィジェット表示制御を追加。
- `get_analysis_condition_missing_message()` に未選択ガードを追加。
- `save_brightness_to_xlsx()` に未選択ガードを追加。
- `load_image()` でメタデータの紙種未設定時は未選択遷移。
- `load_image(show_sheettype_guidance=True)` 時は自動的に未選択へ戻す。
- `reset_to_startup_state()` は未選択へ復帰する。

## 影響範囲
- `src/PressureReader.py`

## 非対象
- 感圧紙種類の有効項目文言の変更。
- 既存の画像処理・圧力換算ロジック変更。
