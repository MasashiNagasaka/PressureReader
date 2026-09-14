# Design: 高圧検出箇所マーク処理の全選択モード対応

## 対象
- `src/PressureReader.py`
  - `mark_lowest_brightness_points`
  - `update_label`
  - `on_mouse_up`
  - `right_click`

## 設計方針
- `mark_lowest_brightness_points` をモード依存マスク生成方式へ変更する。
- モード別に `selection_mask` を構築し、選択あり時はマスク内のみ探索する。
- 選択なし時は従来どおり画像全体を探索する。

## 変更内容
- `mark_lowest_brightness_points` を引数なしに変更し、グローバル状態から選択範囲を判定。
- `update_label` からの呼び出しを引数なしへ変更。
- 多角形/円形の確定時（`right_click`, `on_mouse_up`）にもマーク更新を追加。
