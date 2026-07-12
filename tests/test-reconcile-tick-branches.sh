#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
repo=$(mktemp -d)
trap 'rm -rf "$repo"' EXIT
git -C "$repo" init -q -b main
git -C "$repo" config user.email test@example.invalid
git -C "$repo" config user.name inventory-test
mkdir -p "$repo/system"
printf 'base\n' > "$repo/system/status.md"
git -C "$repo" add .
git -C "$repo" commit -q -m base
base=$(git -C "$repo" rev-parse HEAD)
git -C "$repo" branch ticks/a "$base"
git -C "$repo" branch ticks/b "$base"
printf 'changed\n' > "$repo/system/status.md"
git -C "$repo" add .
tree=$(git -C "$repo" write-tree)
tip=$(printf 'change\n\n' | git -C "$repo" commit-tree "$tree" -p "$base")
git -C "$repo" update-ref refs/heads/ticks/a "$tip"
git -C "$repo" update-ref refs/remotes/origin/ticks/a "$tip"

manifest="$repo/manifest.tsv"
printf 'local\trefs/heads/ticks/a\t%s\n' "$base" > "$manifest"
printf 'remote-live\trefs/heads/ticks/a\t%s\n' "$tip" >> "$manifest"
printf 'tracking\trefs/remotes/origin/ticks/a\t%s\n' "$tip" >> "$manifest"
printf 'local\trefs/heads/ticks/b\t%s\n' "$base" >> "$manifest"
output="$repo/inventory.json"
python3 "$ROOT/scripts/lib/reconcile-tick-branches.py" --repo "$repo" --main main --manifest "$manifest" --output "$output"
python3 - "$output" <<'PY'
import json,sys
p=json.load(open(sys.argv[1]))
assert p['source_counts']=={'local':2,'remote-live':1,'tracking':1}
assert p['unique_tick_names']==2
assert p['unique_tip_shas']==2
assert len(p['refs'])==4
assert all(r['analysis']['merge_base_with_main'] for r in p['refs'])
assert any(r['analysis']['patch_ids'] for r in p['refs'])
assert any(len(r['duplicate_tip_refs']) > 1 for r in p['refs'])
PY

echo 'reconcile tick inventory: PASS'
