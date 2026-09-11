# Design: スケーリング行レイアウト再設計

## 対象
- `src/PressureReader.py`

## 設計方針
- `button_frame` の全体グリッド列計算に依存させず、row=17 を専用フレーム化する。
- 専用フレーム内は `pack(side=LEFT)` で固定順配置し、要素間隔を明示する。

## 変更内容
- `scaling_frame = tk.Frame(button_frame)` を追加し、row=17 に `grid` 配置。
- `button_pixmm`, `pixmm_entry`, `label_pixmm_unit` を `scaling_frame` 配下へ移動。
- `pixmm_entry` を `width=10` に戻し、長めの係数値表示を確保。
- `mm/px` ラベルを `pixmm_entry` 直右（`padx=(1,0)`）へ配置。

## 影響評価
- UIレイアウトのみ変更。
- 既存変数名は維持しているため、後続ロジック参照への影響なし。
