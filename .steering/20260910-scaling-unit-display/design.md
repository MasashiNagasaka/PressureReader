# Design

## Approach
- `button_pixmm` の grid は維持する。
- `pixmm_entry` の `width` と `grid` の `columnspan/padx` を調整する。
- 同じ row に `mm/px` ラベルを追加する。

## Impact
- 変更対象は `src/PressureReader.py` のスケーリング行UI定義のみ。
- 既存の値保存・計算・表示更新ロジックへの影響なし。
