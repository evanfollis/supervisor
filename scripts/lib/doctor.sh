#!/usr/bin/env bash
# workspace.sh doctor — run live-service checks on the supervisor control plane.
#
# The checks here are promotion targets for frictions: when a friction
# captured in supervisor/friction/ points at a gap that would have been
# caught by a standing check, add it here. See ADR-0013 and
# playbooks/self-reflection.md §Promotion paths.
#
# Exit codes:
#   0 — all checks passed
#   1 — at least one check failed (problems printed to stderr)
#   2 — at least one check warned (printed but not failing)

set -uo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$LIB_DIR/workspace-paths.sh"

FAIL=0
WARN=0

if [[ -t 1 ]]; then
  C_OK=$'\e[32m'; C_WARN=$'\e[33m'; C_FAIL=$'\e[31m'; C_DIM=$'\e[2m'; C_RST=$'\e[0m'
else
  C_OK=""; C_WARN=""; C_FAIL=""; C_DIM=""; C_RST=""
fi

say_ok()   { printf '  %s✓%s %s\n' "$C_OK" "$C_RST" "$1"; }
say_warn() { printf '  %s⚠%s %s\n' "$C_WARN" "$C_RST" "$1"; WARN=1; }
say_fail() { printf '  %s✗%s %s\n' "$C_FAIL" "$C_RST" "$1"; FAIL=1; }
note()     { printf '    %s%s%s\n' "$C_DIM" "$1" "$C_RST"; }
section()  { printf '\n%s\n' "$1"; }

now_epoch=$(date -u +%s)
age_hours() {  # seconds → rounded hours
  local s="$1"
  echo $(( s / 3600 ))
}

# --- durability: supervisor repo has a remote and HEAD is pushed (FR-0003) ---
section "durability"
if [[ -d "$SUPERVISOR_ROOT/.git" ]]; then
  remotes=$(git -C "$SUPERVISOR_ROOT" remote 2>/dev/null)
  if [[ -z "$remotes" ]]; then
    say_fail "supervisor repo has no git remote configured"
    note "fix: git -C $SUPERVISOR_ROOT remote add origin <url>"
  else
    say_ok "supervisor repo has remote(s): $(echo $remotes | tr '\n' ' ')"
    head_sha=$(git -C "$SUPERVISOR_ROOT" rev-parse HEAD 2>/dev/null || echo "")
    cur_branch=$(git -C "$SUPERVISOR_ROOT" symbolic-ref --short HEAD 2>/dev/null || echo "")
    if [[ -n "$cur_branch" ]]; then
      upstream=$(git -C "$SUPERVISOR_ROOT" rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>/dev/null || echo "")
      if [[ -z "$upstream" ]]; then
        say_warn "branch '$cur_branch' has no upstream tracking ref"
        note "fix: git -C $SUPERVISOR_ROOT push -u origin $cur_branch"
      else
        ahead=$(git -C "$SUPERVISOR_ROOT" rev-list --count "@{u}..HEAD" 2>/dev/null || echo 0)
        behind=$(git -C "$SUPERVISOR_ROOT" rev-list --count "HEAD..@{u}" 2>/dev/null || echo 0)
        if [[ "$ahead" -gt 0 ]]; then
          say_warn "branch '$cur_branch' is $ahead commit(s) ahead of $upstream (unpushed work)"
        else
          say_ok "branch '$cur_branch' is up to date with $upstream"
        fi
        if [[ "$behind" -gt 0 ]]; then
          note "behind upstream by $behind; review before next push"
        fi
      fi
    fi
  fi
else
  say_fail "supervisor repo is not a git repository"
fi

