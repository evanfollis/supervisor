#!/usr/bin/env bash
set -euo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"

mkdir -p "$WORKSPACE_TELEMETRY_DIR"

python3 "$LIB_DIR/session-trace-scan.py" \
  --workspace-root "$WORKSPACE_ROOT" \
  --sessions-conf "$WORKSPACE_SESSION_CONF" \
  --manifests-dir "$WORKSPACE_SUPERVISOR_SESSIONS_DIR" \
  --trace-file "$WORKSPACE_TELEMETRY_DIR/session-trace.jsonl" \
  --state-file "$WORKSPACE_TELEMETRY_DIR/session-trace-state.json"
