# Design: 起動時スプラッシュとメイン初期表示の最前面化

## 実装方針
- 最前面化処理を関数化し、スプラッシュ1/2とメイン画面初期表示で再利用する。
- スプラッシュ1/2は表示中ずっと最前面にする。
- メイン画面は一時的に最前面化し、短時間後に解除する。

## 変更点
1. `set_window_topmost(window)` を追加
   - `attributes("-topmost", True)` + `lift()` + `focus_force()`
2. `set_window_topmost_temporarily(window, duration_ms)` を追加
   - 最前面化後、`after` で `-topmost` を解除
3. スプラッシュ1
   - 位置確定後に `set_window_topmost(root)` を呼び出し
4. スプラッシュ2
   - `geometry` 設定後に `set_window_topmost(info_root)` を呼び出し
5. メイン画面
   - `root = tk.Tk()` 直後に `set_window_topmost_temporarily(root, 1200)` を呼び出し

## 影響範囲
- `src/PressureReader.py`