# --- secrets: no real bot tokens or private keys committed ---
section "secrets"
if [[ -d "$SUPERVISOR_ROOT/.git" ]]; then
  # xoxb-/xoxp-/ghp_/ghs_/sk- prefixes are high-signal; tune as new formats appear.
  leak=$(git -C "$SUPERVISOR_ROOT" ls-files -z | xargs -0 -r grep -l -E 'xox[bpars]-[0-9A-Za-z-]{20,}|gh[pousr]_[0-9A-Za-z]{30,}|sk-[A-Za-z0-9]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----' 2>/dev/null || true)
  if [[ -z "$leak" ]]; then
    say_ok "no token/key patterns in tracked files"
  else
    say_fail "token/key patterns found in tracked files:"
    echo "$leak" | sed 's/^/      /'
  fi
  # config/slack.env MUST be untracked (kept as local secret file).
  if git -C "$SUPERVISOR_ROOT" ls-files --error-unmatch config/slack.env >/dev/null 2>&1; then
    say_fail "config/slack.env is tracked in git (should be gitignored)"
  else
    if [[ -f "$SUPERVISOR_ROOT/config/slack.env" ]]; then
      perm=$(stat -c %a "$SUPERVISOR_ROOT/config/slack.env")
      if [[ "$perm" != "600" ]]; then
        say_warn "config/slack.env has permissions $perm; should be 600"
      else
        say_ok "config/slack.env present, untracked, mode 600"
      fi
    else
      note "config/slack.env not present (notifier may be disabled)"
    fi
  fi
fi

# --- handoff SLA: any INBOX file older than 24h is a supervisor lapse ---
section "handoff SLA"
inbox="$WORKSPACE_SUPERVISOR_HANDOFF_INBOX"
if [[ -d "$inbox" ]]; then
  stale_count=0
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    mtime=$(stat -c %Y "$f")
    age=$(( now_epoch - mtime ))
    if (( age > 86400 )); then
      say_warn "INBOX handoff aged $(age_hours "$age")h: ${f#$SUPERVISOR_ROOT/}"
      stale_count=$((stale_count + 1))
    fi
  done < <(find "$inbox" -maxdepth 1 -type f -name '*.md' 2>/dev/null)
  if (( stale_count == 0 )); then
    count=$(find "$inbox" -maxdepth 1 -type f -name '*.md' 2>/dev/null | wc -l)
    say_ok "INBOX has $count handoff(s), none older than 24h"
  fi
else
  say_warn "handoff INBOX directory missing: $inbox"
fi

# Also check the runtime handoff dir for anything addressed to 'general' aging past 24h.
gen_handoff_dir="$WORKSPACE_HANDOFF_DIR"
if [[ -d "$gen_handoff_dir" ]]; then
  stale_gen=0
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    mtime=$(stat -c %Y "$f")
    age=$(( now_epoch - mtime ))
    if (( age > 86400 )); then
      say_warn "runtime handoff for general aged $(age_hours "$age")h: $(basename "$f")"
      stale_gen=$((stale_gen + 1))
    fi
  done < <(find "$gen_handoff_dir" -maxdepth 1 -type f -name 'general-*.md' 2>/dev/null)
  (( stale_gen == 0 )) && say_ok "runtime .handoff has no stale general-* handoffs"
fi

# --- timers: reflection + synthesis + maintenance jobs must be active ---
section "systemd timers"
expected_timers=(
  workspace-reflect.timer
  workspace-synthesize.timer
  server-health-capture.timer
  server-maintenance.timer
  server-maintenance-schedule.timer
)
for t in "${expected_timers[@]}"; do
  if systemctl list-unit-files "$t" --no-legend --no-pager 2>/dev/null | grep -q "$t"; then
    state=$(systemctl is-active "$t" 2>/dev/null || echo inactive)
    enabled=$(systemctl is-enabled "$t" 2>/dev/null || echo disabled)
    if [[ "$state" == "active" && "$enabled" == "enabled" ]]; then
      say_ok "$t ($state, $enabled)"
    else
      say_fail "$t is $state / $enabled"
    fi
  else
    say_warn "$t not installed"
  fi
done

# --- supervisor session: the general tmux session should be supervised + up ---
section "general session"
# workspace-session@.service is a template — instantiated units don't show up in
# list-unit-files, so ask is-active directly.
if systemctl list-unit-files 'workspace-session@.service' --no-legend --no-pager 2>/dev/null | grep -q workspace-session; then
  svc_state=$(systemctl is-active "workspace-session@general.service" 2>/dev/null || echo inactive)
  case "$svc_state" in
    active)      say_ok "workspace-session@general.service is active" ;;
    activating)  say_warn "workspace-session@general.service is activating" ;;
    *)           say_fail "workspace-session@general.service is $svc_state" ;;
  esac
