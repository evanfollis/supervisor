#!/usr/bin/env bash
# telemetry-rotate.sh — workspace-shared telemetry rotation primitive (S4-P3).
#
# Rotates shared and supervisor event streams nightly. Hot files stay small;
# immutable compressed segments are retained for later empirical analysis.
#
# Intended to run as a systemd timer (e.g. 00:05 UTC daily). The meta-scan
# continues reading events.jsonl as the rolling 24h surface; archives are for
# deeper queries.
#
# Promoted from command/scripts/rotate-telemetry.sh on 2026-04-17 to address
# the S4-P3 shared-primitive gap flagged in cross-cutting syntheses.

set -euo pipefail

TELEMETRY_DIR="${WORKSPACE_ROOT:-/opt/workspace}/runtime/.telemetry"
STAMP="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
KEEP_DAYS="${TELEMETRY_KEEP_DAYS:-0}"

rotate_stream() {
  local stream="$1"
  local hot="$TELEMETRY_DIR/${stream}.jsonl"
  local archive_dir="$TELEMETRY_DIR/archive/${stream}"
  local archive_path="$archive_dir/${stream}-$STAMP.jsonl.gz"
  local pending="$TELEMETRY_DIR/.${stream}-$STAMP.pending.jsonl"

  if [[ ! -s "$hot" ]]; then
    echo "telemetry-rotate: $hot absent or empty, skipping"
    return 0
  fi

  # Writers open the append target per event. Recreate it immediately after
  # the atomic rename, so compression never blocks capture or hot consumers.
  mkdir -p "$archive_dir"
  mv "$hot" "$pending"
  : > "$hot"

  if ! gzip -c "$pending" > "$archive_path"; then
    echo "telemetry-rotate: compression failed; preserving $pending" >&2
    return 1
  fi
  rm -f "$pending"
  echo "telemetry-rotate: archived immutable segment to $archive_path"

  if [[ "$KEEP_DAYS" =~ ^[0-9]+$ ]] && (( KEEP_DAYS > 0 )); then
    find "$archive_dir" -name "${stream}-*.jsonl.gz" -mtime "+$KEEP_DAYS" -delete
    echo "telemetry-rotate: explicit retention override pruned ${stream} segments older than ${KEEP_DAYS} days"
  else
    echo "telemetry-rotate: ${stream} archive retention is unbounded"
  fi
}

rotate_stream events
rotate_stream supervisor-events
