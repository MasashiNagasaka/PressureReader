# PressureReader

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-0B3D91)
![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-5C3EE8?logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?logo=scipy&logoColor=white)
![openpyxl](https://img.shields.io/badge/openpyxl-Excel-green)
![License](https://img.shields.io/badge/License-Private-lightgrey)

## 概要
PressureReader は、感圧紙画像（PNG）を読み込み、明度値から圧力値を算出して可視化・出力する Windows 向けデスクトップアプリです。  
現行コードは `src/PressureReader.py`（`version = "3.5.0"`）です。

## スクリーンショット
`docs/screenshots/` は現在未作成です。  
スクリーンショットを追加する場合は、このディレクトリに保存してください。

## 主な機能
- PNG を開く
- PDF を PNG に変換（変換後 PNG を自動で開く）
- 解析条件（明度・温度・湿度・スケーリング）設定
- 標準色見本処理
- 選択モード（四角形 / 多角形 / 円）
- 平均圧力・面積表示
- 選択範囲 Excel 出力（`.xlsx`）
- 解析条件を PNG メタデータへ保存 / 読み込み
- 画面リセット（起動直後状態へ復帰、確認ダイアログ付き）
- 一時 PNG の安全クリーンアップ（専用 tmp フォルダ）

## 技術スタック
- 言語: Python
- GUI: Tkinter / ttk
- 画像処理: Pillow, OpenCV, NumPy
- 補間計算: SciPy
- Excel 出力: openpyxl
- PDF 変換: pdf2image + poppler

## セットアップ
### 前提
- Windows
- Python 実行環境: `C:\nagasaka\python\testPressR\Scripts\python.exe`
- Git リポジトリ: `https://github.com/MasashiNagasaka/PressureReader.git`

### クローン
```powershell
git clone https://github.com/MasashiNagasaka/PressureReader.git
cd PressureReader\Project01
```

## 実行方法
```powershell
C:\nagasaka\python\testPressR\Scripts\python.exe src\PressureReader.py
```

## 開発ワークフロー
- 仕様化: `/plan-kaizen`
- 実装: `/add-feature`（または `/add-feature-ui`）
- 初回ドキュメント整備: `/setup-project`
- 検証: `/verify`

## ドキュメント
- PRD: `docs/product-requirements.md`
- 機能設計: `docs/functional-design.md`
- アーキテクチャ: `docs/architecture.md`
- 用語集: `docs/glossary.md`
- ADR: `docs/adr/`
- 仕様アイデア: `docs/ideas/`
- 変更ステアリング: `.steering/`

## 最近の変更履歴
| 日付 | 変更内容 |
|------|---------|
| 2026-09-09 | 標準色見本処理→通常選択モードへの不具合修正 |
| 2026-09-09 | PDF→PNGファイル変換後、変換後の画像を自動で開く |
| 2026-09-09 | スケーリングボタンの押下時のウィンドウサイズ変更 |
| 2026-09-09 | 感圧紙種類を手動変更したときのみ、明度設定をリセット |
| 2026-09-08 | png一時ファイルはtmpフォルダで管理 |

<details>
<summary>過去の変更履歴</summary>

| 日付 | 変更内容 |
|------|---------|
| 2026-09-07 | 画像をPressureReaderに変更 |
| 2026-09-07 | src フォルダ内のファイル名を変更 PressureReader |
| 2026-09-07 | ホワイトリストOK、タイトルをPressureReaderに変更 |
| 2026-09-07 | 画面リセットボタン、ボタンサイズ調整 |
| 2026-09-07 | 画面リセットボタン実装まで |

</details>

<!-- readme-generated: 2026-09-09T14:54:05 -->
