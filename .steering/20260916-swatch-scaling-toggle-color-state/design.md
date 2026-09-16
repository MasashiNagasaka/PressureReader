# Design: 標準色見本・スケーリングの色トグル化

## 実装方針
- ON色は `#9BFD9B` を共通利用する。
- OSテーマ依存を避けるため、対象2ボタンは `tk.Button` を使用し、`bg/activebackground` で色制御する。

## 変更点
1. 標準色見本処理
   - `：ON / ：OFF` 表示を廃止し、テキスト固定化
   - `swatch_toggle_on` の状態に応じて背景色を切替
2. スケーリング
   - `scaling_toggle_on` を追加
   - 同一ボタン押下で ON/OFF 切替
   - ON中は線分入力イベントをバインド、OFFで通常イベントへ復帰
   - 完了/キャンセル/モード変更時にOFF復帰

## 影響範囲
- `src/PressureReader.py`
