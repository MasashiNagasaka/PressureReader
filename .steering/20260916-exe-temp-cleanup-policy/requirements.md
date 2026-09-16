# Requirements

## Goal
- exe(onefile)実行時の `_pressure_tmp` 運用を安定化し、起動時エラーを回避する。

## Functional Requirements
- 起動中の現在実行中 `_MEI...` は削除対象にしない。
- 起動時は「現在実行中以外の古い `_MEI...`」のみ削除する。
- 終了後に `_pressure_tmp` を掃除する既存動作は維持する。

## Non-Functional Requirements
- `python PressureReader.py` の挙動を変えない。
- 削除対象は `_pressure_tmp` 配下に限定し、安全チェックを行う。

