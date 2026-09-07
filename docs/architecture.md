---
last_updated: 2026-09-07
git_commit: ""
status: draft
---

# 技術仕様書 (Architecture Design Document)

## テクノロジースタック
### 言語・ランタイム
- Python 3.x

### フレームワーク・ライブラリ
- Tkinter/ttk, Pillow, OpenCV, NumPy, SciPy, openpyxl, pdf2image

### 開発ツール
- GitHub (`MasashiNagasaka/PressureReader`)
- 実行Python: `C:\nagasaka\python\testPressR\Scripts\python.exe`

## アーキテクチャパターン
### イベント駆動モノリス（GUI単一プロセス）
- 単一プロセスでUI・計算・ファイルI/Oを実行
- グローバル状態を中心としたイベント駆動

## レイヤー責務（論理）
- Presentation: Tkinter widgets / event handler
- Application: 解析フロー制御（読込、選択、保存）
- Domain: 輝度→圧力換算、範囲計算
- Infrastructure: ファイルI/O（PNG/PDF/XLSX）

## データ永続化戦略
### ストレージ方式
- 解析条件: PNGメタデータに保存
- 解析結果: XLSXファイル保存

### バックアップ戦略
- 元データ保護を優先（保存先選択）
- 上書き処理時はユーザー意図に沿う運用を徹底

## パフォーマンス要件
- 通常操作で体感遅延を許容しない
- 画面リセットは即時（0.2秒目安）

## セキュリティアーキテクチャ
- ローカル処理前提
- 機密情報はコードに埋め込まない

## スケーラビリティ設計
- 当面は単一ファイル運用
- 将来的に以下へ分割可能な構造を目標:
  - `ui/`, `domain/`, `infra/`, `app/`

## テスト戦略
- 手動E2Eを主軸（GUI）
- 主要導線の回帰チェックリストを維持
- 将来的にロジック部を単体テスト可能な形へ抽出

## 技術的制約
- Windowsデスクトップ前提の運用
- 日本語ファイル名・画像パスを扱うため、読み込み方式に制約あり
- Poppler配置がPDF変換の前提

