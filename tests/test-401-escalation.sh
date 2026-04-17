#!/usr/bin/env bash
# Test: 401 auth-failure detection in supervisor-project-tick.sh
# Exercises the grep pattern that detects 401 output and verifies:
#   1. URGENT handoff file is created
#   2. S1-P2 telemetry event is emitted to events.jsonl
#
# Run: bash supervisor/tests/test-401-escalation.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LIB_DIR="$REPO_ROOT/scripts/lib"

TMPDIR_TEST="$(mktemp -d /tmp/test-401-XXXXXX)"
trap 'rm -rf "$TMPDIR_TEST"' EXIT

# --- Setup fake workspace paths ---
export WORKSPACE_LAYOUT="split"
export WORKSPACE_ROOT="$TMPDIR_TEST/workspace"
export SUPERVISOR_ROOT="$TMPDIR_TEST/workspace/supervisor"
export RUNTIME_ROOT="$TMPDIR_TEST/workspace/runtime"
export WORKSPACE_HANDOFF_DIR="$TMPDIR_TEST/workspace/runtime/.handoff"
export WORKSPACE_TELEMETRY_DIR="$TMPDIR_TEST/workspace/runtime/.telemetry"
export WORKSPACE_SUPERVISOR_EVENTS_FILE="$TMPDIR_TEST/workspace/supervisor/events/supervisor-events.jsonl"
export WORKSPACE_SUPERVISOR_HANDOFF_INBOX="$TMPDIR_TEST/workspace/supervisor/handoffs/INBOX"
export WORKSPACE_SESSION_CONF="$TMPDIR_TEST/sessions.conf"

mkdir -p "$WORKSPACE_HANDOFF_DIR" "$WORKSPACE_TELEMETRY_DIR" \
         "$(dirname "$WORKSPACE_SUPERVISOR_EVENTS_FILE")" \
         "$WORKSPACE_SUPERVISOR_HANDOFF_INBOX"

# Create a minimal sessions.conf
echo "testproj|$TMPDIR_TEST/project|claude|pm" > "$WORKSPACE_SESSION_CONF"
mkdir -p "$TMPDIR_TEST/project"

# Create a fake handoff
echo "# Test handoff" > "$WORKSPACE_HANDOFF_DIR/testproj-test-2026-01-01.md"

PASS=0
FAIL=0

assert_eq() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$expected" == "$actual" ]]; then
    echo "  PASS: $desc"
    PASS=$(( PASS + 1 ))
  else
    echo "  FAIL: $desc — expected '$expected', got '$actual'"
    FAIL=$(( FAIL + 1 ))
  fi
}

assert_file_exists() {
  local desc="$1" pattern="$2"
  local found
  found=$(find "$3" -name "$pattern" 2>/dev/null | head -1)
  if [[ -n "$found" ]]; then
    echo "  PASS: $desc"
    PASS=$(( PASS + 1 ))
  else
    echo "  FAIL: $desc — no file matching '$pattern' in $3"
    FAIL=$(( FAIL + 1 ))
  fi
}

assert_grep() {
  local desc="$1" pattern="$2" file="$3"
  if grep -qE "$pattern" "$file" 2>/dev/null; then
    echo "  PASS: $desc"
    PASS=$(( PASS + 1 ))
  else
    echo "  FAIL: $desc — pattern '$pattern' not found in $file"
    FAIL=$(( FAIL + 1 ))
  fi
}

# --- Test 1: 401 pattern detection triggers escalation ---
echo "Test 1: 401 pattern detection"

# Create fake tick output containing 401 error
FAKE_LOG="$TMPDIR_TEST/tick-output.log"
cat > "$FAKE_LOG" <<'EOF'
Starting session...
Error: Invalid authentication credentials (status 401)
Session terminated.
EOF

# Extract and run just the detection block from the tick script.
# We simulate the variables that would exist at that point in the script.
PROJECT_NAME="testproj"
ISO_NOW="2026-01-01T00-00-00Z"
HANDOFF_BASENAME="testproj-test-2026-01-01.md"
EXIT_CODE=1
TICK_OUTPUT_LOG="$FAKE_LOG"

