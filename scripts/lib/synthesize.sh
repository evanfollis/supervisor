#!/usr/bin/env bash
# Workspace synthesis driver. Reads per-project reflections from
# /opt/workspace/runtime/.meta/*-reflection-*.md, looks for cross-cutting patterns,
# and proposes workspace-level changes. Uses Opus (architectural reasoning).
# Scheduled offset +2h from per-project reflections so latest data is in.
#
# Usage: synthesize.sh
# Outputs: /opt/workspace/runtime/.meta/cross-cutting-<iso>.md

set -euo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"
PROMPT_TEMPLATE="$LIB_DIR/synthesize-prompt.md"
META_DIR="$WORKSPACE_META_DIR"
ISO_NOW="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
OUTPUT_FILE="$META_DIR/cross-cutting-${ISO_NOW}.md"

mkdir -p "$META_DIR"

# Short-circuit: need at least 2 non-skipped reflections in last 24h to synthesize.
RECENT_COUNT=0
for f in "$META_DIR"/*-reflection-*.md; do
  [[ -f "$f" ]] || continue
  if find "$f" -newermt "24 hours ago" 2>/dev/null | grep -q .; then
    head -n 1 "$f" | grep -q "Reflection skipped" && continue
    RECENT_COUNT=$((RECENT_COUNT + 1))
  fi
done

if [[ "$RECENT_COUNT" -lt 2 ]]; then
  printf '# Synthesis skipped — only %d substantive reflections in last 24h (need ≥2)\n' "$RECENT_COUNT" > "$OUTPUT_FILE"
  echo "synthesize: short-circuit ($RECENT_COUNT reflections)"
  exit 0
fi

PROMPT="$(sed \
  -e "s|{{ISO_NOW}}|$ISO_NOW|g" \
  -e "s|{{OUTPUT_FILE}}|$OUTPUT_FILE|g" \
  -e "s|{{WORKSPACE_META_DIR}}|$WORKSPACE_META_DIR|g" \
  -e "s|{{WORKSPACE_ROOT_CLAUDE_MD}}|$WORKSPACE_ROOT_CLAUDE_MD|g" \
  -e "s|{{WORKSPACE_TELEMETRY_FILE}}|$WORKSPACE_TELEMETRY_DIR/events.jsonl|g" \
  -e "s|{{WORKSPACE_SCRIPTS_ROOT}}|$WORKSPACE_SCRIPTS_ROOT|g" \
  "$PROMPT_TEMPLATE")"

cd "$WORKSPACE_ROOT"

claude -p "$PROMPT" \
  --model claude-opus-4-6 \
  --effort high \
  --disallowedTools \
    "Bash(git commit:*)" "Bash(git push:*)" "Bash(git reset:*)" \
    "Bash(git rebase:*)" "Bash(git checkout:*)" "Bash(git merge:*)" \
    "Bash(git add:*)" "Bash(git restore:*)" "Bash(git clean:*)" \
    "Bash(rm:*)" "Bash(mv:*)" "Bash(systemctl:*)" "Bash(docker:*)" \
    "Edit" "NotebookEdit" \
  2>&1 | tail -n 80

if [[ -f "$OUTPUT_FILE" ]]; then
  echo "synthesize: wrote $OUTPUT_FILE"
else
  echo "synthesize: WARNING — no output file produced" >&2
  exit 2
fi

# Notify the 'general' tmux session if it's alive. Uses display-message so
# we don't touch whatever's focused in the session (e.g. an open Claude prompt).
if command -v tmux >/dev/null 2>&1 && tmux has-session -t general 2>/dev/null; then
  tmux display-message -t general "synthesis ready: $OUTPUT_FILE"
  echo "synthesize: notified general session (tmux display-message)"
fi

# Also drop a pointer file the general session can pick up on next reflection.
echo "$OUTPUT_FILE" > "$WORKSPACE_LATEST_SYNTHESIS_PTR"
