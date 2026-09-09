# 標準色見本処理の誤発火防止 仕様書

> 作成日: 2026-09-09
> ステータス: Draft
> 用途: `/add-feature` 実装入力

---

## 1. 背景・目的

現状、標準色見本処理ボタン押下後に、矩形選択（ドラッグ）前なのに
明度が自動入力されるケースがある。

その後の通常モード復帰は動くようになったが、そもそも採色トリガーが早すぎるため、
意図しない明度設定につながる。

目的は、**「実際にドラッグ選択したときだけ」標準色見本採色が実行されるようにする**こと。

---

## 2. 原因仮説

- `set_mode_rect("14")` 実行時に `rect_selected=True` になっている。
- `root` の `<ButtonRelease-1>` フォールバックが、ボタン押下直後のリリースを拾う。
- その結果、`on_global_mouse_up` → `on_mouse_up` が走り、過去の `start_x/start_y` などを使って
  `calculate_brightness(..., "14")` が実行される可能性がある。

---

## 3. スコープ

### 3.1 実施すること
- 標準色見本採色の開始条件を厳格化し、誤発火を防止する。
- 既存の「明度確定後に通常モード遷移」仕様は維持する。

### 3.2 実施しないこと
- 採色アルゴリズムそのものの変更。
- 多角形/円モードの仕様変更。

---

## 4. 仕様（主案）

### 4.1 明示的な「ドラッグ開始」フラグ導入
- [ ] `swatch_drag_started`（仮名）を追加。
- [ ] `set_mode_rect("14")` 直後は `swatch_drag_started=False`。
- [ ] `on_mouse_down` で `mode=="rect" and current_value=="14"` の時のみ `True` にする。

### 4.2 on_mouse_up 実行条件の厳格化
- [ ] `current_value=="14"` で採色処理に進む条件を以下に限定:
- [ ] `swatch_drag_started == True`
- [ ] `start_x/start_y` が有効（`None` でない）
- [ ] 矩形サイズが最小閾値以上（例: 幅・高さとも2px以上）
- [ ] 条件不成立時は `calculate_brightness(..., "14")` を呼ばない

### 4.3 root側フォールバックのガード強化
- [ ] `on_global_mouse_up` でも `swatch_drag_started==True` を必須条件にする。
- [ ] 標準色見本ボタン押下直後の最初の `ButtonRelease` は無視する
      （`ignore_next_global_release` フラグ等で1回スキップ）。

### 4.4 状態初期化
- [ ] `set_mode_rect("14")` 遷移時に `start_x/start_y/end_x/end_y` を `None` に初期化。
- [ ] `finalize_standard_swatch_selection()` 完了時にも `swatch_drag_started=False` へ戻す。

---

## 5. 受け入れ条件

- [ ] 標準色見本処理ボタン押下だけでは明度が変化しない。
- [ ] 実際にドラッグ選択した時のみ明度が設定される。
- [ ] 明度設定後は通常モードへ自動復帰する。
- [ ] 連続操作しても誤発火しない。

---

## 6. 他の改善策

### 案B: set_mode_rect の初期値見直しのみ
- 内容: `set_mode_rect` で `rect_selected=False` にし、`on_mouse_down` でのみ `True` 化
- 長所: 変更が小さい
- 短所: 既存ロジック依存箇所への影響確認が必要

### 案C: rootのButtonRelease補完を標準色見本時のみ一時停止
- 内容: `current_value=="14"` でボタン押下直後だけ `on_global_mouse_up` を抑止
- 長所: 問題箇所へピンポイント
- 短所: 取りこぼし対策とのトレードオフがある

---

## 7. 実装メモ（/add-feature 引き継ぎ）

### 7.1 変更対象（想定）
- `src/PressureReader.py`

### 7.2 変更ポイント（想定）
- `set_mode_rect`
- `on_mouse_down`
- `on_mouse_up`
- `on_global_mouse_up`
- `finalize_standard_swatch_selection`

---

## 8. テスト観点

- ボタン押下のみ: 明度未変更
- ドラッグあり: 明度更新 + 通常モード復帰
- キャンバス外リリース: 復帰はするが誤採色しない
- 連続実行: 2回以上連続で誤発火なし
