#!/usr/bin/env bash
# telemetry-rotate.sh — workspace-shared telemetry rotation primitive (S4-P3).
#
# Rotates events.jsonl nightly. The hot file stays small; immutable compressed
# segments are retained under archive/events/ for later empirical analysis.
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
ARCHIVE_DIR="$TELEMETRY_DIR/archive/events"
STAMP="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
ARCHIVE_PATH="$ARCHIVE_DIR/events-$STAMP.jsonl.gz"
PENDING_PATH="$TELEMETRY_DIR/.events-$STAMP.pending.jsonl"
KEEP_DAYS="${TELEMETRY_KEEP_DAYS:-0}"

if [[ ! -f "$EVENTS_FILE" ]]; then
  echo "telemetry-rotate: $EVENTS_FILE not found, nothing to rotate"
  exit 0
fi

if [[ ! -s "$EVENTS_FILE" ]]; then
  echo "telemetry-rotate: $EVENTS_FILE is empty, skipping"
  exit 0
fi

# Move the hot segment out of the read path before compression. Writers open
# the append target per event, so recreating it immediately keeps capture
# independent of compression speed and prevents the archive job from blocking
# normal telemetry consumers.
mkdir -p "$ARCHIVE_DIR"
mv "$EVENTS_FILE" "$PENDING_PATH"
: > "$EVENTS_FILE"

if ! gzip -c "$PENDING_PATH" > "$ARCHIVE_PATH"; then
  echo "telemetry-rotate: compression failed; preserving $PENDING_PATH" >&2
  exit 1
fi
rm -f "$PENDING_PATH"
echo "telemetry-rotate: archived immutable segment to $ARCHIVE_PATH"

if [[ "$KEEP_DAYS" =~ ^[0-9]+$ ]] && (( KEEP_DAYS > 0 )); then
  find "$ARCHIVE_DIR" -name 'events-*.jsonl.gz' -mtime "+$KEEP_DAYS" -delete
  echo "telemetry-rotate: explicit retention override pruned segments older than ${KEEP_DAYS} days"
else
  echo "telemetry-rotate: archive retention is unbounded (TELEMETRY_KEEP_DAYS=0)"
fi
