# Design

## Approach
- `c2p()` 内に入力不足専用の例外（`BrightnessInputError`）を追加する。
- `brightness` 入力値が空文字の場合は `ValueError` ではなく `BrightnessInputError` を送出する。
- 例外処理順序を以下にする:
  1. `except BrightnessInputError`  
     - CSV警告を出さずに `-9999` を返す
  2. `except Exception`  
     - 現行のCSV設定エラー警告を表示し `-9999` を返す

## Compatibility
- CSV必須化方針は維持する。
- `sheet_setting_error_shown` の1回警告制御はCSVエラー経路でのみ利用する。
