# Design: 多角形最上頂点のテキスト接触防止チューニング

## 実装方針
- `show_polygon_point_pressure_text(...)` のみを最小差分で修正する。
- 既存の候補位置評価後に、対象頂点ハンドルBBoxを使ってラベル左端の下限を補正する。

## 変更内容
- 追加ロジック:
  - `min_text_left = handle_bbox[2] + 2px` を計算
  - `text_x < min_text_left` の場合、`text_x = min_text_left` に補正
  - 補正後に右端はみ出しをクランプ

## 影響範囲
- 多角形モードの各頂点点圧ラベル位置のみ。
- 圧力値算出、既存タグ運用、他モード表示には影響なし。
