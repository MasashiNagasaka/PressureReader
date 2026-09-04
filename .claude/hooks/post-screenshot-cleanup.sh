#!/usr/bin/env bash
# PostToolUse Hook: スクリーンショット自動移動
# Playwright がルート直下に保存した png/jpeg を artifacts/screenshots/ に移動する
set -euo pipefail

# stdin を消費（hook プロトコル準拠）
cat > /dev/null

# プロジェクトルート直下の画像ファイルを検出
shopt -s nullglob
files=(*.png *.jpeg *.jpg)
[ ${#files[@]} -eq 0 ] && exit 0

# 移動先を作成
mkdir -p artifacts/screenshots

# 移動
for f in "${files[@]}"; do
  mv "$f" "artifacts/screenshots/"
done
