#!/usr/bin/env bash
# supervisor-project-tick.sh — per-project headless execution dispatch.
# Reads the oldest pending handoff for PROJECT_NAME and executes it via
# a headless claude session rooted in the project cwd.
# See ADR-0016 for the full contract.
#
# Usage: supervisor-project-tick.sh <project-name>
#        (also called from workspace-project-tick@<name>.service via %i)

set -uo pipefail

PROJECT_NAME="${1:-}"
if [[ -z "$PROJECT_NAME" ]]; then
  echo "supervisor-project-tick: usage: $0 <project-name>" >&2
  exit 1
fi

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$LIB_DIR/workspace-paths.sh"

ISO_NOW="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
LOCK_DIR="$RUNTIME_ROOT/.locks"
LOCK_FILE="$LOCK_DIR/project-tick-${PROJECT_NAME}.lock"
EVENT_FILE="$WORKSPACE_SUPERVISOR_EVENTS_FILE"
PROMPT_TEMPLATE="$LIB_DIR/supervisor-project-tick-prompt.md"

mkdir -p "$LOCK_DIR" "$(dirname "$EVENT_FILE")"

emit_event() {
  local type="$1" note="$2" ref="${3:-}"
  printf '{"ts":"%s","agent":"tick-%s","type":"%s","ref":"%s","note":"%s"}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$PROJECT_NAME" "$type" "$ref" "$note" \
    >> "$EVENT_FILE"
}

# --- 1. self-race lock --------------------------------------------------------
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "supervisor-project-tick[$PROJECT_NAME]: already running, exiting"
  exit 0
fi

# --- 2. find project cwd from sessions.conf -----------------------------------
PROJECT_CWD=""
while IFS='|' read -r name cwd _agent _role; do
  [[ "${name}" == "${PROJECT_NAME}" ]] && PROJECT_CWD="${cwd}" && break
done < <(grep -v '^#' "$WORKSPACE_SESSION_CONF")

if [[ -z "$PROJECT_CWD" ]]; then
  echo "supervisor-project-tick[$PROJECT_NAME]: not found in sessions.conf" >&2
  exit 1
fi

if [[ ! -d "$PROJECT_CWD" ]]; then
  echo "supervisor-project-tick[$PROJECT_NAME]: PROJECT_CWD=$PROJECT_CWD does not exist" >&2
  exit 1
fi

# --- 3. attended-session interlock -------------------------------------------
# Skip if the project's tmux session was active in the last 15 min.
if command -v tmux >/dev/null 2>&1 && tmux has-session -t "$PROJECT_NAME" 2>/dev/null; then
  last_activity=$(tmux display-message -p -t "$PROJECT_NAME" '#{session_activity}' 2>/dev/null || echo 0)
  now_epoch=$(date -u +%s)
  if [[ "$last_activity" =~ ^[0-9]+$ ]] && (( now_epoch - last_activity < 900 )); then
    echo "supervisor-project-tick[$PROJECT_NAME]: attended session active $(( (now_epoch - last_activity) / 60 )) min ago — skipping"
    exit 0
  fi
fi

# --- 4. find oldest pending handoff -------------------------------------------
HANDOFF_FILE=""
while IFS= read -r candidate; do
  [[ -f "$candidate" ]] || continue
  HANDOFF_FILE="$candidate"
  break
done < <(
  find "$WORKSPACE_HANDOFF_DIR" -maxdepth 1 \
    -name "${PROJECT_NAME}-*.md" \
    ! -name "README.md" \
    -printf '%T@ %p\n' 2>/dev/null \
    | sort -n \
    | awk '{print $2}'
)

if [[ -z "$HANDOFF_FILE" ]]; then
  echo "supervisor-project-tick[$PROJECT_NAME]: no pending handoffs"
  exit 0
fi

HANDOFF_BASENAME="$(basename "$HANDOFF_FILE")"
echo "supervisor-project-tick[$PROJECT_NAME]: processing $HANDOFF_BASENAME"
emit_event "project_tick_started" "processing $HANDOFF_BASENAME" "$HANDOFF_FILE"

# --- 5. render the prompt via Python (handles multiline content safely) -------
if [[ ! -f "$PROMPT_TEMPLATE" ]]; then
  echo "supervisor-project-tick[$PROJECT_NAME]: prompt template missing: $PROMPT_TEMPLATE" >&2
  emit_event "project_tick_failed" "prompt template missing" "$HANDOFF_FILE"
  exit 1
fi

PROMPT_FILE="$(mktemp /tmp/project-tick-prompt-XXXXXX.md)"
# shellcheck disable=SC2064
trap "rm -f '$PROMPT_FILE'" EXIT

# Export as env vars so the python heredoc can read them without quoting issues
export TICK_PROJECT_NAME="$PROJECT_NAME"
export TICK_ISO_NOW="$ISO_NOW"
export TICK_PROJECT_CWD="$PROJECT_CWD"
export TICK_HANDOFF_FILE="$HANDOFF_FILE"
export TICK_HANDOFF_BASENAME="$HANDOFF_BASENAME"
export TICK_WORKSPACE_HANDOFF_DIR="$WORKSPACE_HANDOFF_DIR"
export TICK_LIB_DIR="$LIB_DIR"

