#!/usr/bin/env bash
# Audit the control plane for hardcoded legacy workspace paths.

set -euo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"

STRICT=0
SHOW_DOCS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --strict) STRICT=1; shift ;;
    --docs) SHOW_DOCS=1; shift ;;
    -h|--help)
      echo "Usage: workspace-audit.sh [--strict] [--docs]"
      exit 0
      ;;
    *)
      echo "workspace-audit: unknown arg '$1'" >&2
      exit 2
      ;;
  esac
done

exec_targets=(
  "$WORKSPACE_SCRIPTS_ROOT"
  "$WORKSPACE_SYSTEMD_ROOT"
  "$WORKSPACE_ROOT/workspace.sh"
)

doc_targets=(
  "$SUPERVISOR_ROOT"
  "$WORKSPACE_ROOT_CLAUDE_MD"
  "$WORKSPACE_REMOTE_SETUP_MD"
  "$WORKSPACE_WORKSPACE_MD"
)

exclude_patterns=(
  '!supervisor/.git'
  '!**/workspace-paths.sh'
  '!**/workspace-audit.sh'
  '!**/sessions.conf'
  '!**/projects.conf'
  '!**/workspace-migration-plan.md'
)

scan() {
  local label="$1"
  shift
  local matches
  matches="$(rg -n '/opt/projects' "$@" "${exclude_patterns[@]}" 2>/dev/null || true)"
  matches="$(printf '%s\n' "$matches" \
    | grep -Ev ':[0-9]+:[[:space:]]*#' \
    | grep -Ev '/(sessions|projects)\.conf:' \
    | grep -Ev '/workspace-(paths|audit)\.sh:' \
    | grep -Ev '\$\{WORKSPACE_[^}]+:-/opt/projects/' \
    || true)"
  if [[ -n "$matches" ]]; then
    echo "[$label]"
    printf '%s\n' "$matches"
    echo
    return 1
  fi
  return 0
}

had_exec_matches=0
had_doc_matches=0

if ! scan "executable-path-drift" "${exec_targets[@]}"; then
  had_exec_matches=1
fi

if [[ "$SHOW_DOCS" -eq 1 ]]; then
  if ! scan "documentation-legacy-paths" "${doc_targets[@]}"; then
    had_doc_matches=1
  fi
fi

if [[ "$had_exec_matches" -eq 0 && "$had_doc_matches" -eq 0 ]]; then
  echo "workspace-audit: no hardcoded legacy control-plane paths found"
fi

if [[ "$STRICT" -eq 1 && "$had_exec_matches" -eq 1 ]]; then
  exit 1
fi
