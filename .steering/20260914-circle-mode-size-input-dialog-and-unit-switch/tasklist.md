# Tasklist: 円形モードのサイズ入力ダイアログと単位自動切替

- [x] 要件確認（`docs/ideas/20260914-circle-mode-size-input-dialog-and-post-confirm-point-pressure-spec.md`）
- [x] 単位判定ヘルパー（mm/px）を追加
- [x] 円形サイズ入力ダイアログ（入力欄右に単位）を追加
- [x] 円形新規作成を「中心クリック→半径入力」フローに変更
- [x] 入力完了前の点圧表示を抑止
- [x] 円サイズ表示を入力単位連動（mm/px）に変更
- [x] `C:\nagasaka\python\testPressR\Scripts\python.exe -m py_compile src/PressureReader.py` を実行
- [ ] ユーザー手動確認（単位自動切替・確定前点圧抑止・確定後点圧表示）

## 申し送り
- 円サイズ入力は `ask_circle_radius_value()` で実装。無効値はダイアログ内で警告して再入力を促す。
