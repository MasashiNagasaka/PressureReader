# Tasklist

- [x] `load_sheet_setting_config()` のCSV読み込みを `utf-8-sig` 優先 + `cp932` フォールバックに対応
- [x] 起動時1回ロード（失敗時はエラー保持）
- [x] `c2p()` へCSV優先経路を追加
- [x] CSV経路の例外時は警告1回＋`-9999` 返却へ変更（内蔵設定フォールバック削除）
- [x] `c2p()` の旧ハードコード分岐（全感圧紙）を削除しCSV必須化
- [x] 構文チェック実施
  - `C:\nagasaka\python\testPressR\Scripts\python.exe -m py_compile src/PressureReader.py`
