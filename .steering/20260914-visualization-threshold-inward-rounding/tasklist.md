# Tasklist: 可視化しきい値の境界安定化

- [x] 仕様書を `docs/ideas/20260914-visualization-threshold-inward-rounding-spec.md` に反映
- [x] `swatch_brightness_bounds` を追加し、色見本ごとの境界値を保持
- [x] 色見本表示処理を「`filtered` 平均表示 + `filtered` min/max保持」に拡張
- [x] `apply_threshold` に `threshold_margin = 1` を適用
- [x] 1.0側 min / 0.1側 max で端点クランプを実装（いずれも `filtered` ベース）
- [x] `low_threshold/high_threshold` と `mask_low/mask_high` のデバッグログを追加
- [x] `C:\nagasaka\python\testPressR\Scripts\python.exe -m py_compile src/PressureReader.py` で構文確認
- [x] `region_values` 全画素 min/max を使う案は採用せず、`filtered` ベースに戻した
