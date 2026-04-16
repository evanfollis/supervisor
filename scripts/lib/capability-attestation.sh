#!/usr/bin/env bash

set -euo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"

MODE="${1:---markdown}"

probe_write() {
  local dir="$1"
  local tmp="$dir/.capability-probe-$$"
  if : >"$tmp" 2>/dev/null; then
    rm -f "$tmp"
    printf 'yes\n'
  else
    printf 'no\n'
  fi
}

probe_tmux() {
  if ! command -v tmux >/dev/null 2>&1; then
    printf 'unavailable\n'
    return
  fi

  local out
  out="$(tmux -S /tmp/tmux-0/default ls 2>&1 >/dev/null || true)"
  if [[ -z "$out" ]]; then
    printf 'yes\n'
  elif grep -qi 'Operation not permitted' <<<"$out"; then
    printf 'blocked\n'
  elif grep -qi 'no server running' <<<"$out"; then
    printf 'no-server\n'
  else
    printf 'unknown\n'
  fi
}

probe_systemd() {
  if ! command -v systemctl >/dev/null 2>&1; then
    printf 'unavailable\n'
  elif systemctl list-unit-files --no-legend --no-pager >/dev/null 2>&1; then
    printf 'yes\n'
  else
    printf 'blocked\n'
  fi
}

probe_network() {
  if tr '\0' ' ' </proc/1/cmdline 2>/dev/null | grep -q -- '--unshare-net'; then
    printf 'restricted\n'
  else
    printf 'unknown\n'
  fi
}

classify_posture() {
  local cwd
  cwd="$(pwd -P)"
  if [[ "$cwd" == "$PROJECTS_ROOT"/* ]]; then
    printf 'project\n'
  else
    printf 'workspace-root\n'
  fi
}

workspace_write="$(probe_write "$WORKSPACE_ROOT")"
supervisor_write="$(probe_write "$SUPERVISOR_ROOT")"
runtime_write="$(probe_write "$RUNTIME_ROOT")"
projects_write="$(probe_write "$PROJECTS_ROOT")"
tmux_control="$(probe_tmux)"
systemd_control="$(probe_systemd)"
network_egress="$(probe_network)"
posture="$(classify_posture)"

operator_available="no"
if [[ "$tmux_control" == "yes" || "$systemd_control" == "yes" ]]; then
  operator_available="yes"
fi

effective_role="project"
if [[ "$posture" == "workspace-root" ]]; then
  effective_role="executive+supervisor"
  if [[ "$operator_available" == "yes" ]]; then
    effective_role="${effective_role}+operator"
  else
    effective_role="${effective_role} (attached)"
  fi
fi

case "$MODE" in
  --json)
    python3 - <<PY
import json
print(json.dumps({
  "posture": "${posture}",
  "effective_role": "${effective_role}",
  "workspace_write": "${workspace_write}",
  "supervisor_write": "${supervisor_write}",
  "runtime_write": "${runtime_write}",
  "project_mutation": "${projects_write}",
  "host_tmux_control": "${tmux_control}",
  "host_systemd_control": "${systemd_control}",
  "network_egress": "${network_egress}",
  "operator_available": "${operator_available}",
}, indent=2, sort_keys=True))
PY
    ;;
  --markdown|*)
    cat <<EOF
- posture: \`${posture}\`
- effective role: \`${effective_role}\`
- workspace write: \`${workspace_write}\`
- supervisor write: \`${supervisor_write}\`
- runtime write: \`${runtime_write}\`
- project mutation: \`${projects_write}\`
- host tmux control: \`${tmux_control}\`
- host systemd control: \`${systemd_control}\`
- network egress: \`${network_egress}\`
- operator available: \`${operator_available}\`
EOF
    ;;
esac
