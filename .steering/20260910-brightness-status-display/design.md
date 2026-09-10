# Design

## Approach
- 既存の明度 `Entry` は内部データ保存専用にし、レイアウト対象から外す。
- 代わりに `tk.Label` を新設し、見本ごとの状態テキストを表示する。
- 状態ラベルは `button_frame` と同色背景にし、枠線なしで表示する。
- 感圧紙種類ごとの有効見本セットをヘルパー関数で一元化する。

## Added Structures
- `brightness_slots`: `(value_key, entry, button)` の一覧。
- `brightness_status_labels`: `value_key -> Label` の辞書。
- `get_active_brightness_keys/slots/entries()`: 有効見本の取得。
- `set_brightness_status()`: 状態表示のスタイル適用。

## Behavior Changes
- `update_entries_and_buttons()`
  - 明度 `Entry` をグリッドしない。
  - 見本ボタン + 状態ラベルのみグリッドする。
  - 手動の種類変更時は `未設定` 表示へリセットする。
- `insert_to_visible_entries()`
  - 有効見本へ内部値を投入。
  - 成功/失敗の状態表示を更新。
  - 各見本のデバッグログを出力。
- `are_all_entries_valid()`
  - `winfo_ismapped()` 依存をやめ、有効見本リストで判定する。
