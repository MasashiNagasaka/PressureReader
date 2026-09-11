# Tasklist: スケーリング行レイアウト再設計

- [x] 仕様確認（`docs/ideas/20260911-scaling-row-relayout-fix-spec.md`）
- [x] row=17 の専用フレーム（`scaling_frame`）を追加
- [x] `button_pixmm` / `pixmm_entry` / `label_pixmm_unit` を専用フレームへ移動
- [x] `pixmm_entry` 幅を `width=10` に調整
- [x] `mm/px` を `pixmm_entry` 直右に配置
- [x] 構文チェック（`C:\nagasaka\python\testPressR\Scripts\python.exe -m py_compile src/PressureReader.py`）
- [x] 文字化けチェック（仕様書・コード・ステアリング）
