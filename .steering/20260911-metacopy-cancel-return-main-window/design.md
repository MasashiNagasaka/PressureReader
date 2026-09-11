# Design: 解析条件コピー CANCEL時のメイン復帰

## 対象
- `src/PressureReader.py` の `metaコピ()`

## 設計方針
- `exit()` を使わず、`return` で処理を終了する。
- キャンセルはユーザー操作として静かに中断する。
- メタデータ読取失敗時のみ `messagebox.showwarning` を表示する。

## 変更内容
- `if not src_path:` の分岐を `return` に変更。
- `if not target_paths:` の分岐を `return` に変更。
- `src_img.info` が不正な場合は警告を出し `return` に変更。
