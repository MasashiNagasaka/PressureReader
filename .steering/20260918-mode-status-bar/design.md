# Design: モード状態ステータスバー追加

## 実装方針
- `root` 直下に `status_bar_frame` / `status_bar_label` を追加し、`side=tk.BOTTOM` で固定表示する。
- `update_mode_status_bar()` を追加し、既存の状態変数から表示文言を決定する。

## 表示判定
- 判定元:
  - `swatch_toggle_on.get()`
  - `scaling_toggle_on.get()`
  - `mode`
- 優先順位:
  1. 標準色見本ON → `モード：標準色見本の選択`
  2. スケーリングON → `モード：スケーリングの設定`
  3. `mode in ("rect","polygon","circle")` → `モード：範囲選択`
  4. その他 → 空文字

## 更新タイミング
- `toggle_swatch_mode()`
- `set_conversion_factor()`（ON化時）
- `deactivate_scaling_mode()`（OFF化時）
- `set_mode_rect()` / `set_mode_polygon()` / `set_mode_circle()`
- 起動時の初期化後

## 影響範囲
- 画面下部の表示のみ。解析処理・Excel出力ロジックには影響なし。
