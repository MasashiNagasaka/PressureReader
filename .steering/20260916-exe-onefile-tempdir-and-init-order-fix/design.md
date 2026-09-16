# Design

## Approach
- `cleanup_temp_pngs()` に exe 実行判定を追加する。
  - `sys.frozen == True` の場合は再帰削除処理をスキップする。
  - `_pressure_tmp` の最終削除は既存の終了後処理 `schedule_cleanup_tmp_dir_after_exit()` に任せる。
- `update_entries_and_buttons()` に初期化ガードを追加する。
  - `all_entries` / `all_buttons` が未定義なら即 return。
- `selected_var.trace("w", update_entries_and_buttons)` の登録位置を
  `all_entries` / `all_buttons` 定義後へ移動する。

## Impact
- 対象ファイル: `src/PressureReader.py`
- 影響機能:
  - 起動時一時フォルダクリーンアップ
  - 感圧紙種別選択UI初期化

## Compatibility
- CSVフォーマットと `c2p()` 計算仕様には変更なし。
- 開発実行 (`python PressureReader.py`) の起動フローには影響なし。

