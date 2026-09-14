# Tasklist: 多角形/円形モードの確定後クリック点圧表示

- [x] 要件確認（`docs/ideas/20260914-polygon-circle-post-confirm-click-point-pressure-spec.md`）
- [x] 多角形モード確定後クリックで点圧表示を追加（新規頂点追加は抑止維持）
- [x] 円形モード確定後クリックで点圧表示を追加（新規円開始は抑止維持）
- [x] 多角形モードでクリック/ドラッグを判定し、ドラッグ時は編集操作優先に変更
- [x] 円形モードでクリックとドラッグを判定する最小状態を追加
- [x] 円形移動/リサイズ時は既存どおり範囲再計算される分岐を維持
- [x] モード切替/クリア/画面リセットで追加状態を初期化
- [x] `C:\nagasaka\python\testPressR\Scripts\python.exe -m py_compile src/PressureReader.py` を実行
- [ ] ユーザー手動確認（多角形/円形の確定後クリックとドラッグ挙動）

## 申し送り
- 多角形モードは `polygon_click_point` / `polygon_dragged` を導入し、`on_mouse_up` でクリック確定時のみ点圧表示する実装にしている。
- 円形モードは `on_mouse_down` だけではクリック/ドラッグを区別できないため、`on_mouse_drag` で `circle_dragged` を立て、`on_mouse_up` で分岐する実装にしている。
