#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
# shellcheck disable=SC1091
source "$ROOT/scripts/lib/tick-branch-lifecycle.sh"

repo=$(mktemp -d)
trap 'rm -rf "$repo"' EXIT
git -C "$repo" init -q -b main
git -C "$repo" config user.email test@example.invalid
git -C "$repo" config user.name lifecycle-test
printf 'base\n' > "$repo/file"
git -C "$repo" add file
git -C "$repo" commit -q -m base
base=$(git -C "$repo" rev-parse HEAD)

[[ "$(tick_branch_class "$repo")" == empty ]]
tick_branch_create_pending "$repo" "$base"
[[ "$(tick_branch_class "$repo")" == pending ]]
[[ "$(git -C "$repo" rev-parse main)" == "$base" ]]
if tick_branch_create_pending "$repo" "$base" 2>/dev/null; then
  echo 'existing pending ref was overwritten' >&2
  exit 1
fi
grep -q 'refs/heads/ticks/pending' <(tick_branch_blocking_summary "$repo")

git -C "$repo" update-ref refs/heads/ticks/legacy "$base"
[[ "$(tick_branch_class "$repo")" == multiple ]]
git -C "$repo" update-ref -d refs/heads/ticks/pending "$base"
[[ "$(tick_branch_class "$repo")" == unexpected ]]
git -C "$repo" update-ref -d refs/heads/ticks/legacy "$base"

if grep -Eq 'git -C .*push origin.*ticks|branch -f .*ticks' "$ROOT/scripts/lib/supervisor-tick.sh"; then
  echo 'tick wrapper still has a forcing or push path' >&2
  exit 1
fi

echo 'supervisor tick branch lifecycle: PASS'
