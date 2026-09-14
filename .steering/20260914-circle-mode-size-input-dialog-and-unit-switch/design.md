# Design: 円形モードのサイズ入力ダイアログと単位自動切替

## 対象
- `src/PressureReader.py`
  - スケーリング設定値参照ヘルパー追加
  - 円形サイズ入力ダイアログ追加
  - `on_mouse_down` の円形新規作成導線変更
  - `calculate_brightness3` のサイズ表示拡張

## 設計方針
- 既存スケーリング入力ダイアログと同系の `Toplevel` モーダルUIを採用する。
- 単位は `pixmm_entry` の有効値有無で自動切替する。
- 入力値は半径として扱い、`mm` 入力時のみ `mm -> px` 変換して内部描画に使う。
- 円サイズ表示は入力単位と連動して表示し、面積表示と同時に出す。

## 変更内容
- 追加関数:
  - `get_scaling_factor_value()`
  - `get_circle_input_unit()`
  - `ask_circle_radius_value(unit_label)`
  - `get_circle_size_display_text()`
- `on_mouse_down(mode == "circle")`:
  - 新規円作成をドラッグ方式から入力ダイアログ方式へ変更。
  - 入力完了までは点圧表示を行わない。
  - 入力成功時は `update_circle()` 後に既存の再計算・マーク更新を実行。
- `calculate_brightness3()`:
  - サイズ表示（半径）を追加。
  - 面積表示テキストは既存ロジックを維持しつつ、常に生成されるよう整理。

## 互換性
- 円確定後のクリック/ドラッグ優先ルール、ハンドル編集、円内部移動は既存維持。
- 右クリック真円化仕様は変更しない。
