# Design: 検出値表示（平均/最大/最小）拡張

## 対象ファイル
- `src/PressureReader.py`

## 設計方針
- 既存の平均値表示ロジックを共通化し、平均/最大/最小を同一更新経路で描画する。
- 既存コードで重複していた「感圧紙ごとの測定範囲判定」を関数化して再利用する。

## UI変更
- 既存 `検出値：` セクション配下に専用フレームを追加。
- フレーム内に3行（平均/最大/最小）のラベル + 値入力欄 + `MPa` ラベルを配置。

## ロジック変更
- 追加関数:
  - `clear_detected_value_entries()`
  - `get_selected_sheet_pressure_limits()`
  - `format_detected_pressure_value()`
  - `update_detected_value_entries()`
- 四角形/多角形/円の各計算処理で `filtered_values` から平均・最大・最小を算出し、共通関数でUIへ反映する。

## 互換性
- 既存の `atai_ave_entry` は維持しつつ、`atai_max_entry` / `atai_min_entry` を追加する。
- クリア処理（選択範囲クリア、画面リセット、画像読込時初期化、起動時初期化）は3項目同時クリアに統一する。
