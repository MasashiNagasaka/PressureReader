# Design: 円形モード確定後の新規開始を明示操作限定

## 対象
- `src/PressureReader.py`
  - `on_mouse_down`（`mode == "circle"` 分岐）

## 設計方針
- 既存円（`circle_id`）があるときは、以下の優先順位を維持する。
  - 円内部クリック: 移動開始
  - ハンドルクリック: リサイズ開始
- 上記どちらにも該当しない円外クリックでは、従来の「新規円作成」へ進まず早期 `return` する。
- 既存円がない場合のみ新規円作成フローへ進む。

## 影響範囲
- 直接変更は `on_mouse_down` の円形分岐のみ。
- `clear_selectarea` / `set_mode_circle` / `reset_to_startup_state` は既存のままで、明示操作による新規開始条件を満たす。

## 非変更事項
- 圧力算出ロジック（`calculate_brightness3` など）
- 右クリック確定処理
- 四角形/多角形モード挙動
