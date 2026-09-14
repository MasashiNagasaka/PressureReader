# Tasklist: Excel出力セルの緑・黄・赤カラースケール

- [x] 要件確認（`docs/ideas/20260914-excel-output-green-yellow-red-colorscale-spec.md`）
- [x] `save_brightness_to_xlsx` に3色カラースケール条件付き書式を追加
- [x] `ColorScaleRule` の import を追加
- [x] 対象範囲を `A1` から最終セルまで自動算出して適用
- [x] 既存のセル出力・セル寸法・ズーム・保存処理に影響がないことをコード確認
- [x] `C:\nagasaka\python\testPressR\Scripts\python.exe -m py_compile src/PressureReader.py` を実行
- [ ] ユーザー手動確認（Excelで緑・黄・赤カラースケール表示確認）

## 申し送り
- `999` / `-999` も出力全体に含めて評価されるため、分布端の色に寄る場合がある。
