#!/usr/bin/env bash
# Verify that every committed main-branch history is durable on origin/main.
# With --repair, publish only strict fast-forwards after screening the committed
# range for high-signal secrets. Working-tree changes are never staged or read.

set -uo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$LIB_DIR/workspace-paths.sh"

MODE=audit
SOURCE_TYPE=system
declare -a EXPLICIT_REPOS=()

usage() {
  cat <<'EOF'
Usage: remote-durability.sh [--audit|--repair] [--source system|cron] [--repo PATH ...]

Audit is read-only and exits non-zero when any repository is not verified at
origin/main. Repair may push a committed main branch only when origin/main is
its upstream, the remote has not diverged, and the outgoing range passes the
secret screen. It never stages, commits, rebases, merges, or force-pushes.
EOF
}

while (($#)); do
  case "$1" in
    --audit) MODE=audit ;;
    --repair) MODE=repair ;;
    --source)
      shift
      SOURCE_TYPE="${1:-}"
      [[ "$SOURCE_TYPE" == system || "$SOURCE_TYPE" == cron ]] || {
        echo "remote-durability: invalid source type: $SOURCE_TYPE" >&2
        exit 2
      }
      ;;
    --repo)
      shift
      [[ -n "${1:-}" ]] || { echo 'remote-durability: --repo requires a path' >&2; exit 2; }
      EXPLICIT_REPOS+=("$(readlink -f "$1")")
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "remote-durability: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

