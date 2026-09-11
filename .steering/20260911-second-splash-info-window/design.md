# Design: 起動時スプラッシュ2（info案内ウィンドウ）追加

## 対象
- `src/PressureReader.py`

## 設計方針
- 既存スプラッシュ1を維持し、直後に専用案内ウィンドウを追加する。
- `messagebox.showinfo` はフォント制御が困難なため、`Tk()` + `Label` で案内ウィンドウを構成する。

## 変更内容
- `show_startup_info_window()` を追加。
  - タイトル: `Information`
  - 本文: 指定の4行メッセージ
  - フォント: `("Meiryo ui", 14)`（boldなし）
  - 8秒後に自動クローズ: `after(8000, destroy)`
- 既存スプラッシュ1の `mainloop()` 後に `show_startup_info_window()` を呼ぶ。

## 影響範囲
- 起動シーケンス表示のみ。
- メイン画面機能ロジックには影響しない。
