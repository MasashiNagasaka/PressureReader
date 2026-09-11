# Design: PDF→PNG変換後の感圧紙種類選択ガイダンス

## 対象
- `src/PressureReader.py`

## 設計方針
- `pdf_to_png()` から `load_image()` 呼び出し時にフラグを渡し、表示タイミングを限定する。

## 変更内容
- `load_image(show_sheettype_guidance=False)` に引数追加。
- `pdf_to_png()` の自動オープン時のみ `load_image(show_sheettype_guidance=True)` を呼ぶ。
- 画像読み込みと描画成功後、フラグが真なら中央オーバーレイメッセージを8秒表示する。

## 影響範囲
- PDF→PNG変換後の自動オープン導線のみ。
- PNGを開くボタン経由の挙動は変更しない。
