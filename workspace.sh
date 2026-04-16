#!/bin/bash
# Workspace launcher — manages persistent agent sessions (Claude or Codex) in tmux.
# Primary supervision is systemd (workspace-session@<name>.service), but this
# wrapper also exposes a sandbox-safe recovery path when an attached harness
# cannot reach systemd directly.
# Session names, directories, and agent choice are declared in
# scripts/lib/sessions.conf.

set -euo pipefail
# Resolve symlinks so invocation via /opt/workspace/workspace.sh (a symlink to
# this file) still finds scripts/lib relative to the real location.
SCRIPT_PATH="$(readlink -f "$0")"
LIB_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)/scripts/lib"
source "$LIB_DIR/workspace-paths.sh"
CONF="$WORKSPACE_SESSION_CONF"
RECOVER="$WORKSPACE_SCRIPTS_ROOT/recover-persistent-sessions.sh"
CAPABILITIES="$WORKSPACE_SCRIPTS_ROOT/capability-attestation.sh"

names() { grep -v '^\s*#' "$CONF" | grep -v '^\s*$' | cut -d'|' -f1; }
systemctl_ok() { systemctl list-unit-files --no-legend --no-pager >/dev/null 2>&1; }

case "${1:-status}" in
  start)
    if systemctl_ok; then
      for n in $(names); do
        systemctl enable --now "workspace-session@${n}.service" >/dev/null 2>&1
        echo "ensured: $n"
      done
    else
      echo "systemctl unavailable; falling back to manual recovery"
      exec "$RECOVER"
    fi
    ;;
  stop)
    # Stops the supervisor AND kills the tmux session. Persistent state in the
    # Claude session JSONL survives; only the live process goes away.
    for n in $(names); do
      systemctl stop "workspace-session@${n}.service" 2>/dev/null || true
      tmux kill-session -t "$n" 2>/dev/null && echo "stopped: $n" || true
    done
    ;;
  restart)
    # Restart a single session (or all). The supervisor respawns within ~5s.
    target="${2:-}"
    if [[ -n "$target" ]]; then
      tmux kill-session -t "$target" 2>/dev/null || true
      echo "killed $target — systemd will respawn"
    else
      for n in $(names); do
        tmux kill-session -t "$n" 2>/dev/null || true
      done
      echo "killed all — systemd will respawn each within ~5s"
    fi
    ;;
  status)
    printf '%-20s %-10s %s\n' SESSION SUPERVISOR TMUX
    for n in $(names); do
      sup=$(systemctl is-active "workspace-session@${n}.service" 2>/dev/null || echo inactive)
      tmx=$(tmux has-session -t "$n" 2>/dev/null && echo up || echo down)
      printf '%-20s %-10s %s\n' "$n" "$sup" "$tmx"
    done
    ;;
  recover)
    exec "$RECOVER"
    ;;
  capabilities)
    exec "$CAPABILITIES" --markdown
    ;;
  add)
    # Usage: workspace.sh add <name> <path> [agent] [role]
    if [[ -z "${2:-}" || -z "${3:-}" ]]; then
      echo "Usage: workspace.sh add <name> <path> [agent] [role]"
      exit 1
    fi
    agent="${4:-claude}"
    role="${5:-project}"
    grep -qE "^${2}\|" "$CONF" || echo "${2}|${3}|${agent}|${role}" >> "$CONF"
    if systemctl_ok; then
      systemctl enable --now "workspace-session@${2}.service"
    else
      echo "systemctl unavailable; falling back to manual recovery"
      "$RECOVER"
    fi
    echo "added + started: $2 ($3)"
    ;;
  feature|close|tree)
    # Feature session lifecycle — see supervisor/decisions/0002-feature-sessions.md
    exec "$WORKSPACE_SCRIPTS_ROOT/ws-feature.sh" "$@"
    ;;
  idea)
    exec "$WORKSPACE_SCRIPTS_ROOT/idea-ledger.py" "${@:2}"
    ;;
  idea-focus)
    exec "$WORKSPACE_SCRIPTS_ROOT/idea-focus.sh"
    ;;
  context)
    exec "$WORKSPACE_SCRIPTS_ROOT/current-context.sh"
    ;;
  doctor)
    exec "$WORKSPACE_SCRIPTS_ROOT/doctor.sh"
    ;;
  *)
    echo "Usage: workspace.sh {start|recover|stop|restart [name]|status|capabilities|add <name> <path>}"
    echo "       workspace.sh feature <slug> [--project <name>] [--agent claude|codex]"
    echo "       workspace.sh close <tmux_name> [--force]"
    echo "       workspace.sh tree"
    echo "       workspace.sh idea {new|update|list|show} ..."
    echo "       workspace.sh idea-focus"
    echo "       workspace.sh context"
    echo "       workspace.sh doctor"
    ;;
esac
