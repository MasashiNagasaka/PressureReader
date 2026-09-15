# Requirements

## Goal
- `src/config/sheet_setting.csv` を起動時に1回読み込み、`c2p()` の圧力変換で優先利用する。

## Functional Requirements
- CSVに設定がある感圧紙は、`c2p()` でCSV設定を使って計算する。
- CSVの読み込みまたは利用に失敗した場合は、既存の内蔵ハードコード処理へフォールバックする。
- 既存の白判定・範囲外判定の戻り値仕様は維持する。

## Non-Functional Requirements
- 既存パッケージのみ使用する（追加インストールなし）。
- 文字コードゆれ対策として、CSV読み込みは `utf-8-sig` を優先し、必要時のみ `cp932` を試行する。
- 既存UI/操作フローは変更しない。