else
  say_warn "workspace-session@.service template unit not installed"
fi

# --- harness config visibility (FR-0002): list what hooks are active ---
section "harness config"
settings="/root/.claude/settings.json"
hooks_dir="/root/.claude/hooks"
if [[ -f "$settings" ]]; then
  if python3 -m json.tool "$settings" >/dev/null 2>&1; then
    say_ok "$settings parses as valid JSON"
  else
    say_fail "$settings is not valid JSON"
  fi
  hook_types=$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); h=d.get("hooks",{}); print(",".join(sorted(h.keys())) or "(none)")' "$settings" 2>/dev/null || echo "(parse-error)")
  note "active hook types: $hook_types"
else
  say_warn "$settings not found"
fi
if [[ -d "$hooks_dir" ]]; then
  active_hooks=$(find "$hooks_dir" -maxdepth 1 -type f -executable -not -name '*.disabled' 2>/dev/null | wc -l)
  disabled_hooks=$(find "$hooks_dir" -maxdepth 1 -type f -name '*.disabled' 2>/dev/null | wc -l)
  note "hooks dir: $active_hooks active, $disabled_hooks disabled"
fi

# --- notifier: Slack notifier consumes events.jsonl; confirm it's alive ---
section "notifier"
if systemctl list-unit-files 'workspace-notify.timer' --no-legend --no-pager 2>/dev/null | grep -q workspace-notify; then
  n_state=$(systemctl is-active workspace-notify.timer 2>/dev/null || echo inactive)
  if [[ "$n_state" == "active" ]]; then
    say_ok "workspace-notify.timer is $n_state"
  else
    say_warn "workspace-notify.timer is $n_state"
  fi
else
  note "workspace-notify.timer not installed (notifier may be disabled by design)"
fi

