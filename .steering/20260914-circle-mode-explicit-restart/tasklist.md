# Tasklist: 円形モード確定後の新規開始を明示操作限定

- [x] 要件確認（`requirements.md`）
- [x] `on_mouse_down` の円形分岐で、確定済み円がある場合の円外クリックを早期 `return` に変更
- [x] 既存の移動・ハンドルリサイズ分岐が維持されることをコード上で確認
- [x] `C:\nagasaka\python\testPressR\Scripts\python.exe -m py_compile src/PressureReader.py` を実行
- [ ] ユーザー操作で円形モード挙動を確認

## 申し送り
- 今回は最小差分で `on_mouse_down` のみ変更。既存の明示操作（選択範囲クリア/モード切替/画面リセット）で `circle_id` がリセットされるため、新規開始の導線は維持される。
