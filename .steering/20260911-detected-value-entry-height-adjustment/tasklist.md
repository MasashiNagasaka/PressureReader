# Tasklist: 検出値ラベル修正 + 表示欄縦幅微調整

- [x] 仕様確認（`docs/ideas/20260911-detected-value-entry-height-adjustment-spec.md`）
- [x] セクションラベルを `選択範囲の検出値：` に変更
- [x] 項目ラベルを `検出値（平均）` / `検出値（最大）` / `検出値（最小）` に変更（コロン除去）
- [x] 検出値3項目を `ttk.Entry` から `tk.Entry` へ切替（高さ調整のため）
- [x] 検出値3項目Entryのフォントを小さめに調整
- [x] 構文チェック（`C:\nagasaka\python\testPressR\Scripts\python.exe -m py_compile src/PressureReader.py`）
- [x] 文字化けチェック（仕様書・コード）
