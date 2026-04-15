#!/usr/bin/env bash
# Retention for /opt/workspace/runtime/.meta/ — keep reflections bounded.
# Per project: keep last 14 reflection files.
# Workspace: keep synthesis files from last 30 days.
# Scheduled by workspace-meta-prune.timer (weekly).

set -euo pipefail
LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"
META_DIR="$WORKSPACE_META_DIR"
cd "$META_DIR"

# Per-project reflection retention (keep newest 14 per project name).
shopt -s nullglob
declare -A SEEN
for f in $(ls -1t *-reflection-*.md 2>/dev/null); do
  project="${f%-reflection-*}"
  count=${SEEN[$project]:-0}
  count=$((count + 1))
  SEEN[$project]=$count
  if [[ $count -gt 14 ]]; then
    echo "prune: $f"
    rm -f "$f"
  fi
done

# Synthesis retention: delete cross-cutting files older than 30 days.
find . -maxdepth 1 -name 'cross-cutting-*.md' -mtime +30 -print -delete 2>/dev/null || true

echo "prune-meta: complete"
