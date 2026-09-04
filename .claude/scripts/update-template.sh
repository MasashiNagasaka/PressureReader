#!/usr/bin/env bash
# update-template.sh
# テンプレートリポジトリの最新版を確認し、必要であれば取り込む。
# 対象: .claude/, .github/, CLAUDE.md, AGENTS.md（単純コピー、削除なし）
# 除外: .claude/settings.local.json（常に保護）
#
# 使い方:
#   bash .claude/scripts/update-template.sh [--backup|--no-backup]
#
# 環境変数:
#   TEMPLATE_REPO_URL    - テンプレートリポジトリのURL（デフォルト: 本テンプレートのorigin）
#   TEMPLATE_REPO_BRANCH - 対象ブランチ（デフォルト: main）

set -euo pipefail

TEMPLATE_REPO_URL="${TEMPLATE_REPO_URL:-https://github.com/tmc-ccoe/densei-matsushita-claude-code-template.git}"
TEMPLATE_REPO_BRANCH="${TEMPLATE_REPO_BRANCH:-main}"
VERSION_FILE=".claude/.template-version"
BACKUP_ROOT=".claude/.template-backup"
TARGETS=(".claude" ".github" "CLAUDE.md" "AGENTS.md")
EXCLUDES=(".claude/settings.local.json")

if [ "${UPDATE_TEMPLATE_REEXEC:-}" != "1" ]; then
  script_self="${BASH_SOURCE[0]:-$0}"
  if [ -f "$script_self" ]; then
    reexec_script="$(mktemp)"
    cp "$script_self" "$reexec_script"
    chmod +x "$reexec_script"
    UPDATE_TEMPLATE_REEXEC=1 UPDATE_TEMPLATE_REEXEC_SCRIPT="$reexec_script" exec bash "$reexec_script" "$@"
  fi
fi

cleanup_reexec_script() {
  if [ -n "${UPDATE_TEMPLATE_REEXEC_SCRIPT:-}" ] && [ -f "$UPDATE_TEMPLATE_REEXEC_SCRIPT" ]; then
    rm -f "$UPDATE_TEMPLATE_REEXEC_SCRIPT"
  fi
}
trap cleanup_reexec_script EXIT

# --- 引数解析 -----------------------------------------------------------
BACKUP_MODE="ask"
for arg in "$@"; do
  case "$arg" in
    --backup) BACKUP_MODE="yes" ;;
    --no-backup) BACKUP_MODE="no" ;;
    *)
      echo "不明な引数です: $arg" >&2
      echo "使い方: bash .claude/scripts/update-template.sh [--backup|--no-backup]" >&2
      exit 1
      ;;
  esac
done

# --- 前提チェック ---------------------------------------------------------
if ! command -v git >/dev/null 2>&1; then
  echo "エラー: git コマンドが見つかりません。git をインストールしてください。" >&2
  exit 1
fi

is_excluded() {
  local path="$1"
  local ex
  for ex in "${EXCLUDES[@]}"; do
    if [[ "$path" == "$ex" ]]; then
      return 0
    fi
  done
  return 1
}

# 進捗ログ用ヘルパー。処理ブロックの開始直前に呼び出し、統一フォーマット
# （記号 + ラベル）で「今何をしているか」を1行出力する。
# 完了報告・比較結果・エラーメッセージ等は既存の echo のまま区別する。
log_step() {
  echo "▸ $1"
}

is_wsl_environment() {
  if [ -n "${WSL_DISTRO_NAME:-}" ] || [ -n "${WSL_INTEROP:-}" ]; then
    return 0
  fi

  if [ -r /proc/version ] && grep -qiE 'microsoft|wsl' /proc/version; then
    return 0
  fi

  return 1
}

print_windows_bash_hint() {
  local detail="${1:-}"

  if is_wsl_environment || echo "$detail" | grep -qiE 'WSL|localhost proxy|ミラーリング|NAT モード|proxy'; then
    {
      echo ""
      echo "補足: Windows 環境で WSL 側 Bash から実行されている可能性があります。"
      echo "      社内プロキシ設定が WSL に渡らず GitHub 接続に失敗する場合は、"
      echo "      PowerShell から Git for Windows 付属の Bash で再実行してください。"
      echo '      例: & "C:\Program Files\Git\bin\bash.exe" .claude/scripts/update-template.sh --no-backup'
    } >&2
  fi
}

# --- リモート最新hashの取得 -------------------------------------------------
# 「--」でオプション終端し、URL/ブランチ名がハイフンで始まる場合でも
# gitオプションとして誤解釈されないようにする。
log_step "リモートの最新バージョンを確認しています..."
remote_ref="$(git ls-remote "$TEMPLATE_REPO_URL" -- "refs/heads/$TEMPLATE_REPO_BRANCH" 2>&1)" || {
  echo "エラー: リモートリポジトリへのアクセスに失敗しました。" >&2
  echo "$remote_ref" >&2
  print_windows_bash_hint "$remote_ref"
  exit 1
}
remote_hash="$(echo "$remote_ref" | awk '{print $1}')"

if [ -z "$remote_hash" ]; then
  echo "エラー: リモートブランチ '$TEMPLATE_REPO_BRANCH' のhashを取得できませんでした。" >&2
  exit 1
