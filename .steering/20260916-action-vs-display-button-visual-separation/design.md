# Design: 操作ボタンと表示項目の視覚分離

## 実装方針
- `src/PressureReader.py` の明度行 `button_mihon_*` を `ttk.Button` から `ttk.Label` へ変更する。
- 表示専用の `BrightnessValue.TLabel` スタイルを追加し、操作ボタンと見た目を分離する。
- 既存の変数名・表示切替ロジック（`all_buttons`, `brightness_slots`, `update_entries_and_buttons`）は維持し、回帰リスクを抑える。

## 変更ポイント
1. `ttk.Style` に `BrightnessValue.TLabel` を追加。
2. `button_mihon_15`〜`button_mihon_01` を `ttk.Label(... style=\"BrightnessValue.TLabel\")` へ置換。
3. コメント文言を「ボタン」から「表示ラベル」へ更新。

## レイアウト考慮
- 既存の `grid(row=7+i, column=0, ...)` を維持する。
- 幅 (`width=7`) と中央寄せ (`anchor=\"center\"`) を指定し、見た目の並びを保持する。