# Source workspace-paths for the emit_event function definition
# (we already exported all needed vars above)

emit_event() {
  local type="$1" note="$2" ref="${3:-}"
  printf '{"ts":"%s","agent":"tick-%s","type":"%s","ref":"%s","note":"%s"}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$PROJECT_NAME" "$type" "$ref" "$note" \
    >> "$WORKSPACE_SUPERVISOR_EVENTS_FILE"
}

# Run the detection logic (extracted from supervisor-project-tick.sh lines 194+)
if grep -qiE 'Invalid authentication credentials|"status":[[:space:]]*401|\b401\b.*auth|authentication.*failed|Unauthorized' "$TICK_OUTPUT_LOG" 2>/dev/null; then
  AUTH_FAIL_HANDOFF="$WORKSPACE_SUPERVISOR_HANDOFF_INBOX/URGENT-${PROJECT_NAME}-tick-auth-failure-${ISO_NOW}.md"
  mkdir -p "$WORKSPACE_SUPERVISOR_HANDOFF_INBOX"
  {
    echo "# URGENT — ${PROJECT_NAME} tick auth failure (401)"
    echo
    echo "- **Project**: ${PROJECT_NAME}"
    echo "- **Handoff being processed**: ${HANDOFF_BASENAME}"
  } > "$AUTH_FAIL_HANDOFF"
  emit_event "project_tick_auth_failed" \
    "401 auth failure detected — escalated via URGENT handoff" \
    "$AUTH_FAIL_HANDOFF"
  mkdir -p "$WORKSPACE_TELEMETRY_DIR"
  printf '{"project":"%s","source":"%s.tick","eventType":"tick.escalated","level":"error","sourceType":"system","timestamp":%s,"details":{"reason":"401_auth_failure","handoff":"%s","exitCode":%d}}\n' \
    "$PROJECT_NAME" "$PROJECT_NAME" "$(date -u +%s%3N)" "$HANDOFF_BASENAME" "$EXIT_CODE" \
    >> "$WORKSPACE_TELEMETRY_DIR/events.jsonl"
  DETECTED=1
else
  DETECTED=0
fi

assert_eq "401 pattern detected" "1" "$DETECTED"
assert_file_exists "URGENT handoff created" "URGENT-testproj-*" "$WORKSPACE_SUPERVISOR_HANDOFF_INBOX"
assert_grep "handoff contains project name" "testproj" "$AUTH_FAIL_HANDOFF"
assert_grep "S1-P2 event emitted" '"eventType":"tick.escalated"' "$WORKSPACE_TELEMETRY_DIR/events.jsonl"
assert_grep "S1-P2 event has sourceType" '"sourceType":"system"' "$WORKSPACE_TELEMETRY_DIR/events.jsonl"
assert_grep "S1-P2 event has reason" '"reason":"401_auth_failure"' "$WORKSPACE_TELEMETRY_DIR/events.jsonl"
assert_grep "supervisor event emitted" '"type":"project_tick_auth_failed"' "$WORKSPACE_SUPERVISOR_EVENTS_FILE"

# --- Test 2: non-401 output does NOT trigger escalation ---
echo ""
echo "Test 2: non-401 output does not trigger"

CLEAN_LOG="$TMPDIR_TEST/clean-output.log"
cat > "$CLEAN_LOG" <<'EOF'
Starting session...
Processing handoff...
All tasks completed successfully.
EOF

if grep -qiE 'Invalid authentication credentials|"status":[[:space:]]*401|\b401\b.*auth|authentication.*failed|Unauthorized' "$CLEAN_LOG" 2>/dev/null; then
  FALSE_POSITIVE=1
else
  FALSE_POSITIVE=0
fi

assert_eq "clean output not flagged" "0" "$FALSE_POSITIVE"

# --- Summary ---
echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
