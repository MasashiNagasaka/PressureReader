# Design: 範囲選択トグル追加と状態明確化

## 実装方針
- 既存の範囲選択セクションにトグル `範囲選択` を追加し、ラジオ表示を制御する。
- 既存モード関数のクリア処理をオプション化し、ON復帰時の図形保持を実現する。
- 新規図形作成開始時のみ旧図形をクリアする。

## 主要変更
1. ステータスバー
- `update_mode_status_bar()` で `range_select_toggle_on` を参照
- 範囲選択文言を `モード：範囲選択` に統一
- `range_select_toggle_on=False` の場合、範囲選択文言は出さない

2. 範囲選択UI
- ラベル: `③範囲選択：`
- 追加: `range_select_toggle_on = tk.BooleanVar(value=False)`
- 追加: `button_range_select`（ON/OFF色切替）
- 追加: `apply_range_select_visibility()` でラジオ3種の表示/非表示を制御

3. モード切替の保持制御
- `set_mode_rect(value, clear_shapes=True)`
- `set_mode_polygon(clear_shapes=True)`
- `set_mode_circle(clear_shapes=True)`
- ラジオ選択時は `select_*_mode_from_ui()` を経由し、
  `range_select_toggle_on` かつ図形ありの場合は `clear_shapes=False` で切替

4. 新規作成時の旧図形クリア
- `has_existing_selection_shape()` 追加
- `clear_selection_shapes_only()` 追加
- `on_mouse_down` で新規作成開始時（rect常時、polygon初回、circle初回）に旧図形をクリア
- `range_select_toggle_on=False` では新規作成を抑止し、既存図形編集のみ許可

## レイアウト
- トグル追加に伴い、右ペインの行番号を+1調整（範囲選択以降）
- 他セクションとの重なりを回避
