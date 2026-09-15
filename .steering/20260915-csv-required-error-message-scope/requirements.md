# Requirements

## Goal
- 標準色見本の入力不足時に、CSV設定エラー警告を表示しない。

## Functional Requirements
- `c2p()` で `brightness XX is empty` が発生した場合は、読取失敗扱いで `-9999` を返す。
- 上記ケースでは `sheet_setting.csv の設定利用に失敗` 警告を表示しない。
- CSV読込失敗やCSV構造不整合などの実際のCSVエラー時は、既存どおり警告を表示する。

## Non-Functional Requirements
- 既存の戻り値仕様（`-9999`）を維持する。
- 文字化けを発生させない。
