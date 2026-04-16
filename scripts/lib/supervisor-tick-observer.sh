#!/usr/bin/env bash
# supervisor-tick-observer.sh — executive observation pass after a project tick.
# Spawns a brief headless claude session at /opt/workspace (executive posture)
# to review the tick completion/escalation report against the actual git state.
#
# Usage: supervisor-tick-observer.sh <project-name> <report-file> <report-type> <handoff-basename>
#   report-type: "completion" | "escalation" | "failed"
#
# Called from supervisor-project-tick.sh after the tick completes.
# Non-fatal — observer failure does not affect the tick's reported outcome.

set -uo pipefail

PROJECT_NAME="${1:-}"
REPORT_FILE="${2:-}"
REPORT_TYPE="${3:-completion}"
HANDOFF_BASENAME="${4:-unknown}"

if [[ -z "$PROJECT_NAME" || -z "$REPORT_FILE" ]]; then
  echo "supervisor-tick-observer: usage: $0 <project> <report-file> <type> <handoff>" >&2
  exit 1
fi

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$LIB_DIR/workspace-paths.sh"

ISO_NOW="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
EVENT_FILE="$WORKSPACE_SUPERVISOR_EVENTS_FILE"
PROMPT_TEMPLATE="$LIB_DIR/supervisor-tick-observer-prompt.md"
OBSERVATION_FILE="$WORKSPACE_META_DIR/tick-observation-${PROJECT_NAME}-${ISO_NOW}.md"

mkdir -p "$WORKSPACE_META_DIR"

emit_event() {
  local type="$1" note="$2" ref="${3:-}"
  printf '{"ts":"%s","agent":"observer-%s","type":"%s","ref":"%s","note":"%s"}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$PROJECT_NAME" "$type" "$ref" "$note" \
    >> "$EVENT_FILE"
}

if [[ ! -f "$PROMPT_TEMPLATE" ]]; then
  echo "supervisor-tick-observer: prompt template missing" >&2
  exit 1
fi

# Render the prompt — simple sed substitutions (no multiline content in observer prompt)
PROMPT_FILE="$(mktemp /tmp/tick-observer-prompt-XXXXXX.md)"
trap 'rm -f "$PROMPT_FILE"' EXIT

# Find the project cwd from sessions.conf
PROJECT_CWD=""
while IFS='|' read -r name cwd _agent _role; do
  [[ "${name}" == "${PROJECT_NAME}" ]] && PROJECT_CWD="${cwd}" && break
done < <(grep -v '^#' "$WORKSPACE_SESSION_CONF")

PROJECT_CWD="${PROJECT_CWD:-/opt/workspace/projects/$PROJECT_NAME}"

sed \
  -e "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" \
  -e "s|{{ISO_NOW}}|$ISO_NOW|g" \
  -e "s|{{REPORT_FILE}}|$REPORT_FILE|g" \
  -e "s|{{REPORT_TYPE}}|$REPORT_TYPE|g" \
  -e "s|{{HANDOFF_BASENAME}}|$HANDOFF_BASENAME|g" \
  -e "s|{{PROJECT_CWD}}|$PROJECT_CWD|g" \
  -e "s|{{OBSERVATION_FILE}}|$OBSERVATION_FILE|g" \
  -e "s|{{WORKSPACE_HANDOFF_DIR}}|$WORKSPACE_HANDOFF_DIR|g" \
  "$PROMPT_TEMPLATE" > "$PROMPT_FILE"

echo "supervisor-tick-observer[$PROJECT_NAME]: running observation pass..."

# Run the observer at the workspace root (executive posture via /opt/workspace/CLAUDE.md
# and /opt/workspace/supervisor/AGENT.md).
cd /opt/workspace

EXIT_CODE=0
claude -p "$(cat "$PROMPT_FILE")" \
  --model claude-sonnet-4-6 \
  --disallowedTools \
    "Bash(git commit:*)" "Bash(git push:*)" "Bash(git reset:*)" \
    "Bash(git add:*)" "Bash(rm:*)" "Bash(mv:*)" \
    "Bash(systemctl start:*)" "Bash(systemctl stop:*)" \
    "Bash(systemctl restart:*)" "Bash(systemctl enable:*)" \
    "Bash(docker:*)" \
    "Edit" "NotebookEdit" \
  2>&1 | tail -n 60 || EXIT_CODE=$?
# Note: "Write" is intentionally NOT blocked — the observer needs to write
# the observation file and any escalation handoffs (both in runtime/ paths).
# "Edit" IS blocked to prevent modifying existing source files.

if [[ -f "$OBSERVATION_FILE" ]]; then
  # Check verdict line to decide event type
  verdict=$(grep -i '^\\*\\*Verdict\\*\\*:' "$OBSERVATION_FILE" | head -1 | sed 's/.*: *//' | tr '[:upper:]' '[:lower:]' | tr -d ' ')
  case "$verdict" in
    flag)
      emit_event "tick_observation_flagged" \
        "observer flagged $PROJECT_NAME tick — see $OBSERVATION_FILE" \
        "$OBSERVATION_FILE"
      echo "supervisor-tick-observer[$PROJECT_NAME]: FLAGGED — $OBSERVATION_FILE"
      ;;
    concern)
      emit_event "tick_observation_concern" \
        "observer noted concern in $PROJECT_NAME tick" \
        "$OBSERVATION_FILE"
      echo "supervisor-tick-observer[$PROJECT_NAME]: concern noted — $OBSERVATION_FILE"
      ;;
    *)
      emit_event "tick_observation_clean" \
        "observer: $PROJECT_NAME tick looks clean" \
        "$OBSERVATION_FILE"
      echo "supervisor-tick-observer[$PROJECT_NAME]: clean"
      ;;
  esac
else
  echo "supervisor-tick-observer[$PROJECT_NAME]: no observation file written (exit $EXIT_CODE)" >&2
  emit_event "tick_observation_failed" \
    "observer produced no output for $PROJECT_NAME tick" \
    "$REPORT_FILE"
fi

exit 0