declare -a REPOS=()
if ((${#EXPLICIT_REPOS[@]})); then
  REPOS=("${EXPLICIT_REPOS[@]}")
else
  scan_supervisor_root="${REMOTE_DURABILITY_SUPERVISOR_ROOT:-$SUPERVISOR_ROOT}"
  scan_projects_root="${REMOTE_DURABILITY_PROJECTS_ROOT:-$PROJECTS_ROOT}"
  REPOS+=("$scan_supervisor_root")
  mapfile -t DISCOVERED_GIT_DIRS < <(find "$scan_projects_root" -mindepth 2 -maxdepth 5 -name .git \( -type d -o -type f \) -print 2>/dev/null | sort)
  for git_dir in "${DISCOVERED_GIT_DIRS[@]}"; do
    REPOS+=("${git_dir%/.git}")
  done
fi

emit_event() {
  local repo="$1" status="$2" local_sha="$3" remote_sha="$4" ahead="$5" behind="$6" dirty="$7" note="$8"
  REPO="$repo" STATUS="$status" LOCAL_SHA="$local_sha" REMOTE_SHA="$remote_sha" \
    AHEAD="$ahead" BEHIND="$behind" DIRTY="$dirty" NOTE="$note" \
    SOURCE_TYPE="$SOURCE_TYPE" EVENT_FILE="$EVENT_FILE" python3 - <<'PY'
import json, os, time
status = os.environ["STATUS"]
if status == "synced":
    event_type, level = "remote_durability_verified", "info"
elif status in {"busy", "secret-blocked"}:
    event_type, level = "throttled", "warn"
elif status in {"ahead", "behind", "wrong-branch", "no-origin", "no-upstream", "not-a-repo"}:
    event_type, level = "info", "warn"
else:
    event_type, level = "failure", "error"
event = {
    "project": os.path.basename(os.environ["REPO"]),
    "source": "remote-durability",
    "eventType": event_type,
    "level": level,
    "timestamp": int(time.time() * 1000),
    "sourceType": os.environ["SOURCE_TYPE"],
    "repository": os.environ["REPO"],
    "publicationState": os.environ["STATUS"],
    "localHead": os.environ["LOCAL_SHA"],
    "remoteHead": os.environ["REMOTE_SHA"],
    "ahead": int(os.environ["AHEAD"] or 0),
    "behind": int(os.environ["BEHIND"] or 0),
    "dirtyPaths": int(os.environ["DIRTY"] or 0),
    "note": os.environ["NOTE"],
}
with open(os.environ["EVENT_FILE"], "a", encoding="utf-8") as f:
    f.write(json.dumps(event, separators=(",", ":")) + "\n")
PY
}

has_secret_in_range() {
  local repo="$1" range="$2"
  local pattern='xox[bpars]-[0-9A-Za-z-]{20,}|gh[pousr]_[0-9A-Za-z]{30,}|sk-[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----'
  if git -C "$repo" diff --unified=0 "$range" -- 2>/dev/null \
      | grep '^+' | grep -v '^+++' | grep -Eq "$pattern"; then
    return 0
  fi
  git -C "$repo" log --format='%B' "$range" 2>/dev/null | grep -Eq "$pattern"
}

LOCK_DIR="${REMOTE_DURABILITY_LOCK_DIR:-$RUNTIME_ROOT/.locks}"
EVENT_FILE="$WORKSPACE_TELEMETRY_DIR/remote-durability.jsonl"
mkdir -p "$LOCK_DIR" "$WORKSPACE_TELEMETRY_DIR"
exec 9>"$LOCK_DIR/remote-durability.lock"
if ! flock -n 9; then
  echo 'remote-durability: another verifier holds the lock' >&2
  if ! emit_event "$SUPERVISOR_ROOT" busy unknown unknown 0 0 0 \
      'another verifier holds the lock; bounded service timeout will recover a stalled owner'; then
    echo 'remote-durability: lock contention telemetry write failed' >&2
    exit 1
  fi
  exit 0
fi

printf '%-34s %-13s %5s %6s %5s %-12s %-12s\n' REPOSITORY STATE AHEAD BEHIND DIRTY LOCAL REMOTE
failed=0

for repo in "${REPOS[@]}"; do
  name="${repo#$WORKSPACE_ROOT/}"
  local_sha='unknown'; remote_sha='unknown'; ahead=0; behind=0
  dirty=$(git -C "$repo" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  status=unknown; note='verification did not complete'

  if ! git -C "$repo" rev-parse --git-dir >/dev/null 2>&1; then
    status=not-a-repo; note='repository metadata missing'
  elif [[ "$(git -C "$repo" branch --show-current 2>/dev/null)" != main ]]; then
    status=wrong-branch; note='automatic durability is restricted to main'
  elif ! git -C "$repo" remote get-url origin >/dev/null 2>&1; then
    status=no-origin; note='origin remote is not configured'
  elif [[ "$(git -C "$repo" rev-parse --abbrev-ref '@{upstream}' 2>/dev/null || true)" != origin/main ]]; then
    status=no-upstream; note='main must track origin/main'
  elif ! git -C "$repo" fetch --quiet origin main </dev/null; then
    status=fetch-failed; note='could not refresh origin/main'
  else
    local_sha=$(git -C "$repo" rev-parse HEAD)
    remote_sha=$(git -C "$repo" rev-parse origin/main)
    read -r behind ahead < <(git -C "$repo" rev-list --left-right --count 'origin/main...HEAD')
    if ((behind > 0 && ahead > 0)); then
      status=diverged; note='remote contains commits absent from local main; manual reconciliation required'
    elif ((behind > 0)); then
      status=behind; note='local main is stale but its committed history is present remotely'
    elif ((ahead == 0)); then
      status=synced; note='local HEAD equals origin/main'
    elif [[ "$MODE" == audit ]]; then
      status=ahead; note='committed history is not durable on origin/main'
    elif has_secret_in_range "$repo" 'origin/main..HEAD'; then
      status=secret-blocked; note='outgoing range matched a high-signal secret pattern'
    elif git -C "$repo" push --porcelain origin HEAD:refs/heads/main </dev/null >/dev/null; then
      git -C "$repo" fetch --quiet origin main </dev/null || true
      remote_sha=$(git -C "$repo" rev-parse origin/main 2>/dev/null || echo unknown)
      if git -C "$repo" merge-base --is-ancestor "$local_sha" "$remote_sha" 2>/dev/null; then
        status=synced; ahead=0; note='published strict fast-forward and verified local HEAD is durable remotely'
      else
        status=verify-failed; note='push returned success but remote SHA did not match local HEAD'
      fi
    else
      status=push-failed; note='non-forcing push failed'
    fi
  fi

  printf '%-34s %-13s %5s %6s %5s %-12s %-12s\n' \
    "$name" "$status" "$ahead" "$behind" "$dirty" "${local_sha:0:12}" "${remote_sha:0:12}"
  if ! emit_event "$repo" "$status" "$local_sha" "$remote_sha" "$ahead" "$behind" "$dirty" "$note"; then
    echo "remote-durability: telemetry write failed for $repo" >&2
    failed=1
  fi
  [[ "$status" == synced ]] || failed=1
done

exit "$failed"
