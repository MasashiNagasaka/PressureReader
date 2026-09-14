# Design: 選択範囲Excel出力の多角形/円形対応

## 対象
- `src/PressureReader.py`
  - `save_brightness_to_xlsx()`
  - 選択判定ヘルパー（`no_selection_for_export`）

## 設計方針
- 出力前判定をモード別に分岐し、四角形以外も有効選択として扱う。
- 出力領域はモードごとに `gray_region` + `mask_region` を構築する。
  - 四角形: 矩形領域 + 全Trueマスク
  - 多角形: fillPolyマスクの外接矩形切り出し
  - 円形: ellipseマスクの外接矩形切り出し
- 変換処理は既存ロジックを維持し、`mask_region=False` は空欄出力にする。

## 影響範囲
- Excel出力処理のみ。
- 画面表示/解析計算/ファイル保存形式への仕様変更はなし。
