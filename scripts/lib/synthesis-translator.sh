#!/usr/bin/env bash
# synthesis-translator.sh — translate synthesis proposals into executable handoffs.
#
# Closes the translation gap identified 2026-04-23: the synthesize.sh job
# writes diagnostic output to runtime/.meta/cross-cutting-*.md but nothing
# converts those concrete proposals into handoffs that sessions actually
# pick up and execute. Without this primitive, synthesis proposals sit
# unexecuted indefinitely, producing "perfect diagnosis, zero execution"
# (see cross-cutting-2026-04-23T15-24-05Z.md §Headline).
#
# Usage: synthesis-translator.sh <synthesis-file>
#
# Called from synthesize.sh immediately after the main synthesis run so
# every synthesis cycle auto-emits handoffs for its live proposals.
#
# Output:
#   - Handoffs to /opt/workspace/runtime/.handoff/ for project-scope work
#   - Handoffs to /opt/workspace/supervisor/handoffs/INBOX/ for supervisor-scope
#
# Policy: applies the "people-or-money" rubric — anything that isn't a named
# external human or a dollar amount is autonomous-bucket.

set -euo pipefail

SYNTHESIS_FILE="${1:-}"
if [[ -z "$SYNTHESIS_FILE" || ! -f "$SYNTHESIS_FILE" ]]; then
  echo "usage: $0 <synthesis-file>" >&2
  echo "       synthesis file not found: ${SYNTHESIS_FILE:-<missing>}" >&2
  exit 2
fi

# Short-circuit if the synthesis itself short-circuited.
if head -1 "$SYNTHESIS_FILE" | grep -q '^# Synthesis skipped'; then
  echo "synthesis-translator: source short-circuited; nothing to translate"
  exit 0
fi

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPT_TEMPLATE="$LIB_DIR/synthesis-translator-prompt.md"
ISO_FILENAME="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
ISO_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
HANDOFF_DIR="/opt/workspace/runtime/.handoff"
INBOX_DIR="/opt/workspace/supervisor/handoffs/INBOX"
LOG_FILE="/opt/workspace/runtime/.meta/synthesis-translator-${ISO_FILENAME}.log"

mkdir -p "$HANDOFF_DIR" "$INBOX_DIR" "$(dirname "$LOG_FILE")"

if [[ ! -f "$PROMPT_TEMPLATE" ]]; then
  echo "synthesis-translator: prompt template missing: $PROMPT_TEMPLATE" >&2
  exit 1
fi

PROMPT="$(sed \
  -e "s|{{SYNTHESIS_FILE}}|$SYNTHESIS_FILE|g" \
  -e "s|{{ISO_NOW}}|$ISO_TS|g" \
  -e "s|{{ISO_FILENAME}}|$ISO_FILENAME|g" \
  -e "s|{{HANDOFF_DIR}}|$HANDOFF_DIR|g" \
  -e "s|{{INBOX_DIR}}|$INBOX_DIR|g" \
  "$PROMPT_TEMPLATE")"

echo "synthesis-translator: translating $SYNTHESIS_FILE"

# Haiku is fast + cheap + sufficient for the parse-and-emit shape.
# --disallowedTools blocks anything that could write outside the two target
#   dirs, run git, delete files, or shell out destructively. The translator
#   only needs the Read tool (to read the synthesis + target repos for
#   verification) and the Write tool (to emit handoffs).
# Match the permission-mode pattern used by synthesize.sh (no
# --dangerously-skip-permissions; that flag is rejected when running as
# root). --permission-mode acceptEdits permits Write/Edit to proceed in a
# non-interactive systemd service context without prompting.
claude -p "$PROMPT" \
  --model claude-haiku-4-5-20251001 \
  --permission-mode acceptEdits \
  --disallowedTools \
    "Bash(git commit:*)" "Bash(git push:*)" "Bash(git reset:*)" \
    "Bash(git rebase:*)" "Bash(git checkout:*)" "Bash(git merge:*)" \
    "Bash(git add:*)" "Bash(git restore:*)" "Bash(git clean:*)" \
    "Bash(rm:*)" "Bash(mv:*)" "Bash(cp:*)" "Bash(systemctl:*)" \
    "Bash(docker:*)" "Bash(tmux send-keys:*)" \
    "Edit" "NotebookEdit" \
  2>&1 | tee "$LOG_FILE" | tail -n 40

EXIT_CODE="${PIPESTATUS[0]}"
if [[ "$EXIT_CODE" -ne 0 ]]; then
  echo "synthesis-translator: claude returned non-zero ($EXIT_CODE); see $LOG_FILE" >&2
  exit "$EXIT_CODE"
fi

# Emit a structured completion event so synthesis job + reflection can
# observe the translation rate (friction event shape per ADR-0029 §Layer 5).
EVENTS_FILE="/opt/workspace/runtime/friction/events.jsonl"
mkdir -p "$(dirname "$EVENTS_FILE")"
printf '{"ts":"%s","layer":"validation","source":"synthesis-translator","eventType":"success","reason":"translation complete","ref":"%s"}\n' \
  "$ISO_TS" "$SYNTHESIS_FILE" >> "$EVENTS_FILE"

echo "synthesis-translator: complete at $ISO_TS (log: $LOG_FILE)"
