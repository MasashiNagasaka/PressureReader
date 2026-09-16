# Design: PDF→PNG変換して開く 文言更新

## 変更方針
- UIテキストのみを最小差分で変更する。
- 既存のイベント・コマンドバインドは変更しない。

## 実装ポイント
1. `button_p2p` の `text` を `PDF→PNG変換して開く` へ変更。
2. `no_image()` の表示文言を新しいボタン名に合わせて更新。
3. `button_p2p` の `padding` を調整し、長い文言でも崩れない見た目にする。

## 影響範囲
- `src/PressureReader.py` のみ。
