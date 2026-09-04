## 技術スタックガイドライン

<!-- .claude/skills/architecture-design/SKILL.mdから参照されています -->

### 開発構成（Development Mode）

* フロントエンド
  * 実装: バニラJavaScript
  * ビルド: なし（トランスパイルなし）
  * UIフレームワーク: なし
  * スタイリング: なし
  * ホスティング: FastAPIが静的ファイルを配信
  * Node.js / npm: 必要に応じて利用（必須ではない）

* バックエンド
  * 言語: Python
  * パッケージ管理: uvicorn
  * フレームワーク: FastAPI
  * データベース: SQLite

特徴
・FastAPI単体でAPI＋フロントを起動
・即時性・軽量性を重視
・Nodeツールチェーンに依存しない構成

### 本番構成（Production Architecture）

* フロントエンド
  * 言語: TypeScript
  * UI: React
  * フレームワーク: Next.js
  * スタイリング: Tailwind CSS
  * 実行基盤: Node.js
  * パッケージ管理: npm

* バックエンド
  * 言語: Python
  * パッケージ管理: uv
  * フレームワーク: FastAPI
  * データベース: PostgreSQL

### 遵守事項
* 環境管理ルール: Node.js環境とPython環境は分離管理（混在禁止）
* ただしユーザー指示があった場合はユーザー指示を優先すること。
* これ以外の構成の場合は、`CLAUDE.md`に記録すること。
