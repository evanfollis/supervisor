#!/usr/bin/env bash
# supervisor-tick.sh — the between-attended-session driver for the supervisor.
# See decisions/0014-supervisor-tick-and-pm-pattern.md for the full contract.
#
# Responsibilities:
#   1. Stacked interlock (flock + Claude JSONL + Codex JSONL + tmux + hold).
#   2. Snapshot project-repo HEADs for post-run boundary audit.
#   3. Spawn a headless claude session with a scoped prompt.
#   4. Audit: git diff filtered by Tier-C globs, per-project HEAD unchanged.
#   5. Commit Tier-A writes to branch ticks/<YYYY-MM-DD>-<HH>. Never push.
#   6. Emit session_reflected event + a per-tick report.

set -uo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$LIB_DIR/workspace-paths.sh"

TICK_AGENT_LABEL="tick"
LOCK_DIR="$RUNTIME_ROOT/.locks"
LOCK_FILE="$LOCK_DIR/supervisor-tick.lock"
HOLD_FILE="$LOCK_DIR/supervisor-tick.hold"
SUP="$SUPERVISOR_ROOT"
ISO_NOW="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
REPORT="$WORKSPACE_META_DIR/supervisor-tick-${ISO_NOW}.md"
EVENT_FILE="$WORKSPACE_SUPERVISOR_EVENTS_FILE"
mkdir -p "$LOCK_DIR" "$WORKSPACE_META_DIR" "$(dirname "$EVENT_FILE")"

emit_event() {
  local type="$1" note="$2" ref="${3:-$REPORT}"
  printf '{"ts":"%s","agent":"%s","type":"%s","ref":"%s","note":"%s"}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$TICK_AGENT_LABEL" "$type" "$ref" "$note" \
    >> "$EVENT_FILE"
}

skip_with_reason() {
  local reason="$1"
  printf '# Supervisor tick skipped — %s\n\n_timestamp_: %s\n' "$reason" "$ISO_NOW" > "$REPORT"
  emit_event "session_reflected" "tick skipped — $reason"
  echo "supervisor-tick: SKIP — $reason" >&2
  exit 0
}

# --- 1. self-race lock --------------------------------------------------------
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "supervisor-tick: another tick holds the lock, exiting cleanly"
  exit 0
fi

# --- 2. manual hold -----------------------------------------------------------
if [[ -e "$HOLD_FILE" ]]; then
  skip_with_reason "manual hold file present ($HOLD_FILE)"
fi

# --- 3. attended-session signals ---------------------------------------------
# Claude JSONL
CLAUDE_DIR="/root/.claude/projects/-opt-workspace-supervisor"
if [[ -d "$CLAUDE_DIR" ]]; then
  if find "$CLAUDE_DIR" -maxdepth 1 -name '*.jsonl' -newermt '15 minutes ago' 2>/dev/null | grep -q .; then
    skip_with_reason "Claude supervisor JSONL active in last 15 min"
  fi
fi

# Codex JSONL — broad check (fallback): any codex session file touched recently.
# Narrow check (cwd match) is brittle across codex versions; the broad check is
# a conservative over-skip rather than an under-skip.
CODEX_ROOT="/root/.codex/sessions"
if [[ -d "$CODEX_ROOT" ]]; then
  if find "$CODEX_ROOT" -name 'rollout-*.jsonl' -newermt '15 minutes ago' 2>/dev/null \
     | xargs -r -I {} grep -l -m1 -F '/opt/workspace/supervisor' {} >/dev/null 2>&1; then
    skip_with_reason "Codex session referencing supervisor cwd active in last 15 min"
  fi
fi

# Tmux attended-session signal
if command -v tmux >/dev/null 2>&1; then
  if tmux has-session -t general 2>/dev/null; then
    last_activity=$(tmux display-message -p -t general '#{session_activity}' 2>/dev/null || echo 0)
    now_epoch=$(date -u +%s)
    if [[ "$last_activity" =~ ^[0-9]+$ ]] && (( now_epoch - last_activity < 900 )); then
      skip_with_reason "tmux 'general' session had activity $(( (now_epoch - last_activity) / 60 )) min ago"
    fi
  fi
fi

# --- 4. pre-run audit snapshots ----------------------------------------------
if [[ ! -d "$SUP/.git" ]]; then
  skip_with_reason "supervisor repo missing .git (unexpected)"
fi

PRE_SUP_HEAD=$(git -C "$SUP" rev-parse HEAD 2>/dev/null || echo unknown)
PRE_SUP_DIRTY=$(git -C "$SUP" status --porcelain 2>/dev/null || true)

