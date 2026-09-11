# Design: Excel出力前スケーリング必須化（押下時メッセージ）

## 対象
- `src/PressureReader.py`

## 設計方針
- `save_brightness_to_xlsx()` の先頭でガードし、以降の出力処理へ進ませない。
- 既存UIメッセージ表示（中央ピンクラベル）に合わせた案内表示にする。

## 変更内容
- `pixmm_entry.get().strip()` を `float` 変換して検証。
- 条件:
  - 空欄
  - 数値変換不可
  - 0以下
  の場合に `スケーリングを設定してください` を表示して `return`。
- 既存の `conversion_factor=0` フォールバックは削除。
- 有効値時のみ `initialfile` の `conversion_factor` に反映。

## 影響評価
- Excel出力前の入力バリデーションのみ変更。
- 検出値算出・出力データ作成ロジック自体は不変。
