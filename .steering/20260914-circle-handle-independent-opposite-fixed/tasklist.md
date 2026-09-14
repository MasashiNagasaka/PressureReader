# Tasklist: 円形ハンドルの独立移動（反対側固定）

- [x] 要件確認（`docs/ideas/20260914-circle-handle-independent-opposite-fixed-spec.md`）
- [x] `on_mouse_drag` のハンドル分岐を境界座標ベースへ変更
- [x] 左右/上下で「掴んだ側のみ移動、反対側固定」を実装
- [x] 最小サイズクランプ（2px）を実装
- [x] 既存の円内部移動・再計算分岐へ影響がないことをコードで確認
- [x] `C:\nagasaka\python\testPressR\Scripts\python.exe -m py_compile src/PressureReader.py` を実行
- [ ] ユーザー手動確認（4ハンドルの独立移動）

## 申し送り
- `min_size = 2.0` を `on_mouse_drag` のハンドル処理内で使用。将来調整する場合は定数化を検討。