fi

# リモート応答がコミットhash形式（40桁16進数）であることを検証する。
# プロキシのエラーページ等、想定外の応答が .template-version に紛れ込むのを防ぐ。
if ! [[ "$remote_hash" =~ ^[0-9a-f]{40}$ ]]; then
  echo "エラー: リモートから取得したhashの形式が不正です: $remote_hash" >&2
  exit 1
fi

# --- 手元のバージョン記録 ---------------------------------------------------
local_hash=""
if [ -f "$VERSION_FILE" ]; then
  local_hash="$(tr -d '[:space:]' < "$VERSION_FILE")"
fi

if [ -n "$local_hash" ] && [ "$local_hash" = "$remote_hash" ]; then
  echo "最新です（hash: $remote_hash）。更新は不要です。"
  exit 0
fi

if [ -z "$local_hash" ]; then
  echo "手元にバージョン記録がありません（未追跡）。最新テンプレートを取り込みます。"
else
  echo "新しいテンプレートが見つかりました。"
  echo "  手元: $local_hash"
  echo "  最新: $remote_hash"
fi

# --- バックアップ要否確認 ---------------------------------------------------
if [ "$BACKUP_MODE" = "ask" ]; then
  log_step "バックアップの要否を確認しています..."
  if [ -t 0 ]; then
    read -r -p "上書き前に既存ファイルをバックアップしますか？ [y/N]: " answer
    case "$answer" in
      [yY]*) BACKUP_MODE="yes" ;;
      *) BACKUP_MODE="no" ;;
    esac
  else
    echo "非対話環境のため、バックアップなしで続行します（--backup で明示指定可能）。"
    BACKUP_MODE="no"
  fi
fi

backup_dir=""
if [ "$BACKUP_MODE" = "yes" ]; then
  log_step "既存ファイルをバックアップしています..."
  backup_stamp="$(date +"%Y%m%d-%H%M")"
  backup_dir="$BACKUP_ROOT/$backup_stamp"
  mkdir -p "$backup_dir"
  echo "バックアップ先: $backup_dir"
fi

# --- 一時ディレクトリへclone -------------------------------------------------
tmp_dir="$(mktemp -d)"
cleanup() {
  rm -rf "$tmp_dir"
  cleanup_reexec_script
}
trap cleanup EXIT

on_error() {
  echo "エラー: 更新処理中に失敗しました。" >&2
  if [ "$BACKUP_MODE" = "yes" ] && [ -n "$backup_dir" ] && [ -d "$backup_dir" ]; then
    echo "バックアップから手動復元できます: $backup_dir" >&2
  fi
}
trap on_error ERR

log_step "テンプレートを取得しています..."
clone_output="$(git clone --depth 1 --branch "$TEMPLATE_REPO_BRANCH" -- "$TEMPLATE_REPO_URL" "$tmp_dir" 2>&1)" || {
  echo "エラー: テンプレートのcloneに失敗しました。" >&2
  if [ -n "$clone_output" ]; then
    echo "$clone_output" >&2
  fi
  print_windows_bash_hint "$clone_output"
  exit 1
}

# --- 単純コピー（削除なし、除外あり） ----------------------------------------
copied_count=0

copy_file() {
  local rel_path="$1"
  local src_file="$2"

  if is_excluded "$rel_path"; then
    return 0
  fi

  if [ "$BACKUP_MODE" = "yes" ] && [ -f "$rel_path" ]; then
    mkdir -p "$backup_dir/$(dirname "$rel_path")"
    cp "$rel_path" "$backup_dir/$rel_path"
  fi

  mkdir -p "$(dirname "$rel_path")"
  cp "$src_file" "$rel_path"
  copied_count=$((copied_count + 1))
}

log_step "ファイルを反映しています..."
for target in "${TARGETS[@]}"; do
  src_path="$tmp_dir/$target"

  if [ ! -e "$src_path" ]; then
    continue
  fi

  if [ -d "$src_path" ]; then
    while IFS= read -r -d '' file; do
      rel="${file#"$tmp_dir"/}"
      copy_file "$rel" "$file"
    done < <(find "$src_path" -type f -print0)
  else
    copy_file "$target" "$src_path"
  fi
done

# --- バージョン記録の更新 ---------------------------------------------------
mkdir -p "$(dirname "$VERSION_FILE")"
printf '%s' "$remote_hash" > "$VERSION_FILE"

# --- 結果報告 --------------------------------------------------------------
echo ""
echo "テンプレートの更新が完了しました。"
echo "  取り込んだコミット: $remote_hash"
echo "  上書き/追加したファイル数: $copied_count"
if [ "$BACKUP_MODE" = "yes" ]; then
  echo "  バックアップ: $backup_dir"
else
  echo "  バックアップ: なし"
fi

# CLAUDE.md や .claude/commands 等はセッション開始時にのみ読み込まれ、
# 実行中のセッションには反映されない。実際にファイルが更新された
# 場合のみ、AIコーディングツールの再起動（新規セッション開始）を促す。
if [ "$copied_count" -ge 1 ]; then
  echo ""
  echo "⚠ 変更を反映するには、Claude Code / GitHub Copilot 等の"
  echo "  AIコーディングツールを再起動（新規セッション開始）してください。"
fi
