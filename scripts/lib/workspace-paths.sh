#!/usr/bin/env bash
# Shared workspace path resolution.
# Supports the current legacy layout and the future split layout.

if [[ -n "${__WORKSPACE_PATHS_SH:-}" ]]; then
  return 0 2>/dev/null || exit 0
fi
__WORKSPACE_PATHS_SH=1

set -u

if [[ -f /etc/workspace.env ]]; then
  # Import the host's active workspace topology unless the caller has already
  # overridden values in the environment.
  set -a
  # shellcheck disable=SC1091
  source /etc/workspace.env
  set +a
fi

WORKSPACE_LAYOUT="${WORKSPACE_LAYOUT:-legacy}"

if [[ -z "${WORKSPACE_ROOT:-}" ]]; then
  case "$WORKSPACE_LAYOUT" in
    legacy) WORKSPACE_ROOT=/opt/projects ;;
    split) WORKSPACE_ROOT=/opt/workspace ;;
    *)
      echo "workspace-paths: unknown WORKSPACE_LAYOUT '$WORKSPACE_LAYOUT'" >&2
      return 1 2>/dev/null || exit 1
      ;;
  esac
fi

case "$WORKSPACE_LAYOUT" in
  legacy)
    default_supervisor_root="$WORKSPACE_ROOT/supervisor"
    default_projects_root="$WORKSPACE_ROOT"
    default_runtime_root="$WORKSPACE_ROOT"
    default_infra_root="$WORKSPACE_ROOT"
    ;;
  split)
    default_supervisor_root="$WORKSPACE_ROOT/supervisor"
    default_projects_root="$WORKSPACE_ROOT/projects"
    default_runtime_root="$WORKSPACE_ROOT/runtime"
    default_infra_root="$default_supervisor_root"
    ;;
  *)
    echo "workspace-paths: unknown WORKSPACE_LAYOUT '$WORKSPACE_LAYOUT'" >&2
    return 1 2>/dev/null || exit 1
    ;;
esac

export WORKSPACE_ROOT
export SUPERVISOR_ROOT="${SUPERVISOR_ROOT:-$default_supervisor_root}"
export PROJECTS_ROOT="${PROJECTS_ROOT:-$default_projects_root}"
export RUNTIME_ROOT="${RUNTIME_ROOT:-$default_runtime_root}"
export WORKSPACE_INFRA_ROOT="${WORKSPACE_INFRA_ROOT:-$default_infra_root}"

export WORKSPACE_SCRIPTS_ROOT="${WORKSPACE_SCRIPTS_ROOT:-$WORKSPACE_INFRA_ROOT/scripts/lib}"
export WORKSPACE_SYSTEMD_ROOT="${WORKSPACE_SYSTEMD_ROOT:-$WORKSPACE_INFRA_ROOT/systemd}"
export WORKSPACE_SESSION_CONF="${WORKSPACE_SESSION_CONF:-$WORKSPACE_SCRIPTS_ROOT/sessions.conf}"
export WORKSPACE_PROJECTS_CONF="${WORKSPACE_PROJECTS_CONF:-$WORKSPACE_SCRIPTS_ROOT/projects.conf}"

export WORKSPACE_META_DIR="${WORKSPACE_META_DIR:-$RUNTIME_ROOT/.meta}"
export WORKSPACE_HANDOFF_DIR="${WORKSPACE_HANDOFF_DIR:-$RUNTIME_ROOT/.handoff}"
export WORKSPACE_FEATURES_ROOT="${WORKSPACE_FEATURES_ROOT:-$RUNTIME_ROOT/.features}"
export WORKSPACE_TELEMETRY_DIR="${WORKSPACE_TELEMETRY_DIR:-$RUNTIME_ROOT/.telemetry}"
export WORKSPACE_HEALTH_STATUS_FILE="${WORKSPACE_HEALTH_STATUS_FILE:-$RUNTIME_ROOT/.health-status.txt}"

