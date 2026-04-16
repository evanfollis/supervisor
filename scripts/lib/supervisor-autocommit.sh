#!/usr/bin/env bash
# supervisor-autocommit.sh — Tier-A governance auto-commit (S3-P3).
#
# Runs every 2h (independent of the supervisor tick). If Tier-A governance
# paths (friction/ handoffs/ system/ ideas/ decisions/) are dirty and no
# attended session has been active in the last 10 minutes, commit them to an
# autocommit/YYYY-MM-DD-HH branch and rewind main. This prevents a dirty
# Tier-A state from blocking the tick's dirty-tree gate indefinitely.
#
# Scope: Tier-A paths ONLY. Never touches Tier-C (project code). Never pushes.
# See decisions/0014-supervisor-tick-and-pm-pattern.md for branch/commit policy.

set -uo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$LIB_DIR/workspace-paths.sh"

SUP="$SUPERVISOR_ROOT"
ISO_NOW="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
EVENT_FILE="$WORKSPACE_SUPERVISOR_EVENTS_FILE"
LOCK_FILE="$RUNTIME_ROOT/.locks/supervisor-autocommit.lock"
mkdir -p "$RUNTIME_ROOT/.locks" "$(dirname "$EVENT_FILE")"

emit_event() {
  local type="$1" note="$2"
  printf '{"ts":"%s","agent":"autocommit","type":"%s","ref":"autocommit/%s","note":"%s"}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$type" "$ISO_NOW" "$note" \
    >> "$EVENT_FILE"
}

log() { echo "supervisor-autocommit: $*" >&2; }
skip() { log "SKIP — $1"; emit_event "session_reflected" "autocommit skipped — $1"; exit 0; }

# --- 1. self-race lock ---
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  skip "another autocommit holds the lock"
fi

# --- 2. repo must exist ---
[[ -d "$SUP/.git" ]] || skip "supervisor repo missing .git"

# --- 3. yield to attended session (tmux activity in last 10 min) ---
if command -v tmux >/dev/null 2>&1 && tmux has-session -t general 2>/dev/null; then
  last_activity=$(tmux display-message -p -t general '#{session_activity}' 2>/dev/null || echo 0)
  now_epoch=$(date -u +%s)
  if [[ "$last_activity" =~ ^[0-9]+$ ]] && (( now_epoch - last_activity < 600 )); then
    skip "general session active $(( (now_epoch - last_activity) / 60 )) min ago — deferring to human"
  fi
fi

# --- 4. check Tier-A dirty state ---
TIER_A_DIRTY=$(git -C "$SUP" status --porcelain \
  -- friction/ handoffs/ system/ ideas/ decisions/ 2>/dev/null || true)

[[ -n "$TIER_A_DIRTY" ]] || skip "Tier-A paths clean — nothing to commit"

# --- 5. stage Tier-A paths and commit to autocommit/ branch ---
PRE_HEAD=$(git -C "$SUP" rev-parse HEAD 2>/dev/null || skip "cannot resolve HEAD")

git -C "$SUP" add \
  friction/ handoffs/ system/ ideas/ decisions/ \
  2>/dev/null || true

if git -C "$SUP" diff --cached --quiet 2>/dev/null; then
  skip "staged diff empty after add (all changes may be gitignored)"
fi

BRANCH="autocommit/$(date -u +%Y-%m-%d-%H)"

git -C "$SUP" \
  -c user.email='autocommit@workspace.local' \
  -c user.name='supervisor-autocommit' \
  commit --quiet -m "autocommit ${ISO_NOW}: Tier-A governance artifacts

Automated pre-tick commit to prevent dirty-tree gate deadlock (S3-P3).
Tier-A paths only: friction/ handoffs/ system/ ideas/ decisions/.

agent: autocommit" || { log "commit failed"; emit_event "session_reflected" "autocommit commit failed"; exit 1; }

NEW_SHA=$(git -C "$SUP" rev-parse HEAD)
git -C "$SUP" branch -f "$BRANCH" "$NEW_SHA"
git -C "$SUP" reset --hard "$PRE_HEAD" >/dev/null

emit_event "session_reflected" "autocommit: Tier-A → $BRANCH (sha=${NEW_SHA:0:12})"
log "committed Tier-A writes to $BRANCH (sha=${NEW_SHA:0:12}); main rewound to $PRE_HEAD"