# Refuse to run on a dirty working tree — an attended session may be in flight
# with uncommitted work. Safer to skip than to risk committing partial state.
if [[ -n "$PRE_SUP_DIRTY" ]]; then
  skip_with_reason "supervisor working tree was dirty at tick start; refusing to run"
fi

PRE_SUP_BRANCH=$(git -C "$SUP" symbolic-ref --short HEAD 2>/dev/null || echo detached)

# Snapshot project HEADs (never-write boundary for Tier C).
PROJECT_HEAD_SNAPSHOT=""
for p in /opt/workspace/projects/*; do
  [[ -d "$p/.git" ]] || continue
  pname=$(basename "$p")
  phead=$(git -C "$p" rev-parse HEAD 2>/dev/null || echo none)
  PROJECT_HEAD_SNAPSHOT+="$pname $phead"$'\n'
done

# --- 5. render + run the tick -------------------------------------------------
PROMPT_TEMPLATE="$LIB_DIR/supervisor-tick-prompt.md"
if [[ ! -f "$PROMPT_TEMPLATE" ]]; then
  skip_with_reason "tick prompt template missing: $PROMPT_TEMPLATE"
fi

PROMPT="$(sed \
  -e "s|{{ISO_NOW}}|$ISO_NOW|g" \
  -e "s|{{REPORT}}|$REPORT|g" \
  -e "s|{{SUPERVISOR_ROOT}}|$SUP|g" \
  -e "s|{{RUNTIME_ROOT}}|$RUNTIME_ROOT|g" \
  -e "s|{{EVENT_FILE}}|$EVENT_FILE|g" \
  -e "s|{{WORKSPACE_HANDOFF_DIR}}|$WORKSPACE_HANDOFF_DIR|g" \
  "$PROMPT_TEMPLATE")"

cd "$SUP"

echo "supervisor-tick: running at $ISO_NOW"
# --dangerously-skip-permissions is required for non-interactive runs.
# --disallowedTools blocks the riskiest Bash patterns + NotebookEdit.
# Edit is NOT blocked globally: the tick needs to edit Tier A files. Tier C is
# defended by the OS-level sandbox declared in the systemd unit
# (ProtectSystem=strict + ReadWritePaths=<Tier A>).
claude -p "$PROMPT" \
  --model claude-sonnet-4-6 \
  --effort medium \
  --disallowedTools \
    "Bash(git push:*)" "Bash(git reset --hard:*)" "Bash(git rebase:*)" \
    "Bash(git checkout -- :*)" "Bash(git restore --staged :*)" \
    "Bash(rm -rf:*)" "Bash(docker:*)" "Bash(systemctl:*)" \
    "Bash(npm publish:*)" "Bash(gh pr:*)" "Bash(gh release:*)" \
    "NotebookEdit" \
  2>&1 | tail -n 120 || {
    emit_event "session_reflected" "tick claude invocation failed"
    echo "supervisor-tick: claude invocation failed" >&2
  }

# --- 6. post-run boundary audit ----------------------------------------------
# Tier C: any git status hit aborts.
# Tier C-special (decisions/): only *modifications* abort; new untracked drafts
# are allowed (tick may draft new proposed ADRs per ADR-0014 Tier B).
declare -a TIER_C_GLOBS=(
  'AGENT.md' 'CLAUDE.md' 'AGENTS.md'
  'scripts/lib/*'
  'workspace.sh'
  'systemd/*'
  'config/*'
)
POST_SUP_DIRTY=$(git -C "$SUP" status --porcelain 2>/dev/null || true)

# Parse porcelain. Format: "XY path" where X=index status, Y=worktree status.
# Status codes we care about:
#   "??"       untracked (new file) — allowed for Tier B
#   " M"/"M "  modified existing — forbidden for any Tier C
#   "A "/"AM"  added to index — treat as modification for Tier C
#   "D ", " D" deletion — forbidden
#   "R  old -> new" rename — forbidden on Tier C
BREACH_LIST=""
while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  status="${line:0:2}"
  path="${line:3}"
  if [[ "$path" == *" -> "* ]]; then
    p1="${path%% -> *}"
    p2="${path##* -> }"
    paths=("$p1" "$p2")
  else
    paths=("$path")
  fi
  is_untracked=0
  [[ "$status" == "??" ]] && is_untracked=1
  for p in "${paths[@]}"; do
    # Standard Tier C — any status is a breach.
    for g in "${TIER_C_GLOBS[@]}"; do
      # shellcheck disable=SC2053
      if [[ "$p" == $g ]]; then
        BREACH_LIST+="  $p (matched $g, status=$status)"$'\n'
      fi
    done
    # decisions/*.md — allow new untracked drafts, forbid modifications.
    if [[ "$p" == decisions/*.md && "$is_untracked" -eq 0 ]]; then
      BREACH_LIST+="  $p (existing ADR modified, status=$status)"$'\n'
    fi
  done
done <<< "$POST_SUP_DIRTY"

# Per-project HEAD audit.
HEAD_BREACH_LIST=""
while IFS=' ' read -r pname phead_before; do
  [[ -z "$pname" ]] && continue
  phead_after=$(git -C "/opt/workspace/projects/$pname" rev-parse HEAD 2>/dev/null || echo none)
  if [[ "$phead_before" != "$phead_after" ]]; then
    HEAD_BREACH_LIST+="  $pname: $phead_before -> $phead_after"$'\n'
  fi
done <<< "$PROJECT_HEAD_SNAPSHOT"

if [[ -n "$BREACH_LIST" || -n "$HEAD_BREACH_LIST" ]]; then
  mkdir -p "$SUP/handoffs/INBOX"
  cat > "$SUP/handoffs/INBOX/URGENT-tick-boundary-breach-${ISO_NOW}.md" <<EOF
# URGENT — supervisor tick touched a Tier-C path

Tick at ${ISO_NOW} violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
${BREACH_LIST:-  (none)}

Project HEAD changes:
${HEAD_BREACH_LIST:-  (none)}

Pre-run supervisor HEAD: ${PRE_SUP_HEAD}
Post-run supervisor dirty tree:
\`\`\`
$(echo "$POST_SUP_DIRTY" | sed 's/^/    /')
\`\`\`

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
EOF
  emit_event "session_reflected" "tick boundary breach — see INBOX"
  echo "supervisor-tick: BOUNDARY BREACH — see $SUP/handoffs/INBOX/URGENT-tick-boundary-breach-${ISO_NOW}.md" >&2
  exit 3
fi

# --- 7. commit Tier-A writes to a ticks/ branch (never main) -----------------
POST_SUP_DIRTY=$(git -C "$SUP" status --porcelain 2>/dev/null || true)
if [[ -n "$POST_SUP_DIRTY" ]]; then
  branch="ticks/$(date -u +%Y-%m-%d-%H)"
  # Flow: stage explicit Tier-A paths, commit on the current branch (advances
  # main locally), move the new commit onto the ticks/ branch, then rewind the
  # main branch pointer so main is unchanged. Working tree ends up clean. The
  # tick never pushes — ADR-0014 §Push discipline.
  git -C "$SUP" add \
    friction/ handoffs/ system/ ideas/ decisions/ \
    2>/dev/null || true
  if ! git -C "$SUP" diff --cached --quiet 2>/dev/null; then
    git -C "$SUP" \
      -c user.email='tick@workspace.local' \
      -c user.name='supervisor-tick' \
      commit --quiet -m "tick ${ISO_NOW}: Tier-A updates

session_id: tick-${ISO_NOW}
agent: tick" || {
        echo "supervisor-tick: commit failed" >&2
        emit_event "session_reflected" "tick commit failed — see log"
        exit 4
      }
    new_sha=$(git -C "$SUP" rev-parse HEAD)
    git -C "$SUP" branch -f "$branch" "$new_sha"
    # Rewind the primary branch to its pre-tick HEAD. --hard on a clean tree
    # (everything was just committed) is safe; it restores the checked-out
    # files to the pre-tick state while the tick's commit lives on $branch.
    git -C "$SUP" reset --hard "$PRE_SUP_HEAD" >/dev/null
    emit_event "session_reflected" "tick committed to $branch (sha=${new_sha:0:12})"
    echo "supervisor-tick: committed Tier-A writes to $branch (attended review to merge)"
  else
    # Changes were all in gitignored paths (events/, .meta/ etc.) — nothing to
    # commit. Leave them as-is.
    echo "supervisor-tick: changes were gitignored; no commit needed"
  fi
fi

# --- 8. run doctor and note the result ---------------------------------------
doctor_status="not-run"
if "$SUP/workspace.sh" doctor >/dev/null 2>&1; then
  doctor_status="green"
elif [[ $? -eq 2 ]]; then
  doctor_status="warn"
else
  doctor_status="fail"
fi

# --- 9. session_reflected event + report trailer -----------------------------
if ! grep -q "session_reflected" <(tail -n 20 "$EVENT_FILE" 2>/dev/null) ; then
  emit_event "session_reflected" "tick complete — doctor=$doctor_status"
fi

# Append a brief summary if the model didn't write the report itself.
if [[ ! -s "$REPORT" ]]; then
  cat > "$REPORT" <<EOF
# Supervisor tick — $ISO_NOW

_status_: completed (minimal report; model did not write a detailed summary)
_doctor_: $doctor_status
EOF
fi

echo "supervisor-tick: done (doctor=$doctor_status)"
exit 0
