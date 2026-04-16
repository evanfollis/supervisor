#!/usr/bin/env bash
# Sandbox-safe recovery path for persistent workspace sessions when the
# attached harness cannot reach systemd. Starts detached restart loops that
# keep invoking session-supervisor.sh for any missing sessions.

set -euo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"

CONF="${WORKSPACE_SESSION_CONF:?missing WORKSPACE_SESSION_CONF}"
SUPERVISOR="${WORKSPACE_SESSION_SUPERVISOR:-$WORKSPACE_SCRIPTS_ROOT/session-supervisor.sh}"
STATE_ROOT="${RUNTIME_ROOT}/.session-supervisors/manual"
PID_DIR="$STATE_ROOT/pids"
LOG_DIR="$STATE_ROOT/logs"

mkdir -p "$PID_DIR" "$LOG_DIR"

trim() {
  local s="${1:-}"
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s\n' "$s"
}

session_loop_cmd() {
  local name="$1" dir="$2" agent="$3" role="$4"
  printf 'while true; do "%s" "%s" "%s" "%s" "%s"; rc=$?; printf "%%s session-loop[%s]: supervisor exited rc=%%s\\n" "$(date -u +%%Y-%%m-%%dT%%H:%%M:%%SZ)" "$rc"; sleep 5; done' \
    "$SUPERVISOR" "$name" "$dir" "$agent" "$role" "$name"
}

start_loop() {
  local name="$1" dir="$2" agent="$3" role="$4"
  local pidfile="$PID_DIR/${name}.pid"
  local logfile="$LOG_DIR/${name}.log"

  if [[ -f "$pidfile" ]]; then
    local existing_pid
    existing_pid="$(cat "$pidfile" 2>/dev/null || true)"
    if [[ -n "$existing_pid" ]] && kill -0 "$existing_pid" 2>/dev/null; then
      echo "loop-up: $name pid=$existing_pid"
      return 0
    fi
    rm -f "$pidfile"
  fi

  if tmux has-session -t "$name" 2>/dev/null; then
    echo "session-up: $name"
    return 0
  fi

  local cmd
  cmd="$(session_loop_cmd "$name" "$dir" "$agent" "$role")"
  nohup bash -lc "$cmd" >>"$logfile" 2>&1 &
  local pid=$!
  echo "$pid" > "$pidfile"
  echo "started: $name pid=$pid log=$logfile"
}

while IFS='|' read -r raw_name raw_dir raw_agent raw_role _; do
  raw_name="$(trim "$raw_name")"
  [[ -z "$raw_name" || "$raw_name" == \#* ]] && continue
  raw_dir="$(trim "$raw_dir")"
  raw_agent="$(trim "$raw_agent")"
  raw_role="$(trim "$raw_role")"

  if [[ -z "$raw_dir" || ! -d "$raw_dir" ]]; then
    echo "skip: $raw_name missing dir '$raw_dir'" >&2
    continue
  fi

  start_loop "$raw_name" "$raw_dir" "${raw_agent:-claude}" "${raw_role:-project}"
done < "$CONF"

