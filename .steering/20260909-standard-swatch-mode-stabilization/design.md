# Design: standard-swatch-mode-stabilization

## 2026-09-09 実装設計（反映済み）
- 対象: `src/PressureReader.py` の `calculate_brightness(..., value_key=="14")` ブロック。
- 明度抽出後の `avg_list` が1件以上なら `root.after_idle(lambda: set_mode_rect("99"))` を実行し、通常モードへ戻す。
- 白基準値の算出は以下の順序:
1. `brightness_entry_01` を `float` 変換
2. 失敗時は可視明度エントリを `row` 順で並べ、末尾から最初の数値を採用
- 白基準値が取得できた場合のみ `white_Value/white_flag/white_Press` を更新する。
- `white_Press = c2p(white_Value)` は `try/except ValueError` で保護し、例外時も処理継続する。

## 変更対象
- `src/PressureReader.py`

## 設計方針
1. イベント依存を減らし、「明度確定」を遷移トリガーに使う。
2. 誤発火対策として「ドラッグ開始済みフラグ」を導入する。
3. グローバル `ButtonRelease` は維持しつつ、ボタン押下直後の1回を明示的に無視する。
4. 温湿度空欄時の `c2p` 呼び出しをガードして例外伝播を止める。

## 詳細設計

### A. 標準色見本モード突入 (`set_mode_rect("14")`)
- `rect_selected=False` に初期化（押下直後に採色へ行かせない）。
- `swatch_drag_started=False`。
- `ignore_next_global_release=True`。
- `start_x/start_y/end_x/end_y=None`。

### B. 実ドラッグの成立 (`on_mouse_down`)
- `mode=="rect" and current_value=="14"` のとき `swatch_drag_started=True` を立てる。

### C. 採色前チェック (`on_mouse_up`)
- `current_value=="14"` のとき:
  - `swatch_drag_started` が False なら return。
  - `start_x/start_y` が None なら return。
  - 幅/高さが最小閾値未満（2px）なら return。
- 条件成立時のみ `calculate_brightness(..., "14")` を許可。

### D. 明度確定後の遷移 (`calculate_brightness`)
- `value_key=="14"` ブロックで `avg_list` 反映後、
  `schedule_transition_to_normal_mode_after_swatch()` を呼ぶ。
- 遷移は `root.after_idle(transition_to_normal_mode_after_swatch)` で実行。
- 多重遷移防止に `swatch_transition_pending` を使用。

### E. 例外防止 (`calculate_brightness`)
- `white_Press = c2p(white_Value)` は温湿度が空欄でない場合のみ実行。
- `ValueError` は握って処理継続（遷移を止めない）。

### F. フォールバック (`on_global_mouse_up`)
- `ignore_next_global_release=True` の最初の1回は無視。
- `swatch_drag_started` が False の場合はフォールバック経路に入らない。

## 追加状態変数
- `standard_swatch_finalize_running`
- `swatch_transition_pending`
- `swatch_drag_started`
- `ignore_next_global_release`

## 影響範囲
- 標準色見本処理（`current_value=="14"`）の矩形入力系に限定。
- 通常解析（`current_value=="99"`）は既存ロジックを維持。

## リスク
- 閾値（2px）が厳しすぎる/緩すぎる場合に UX へ影響。
- 既存イベントバインドとの相互作用で予期せぬ return が起こる可能性。

## 検証方針
- ボタン押下のみ、ドラッグあり、キャンバス外リリース、連続実行を最低限確認。
