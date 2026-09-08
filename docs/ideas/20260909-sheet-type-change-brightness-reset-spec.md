# 感圧紙種類変更時の明度リセット 仕様書

> 作成日: 2026-09-09
> ステータス: Draft
> 用途: `/add-feature` での実装入力

---

## 1. 背景・目的

現状では、感圧紙の選択（`selected_var`）を変更した際に、
表示される明度入力欄（Entry）の切替は行われるが、明度値そのものは保持される。

そのため、種類変更前の設定が残って誤操作につながる可能性がある。

目的は、**感圧紙の種類を手動変更したときに、明度の表示と設定を初期化（リセット）する**こと。

---

## 2. スコープ

### 2.1 実施すること
- 感圧紙の選択リスト（OptionMenu）で種類変更した際、明度設定をリセットする。
- リセット後のUI表示は、変更後の種類に対応した入力欄のみ表示する。
- リセット時にしきい値表示（平均圧表示）も初期化する。

### 2.2 実施しないこと
- 解析ロジック（圧力計算式）の変更。
- 温度・湿度・pix/mm など、明度以外の設定変更。

---

## 3. 現状整理

- `selected_var.trace("w", update_entries_and_buttons)` で種類変更を監視している。
- `update_entries_and_buttons()` は Entry/Button の表示切替のみを実施している。
- `selected_var.set(...)` は手動変更だけでなく、画像メタ読込処理（`load_image`）内でも呼ばれる。

このため、単純に trace 内で値クリアすると、**メタ読込時の復元値まで消える**副作用がある。

---

## 4. 仕様

### 4.1 リセット対象（手動変更時）
- [ ] 明度Entry（`brightness_entry_15` ～ `brightness_entry_01`）を全クリア。
- [ ] 平均圧表示（`atai_ave_entry`）をクリア。
- [ ] 変更後の種類に応じた明度Entry/Buttonのみ表示。

### 4.2 リセット対象外
- [ ] `ondo_entry`（温度）
- [ ] `shitsudo_entry`（湿度）
- [ ] `pixmm_entry`（スケーリング）
- [ ] 画像そのもの・選択領域

### 4.3 トリガー条件
- [ ] OptionMenuからの**手動種類変更**時のみリセットを実行。
- [ ] `load_image` のメタ読込で `selected_var.set(...)` する経路ではリセットを抑止。

### 4.4 実装方式（推奨）
- [ ] `suppress_sheet_type_reset`（仮名）フラグを導入。
- [ ] メタ読込時は `suppress_sheet_type_reset = True` の間に `selected_var.set(...)` を実行し、完了後 False に戻す。
- [ ] `update_entries_and_buttons()` 冒頭でフラグを判定し、False のときのみ明度クリアを行う。

---

## 5. 品質要件

- 一貫性: 種類変更後に旧種類の明度値が残らないこと。
- 安全性: メタ読込時の復元値が意図せず消えないこと。
- 可用性: 種類変更で例外が発生せず従来操作を阻害しないこと。

---

## 6. 実装メモ（/add-feature 引き継ぎ）

### 6.1 変更対象（想定）
- `src/PressureReader.py`

### 6.2 主な変更ポイント
- `selected_var` 変更時ハンドラ（`update_entries_and_buttons`）
- `load_image` 内のメタ読込時 `selected_var.set(...)` 周辺
- 必要に応じて初期化用ヘルパー関数の追加

---

## 7. 受け入れ条件

- [ ] OptionMenuで種類を手動変更すると、明度Entryがクリアされる。
- [ ] 種類変更後、表示される明度欄は対象種類のものだけになる。
- [ ] `atai_ave_entry` がクリアされる。
- [ ] PNGメタ読込で種類・明度を復元した際、復元値が消えない。
- [ ] 温度・湿度・pix/mm は種類変更のみでは変更されない。

---

## 8. 参照

- `src/PressureReader.py` の `update_entries_and_buttons`
- `src/PressureReader.py` の `selected_var.trace("w", ...)`
- `src/PressureReader.py` の `load_image`（メタ読込での `selected_var.set(...)`）