# --- events stream: has it been appended to in the last 24h? ---
section "events stream"
evfile="$WORKSPACE_SUPERVISOR_EVENTS_FILE"
if [[ -f "$evfile" ]]; then
  mtime=$(stat -c %Y "$evfile")
  age=$(( now_epoch - mtime ))
  if (( age < 86400 )); then
    say_ok "events file updated $(age_hours "$age")h ago: $evfile"
  else
    say_warn "events file stale ($(age_hours "$age")h since last append): $evfile"
  fi
  # Confirm the file parses: one JSON object per line.
  bad=$(python3 -c '
import json, sys
bad=0
for i,line in enumerate(open(sys.argv[1]),1):
    line=line.strip()
    if not line: continue
    try: json.loads(line)
    except Exception: bad+=1
print(bad)
' "$evfile" 2>/dev/null || echo error)
  if [[ "$bad" == "0" ]]; then
    say_ok "events file parses (1 JSON object per line)"
  else
    say_fail "events file has $bad malformed line(s)"
  fi
else
  say_warn "events file missing: $evfile"
fi

# --- synthesis pointer: did the last synthesis run recently? ---
section "synthesis pointer"
ptr="$WORKSPACE_LATEST_SYNTHESIS_PTR"
if [[ -f "$ptr" ]]; then
  target=$(cat "$ptr")
  if [[ -f "$target" ]]; then
    mtime=$(stat -c %Y "$target")
    age=$(( now_epoch - mtime ))
    if (( age < 129600 )); then  # 36h — synthesis runs every 12h
      say_ok "latest synthesis $(age_hours "$age")h old: $(basename "$target")"
    else
      say_warn "latest synthesis is $(age_hours "$age")h old (expected <36h)"
    fi
  else
    say_fail "synthesis pointer targets missing file: $target"
  fi
else
  say_warn "no synthesis pointer at $ptr"
fi

# --- supervisor tick: timer + recent report + ticks/ branch age (ADR-0014) ---
section "supervisor tick"
if systemctl list-unit-files 'workspace-supervisor-tick.timer' --no-legend --no-pager 2>/dev/null | grep -q workspace-supervisor-tick; then
  tick_state=$(systemctl is-active workspace-supervisor-tick.timer 2>/dev/null || echo inactive)
  tick_enabled=$(systemctl is-enabled workspace-supervisor-tick.timer 2>/dev/null || echo disabled)
  if [[ "$tick_state" == "active" && "$tick_enabled" == "enabled" ]]; then
    say_ok "workspace-supervisor-tick.timer ($tick_state, $tick_enabled)"
    # Freshness: last report (including skipped runs) within 4h when enabled.
    latest=$(ls -t "$WORKSPACE_META_DIR"/supervisor-tick-*.md 2>/dev/null | head -1 || echo "")
    if [[ -n "$latest" ]]; then
      mtime=$(stat -c %Y "$latest")
      age=$(( now_epoch - mtime ))
      if (( age < 14400 )); then
        say_ok "latest tick report $(age_hours "$age")h old: $(basename "$latest")"
      elif (( age < 28800 )); then
        say_warn "latest tick report $(age_hours "$age")h old (expected <4h)"
      else
        say_fail "latest tick report $(age_hours "$age")h old — timer may be broken"
      fi
    else
      say_warn "no supervisor-tick-*.md report found yet (timer just enabled?)"
    fi
  else
    say_fail "workspace-supervisor-tick.timer is $tick_state / $tick_enabled"
  fi
else
  say_warn "workspace-supervisor-tick.timer not installed"
fi

# Ticks branch age — attended sessions must merge/delete within 24h/72h.
if [[ -d "$SUPERVISOR_ROOT/.git" ]]; then
  while IFS= read -r b; do
    [[ -z "$b" ]] && continue
    committer_ts=$(git -C "$SUPERVISOR_ROOT" log -1 --format='%ct' "$b" 2>/dev/null || echo 0)
    age=$(( now_epoch - committer_ts ))
    if (( age > 259200 )); then
      say_fail "tick branch '$b' aged $(age_hours "$age")h (>72h — attended merge overdue)"
    elif (( age > 86400 )); then
      say_warn "tick branch '$b' aged $(age_hours "$age")h (>24h — attended merge needed)"
    else
      say_ok "tick branch '$b' fresh ($(age_hours "$age")h)"
    fi
  done < <(git -C "$SUPERVISOR_ROOT" branch --list 'ticks/*' --format='%(refname:short)' 2>/dev/null)
fi

# Hold file reminder — if present, the tick is suspended.
if [[ -e "$RUNTIME_ROOT/.locks/supervisor-tick.hold" ]]; then
  say_warn "tick is suspended — hold file present at $RUNTIME_ROOT/.locks/supervisor-tick.hold"
fi

# --- friction surface: new records suggest the reflection discipline is live ---
section "friction surface"
fric="$SUPERVISOR_ROOT/friction"
if [[ -d "$fric" ]]; then
  total=$(find "$fric" -maxdepth 1 -name 'FR-*.md' 2>/dev/null | wc -l)
  recent=$(find "$fric" -maxdepth 1 -name 'FR-*.md' -newermt '7 days ago' 2>/dev/null | wc -l)
  if (( total == 0 )); then
    say_warn "friction/ exists but no FR records captured yet"
  elif (( recent == 0 )); then
    say_warn "friction/ has $total records, none in the last 7 days — look harder or confirm calm"
  else
    say_ok "friction/: $total total, $recent in last 7d"
  fi
else
  say_fail "friction/ surface missing at $fric"
fi

# --- summary ---
section "summary"
if (( FAIL )); then
  printf '%sdoctor: FAIL%s — fix the ✗ items before the next push.\n' "$C_FAIL" "$C_RST"
  exit 1
elif (( WARN )); then
  printf '%sdoctor: WARN%s — ✓ items pass; review the ⚠ items.\n' "$C_WARN" "$C_RST"
  exit 2
else
  printf '%sdoctor: all checks passed.%s\n' "$C_OK" "$C_RST"
  exit 0
fi
