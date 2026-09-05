#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEST_ROOT"' EXIT

META_DIR="$TEST_ROOT/meta"
mkdir -p "$META_DIR"

latest="$META_DIR/cross-cutting-2026-01-01T00-00-00Z.md"
stale="$META_DIR/cross-cutting-2026-01-02T00-00-00Z.md"
printf 'latest substantive synthesis\n' > "$latest"
printf 'older unreferenced synthesis\n' > "$stale"
touch -d '40 days ago' "$latest" "$stale"
ln -s "$(basename "$latest")" "$META_DIR/LATEST_SYNTHESIS"

WORKSPACE_META_DIR="$META_DIR" \
WORKSPACE_LATEST_SYNTHESIS_PTR="$META_DIR/LATEST_SYNTHESIS" \
  bash "$REPO_ROOT/scripts/lib/prune-meta.sh"

test -f "$latest"
test -L "$META_DIR/LATEST_SYNTHESIS"
test "$(readlink -f "$META_DIR/LATEST_SYNTHESIS")" = "$latest"
test ! -e "$stale"
test -f "$META_DIR/archive/syntheses/$(basename "$stale").gz"

echo 'test-prune-meta: PASS'
