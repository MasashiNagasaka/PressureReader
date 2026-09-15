# Design

## Data Source
- CSV path: `src/config/sheet_setting.csv`
- record types:
  - `sheet`
  - `condition`
  - `brightness`
  - `line`
  - `region`
  - `Standard_Chart_x`
  - `Standard_Chart_y`

## Loader
- `load_sheet_setting_config()` でCSVを読み込み、内部辞書へ正規化する。
- 正規化後の要素:
  - `press_max`, `press_min`
  - `temp_humidity_enabled`
  - `brightness` (seq順)
  - `lines` (seq順, `(m, b)`)
  - `regions`
  - `charts` (`region` or `_DEFAULT_`)
- バリデーション:
  - 必須項目
  - seq連続性
  - line/region件数整合
  - chart x/y件数整合

## Runtime Integration
- 起動時に1回だけ `load_sheet_setting_config()` を実行。
- `c2p()` の先頭で、選択中感圧紙がCSV設定に存在すればCSV計算経路へ入る。
- CSV計算経路で例外が出た場合:
  - 警告を1回表示
  - `-9999` を返す
- 選択中感圧紙がCSV未定義の場合:
  - 警告を1回表示
  - `-9999` を返す

## Compatibility
- 既存 `c2p()` 本体（各感圧紙のハードコード分岐）は削除し、CSV必須運用に統一する。
