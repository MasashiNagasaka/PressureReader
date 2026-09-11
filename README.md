# PressureReader

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-0B3D91)
![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-5C3EE8?logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?logo=scipy&logoColor=white)
![openpyxl](https://img.shields.io/badge/openpyxl-Excel-green)
![License](https://img.shields.io/badge/License-Private-lightgrey)

## 概要
PressureReader は、感圧紙画像（PNG / PDF）を読み込み、解析条件（色見本・温湿度・スケーリング）を設定して圧力値を可視化・Excel出力する Windows 向けデスクトップアプリです。

現在のメイン実行ファイルは `src/PressureReader.py` で、バージョンは `3.5.0` です。

## 主な機能
- PNG を開く
- PDF⇒PNG変換（変換後のPNGを自動表示）
- 標準色見本処理（明度設定）
- 温度[℃] / 湿度[%] 入力
- スケーリング設定（mm/px）
- 選択範囲の可視化（四角形 / 円 / 多角形）
- 選択範囲Excel出力（.xlsx）
- PNGへの解析条件保存 / 解析条件コピー
- 画面リセット

## 実行環境
- OS: Windows
- Python 実行パス（本プロジェクト運用）: `C:\nagasaka\python\testPressR\Scripts\python.exe`
- リポジトリ: `MasashiNagasaka/PressureReader`

## セットアップ
```powershell
git clone https://github.com/MasashiNagasaka/PressureReader.git
cd PressureReader\Project01
```

必要に応じて仮想環境を有効化:
```powershell
C:\nagasaka\python\testPressR\Scripts\activate.bat
```

## 起動方法
```powershell
C:\nagasaka\python\testPressR\Scripts\python.exe src\PressureReader.py
```

## 入力データ（事前準備）
- 画像PDF: 感圧紙（圧力計測後）および標準色見本
- 温度[℃]、湿度[%]: 圧力計測時の値
- スケール: 感圧紙の寸法[mm]

## プロジェクトワークフロー
- 仕様策定: `/plan-kaizen`
- 実装: `/add-feature`（必要に応じて `/add-feature-ui`）
- 初回ドキュメント整備: `/setup-project`
- 検証: `/verify`
- README更新: `/generate-readme`

## ディレクトリ概要
- `src/` : アプリ本体
- `docs/` : 長期ドキュメント（PRD/設計/アーキ）
- `docs/ideas/` : 仕様メモ・アイデア
- `.steering/` : 変更単位の実行仕様
- `.claude/` : コマンド・ルール・ガイドライン

## スクリーンショット
`docs/screenshots/` は現在未整備です。追加時に本READMEへ反映します。

## 最近の変更履歴
| 日付 | 変更内容 |
|------|---------|
| 2026-09-11 | リストボックスのデフォルト状態「感圧紙を選択」を追加 |
| 2026-09-11 | ガイダンスメッセージを調整 |
| 2026-09-11 | スケーリング未設定時のメッセージを変更 |
| 2026-09-11 | 各エントリの表示位置を調整 |
| 2026-09-11 | 検出値（平均/最大/最小）表示欄の調整 |
| 2026-09-11 | 圧力最大点ラベルを高圧検出箇所に変更 |
| 2026-09-10 | スケーリングの単位表示を追加 |
| 2026-09-10 | 明度の数値を非表示化 |
| 2026-09-09 | UI配置見直し（上から下フロー） |
| 2026-09-09 | PDF→PNG変換後に画像を自動で開く |

<details>
<summary>過去の主な履歴</summary>

| 日付 | 変更内容 |
|------|---------|
| 2026-09-08 | PNG一時ファイルをtmpフォルダ管理へ変更 |
| 2026-09-07 | アプリ名を PressureReader に統一 |
| 2026-09-07 | `src` 配下ファイル名整理 |
| 2026-09-07 | 画面リセットボタン追加 |
| 2026-09-07 | 画面リセットボタン、ボタンサイズ調整 |

</details>

<!-- readme-generated: 2026-09-11T14:54:20 -->

