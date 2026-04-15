#!/usr/bin/env bash
# Enable + start systemd supervision for every session in sessions.conf.
# Idempotent. Safe to re-run.

set -euo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"

CONF="$WORKSPACE_SESSION_CONF"

systemctl daemon-reload

while IFS='|' read -r name dir; do
  [[ -z "$name" || "$name" == \#* ]] && continue
  unit="workspace-session@${name}.service"
  systemctl enable "$unit" 2>&1 | grep -v 'already enabled' || true
  if systemctl is-active --quiet "$unit"; then
    echo "sessions: $name already active"
  else
    systemctl start "$unit"
    echo "sessions: started $name"
  fi
done < "$CONF"
