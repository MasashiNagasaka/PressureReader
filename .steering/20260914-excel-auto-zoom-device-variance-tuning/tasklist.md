# Tasklist: Excel自動ズームの実機差調整しやすさ向上

- [x] 要件確認（`docs/ideas/20260914-excel-auto-zoom-fit-output-range-spec.md`）
- [x] ズーム算出処理を関数化
- [x] 調整パラメータを関数内へ集約（実効表示領域・補正係数・クランプ）
- [x] 既存ズーム値方針を維持することをコード確認
- [x] `C:\nagasaka\python\testPressR\Scripts\python.exe -m py_compile src/PressureReader.py` を実行
- [ ] ユーザー手動確認（見え方差への調整容易性）

## 申し送り
- 実機差があるため、将来は `zoom_bias` と `min_zoom` の運用値見直しが最も効果的。
