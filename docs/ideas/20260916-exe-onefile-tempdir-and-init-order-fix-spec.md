# exe(onefile)起動時エラー対策 仕様書

> 作成日: 2026-09-16
> ステータス: Draft
> 想定コマンド: `/add-feature`

---

## 1. 背景

`python PressureReader.py` では問題ないが、`PressureReader.exe` / `PressureReader_debug.exe` 実行時のみ以下が発生する。

- `sheet setting csv not found: ... _pressure_tmp\\_MEI...\\config\\sheet_setting.csv`
- `NameError: name 'all_entries' is not defined`

---

## 2. 原因

### 2.1 onefile展開先と一時フォルダ削除の競合

- onefile実行時は、exe内リソースが `_pressure_tmp\\_MEIxxxxxx` に展開される。
- `sheet_setting.csv` もこの展開先から読み込まれる。
- 起動初期に `_pressure_tmp` を再帰削除すると、実行中の `_MEIxxxxxx` 配下まで消してしまい、CSVが見つからなくなる。

### 2.2 UI初期化順と trace コールバック発火順の競合

- `selected_var.trace("w", update_entries_and_buttons)` が `all_entries` 定義前に有効化されると、
  先にコールバックが走った場合に `NameError` が起きる。
- この順序依存は exe 起動時に顕在化しやすい。

---

## 3. 対策方針

1. exe(onefile)実行中 (`sys.frozen == True`) は、`cleanup_temp_pngs()` で `_pressure_tmp` を再帰削除しない。
2. `_pressure_tmp` の削除は終了後処理 (`schedule_cleanup_tmp_dir_after_exit`) に集約する。
3. `selected_var.trace(...)` は `all_entries` / `all_buttons` 定義後に登録する。
4. `update_entries_and_buttons()` に未初期化ガードを追加する。

---

## 4. 仕様詳細

### 4.1 起動時クリーンアップ

- 開発実行 (`python PressureReader.py`) では従来どおり `_pressure_tmp` の整理を許可する。
- exe実行時は、起動中に `_pressure_tmp` 再帰削除を行わない。

### 4.2 終了時クリーンアップ

- 終了時は `on_app_close -> schedule_cleanup_tmp_dir_after_exit` で後段削除する。
- 実行中ファイルロック回避のため、別プロセスの短時間リトライ削除を維持する。

### 4.3 UI初期化順

- `all_entries` / `all_buttons` 未定義の間は `update_entries_and_buttons()` を即 return する。
- `selected_var.trace("w", update_entries_and_buttons)` は配列定義後に移動する。

---

## 5. 非対象

- `sheet_setting.csv` のフォーマット変更
- CSV読込ロジック (`load_sheet_setting_config`) のパース仕様変更
- 圧力換算ロジック (`c2p`) の計算仕様変更

---

## 6. 受け入れ条件

- [ ] `PressureReader.exe` 起動直後に `sheet setting csv not found` が発生しない。
- [ ] `PressureReader_debug.exe` 起動直後に `NameError: all_entries` が発生しない。
- [ ] PNG読込後も同エラーが再発しない。
- [ ] アプリ終了後、`_pressure_tmp` は最終的に削除される（即時でなくても可）。
- [ ] `python PressureReader.py` の既存挙動に退行がない。

---

## 7. 確認ポイント

- 実行場所: `C:\\nagasaka\\kanatsu\\PressureReader_v3.5.0`
- 対象exe:
  - `PressureReader.exe`
  - `PressureReader_debug.exe`

