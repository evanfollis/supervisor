#!/usr/bin/env bash
# Hot/cold lifecycle for /opt/workspace/runtime/.meta/.
#
# Full reflection and synthesis artifacts are empirical evidence. Older files
# leave the hot working set but are compressed, not deleted:
# - newest 14 reflections per project remain directly readable
# - synthesis files from the last 30 days remain directly readable
# - older artifacts move to archive/{reflections,syntheses}/ as .gz files
# Scheduled by workspace-meta-prune.timer (weekly).

set -euo pipefail
LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"
META_DIR="$WORKSPACE_META_DIR"
ARCHIVE_ROOT="$META_DIR/archive"
cd "$META_DIR"

archive_file() {
  local source="$1" target_dir="$2" target
  mkdir -p "$target_dir"
  target="$target_dir/$(basename "$source").gz"
  if [[ -e "$target" ]]; then
    echo "archive: target already exists, preserving source: $target" >&2
    return 0
  fi
  gzip -c "$source" > "$target"
  rm -f "$source"
  echo "archive: $source -> $target"
}

# Per-project reflection retention (keep newest 14 per project name).
shopt -s nullglob
declare -A SEEN
for f in $(ls -1t *-reflection-*.md 2>/dev/null); do
  project="${f%-reflection-*}"
  count=${SEEN[$project]:-0}
  count=$((count + 1))
  SEEN[$project]=$count
  if [[ $count -gt 14 ]]; then
    archive_file "$f" "$ARCHIVE_ROOT/reflections/$project"
  fi
done

# Synthesis hot-set retention: archive files older than 30 days.
while IFS= read -r -d '' f; do
  archive_file "$f" "$ARCHIVE_ROOT/syntheses"
done < <(find . -maxdepth 1 -name 'cross-cutting-*.md' -mtime +30 -print0 2>/dev/null)

echo "prune-meta: hot working set bounded; full artifacts retained compressed"
