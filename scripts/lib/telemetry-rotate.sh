#!/usr/bin/env bash
# telemetry-rotate.sh — workspace-shared telemetry rotation primitive (S4-P3).
#
# Rotates events.jsonl nightly. Compresses today's log to events-YYYY-MM-DD.jsonl.gz
# in the same directory, then truncates events.jsonl. Keeps 30 days of archives.
#
# Intended to run as a systemd timer (e.g. 00:05 UTC daily). The meta-scan
# continues reading events.jsonl as the rolling 24h surface; archives are for
# deeper queries.
#
# Promoted from command/scripts/rotate-telemetry.sh on 2026-04-17 to address
# the S4-P3 shared-primitive gap flagged in cross-cutting syntheses.

set -euo pipefail

TELEMETRY_DIR="${WORKSPACE_ROOT:-/opt/workspace}/runtime/.telemetry"
EVENTS_FILE="$TELEMETRY_DIR/events.jsonl"
ARCHIVE_NAME="events-$(date -u +%Y-%m-%d).jsonl.gz"
ARCHIVE_PATH="$TELEMETRY_DIR/$ARCHIVE_NAME"
KEEP_DAYS="${TELEMETRY_KEEP_DAYS:-30}"

if [[ ! -f "$EVENTS_FILE" ]]; then
  echo "telemetry-rotate: $EVENTS_FILE not found, nothing to rotate"
  exit 0
fi

if [[ ! -s "$EVENTS_FILE" ]]; then
  echo "telemetry-rotate: $EVENTS_FILE is empty, skipping"
  exit 0
fi

gzip -c "$EVENTS_FILE" > "$ARCHIVE_PATH"
echo "telemetry-rotate: archived to $ARCHIVE_PATH"

: > "$EVENTS_FILE"
echo "telemetry-rotate: truncated $EVENTS_FILE"

find "$TELEMETRY_DIR" -name 'events-*.jsonl.gz' -mtime "+$KEEP_DAYS" -delete
echo "telemetry-rotate: pruned archives older than ${KEEP_DAYS} days"
