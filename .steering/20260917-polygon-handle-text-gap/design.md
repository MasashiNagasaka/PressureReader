# Design: 多角形頂点ハンドルとテキストの余白確保

## 実装方針
- 既存の `_collect_avoid_bboxes(...)` を拡張し、`polygon_handle` タグを持つ頂点ハンドルのBBoxのみ拡張して扱う。
- 頂点ハンドル作成時に専用タグ `polygon_handle` を付与し、他の `mark` と識別できるようにする。

## 変更箇所
- `src/PressureReader.py`
  - `_collect_avoid_bboxes(...)`
    - 重複ID除外（同一アイテムの重複計上防止）
    - `polygon_handle` に対する6pxマージン拡張
  - 多角形頂点ハンドル作成処理（`on_mouse_down` の polygon 分岐）
    - `tags=("mark", "polygon_handle")` 付与

## 影響範囲
- 多角形モードのテキスト配置評価精度のみ改善。
- 既存の描画削除処理（`canvas.delete("mark", ...)`）との互換性は維持される。
