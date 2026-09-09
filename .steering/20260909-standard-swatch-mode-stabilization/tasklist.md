# Tasklist: standard-swatch-mode-stabilization

## 2026-09-09 追加タスク（明度確定後遷移の再実装）
- [x] `calculate_brightness(value_key=="14")` に `after_idle` による通常モード遷移を再追加
- [x] 部分設定（明度欄の一部のみ設定）でも遷移可能な条件に修正（`len(avg_list) > 0`）
- [x] `brightness_entry_01` 空欄時のフォールバック（可視欄末尾の有効値）を追加
- [x] `c2p()` 呼び出しの `ValueError` をガードし、例外で遷移が止まらないよう修正
- [x] `C:\\nagasaka\\python\\testPressR\\Scripts\\python.exe -m py_compile src/PressureReader.py` 実施

- [x] `set_mode_rect("14")` 初期化ロジックを追加（誤発火防止）
- [x] `swatch_drag_started` / `ignore_next_global_release` 状態変数を導入
- [x] `on_mouse_down` で標準色見本の実ドラッグ開始を記録
- [x] `on_mouse_up` で標準色見本時の実行条件を厳格化
- [x] `calculate_brightness(value_key=="14")` で遷移予約処理を追加
- [x] 温湿度空欄時の `c2p` 呼び出しをガード
- [x] `on_global_mouse_up` に1回無視 + ドラッグ済み条件を追加
- [x] `python -m py_compile src\\PressureReader.py` で構文確認
- [ ] 手動E2E確認（ユーザー実行）
  - [ ] 標準色見本ボタン押下のみで明度が変化しない
  - [ ] ドラッグ選択時のみ明度が更新される
  - [ ] 明度更新後に通常モードへ復帰する
  - [ ] 温湿度未入力で例外停止しない
  - [ ] 連続操作で固着/誤発火しない
