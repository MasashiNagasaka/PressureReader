# Design: スケーリング未設定メッセージ文言更新

## 対象
- `src/PressureReader.py`

## 設計方針
- ロジックには触れず、対象メッセージ文字列のみ置換する。

## 変更内容
- `save_brightness_to_xlsx()` の `except (ValueError, TypeError):` 節で表示する文字列を更新。

## 影響範囲
- Excel出力ボタン押下時のスケーリング未設定メッセージ表示のみ。
