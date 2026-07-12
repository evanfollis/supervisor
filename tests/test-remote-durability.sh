#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
remote="$tmp/remote.git"
repo="$tmp/repo"

git init -q --bare "$remote"
git clone -q "$remote" "$repo"
git -C "$repo" switch -q -c main
git -C "$repo" config user.email test@example.invalid
git -C "$repo" config user.name durability-test
printf 'base\n' > "$repo/file"
git -C "$repo" add file
git -C "$repo" commit -q -m base
git -C "$repo" push -q -u origin main

RUNTIME_ROOT="$tmp/runtime" WORKSPACE_TELEMETRY_DIR="$tmp/runtime/telemetry" \
  REMOTE_DURABILITY_LOCK_DIR="$tmp/runtime/.locks" \
  "$ROOT/scripts/lib/remote-durability.sh" --audit --repo "$repo" >/dev/null

# Exercise the production discovery path, including a nested managed repo.
mkdir -p "$tmp/projects"
git clone -q -b main "$remote" "$tmp/projects/discovered"
REMOTE_DURABILITY_SUPERVISOR_ROOT="$repo" REMOTE_DURABILITY_PROJECTS_ROOT="$tmp/projects" \
  REMOTE_DURABILITY_LOCK_DIR="$tmp/runtime/.locks" \
  RUNTIME_ROOT="$tmp/runtime" WORKSPACE_TELEMETRY_DIR="$tmp/runtime/telemetry" \
  "$ROOT/scripts/lib/remote-durability.sh" --audit > "$tmp/discovery.out"
grep -q 'projects/discovered.*synced' "$tmp/discovery.out"

printf 'next\n' >> "$repo/file"
git -C "$repo" commit -qam next
if RUNTIME_ROOT="$tmp/runtime" WORKSPACE_TELEMETRY_DIR="$tmp/runtime/telemetry" \
  REMOTE_DURABILITY_LOCK_DIR="$tmp/runtime/.locks" \
  "$ROOT/scripts/lib/remote-durability.sh" --audit --repo "$repo" >/dev/null 2>&1; then
  echo 'audit accepted an ahead repository' >&2
  exit 1
fi

RUNTIME_ROOT="$tmp/runtime" WORKSPACE_TELEMETRY_DIR="$tmp/runtime/telemetry" \
  REMOTE_DURABILITY_LOCK_DIR="$tmp/runtime/.locks" \
  "$ROOT/scripts/lib/remote-durability.sh" --repair --repo "$repo" >/dev/null
[[ "$(git -C "$repo" rev-parse HEAD)" == "$(git --git-dir="$remote" rev-parse main)" ]]

printf 'ghp_123456789012345678901234567890123456\n' >> "$repo/file"
git -C "$repo" commit -qam 'add fake credential-shaped fixture'
if RUNTIME_ROOT="$tmp/runtime" WORKSPACE_TELEMETRY_DIR="$tmp/runtime/telemetry" \
  REMOTE_DURABILITY_LOCK_DIR="$tmp/runtime/.locks" \
  "$ROOT/scripts/lib/remote-durability.sh" --repair --repo "$repo" >/dev/null 2>&1; then
  echo 'repair published a credential-shaped range' >&2
  exit 1
fi
[[ "$(git -C "$repo" rev-parse HEAD)" != "$(git --git-dir="$remote" rev-parse main)" ]]

python3 - "$tmp/runtime/telemetry/remote-durability.jsonl" <<'PY'
import json, sys
events = [json.loads(line) for line in open(sys.argv[1], encoding="utf-8")]
assert any(e["publicationState"] == "synced" for e in events)
assert any(e["publicationState"] == "secret-blocked" for e in events)
assert any(e["publicationState"] == "secret-blocked" and e["eventType"] == "throttled" for e in events)
PY

# Credential-shaped commit messages are public metadata and must also block.
git -C "$repo" reset -q --hard origin/main
printf 'safe content\n' >> "$repo/file"
git -C "$repo" commit -qam 'contains ghp_123456789012345678901234567890123456'
if RUNTIME_ROOT="$tmp/runtime" WORKSPACE_TELEMETRY_DIR="$tmp/runtime/telemetry" \
  REMOTE_DURABILITY_LOCK_DIR="$tmp/runtime/.locks" \
  "$ROOT/scripts/lib/remote-durability.sh" --repair --repo "$repo" >/dev/null 2>&1; then
  echo 'repair published a credential-shaped commit message' >&2
  exit 1
fi

# Ambiguous upstream configuration is never repaired implicitly.
git -C "$repo" reset -q --hard origin/main
git -C "$repo" branch --unset-upstream
if RUNTIME_ROOT="$tmp/runtime" WORKSPACE_TELEMETRY_DIR="$tmp/runtime/telemetry" \
  REMOTE_DURABILITY_LOCK_DIR="$tmp/runtime/.locks" \
  "$ROOT/scripts/lib/remote-durability.sh" --repair --repo "$repo" >/dev/null 2>&1; then
  echo 'repair accepted a repository without an upstream' >&2
  exit 1
fi

# Contention is designed backpressure: it must be visible as throttled telemetry.
(
  mkdir -p "$tmp/runtime/.locks"
  exec 8>"$tmp/runtime/.locks/remote-durability.lock"
  flock 8
  RUNTIME_ROOT="$tmp/runtime" WORKSPACE_TELEMETRY_DIR="$tmp/runtime/telemetry" \
    REMOTE_DURABILITY_LOCK_DIR="$tmp/runtime/.locks" \
    "$ROOT/scripts/lib/remote-durability.sh" --audit --repo "$repo" >/dev/null 2>&1
)
python3 - "$tmp/runtime/telemetry/remote-durability.jsonl" <<'PY'
import json, sys
events = [json.loads(line) for line in open(sys.argv[1], encoding="utf-8")]
assert any(e["publicationState"] == "busy" and e["eventType"] == "throttled" for e in events)
PY

echo 'remote durability: PASS'
