# Tasklist

- [x] `load_sheet_setting_config()` のCSV読み込みを `utf-8-sig` 優先 + `cp932` フォールバックに対応
- [x] 起動時1回ロード（失敗時はエラー保持）
- [x] `c2p()` へCSV優先経路を追加
- [x] CSV経路の例外時フォールバック（内蔵設定へ復帰）を追加
- [x] 構文チェック実施
  - `C:\nagasaka\python\testPressR\Scripts\python.exe -m py_compile src/PressureReader.py`
