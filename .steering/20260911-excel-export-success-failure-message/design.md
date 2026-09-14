# Design: Excel出力の成功/失敗メッセージ表示

## 対象
- `src/PressureReader.py`
  - `save_brightness_to_xlsx()`

## 設計方針
- `wb.save(file_path)` を `try/except` で囲み、保存成功/失敗でメッセージを出し分ける。
- 既存の通知スタイル（`tk.Label` + `root.after(...destroy)`）を再利用する。

## 変更内容
- 保存成功時:
  - `Excelファイルを出力しました` を中央表示（2秒）
- 保存失敗時:
  - `Excelファイルの出力に失敗しました` を中央表示（2秒）
