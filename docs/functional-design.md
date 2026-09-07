---
last_updated: 2026-09-07
git_commit: ""
status: draft
---

# 機能設計書 (Functional Design Document)

## システム構成図
- デスクトップ単体アプリ（Python/Tkinter）
- 主要I/O:
  - 入力: PNG, PDF
  - 出力: PNG（メタ保存）, XLSX
  - 補助: `pr_images`（UI画像）, `poppler`（PDF変換）

## 技術スタック
- GUI: Tkinter / ttk
- 画像処理: Pillow, OpenCV, NumPy
- 補間: SciPy (`interp1d`)
- Excel出力: openpyxl
- PDF変換: pdf2image + poppler

## データモデル定義
### エンティティ: 解析条件
- `sheet_type`: シート種別（15種）
- `brightness_refs`: 色見本入力値（0.1〜1.5の一部）
- `ondo`: 温度
- `shitsudo`: 湿度
- `pixmm`: mm/px換算値

### メタデータ形式
- PNG `info` キーに `press{...}` 形式で17項目を保存

## コンポーネント設計
### 1. 画像入出力
- `load_image`: PNG読込・メタ復元
- `meta`: 解析条件のPNG保存
- `metaコピ`: 解析条件の複製

### 2. 解析エンジン
- `c2p`: 輝度→圧力換算
- `calculate_brightness*`: 範囲別（矩形/多角形/円）平均計算

### 3. UIイベント
- `on_mouse_down/drag/up/right_click`
- `set_mode_rect/polygon/circle`
- `clear_selectarea`（v3.5.0で起動直後状態への復帰を担当）

### 4. 出力
- `save_brightness_to_xlsx`
- `pdf_to_png`

## ユースケース図
### UC-01: 解析実行
1. PNGを開く
2. 解析条件入力またはメタ復元
3. 範囲選択
4. 結果確認
5. 必要に応じて保存（PNG/XLSX）

### UC-02: 作業やり直し（v3.5.0）
1. `画面リセット`押下
2. 選択範囲・補助表示・結果表示をクリア
3. 解析条件（明度・温湿度・スケーリング）を初期化
4. プレスケール種別を`LLW 持続圧`へ戻す
5. 測定範囲可視化をOFFへ戻す
6. 画像未選択状態へ戻す
7. 矩形モードで再測定開始

## 画面遷移図(該当する場合)
- 単画面アプリのため画面遷移はなし（同一画面上で状態遷移）

## API設計(該当する場合)
- 外部APIなし

## UI設計（該当する場合)
- 左: 画像キャンバス
- 右: 設定・操作パネル（縦スクロール）
- v3.5.0追加:
  - ボタン名: `画面リセット`
  - 表示: アイコン＋テキスト
  - 位置: 右パネル最下段
  - アイコン: `src/pr_images/reset_window.png`

## ファイル構造（該当する場合）
- 主体: `src/PressReader_v3.5.0.py`（改名後）
- 画像資材: `src/pr_images/`
- PDF変換依存: `src/poppler/`

## エラーハンドリング
- 未読込時操作: ガード関数で抑止
- クリア処理: 例外を出さず冪等に実行
- ファイル選択キャンセル: 安全に処理復帰
- 解析条件が空欄でもリセットで`float()`例外を発生させない

## テスト戦略
### ユニットテスト
- 将来の責務分離後に換算ロジック単体化を検討

### 統合テスト
- 主要導線: 読込→選択→表示→保存

### E2Eテスト
- GUI手動確認を標準
- 画面リセットの各モード回帰（矩形/多角形/円）
- 画面リセット後の初期化回帰（明度/温湿度/pixmm、プレスケール、可視化OFF、画像未選択）
