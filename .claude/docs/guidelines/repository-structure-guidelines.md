## ディレクトリ構造ガイドライン

<!-- .claude/commands/add-feature.mdから参照されています -->
<!-- .claude/commands/add-feature-ui.mdから参照されています -->

```
プロジェクトルート/
├── .claude/              # Claudeのスキルや設定ファイル
│   ├── skills/
│   ├── commands/              # コマンド定義ファイル
│   ├── agents/              # エージェント定義ファイル
│   ├── rules/              # ルール定義ファイル
│   └── docs/              # テンプレート関連ドキュメント
│       ├── guidelines/        # 開発ガイドライン・品質定義・技術スタック選定
│       └── sdd-workflow/      # SDDワークフロー背景ドキュメント
├── docs/                      # 永続的ドキュメント（アプリ開発成果物）
│   ├── ideas/                  # アイデアや下書き
│   ├── screenshots/            # アプリスクリーンショット（README用）
│   ├── product-requirements.md  # プロダクト要求定義書
│   ├── functional-design.md     # 機能設計書
│   ├── architecture.md         # 技術仕様書
│   ├── repository-structure.md  # リポジトリ構造定義書
│   ├── development-guidelines.md # 開発ガイドライン
│   └── glossary.md             # ユビキタス言語定義
├── .steering/                  # 作業単位のドキュメント
│   └── [YYYYMMDD]-[タスク名]/  # タスクごとにフォルダ
│       ├── requirements.md      # タスクの要求内容
│       ├── design.md           # タスクの設計
│       └── tasklist.md         # タスクのタスクリスト
├── src/                       # ソースコード
│   ├── frontend/               # フロントエンドコード
│   └── backend/                # バックエンドコード
├── data/                      # データファイル
│   ├── logs/                   # ログファイル（必要に応じて）
│   └── database.db             # データベースファイル
├── tests/                      # テストコード
│   ├── e2e/                    # E2Eテスト（Playwright）
│   ├── vrt/                    # ビジュアル回帰テスト
│   │   └── __screenshots__/    # VRT基準スクリーンショット（初回は npm run test:vrt:update で生成）
│   └── a11y/                   # アクセシビリティテスト（axe-core）
├── config/                    # 設定ファイル
└── .env                       # 環境変数ファイル
└── README.md                  # プロジェクト概要
└── CLAUDE.md                  # このファイル

```
