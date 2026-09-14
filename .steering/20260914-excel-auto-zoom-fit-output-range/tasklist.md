# Tasklist: Excel出力時の自動ズーム調整

- [x] 要件確認（`docs/ideas/20260914-excel-auto-zoom-fit-output-range-spec.md`）
- [x] `save_brightness_to_xlsx` のズーム算出を実測基準（100%で16行×56列）へ置き換え
- [x] `ws.sheet_view.zoomScale` 設定を追加
- [x] ズーム値を `10`〜`400` にクランプ
- [x] 余裕係数 `fit_margin=0.95` を適用し、縦横の小さい方でフィットさせる
- [x] 既存のセル出力・セル寸法設定・保存処理に影響がないことをコード確認
- [x] `C:\nagasaka\python\testPressR\Scripts\python.exe -m py_compile src/PressureReader.py` を実行
- [ ] ユーザー手動確認（小範囲/大範囲でExcel初期ズーム確認）

## 申し送り
- 実機差が残る場合は `fit_margin` を `0.95 -> 0.92` へ下げると、より全体表示寄りに調整可能。
