# PressureReader

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-0B3D91)
![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-5C3EE8?logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-Private-lightgrey)

## 概要
PressureReaderは、感圧画像（PNG）から圧力値を算出し、可視化・保存するデスクトップ解析ツールです。  
v3.5.0では「画面リセット」機能を追加予定です（Python実行直後の初期状態へ復帰）。

## 主な機能
- PNG読込と解析条件復元（メタデータ）
- 範囲選択（四角形 / 多角形 / 円）
- 圧力値表示・測定範囲可視化
- 解析条件のPNG保存 / 複製
- 選択範囲のExcel出力（xlsx）
- PDF=>PNG変換
- 画面リセット（起動直後状態への復帰）

## スクリーンショット
- 追加予定（`docs/screenshots/`）

## 技術スタック
- Python
- Tkinter/ttk
- Pillow
- OpenCV
- NumPy
- SciPy
- openpyxl
- pdf2image + poppler

## セットアップ
### 前提
- Windows環境
- Python実行環境:
  - `C:\nagasaka\python\testPressR\Scripts\python.exe`

### 実行
```powershell
C:\nagasaka\python\testPressR\Scripts\python.exe src\PressReader_v3.5.0.py
```

## 開発フロー
- 仕様策定: `docs/ideas/` にメモ作成 → `/plan-kaizen`
- 実装: `/add-feature` または `/add-feature-ui`
- 検証: `/verify` 相当の動作確認を必須実施

## ドキュメント
- PRD: `docs/product-requirements.md`
- 機能設計: `docs/functional-design.md`
- アーキテクチャ: `docs/architecture.md`
- リポジトリ構造: `docs/repository-structure.md`
- 開発ガイドライン: `docs/development-guidelines.md`
- 用語集: `docs/glossary.md`
- ADR: `docs/adr/`
