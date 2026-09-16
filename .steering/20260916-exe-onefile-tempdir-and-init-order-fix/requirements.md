# Requirements

## Goal
- `PressureReader.exe` / `PressureReader_debug.exe` 実行時のみ発生する起動エラーを解消する。

## Functional Requirements
- exe(onefile)実行中、起動時クリーンアップで実行中の `_pressure_tmp\_MEIxxxxxx` を削除しないこと。
- `sheet_setting.csv` が exe 起動後も読めること。
- `selected_var` の trace コールバックで `all_entries` 未定義エラーが発生しないこと。

## Non-Functional Requirements
- `python PressureReader.py` の既存挙動を変えないこと。
- 変更範囲は最小にすること。

