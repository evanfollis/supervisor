#!/usr/bin/env bash
set -euo pipefail

ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT

WORKSPACE_ROOT="$ROOT/workspace"
PROJECT_DIR="$WORKSPACE_ROOT/projects/demo"
BIN_DIR="$ROOT/bin"

mkdir -p "$PROJECT_DIR" "$BIN_DIR" "$WORKSPACE_ROOT/runtime/.telemetry"
printf '{"project":"demo","source":"test","eventType":"info","level":"info","sourceType":"system","timestamp":1}\n' \
  > "$WORKSPACE_ROOT/runtime/.telemetry/events.jsonl"

cat > "$BIN_DIR/claude" <<'EOF'
#!/usr/bin/env bash
echo "fake claude: no reflection artifact"
exit 0
EOF
chmod +x "$BIN_DIR/claude"

set +e
WORKSPACE_LAYOUT=split \
WORKSPACE_ROOT="$WORKSPACE_ROOT" \
WORKSPACE_META_DIR="$WORKSPACE_ROOT/runtime/.meta" \
WORKSPACE_HANDOFF_DIR="$WORKSPACE_ROOT/runtime/.handoff" \
WORKSPACE_TELEMETRY_DIR="$WORKSPACE_ROOT/runtime/.telemetry" \
PATH="$BIN_DIR:$PATH" \
  /opt/workspace/supervisor/scripts/lib/reflect.sh demo "$PROJECT_DIR" \
  > "$ROOT/stdout" 2> "$ROOT/stderr"
status=$?
set -e

if [[ "$status" -ne 2 ]]; then
  echo "expected reflect.sh to exit 2, got $status" >&2
  cat "$ROOT/stdout" >&2
  cat "$ROOT/stderr" >&2
  exit 1
fi

EVENT_FILE="$WORKSPACE_ROOT/runtime/.telemetry/events.jsonl"
grep -q '"eventType":"failure"' "$EVENT_FILE"
grep -q '"sourceType":"system"' "$EVENT_FILE"
grep -q '"source":"demo.reflect"' "$EVENT_FILE"
grep -q '"reason":"no_output_file"' "$EVENT_FILE"
grep -q '"exitCode":2' "$EVENT_FILE"

cat > "$BIN_DIR/claude" <<'EOF'
#!/usr/bin/env bash
echo "fake claude: invocation failed"
exit 7
EOF
chmod +x "$BIN_DIR/claude"

set +e
WORKSPACE_LAYOUT=split \
WORKSPACE_ROOT="$WORKSPACE_ROOT" \
WORKSPACE_META_DIR="$WORKSPACE_ROOT/runtime/.meta" \
WORKSPACE_HANDOFF_DIR="$WORKSPACE_ROOT/runtime/.handoff" \
WORKSPACE_TELEMETRY_DIR="$WORKSPACE_ROOT/runtime/.telemetry" \
PATH="$BIN_DIR:$PATH" \
  /opt/workspace/supervisor/scripts/lib/reflect.sh demo "$PROJECT_DIR" \
  > "$ROOT/stdout-failed" 2> "$ROOT/stderr-failed"
status=$?
set -e

if [[ "$status" -ne 7 ]]; then
  echo "expected reflect.sh to preserve claude exit 7, got $status" >&2
  cat "$ROOT/stdout-failed" >&2
  cat "$ROOT/stderr-failed" >&2
  exit 1
fi

grep -q '"reason":"claude_invocation_failed"' "$EVENT_FILE"
grep -q '"exitCode":7' "$EVENT_FILE"

echo "reflect failure telemetry test passed"
