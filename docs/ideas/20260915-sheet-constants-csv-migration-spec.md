# 感圧紙定数のCSV外部化 仕様書（CSV必須・旧フォールバック削除版）

> 作成日: 2026-09-15  
> ステータス: Revised  
> 想定コマンド: `/add-feature`

---

## 1. 背景・目的
- `src/PressureReader.py` の感圧紙ごとの定数をCSVへ移し、保守性を上げる。
- `region` ごとに `Standard_Chart_x` / `Standard_Chart_y` を配列行で持つ形式にし、可読性を上げる。
- CSVは起動時に1回だけ読み込む。
- `c2p()` 内の旧ハードコード分岐（感圧紙ごとの巨大 `if/elif`）を廃止し、CSV設定のみを唯一の正規データソースにする。

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
- `c2p` は `SHEET_CONFIG` 参照へ完全置換する。
- `temp_humidity_enabled == TRUE` のときのみ `lines/regions` 判定を実施。
- 旧ハードコード分岐（`if selected_var.get() == "...":` 以下の全定数定義）を削除する。

### 6.1 CSV必須化ポリシー
- `src/config/sheet_setting.csv` が存在しない、または起動時ロードに失敗した場合:
  - 警告表示後、アプリは解析機能を継続しない（起動失敗扱い）。
  - 旧ハードコードへの自動フォールバックは行わない。
- 実行中に選択中 `sheet_type` の設定が `SHEET_CONFIG` に存在しない場合:
  - その場でエラー通知し、圧力換算は失敗扱い（`-9999`）とする。
  - 旧ハードコードへは遷移しない。

### 6.2 不要コード削除対象
- `c2p()` のCSV経路 `try/except` 後に続く、感圧紙別の旧分岐ブロック一式。
- 旧分岐維持のためだけに残っているフォールバック制御。
- ただし既存仕様として維持すべき判定値（白判定、範囲外判定、戻り値規約）はCSV経路側でそのまま保持。

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
- CSV未ロード状態で `c2p()` が呼ばれるケースはエラーとして検出し、結果を返さない

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
  - 旧ハードコード削除後も、代表データで計算結果が従来CSV経路と一致

---

## 9. 受け入れ条件（CSV必須化）
- [ ] `c2p()` 内に感圧紙別ハードコード（`if selected_var.get() == ...`）が残っていない
- [ ] `sheet_setting.csv` 不在時は明示エラーとなり、旧処理へフォールバックしない
- [ ] CSV読み込み失敗時に旧処理へフォールバックしない
- [ ] `sheet_setting.csv` が正常な場合、全15感圧紙で従来CSV経路と同等結果
- [ ] 既存の白判定・範囲外判定（`999`, `-999`, `-9999`）の挙動が維持される

---

## 10. 対象感圧紙（15種）
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
