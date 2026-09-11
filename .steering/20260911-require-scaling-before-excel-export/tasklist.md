# Tasklist: Excel出力前スケーリング必須化（押下時メッセージ）

- [x] 仕様確認（`docs/ideas/20260911-require-scaling-before-excel-export-spec.md`）
- [x] `save_brightness_to_xlsx()` 先頭に `pixmm_entry` の妥当性ガード追加
- [x] 未設定/不正値/0以下でメッセージ表示して処理中断
- [x] `conversion_factor=0` フォールバックを削除
- [x] 構文チェック（`C:\nagasaka\python\testPressR\Scripts\python.exe -m py_compile src/PressureReader.py`）
- [x] 文字化けチェック（仕様書・コード・ステアリング）