python3 - > "$PROMPT_FILE" <<'PYEOF'
import os, sys
from pathlib import Path

template = Path(os.environ['TICK_LIB_DIR'] + '/supervisor-project-tick-prompt.md').read_text()
project_cwd = os.environ['TICK_PROJECT_CWD']

claude_md_path = Path(project_cwd) / 'CLAUDE.md'
claude_md = (
    ''.join(claude_md_path.read_text().splitlines(keepends=True)[:80])
    if claude_md_path.exists()
    else '(no CLAUDE.md found)'
)

# Discover the project's context front-door file.
# Convention: CONTEXT.md takes priority; fall back to CURRENT_STATE.md.
# Agents may use either name; they own their repo's structure.
ctx_candidates = ['CONTEXT.md', 'CURRENT_STATE.md']
current_state_path = None
for name in ctx_candidates:
    candidate = Path(project_cwd) / name
    if candidate.exists():
        current_state_path = candidate
        break

current_state = (
    current_state_path.read_text()
    if current_state_path
    else ('(no context front-door file found — create CONTEXT.md or CURRENT_STATE.md as part of this tick.\n'
          'Use /opt/workspace/supervisor/scripts/lib/CURRENT_STATE_TEMPLATE.md as a starting point,\n'
          'but design the structure to fit this project. You own it.)')
)

handoff = Path(os.environ['TICK_HANDOFF_FILE']).read_text()

subs = {
    '{{PROJECT_NAME}}':          os.environ['TICK_PROJECT_NAME'],
    '{{ISO_NOW}}':               os.environ['TICK_ISO_NOW'],
    '{{PROJECT_CWD}}':           os.environ['TICK_PROJECT_CWD'],
    '{{HANDOFF_FILE}}':          os.environ['TICK_HANDOFF_FILE'],
    '{{HANDOFF_BASENAME}}':      os.environ['TICK_HANDOFF_BASENAME'],
    '{{WORKSPACE_HANDOFF_DIR}}': os.environ['TICK_WORKSPACE_HANDOFF_DIR'],
    '{{PROJECT_CLAUDE_MD}}':     claude_md,
    '{{CURRENT_STATE}}':         current_state,
    '{{HANDOFF_CONTENT}}':       handoff,
}
for k, v in subs.items():
    template = template.replace(k, v)
sys.stdout.write(template)
PYEOF

if [[ ! -s "$PROMPT_FILE" ]]; then
  echo "supervisor-project-tick[$PROJECT_NAME]: prompt rendering failed" >&2
  emit_event "project_tick_failed" "prompt rendering failed" "$HANDOFF_FILE"
  exit 1
fi

# --- 6. run the headless session ----------------------------------------------
cd "$PROJECT_CWD"

EXIT_CODE=0
claude -p "$(cat "$PROMPT_FILE")" \
  --model claude-sonnet-4-6 \
  --disallowedTools \
    "Bash(git push --force:*)" \
    "Bash(git reset --hard:*)" \
    "Bash(git rebase:*)" \
    "Bash(rm -rf:*)" \
    "Bash(docker:*)" \
    "Bash(systemctl:*)" \
    "Bash(npm publish:*)" \
    "Bash(gh release:*)" \
    "NotebookEdit" \
  2>&1 | tail -n 200 || EXIT_CODE=$?

# --- 7. emit completion or escalation event -----------------------------------
COMPLETION_FILE="${WORKSPACE_HANDOFF_DIR}/general-${PROJECT_NAME}-tick-complete-${ISO_NOW}.md"
ESCALATION_FILE="${WORKSPACE_HANDOFF_DIR}/general-${PROJECT_NAME}-tick-escalation-${ISO_NOW}.md"

if [[ -f "$ESCALATION_FILE" ]]; then
  emit_event "project_tick_escalated" \
    "escalation for $HANDOFF_BASENAME — see $(basename "$ESCALATION_FILE")" \
    "$ESCALATION_FILE"
  echo "supervisor-project-tick[$PROJECT_NAME]: escalated — $ESCALATION_FILE"
elif [[ -f "$COMPLETION_FILE" ]]; then
  emit_event "project_tick_succeeded" \
    "completed $HANDOFF_BASENAME" \
    "$COMPLETION_FILE"
  echo "supervisor-project-tick[$PROJECT_NAME]: completed — $COMPLETION_FILE"
elif [[ "$EXIT_CODE" -ne 0 ]]; then
  emit_event "project_tick_failed" \
    "claude exit $EXIT_CODE processing $HANDOFF_BASENAME" \
    "$HANDOFF_FILE"
  echo "supervisor-project-tick[$PROJECT_NAME]: FAILED (exit $EXIT_CODE)" >&2
  exit "$EXIT_CODE"
else
  # Model ran but wrote no report — still treat as done (may have deleted handoff)
  emit_event "project_tick_succeeded" \
    "completed $HANDOFF_BASENAME (no report written)" \
    "$HANDOFF_FILE"
  echo "supervisor-project-tick[$PROJECT_NAME]: done (no report written)"
fi

exit 0
