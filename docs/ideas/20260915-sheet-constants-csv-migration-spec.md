# 感圧紙定数のCSV外部化 仕様書（regionブロック配列版）

> 作成日: 2026-09-15  
> ステータス: Draft  
> 想定コマンド: `/add-feature`

---

## 1. 背景・目的
- `src/PressureReader.py` の感圧紙ごとの定数をCSVへ移し、保守性を上げる。
- `region` ごとに `Standard_Chart_x` / `Standard_Chart_y` を配列行で持つ形式にし、可読性を上げる。
- CSVは起動時に1回だけ読み込む。

---

## 2. 対象
- 感圧紙種類（例: `4LW 持続圧`）
- `after_values`（CSV上は `brightness`）
- 温湿度条件判定用 `lines`（`m`,`b`）
- 温湿度条件判定用 `regions`
- `press_Max`, `press_Min`
- 温湿度条件判定の有無フラグ（`HHS`対応）
- `Standard_Chart_x`
- `Standard_Chart_y`

---

## 3. 管理方式
- 単一CSV: `src/config/sheet_setting.csv`
- ヘッダなし、行タイプ可変フォーマット
- 起動時1回ロードし、`SHEET_CONFIG` に保持

---

## 4. CSVフォーマット（ヘッダなし）

### 4.1 基本ルール
- 1行は先頭要素で意味が決まる可変長レコード。
- 感圧紙ブロック開始は `sheet,<sheet_type>`。
- `sheet` 行以降の行は、直近の `sheet_type` に属する。
- `region` ごとに `Standard_Chart_x` / `Standard_Chart_y` をセットで持つ。

### 4.2 行タイプ定義
- `sheet,<sheet_type>`
  - 例: `sheet,4LW 持続圧`
- `condition,<press_max>,<press_min>,<temp_humidity_enabled>`
  - 例: `condition,0.2,0.05,TRUE`
- `brightness,<seq>,<after_value>`
  - 例: `brightness,0,1.0`
- `line,<seq>,<m>,<b>`
  - 例: `line,0,-0.2,77`
- `region,<region_name>`
  - 例: `region,A`
- `Standard_Chart_x,<x1>,<x2>,...,<xn>`
  - 例: `Standard_Chart_x,0.0406,0.04178,0.04295`
- `Standard_Chart_y,<y1>,<y2>,...,<yn>`
  - 例: `Standard_Chart_y,0.09484,0.09779,0.09779`

### 4.3 regionブロック構造
1つの region は次の3行を1セットとする。
- `region,<name>`
- `Standard_Chart_x,...`
- `Standard_Chart_y,...`

例:
- `region,A`
- `Standard_Chart_x,0.0406,0.04178,0.04295`
- `Standard_Chart_y,0.09484,0.09779,0.09779`

---

## 5. fallbackの扱い
- fallback専用行は持たない。
- 既存コード同様、fallback は `region = regions[-1]`。
- そのため `region` 行は順序付きで保持する（最後がfallback）。

---

## 6. 実装方針
- `load_sheet_config_from_csv()` を追加。
- 行タイプごとにパースして `SHEET_CONFIG` を構築。
- `sheet` 行が出るまでのデータ行はエラー。
- `region` 行の直後に `Standard_Chart_x`、次行に `Standard_Chart_y` が来ることを前提に読み込む。
- `c2p` は `SHEET_CONFIG` 参照へ置換。
- `temp_humidity_enabled == TRUE` のときのみ `lines/regions` 判定を実施。

---

## 7. バリデーション
- 各ブロック先頭は `sheet` 行
- 各 `sheet_type` で `condition` は1件
- `temp_humidity_enabled` は `TRUE/FALSE`（`True/False`、`true/false` も許容）
- `brightness` の `seq` は連番（0..n-1）
- `line` の `seq` は連番（0..n-1）
- `region` は1件以上
- `temp_humidity_enabled == TRUE` の場合
  - `line` 件数 + 1 == `region` 件数
- 各 `region` で:
  - `Standard_Chart_x` 行と `Standard_Chart_y` 行が必須
  - x要素数 == y要素数
  - x/y要素はすべて数値
- 数値変換エラー時は起動時エラーとして停止

---

## 8. 比較監査（必須）
- 比較元:
  - `bkup/PressureReader_260915_00.py`
  - `src/config/sheet_setting.csv`
- 比較対象:
  - `sheet_type`
  - `after_values`
  - `lines(m,b)`
  - `regions`
  - `press_Max`, `press_Min`
  - `temp_humidity_enabled`
  - `Standard_Chart_x`
  - `Standard_Chart_y`
- 結果:
  - `outputs/sheet_constants_csv_audit_YYYYMMDD_HHMMSS.xlsx`
  - シート: `summary`, `legacy_extracted`, `csv_loaded`, `diff`
- 受入条件:
  - `diff` が0件

---

## 9. 対象感圧紙（15種）
- 4LW 持続圧
- 4LW 瞬間圧
- 5LW 持続圧
- 5LW 瞬間圧
- LW 持続圧
- LW 瞬間圧
- 3LW 持続圧
- 3LW 瞬間圧
- MS 持続圧
- MS 瞬間圧
- HS 持続圧
- HS 瞬間圧
- LLW 持続圧
- LLW 瞬間圧
- HHS（`temp_humidity_enabled=FALSE`）
