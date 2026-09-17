# Design: 範囲選択図形とテキストの重なり回避

## 実装方針
- `src/PressureReader.py` にテキスト配置共通ヘルパーを追加し、既存の `create_text` 呼び出しを置き換える。
- 既存ロジックのうち「表示位置決定」のみを変更し、圧力算出・値更新フローは維持する。

## 追加した共通処理
- `_collect_avoid_bboxes(...)`: 回避対象図形のBBox収集
- `_measure_text_bbox(...)`: テキスト描画想定BBox算出
- `_overlap_area(...)`: BBox重なり面積算出
- `_find_non_overlapping_text_position(...)`: 候補位置の評価・選定
- `_create_non_overlapping_text(...)`: 非重複配置で `canvas.create_text` を実行

## 変更箇所
- 点圧表示
  - `show_point_pressure_text(...)`
  - `show_polygon_point_pressure_text(...)`
- 面積表示
  - `calculate_brightness2(...)`（多角形）
  - `calculate_brightness3(...)`（円形）
  - `on_mouse_up(...)`（四角形）

## 互換性・影響
- 計算値・出力値への影響はなし。
- 表示タグは既存のまま維持するため、既存の削除・再描画処理と互換。
