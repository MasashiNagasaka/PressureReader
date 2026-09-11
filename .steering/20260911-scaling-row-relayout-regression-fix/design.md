# Design: スケーリング行の局所レイアウト化

## 対象
- `src/PressureReader.py`

## 設計方針
- row=17 の `button_pixmm` は既存と同じ `button_frame` のグリッドに配置する。
- `pixmm_entry` と `mm/px` だけを小フレーム `pixmm_unit_frame` に入れ、同一セル内で横並び固定する。
- `pixmm_unit_frame` は `column=2` の単一カラムに置き、`columnspan` を広げない。
- これにより、色見本/温湿度が使う列幅計算への副作用を抑える。

## 変更内容
- `pixmm_unit_frame` を `row=17, column=2, columnspan=1` に追加。
- `pixmm_entry` を `pixmm_unit_frame` 配下へ移動し `width=10` を維持。
- `label_pixmm_unit` を `pixmm_entry` 直右 (`padx=(1,0)`) に配置。

## 影響範囲
- UI レイアウトのみ。
- `pixmm_entry` 変数名は維持するため、既存ロジック参照への影響はない。
