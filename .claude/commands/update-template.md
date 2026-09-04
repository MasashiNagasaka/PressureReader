---
description: プロジェクトフォルダに取り込んだテンプレート（.claude/, .github/, CLAUDE.md, AGENTS.md）を、テンプレートリポジトリの最新版に自動更新する
---

# テンプレート自動更新

**目的:** テンプレート（`.claude/`, `.github/`, `CLAUDE.md`, `AGENTS.md`）をリモートリポジトリの最新版と比較し、新しければ自動で取り込む。手動でのファイル再コピーを不要にする。

**引数:** なし（バックアップの要否は実行中に確認する）

---

## ステップ1: 更新スクリプトの実行

### Windows の場合

Windows では bare `bash` を直接実行しないこと。`bash` が WSL 側に解決されると、社内プロキシ設定が WSL に渡らず GitHub への HTTPS 接続に失敗する場合がある。

PowerShell で以下を実行し、Git for Windows 付属の `bash.exe` を解決してから更新スクリプトを起動する。

```powershell
$ErrorActionPreference = "Stop"

$scriptPath = ".claude/scripts/update-template.sh"
$bashPath = $env:UPDATE_TEMPLATE_BASH

if ($bashPath) {
  if (-not (Test-Path -LiteralPath $bashPath)) {
    throw "UPDATE_TEMPLATE_BASH が指定されていますが、bash.exe が見つかりません: $bashPath"
  }
} else {
  $candidates = @()

  $gitCommand = Get-Command git -ErrorAction SilentlyContinue
  if ($gitCommand -and $gitCommand.Source) {
    $gitExe = $gitCommand.Source
    $gitRoot = Split-Path -Parent (Split-Path -Parent $gitExe)
    $candidates += Join-Path $gitRoot "bin/bash.exe"
    $candidates += Join-Path $gitRoot "usr/bin/bash.exe"
  }

  $candidates += "C:\Program Files\Git\bin\bash.exe"
  $candidates += "C:\Program Files\Git\usr\bin\bash.exe"

  $bashPath = $candidates |
    Where-Object { Test-Path -LiteralPath $_ } |
    Select-Object -First 1
}

if (-not $bashPath) {
  throw "Git for Windows 付属の bash.exe が見つかりません。Windows では WSL 側 Bash への誤実行を避けるため、bare 'bash' にはフォールバックしません。Git for Windows をインストールするか、UPDATE_TEMPLATE_BASH に bash.exe のパスを指定してください。"
}

& $bashPath $scriptPath
```

バックアップ要否を非対話で指定したい場合は、最後の行に引数を追加する。

```powershell
& $bashPath $scriptPath --backup
& $bashPath $scriptPath --no-backup
```

### Linux / macOS / Git Bash の場合

以下のコマンドを実行する。

```bash
bash .claude/scripts/update-template.sh
```

バックアップ要否を非対話で指定したい場合:

```bash
bash .claude/scripts/update-template.sh --backup
bash .claude/scripts/update-template.sh --no-backup
```

- リモートの最新コミットhashと、手元の `.claude/.template-version` を比較する。
- 実行中は `▸` で始まる進捗ログ（例: `▸ リモートの最新バージョンを確認しています...`）が処理の節目ごとに表示される。実行される処理のみログが出るため、最新の場合はリモート確認のログのみで終了する。
- 一致する場合は「最新です」と表示されそのまま終了する。次のステップは不要。
- 不一致（または `.claude/.template-version` が未作成）の場合、続けてバックアップ要否を尋ねるプロンプトが表示される。ユーザーの回答をそのまま待つ。

## ステップ2: バックアップ要否の確認

スクリプトの対話プロンプト（`上書き前に既存ファイルをバックアップしますか？ [y/N]:`）に対して、ユーザーの意図を確認する。

- ユーザーが明示的にバックアップを希望する場合: `y` を入力する。
- 特に希望がない、またはバックアップ不要と回答した場合: `N`（またはそのままEnter）を入力する。

> 非対話的に実行したい場合は、Windows では上記 PowerShell 例の最後に `--backup` または `--no-backup` を付ける。Linux / macOS / Git Bash では `bash .claude/scripts/update-template.sh --backup` または `--no-backup` を直接使ってもよい。

## ステップ3: 結果の報告

スクリプトの標準出力を確認し、以下をユーザーに要約して報告する。

- 更新が行われたか（最新だった場合はスキップされた旨）
- 取り込んだコミットhash
- 上書き・追加されたファイル数
- バックアップを作成した場合はその保存先パス（`.claude/.template-backup/[YYYYMMDD-HHmm]/`）

## 注意事項

- 上書き対象は `.claude/`, `.github/`, `CLAUDE.md`, `AGENTS.md` のみ。`docs/`, `src/`, `.steering/` 等のプロジェクト固有ファイルには一切影響しない。
- `.claude/settings.local.json` は常に上書き対象外（保護される）。
- コピーは追加・上書きのみで削除は行わない。リモートに存在しないローカル独自ファイル（例: 独自追加した `.claude/commands/*.md`）はそのまま残る。
- リモートにも存在する同名ファイルをローカルで編集していた場合は、常に強制的にリモート版で上書きされる。
- リモートリポジトリのURL・ブランチを変更したい場合は、環境変数 `TEMPLATE_REPO_URL` / `TEMPLATE_REPO_BRANCH` を設定してから実行する。
- Windows で Git for Windows 付属の `bash.exe` が自動検出できない場合は、環境変数 `UPDATE_TEMPLATE_BASH` に `bash.exe` のフルパスを指定する。WSL 側 Bash への誤実行を避けるため、Windows 手順では bare `bash` へ自動フォールバックしない。
