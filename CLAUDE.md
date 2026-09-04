<!-- Python追加パッケージのホワイトリストに対応しました。2026-09-04 Auther=Hiroaki Iwata -->
# プロジェクトメモリ

* 日本語で対話すること。
* `AskUserQuestion`ツールを使って、ユーザーに選択肢を示しながら対話すること。

## plan モードと plan-kaizen の使い分け

- **plan モード**（EnterPlanMode）: 実装方法の計画（How）に使う。plan ファイル自体は `.claude/plans/` に保存される（Claude Code 内部動作）が、plan 承認後に生成する仕様書・設計メモは `docs/ideas/` に保存すること。
- **`/plan-kaizen`**: 仕様の壁打ち・策定（What）に使う。成果物は `docs/ideas/` に保存する。plan モードとは併用しない。

## 基本的な開発ワークフロー

1. **ドキュメント作成**: 永続ドキュメント(`docs/`)で「何を作るか」を定義
2. **仕様策定** *(任意)*: アイデア段階から既存コード・ドキュメントを踏まえて壁打ちし、仕様書MDを仕上げる
3. **作業計画**: ステアリングファイル(`.steering/`)で「今回何をするか」を計画
4. **実装**: `tasklist.md`に従って実装し、進捗を随時更新。ソースコードは `src`配下に保存
5. **検証**: 品質ゲート・動作確認・リグレッションチェック
6. **更新**: 必要に応じてドキュメント更新
7. **機能追加・バグ修正**: 上記ステップ2からスタートする

- 1は`/setup-project`コマンド、2は`/plan-kaizen`コマンド、3-6は`/add-feature`コマンドで着火する想定。
- `/add-feature`コマンドの代わりに `/add-feature-ui`コマンドを使うとE2Eテストまでおこなう。
- `/auto-add-feature-with-plan`コマンドは、仕様策定（plan-kaizen）から実装・コミット・pushまでを一括自動実行する（ユーザー確認なし）。**小規模・低リスク変更に限定すること。**
- `/auto-add-feature-ui-with-plan`コマンドは、`/auto-add-feature-with-plan`のE2Eテストあり版。
- `/resume-work`コマンドは、途中で中断した作業の再開に使用する。
- `/fix-bug`コマンドは、バグ修正に使用する（再現→最小化→仮説→修正→回帰確認の順で進める）。
- `/generate-readme`コマンドは、アプリ用README.mdの自動生成・更新に使用する。
- スキルを直接呼び出して開発ワークフローを迂回することは禁止。詳細は `.claude/rules/workflow-guardrails.md` を参照。

### ドキュメント・ファイルの役割

| 場所 | 役割 | 作成タイミング |
|---|---|---|
| `docs/` | プロダクト全体の長期ドキュメント（PRD・設計書など） | `/setup-project` 実行時 |
| `docs/glossary.md` | プロジェクト共有言語（ドメイン用語・命名規則・禁止語） | `/setup-project` 実行時に生成 |
| `docs/ideas/` | アイデアメモ・壁打ち結果・仕様書（実装前の素材） | `/plan-kaizen` 実行時 |
| `.steering/YYYYMMDD-name/` | 変更単位の実行仕様（requirements.md / design.md / tasklist.md） | `/add-feature` 実行時 |

- `.steering/` は「変更単位spec管理領域」として位置づける。軽微な修正では作成せずタスクで管理してよい。
- 1変更 = 1ディレクトリ。完了後も履歴として残す。
- プロジェクト内で用語を統一するときは `docs/glossary.md` を共有言語として使うこと（存在する場合）。

## ビルトインコマンドの活用

Claude Code のビルトインコマンドを以下のタイミングで活用すること。

- **`/run-skill-generator`**: 新規プロジェクト作成後、または起動方法・依存関係・環境変数が変わったときに実行する。プロジェクト固有の起動手順・テストコマンド・確認URLを `.claude/skills/run-<project>/` に生成する。secrets や `.env` の実値は記録しない。
- **`/run`**: アプリを起動し、基本的な動作を確認する。
- **`/verify`**: 実装完了後に変更が本当に動くか確認する。**単体テスト合格だけで完了扱いにしない。必ず `/verify` または同等の動作確認を実施すること。**

> `/verify` は `/add-feature` のステップ7.5（動作確認・リグレッションチェック）に相当する。`testing` skill は `/add-feature` から自動呼び出しされる詳細基準・補助手順であり、`/verify` の内部実装を支援する。

## ガイドライン

- 技術スタック選定: `.claude/docs/guidelines/tech-stack-guidelines.md` を参照
- ディレクトリ構造: `.claude/docs/guidelines/repository-structure-guidelines.md` を参照

## スクリーンショット

- Playwright でスクリーンショットを撮る際は `artifacts/screenshots/` に保存すること
- ルート直下に png を保存しないこと（PostToolUse Hook が自動移動するが、最初から正しい場所に保存するのが望ましい）
- README 用スクリーンショットは `docs/screenshots/` に保存すること（移動対象外）

## 開発ガイドライン

- コーディング規約・AI生成コードのアンチパターン・ドキュメント管理戦略: `.claude/docs/guidelines/development-guidelines.md`
- アーキテクチャ意思決定の記録: `docs/adr/`
- フィードバック速度の階層とDoD: `.claude/docs/guidelines/definition-of-done.md`

<!-- Python追加パッケージのホワイトリストに対応しました。2026-09-04 Auther=Hiroaki Iwata -->
## Python追加パッケージのホワイトリスト

- Python依存関係の追加・更新・検証時は、`.claude/rules/python-dependency-whitelist.md` を必ず参照し、遵守すること。
- Pythonの追加パッケージを直接指定してインストールする前に、必ず `.python_packages_list/` 配下の実在ホワイトリストファイルを確認すること。
- `.python_packages_list/` 配下のホワイトリストファイルの改変は**厳禁**とする。
- ホワイトリストに記載されたパッケージが解決する従属（推移的）パッケージは、個別のホワイトリスト記載を不要とし、インストールを許可する。
- ホワイトリストに記載されていないパッケージを直接指定してインストールすることは**厳禁**とする。

## Pythonホワイトリスト参照ルール（最優先）
- Python依存関係の追加・更新・検証を伴う場合は、必ず .python_packages_list/ ディレクトリを確認すること。
- **ファイル名を固定決め打ちしてはならない。** .python_packages_list/ 配下の実在ファイルを列挙し、参照対象を決定すること。
- .python_packages_list/ フォルダ、または参照すべきホワイトリストファイルが存在しない場合は、**そのまま処理を進めることを厳禁**とする。
- 上記不足がある場合は処理を停止し、**必ずユーザーに確認を取ってから**再開すること。
- 本節は、ホワイトリスト名の固定例示より優先して適用する。

