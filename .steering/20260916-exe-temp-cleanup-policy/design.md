# Design

## Approach
- `cleanup_old_mei_dirs_on_startup()` を追加する。
  - exe実行時のみ有効 (`sys.frozen`)。
  - `_pressure_tmp` 直下の `_MEI...` ディレクトリを走査。
  - `RESOURCE_dir` が示す「現在実行中 `_MEI...`」は除外。
  - それ以外の古い `_MEI...` のみ削除。
- 既存の `cleanup_temp_pngs()` は維持。
  - exe実行時は再帰削除を行わず、終了後処理へ委譲する既存設計を維持。

## Safety
- `is_path_in_dir()` で `_pressure_tmp` 配下判定を行う。
- `entry.is_dir(follow_symlinks=False)` でシンボリックリンク追従を回避。
- 削除失敗時は警告ログのみ出して処理継続。

## Compatibility
- `python PressureReader.py` では新関数は早期 return するため従来挙動を維持。