# The supervisor event stream lives on runtime storage, never inside the git
# repo (ADR-0012). Guard against a stale env export that points at the legacy
# repo path (supervisor/events/…): force it back to runtime so no inherited
# shell environment can reopen the git-resident event surface.
_ws_ev="${WORKSPACE_SUPERVISOR_EVENTS_FILE:-$WORKSPACE_TELEMETRY_DIR/supervisor-events.jsonl}"
case "$_ws_ev" in
  "$SUPERVISOR_ROOT"/events/*) _ws_ev="$WORKSPACE_TELEMETRY_DIR/supervisor-events.jsonl" ;;
esac
export WORKSPACE_SUPERVISOR_EVENTS_FILE="$_ws_ev"
unset _ws_ev
export WORKSPACE_SUPERVISOR_SESSIONS_DIR="${WORKSPACE_SUPERVISOR_SESSIONS_DIR:-$SUPERVISOR_ROOT/sessions}"
export WORKSPACE_SUPERVISOR_HANDOFF_INBOX="${WORKSPACE_SUPERVISOR_HANDOFF_INBOX:-$SUPERVISOR_ROOT/handoffs/INBOX}"
export WORKSPACE_SUPERVISOR_DECISIONS_DIR="${WORKSPACE_SUPERVISOR_DECISIONS_DIR:-$SUPERVISOR_ROOT/decisions}"

export WORKSPACE_ROOT_CLAUDE_MD="${WORKSPACE_ROOT_CLAUDE_MD:-$WORKSPACE_ROOT/CLAUDE.md}"
export WORKSPACE_REMOTE_SETUP_MD="${WORKSPACE_REMOTE_SETUP_MD:-$WORKSPACE_ROOT/REMOTE_SETUP.md}"
export WORKSPACE_WORKSPACE_MD="${WORKSPACE_WORKSPACE_MD:-$WORKSPACE_ROOT/WORKSPACE.md}"
export WORKSPACE_LATEST_SYNTHESIS_PTR="${WORKSPACE_LATEST_SYNTHESIS_PTR:-$WORKSPACE_META_DIR/LATEST_SYNTHESIS}"
export WORKSPACE_LATEST_SERVER_HEALTH_PTR="${WORKSPACE_LATEST_SERVER_HEALTH_PTR:-$WORKSPACE_META_DIR/LATEST_SERVER_HEALTH}"
export WORKSPACE_LATEST_SERVER_MAINTENANCE_PTR="${WORKSPACE_LATEST_SERVER_MAINTENANCE_PTR:-$WORKSPACE_META_DIR/LATEST_SERVER_MAINTENANCE}"
export WORKSPACE_LATEST_SERVER_MAINTENANCE_SCHEDULE_PTR="${WORKSPACE_LATEST_SERVER_MAINTENANCE_SCHEDULE_PTR:-$WORKSPACE_META_DIR/LATEST_SERVER_MAINTENANCE_SCHEDULE}"

workspace_agent_slug() {
  local candidate="${1:-${WORKSPACE_AGENT:-}}"
  case "$candidate" in
    claude|codex) printf '%s\n' "$candidate" ;;
    *) printf 'unknown\n' ;;
  esac
}

workspace_show_paths() {
  cat <<EOF
WORKSPACE_LAYOUT=$WORKSPACE_LAYOUT
WORKSPACE_ROOT=$WORKSPACE_ROOT
SUPERVISOR_ROOT=$SUPERVISOR_ROOT
PROJECTS_ROOT=$PROJECTS_ROOT
RUNTIME_ROOT=$RUNTIME_ROOT
WORKSPACE_INFRA_ROOT=$WORKSPACE_INFRA_ROOT
WORKSPACE_SCRIPTS_ROOT=$WORKSPACE_SCRIPTS_ROOT
WORKSPACE_SYSTEMD_ROOT=$WORKSPACE_SYSTEMD_ROOT
WORKSPACE_SESSION_CONF=$WORKSPACE_SESSION_CONF
WORKSPACE_PROJECTS_CONF=$WORKSPACE_PROJECTS_CONF
WORKSPACE_META_DIR=$WORKSPACE_META_DIR
WORKSPACE_HANDOFF_DIR=$WORKSPACE_HANDOFF_DIR
WORKSPACE_FEATURES_ROOT=$WORKSPACE_FEATURES_ROOT
WORKSPACE_TELEMETRY_DIR=$WORKSPACE_TELEMETRY_DIR
WORKSPACE_HEALTH_STATUS_FILE=$WORKSPACE_HEALTH_STATUS_FILE
WORKSPACE_SUPERVISOR_EVENTS_FILE=$WORKSPACE_SUPERVISOR_EVENTS_FILE
WORKSPACE_SUPERVISOR_SESSIONS_DIR=$WORKSPACE_SUPERVISOR_SESSIONS_DIR
EOF
}
