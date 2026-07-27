#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

repo="$TMP/repo"
mkdir -p "$repo/.prompteval/codex-task/golden" "$repo/fixtures" "$repo/src"
git -C "$TMP" init -q repo

printf '# Fixture\n' > "$repo/README.md"
printf '.env\nnode_modules/\n__pycache__/\n' > "$repo/.gitignore"
printf 'fixtures/\n' > "$repo/.ignore"
printf '%s\n' \
  'NextResponse.redirect(new URL("/sealed", req.url))' \
  'new URL(path, req.url)' \
  > "$repo/.prompteval/codex-task/golden/holdout.jsonl"
printf '%s\n' \
  'NextResponse.redirect(new URL("/ignored", req.url))' \
  'new URL(path, req.url)' \
  > "$repo/fixtures/ignored.ts"
printf 'export const clean = true;\n' > "$repo/src/clean.ts"
git -C "$repo" add -f .

output=$(bash "$ROOT/scripts/lib/preflight-deploy.sh" "$repo" 2>&1 || true)
grep -F 'No NextResponse.redirect(new URL..req.url)   ✓' <<< "$output" >/dev/null
grep -F 'No new URL(path, req.url) in handlers        ✓' <<< "$output" >/dev/null

printf 'new URL(path, req.url)\n' > "$repo/src/bad.ts"
git -C "$repo" add src/bad.ts
output=$(bash "$ROOT/scripts/lib/preflight-deploy.sh" "$repo" 2>&1 || true)
grep -F 'No new URL(path, req.url) in handlers        ✗' <<< "$output" >/dev/null

echo "preflight deploy source-scan boundary: PASS"
