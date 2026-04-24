#!/usr/bin/env bash
# Per-project 12h reflection driver.
# Spawns claude -p in the project directory with a scoped toolset and the
# artifact-driven prompt template. Reflection is read-only and propose-only:
# it writes exactly one file to <project>/.meta/<project>-reflection-<iso>.md
# and never commits or pushes.
#
# Usage: reflect.sh <project-name> <project-dir>
#   reflect.sh command /opt/workspace/projects/command
#
# Short-circuits if there's been no activity in the last 12h.

set -euo pipefail

PROJECT="${1:?project name required}"
PROJECT_DIR="${2:?project dir required}"
PROMPT_TEMPLATE_OVERRIDE="${3:-}"
LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"
if [[ -n "$PROMPT_TEMPLATE_OVERRIDE" ]]; then
  # Allow either absolute path or a basename resolved under LIB_DIR.
  if [[ "$PROMPT_TEMPLATE_OVERRIDE" == /* ]]; then
    PROMPT_TEMPLATE="$PROMPT_TEMPLATE_OVERRIDE"
  else
    PROMPT_TEMPLATE="$LIB_DIR/$PROMPT_TEMPLATE_OVERRIDE"
  fi
else
  PROMPT_TEMPLATE="$LIB_DIR/reflect-prompt.md"
fi
if [[ ! -f "$PROMPT_TEMPLATE" ]]; then
  echo "reflect: prompt template not found: $PROMPT_TEMPLATE" >&2
  exit 1
fi

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "reflect: project dir not found: $PROJECT_DIR" >&2
  exit 1
fi

META_DIR="$WORKSPACE_META_DIR"
mkdir -p "$META_DIR"
ISO_NOW="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
OUTPUT_FILE="$META_DIR/${PROJECT}-reflection-${ISO_NOW}.md"
WORKSPACE_SESSION_MEMORY_DIR="/root/.claude/projects/-$(echo "$WORKSPACE_ROOT" | sed 's|^/||; s|/|-|g')/memory"

# Claude Code's per-cwd JSONL directory. Encoding: slashes → hyphens, prefix "-".
# e.g. /opt/workspace/projects/atlas → -opt-workspace-projects-atlas
SESSION_DIR="/root/.claude/projects/-$(echo "$PROJECT_DIR" | sed 's|^/||; s|/|-|g')"

# Pre-flight activity check — avoid spawning Claude if nothing happened.
COMMIT_COUNT=0
if [[ -d "$PROJECT_DIR/.git" ]]; then
  COMMIT_COUNT=$(git -C "$PROJECT_DIR" log --since="12 hours ago" --oneline 2>/dev/null | wc -l || echo 0)
fi

TELEMETRY_COUNT=0
if [[ -f "$WORKSPACE_TELEMETRY_DIR/events.jsonl" ]]; then
  # Rough filter: events whose JSON mentions the project name in the last ~12h slice of the file.
  # (Per-project telemetry filtering is best-effort; the Claude session does the authoritative read.)
  TELEMETRY_COUNT=$(tail -n 5000 "$WORKSPACE_TELEMETRY_DIR/events.jsonl" 2>/dev/null | grep -c -F "\"$PROJECT\"" || true)
fi

# Session JSONL activity: count transcript files modified in the last 12h.
JSONL_RECENT=0
if [[ -d "$SESSION_DIR" ]]; then
  JSONL_RECENT=$(find "$SESSION_DIR" -maxdepth 1 -name '*.jsonl' -newermt "12 hours ago" 2>/dev/null | wc -l)
fi

if [[ "$COMMIT_COUNT" -eq 0 && "$TELEMETRY_COUNT" -eq 0 && "$JSONL_RECENT" -eq 0 ]]; then
  printf '# Reflection skipped — no activity in window ending %s\n' "$ISO_NOW" > "$OUTPUT_FILE"
  echo "reflect[$PROJECT]: short-circuit (no commits, no telemetry, no session activity)"
  exit 0
fi

# Render the prompt with substitutions.
PROMPT="$(sed \
  -e "s|{{PROJECT}}|$PROJECT|g" \
  -e "s|{{PROJECT_DIR}}|$PROJECT_DIR|g" \
  -e "s|{{OUTPUT_FILE}}|$OUTPUT_FILE|g" \
  -e "s|{{ISO_NOW}}|$ISO_NOW|g" \
  -e "s|{{SESSION_DIR}}|$SESSION_DIR|g" \
  -e "s|{{WORKSPACE_TELEMETRY_FILE}}|$WORKSPACE_TELEMETRY_DIR/events.jsonl|g" \
  -e "s|{{WORKSPACE_META_DIR}}|$WORKSPACE_META_DIR|g" \
  -e "s|{{WORKSPACE_ROOT_CLAUDE_MD}}|$WORKSPACE_ROOT_CLAUDE_MD|g" \
  -e "s|{{WORKSPACE_HANDOFF_DIR}}|$WORKSPACE_HANDOFF_DIR|g" \
  -e "s|{{WORKSPACE_SESSION_MEMORY_DIR}}|$WORKSPACE_SESSION_MEMORY_DIR|g" \
  "$PROMPT_TEMPLATE")"

# Safety net — capture HEAD and working tree state. If the reflection session
# mutates the repo despite --disallowedTools, we abort loudly.
BEFORE_HEAD="none"
BEFORE_DIRTY=""
if [[ -d "$PROJECT_DIR/.git" ]]; then
  BEFORE_HEAD=$(git -C "$PROJECT_DIR" rev-parse HEAD 2>/dev/null || echo none)
  BEFORE_DIRTY=$(git -C "$PROJECT_DIR" status --porcelain 2>/dev/null || true)
fi

cd "$PROJECT_DIR"

# --dangerously-skip-permissions is required for non-interactive runs; it
# bypasses the allowlist, so the safety net is --disallowedTools blocking
# anything that could mutate the repo, plus the prompt's propose-only contract.
claude -p "$PROMPT" \
  --model claude-sonnet-4-6 \
  --effort medium \
  --disallowedTools \
    "Bash(git commit:*)" "Bash(git push:*)" "Bash(git reset:*)" \
    "Bash(git rebase:*)" "Bash(git checkout:*)" "Bash(git merge:*)" \
    "Bash(git add:*)" "Bash(git restore:*)" "Bash(git clean:*)" \
    "Bash(rm:*)" "Bash(mv:*)" "Bash(npm publish:*)" "Bash(gh pr:*)" \
    "Bash(gh release:*)" "Bash(docker:*)" "Bash(systemctl:*)" \
    "Edit" "NotebookEdit" \
  2>&1 | tail -n 80

if [[ -f "$OUTPUT_FILE" ]]; then
  echo "reflect[$PROJECT]: wrote $OUTPUT_FILE"
else
  echo "reflect[$PROJECT]: WARNING — no output file produced" >&2
  exit 2
fi

resolve_claim_path() {
  local raw="$1"
  if [[ "$raw" == /* ]]; then
    printf '%s\n' "$raw"
  elif [[ "$raw" == runtime/* || "$raw" == supervisor/* || "$raw" == projects/* ]]; then
    printf '%s\n' "$WORKSPACE_ROOT/$raw"
  else
    printf '%s\n' "$PROJECT_DIR/$raw"
  fi
}

# Reflection output feeds synthesis and executive reentry. Claims about
# written handoffs/files must be real or they create false confidence.
mapfile -t CLAIMED_FILES < <(grep -oP '(?:Writing|Filed handoff) `\K[^`]+' "$OUTPUT_FILE" 2>/dev/null | sort -u || true)
MISSING_CLAIMS=()
for raw_path in "${CLAIMED_FILES[@]}"; do
  resolved_path="$(resolve_claim_path "$raw_path")"
  if [[ ! -e "$resolved_path" ]]; then
    MISSING_CLAIMS+=("$raw_path")
  fi
done

if [[ "${#MISSING_CLAIMS[@]}" -gt 0 ]]; then
  {
    printf '\n## Verification warnings\n'
    printf '\nThe reflection text claims actions that did not land on disk:\n'
    for missing in "${MISSING_CLAIMS[@]}"; do
      printf -- '- WARNING: claimed file `%s` does not exist.\n' "$missing"
    done
  } >> "$OUTPUT_FILE"
fi

# Safety net — verify the reflection session did not mutate the repo.
if [[ -d "$PROJECT_DIR/.git" ]]; then
  AFTER_HEAD=$(git -C "$PROJECT_DIR" rev-parse HEAD 2>/dev/null || echo none)
  AFTER_DIRTY=$(git -C "$PROJECT_DIR" status --porcelain 2>/dev/null || true)
  mkdir -p "$WORKSPACE_HANDOFF_DIR"
  if [[ "$BEFORE_HEAD" != "$AFTER_HEAD" ]]; then
    echo "reflect[$PROJECT]: CRITICAL — HEAD changed ($BEFORE_HEAD → $AFTER_HEAD). Reflection is supposed to be read-only." >&2
    cat > "$WORKSPACE_HANDOFF_DIR/URGENT-${PROJECT}-reflection-mutated-head.md" <<EOF
Reflection session for ${PROJECT} at ${ISO_NOW} advanced HEAD from
${BEFORE_HEAD} to ${AFTER_HEAD}. --disallowedTools did not catch it.
Investigate immediately — the blocklist pattern for git writes may be
incorrect, or the model found an unblocked path (gh, curl, direct fs).
EOF
    exit 3
  fi
  # Filter out context front-door files (CONTEXT.md, CURRENT_STATE.md) —
  # reflections are permitted (and expected) to maintain them.
  # Any other working-tree mutation is unexpected.
  BEFORE_DIRTY_FILTERED=$(echo "$BEFORE_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md' || true)
  AFTER_DIRTY_FILTERED=$(echo "$AFTER_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md' || true)
  if [[ "$BEFORE_DIRTY_FILTERED" != "$AFTER_DIRTY_FILTERED" ]]; then
    echo "reflect[$PROJECT]: WARNING — working tree changed during reflection (excluding CURRENT_STATE.md)." >&2
    cat > "$WORKSPACE_HANDOFF_DIR/URGENT-${PROJECT}-reflection-dirty-tree.md" <<EOF
Reflection session for ${PROJECT} at ${ISO_NOW} modified the working tree
(excluding expected CURRENT_STATE.md writes).
Before:
${BEFORE_DIRTY}
After:
${AFTER_DIRTY}
EOF
  fi

  # Post-reflection CURRENT_STATE.md auto-commit (cross-cutting 2026-04-20T03:25Z
  # Proposal 2 Option A). Reflections Write CURRENT_STATE.md, but --disallowedTools
  # blocks the in-session commit, leaving updates uncommitted for 24–48h and
  # silently dropped on next merge. Commit exactly that path here; all other
  # working-tree changes already triggered the warning above and are left as-is.
  if [[ -f "$PROJECT_DIR/CURRENT_STATE.md" ]] \
     && ! git -C "$PROJECT_DIR" diff --quiet -- CURRENT_STATE.md 2>/dev/null; then
    if git -C "$PROJECT_DIR" commit --only -- CURRENT_STATE.md \
         -m "reflect: auto-update CURRENT_STATE.md ${ISO_NOW}" \
         -m "Generated by scripts/lib/reflect.sh after the ${PROJECT} reflection session." \
         -m "session_id=reflect-${PROJECT}-${ISO_NOW}" \
         >/dev/null 2>&1; then
      echo "reflect[$PROJECT]: committed CURRENT_STATE.md update"
    else
      echo "reflect[$PROJECT]: WARNING — CURRENT_STATE.md commit failed (pre-commit hook? staged conflict?)" >&2
    fi
  fi
fi
