#!/usr/bin/env bash
# PostToolUse Hook: 言語自動検出リンター + additionalContext JSON出力
# ファイル編集後に自動実行され、リンター違反をエージェントにフィードバックする
set -euo pipefail

input="$(cat)"
file="$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null)"

# ファイルパスが取得できない場合はスキップ
[ -z "$file" ] && exit 0

diag=""

case "$file" in
  *.ts|*.tsx|*.js|*.jsx)
    # TypeScript/JavaScript: npm run lint を使用
    if [ -f package.json ]; then
      diag="$(npm run lint --silent 2>&1 | head -20)" || true
    fi
    ;;
  *.py)
    # Python: ruff を使用（インストール済みの場合）
    if command -v ruff >/dev/null 2>&1; then
      ruff check --fix "$file" >/dev/null 2>&1 || true
      ruff format "$file" >/dev/null 2>&1 || true
      diag="$(ruff check "$file" 2>&1 | head -20)" || true
    fi
    ;;
  *.go)
    # Go: golangci-lint を使用（インストール済みの場合）
    if command -v golangci-lint >/dev/null 2>&1; then
      diag="$(golangci-lint run "$file" 2>&1 | head -20)" || true
    fi
    ;;
  *)
    # 対象外の拡張子はスキップ
    exit 0
    ;;
esac

# 違反がある場合のみ、additionalContext JSON形式で出力
if [ -n "$diag" ]; then
  jq -n --arg msg "$diag" '{
    hookSpecificOutput: {
      hookEventName: "PostToolUse",
      additionalContext: $msg
    }
  }'
fi
