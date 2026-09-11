# Design: 検出値表示欄の枠線除去と右端重なり解消

## 対象
- `src/PressureReader.py`

## 設計方針
- 変更は検出値表示エリア（`detected_value_frame`）に限定する。
- Entryウィジェットを枠線なしに設定し、フォーカス時強調枠も無効化する。
- 右端余白は `detected_value_frame` および `MPa` ラベルの `padx` で調整し、スクロールバー有無で崩れない見え方にする。

## 変更内容
- `detected_value_frame.grid(..., padx=(11,12), ...)` へ変更し、右余白を追加。
- 3つの `tk.Entry` に以下を適用:
  - `relief="flat"`
  - `bd=0`
  - `highlightthickness=0`
  - `highlightbackground="#ffffff"`
  - `highlightcolor="#ffffff"`
- 3つの `MPa` ラベルの右 `padx` を追加して詰まり感を緩和。

## 影響評価
- 見た目のみ変更。
- Entry参照名や値更新処理は変更しないため、ロジック影響はない。
