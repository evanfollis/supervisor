#!/usr/bin/env bash
# Per-session tmux supervisor. Runs under systemd as workspace-session@<name>.service.
# Starts a detached tmux session running `claude --remote-control <name>` and
# then blocks until that tmux session dies. systemd's Restart=on-failure then
# respawns us, which respawns the session.
#
# Usage: session-supervisor.sh <name> <dir> [agent] [role]
#
# Reads from /opt/workspace/supervisor/scripts/lib/projects.conf if dir is omitted.

set -euo pipefail

NAME="${1:?session name required}"
DIR="${2:-}"
AGENT="${3:-}"
ROLE="${4:-}"

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"

CONF="$WORKSPACE_SESSION_CONF"
if [[ -z "$DIR" || -z "$AGENT" ]]; then
  CONF_LINE=$(grep -E "^${NAME}\|" "$CONF" 2>/dev/null | head -1 || true)
  [[ -z "$DIR" ]]   && DIR=$(echo   "$CONF_LINE" | cut -d'|' -f2)
  [[ -z "$AGENT" ]] && AGENT=$(echo "$CONF_LINE" | cut -d'|' -f3)
  [[ -z "$ROLE" ]]  && ROLE=$(echo  "$CONF_LINE" | cut -d'|' -f4)
fi
AGENT="${AGENT:-claude}"
ROLE="${ROLE:-project}"

if [[ -z "$DIR" || ! -d "$DIR" ]]; then
  echo "session-supervisor[$NAME]: directory not found ($DIR)" >&2
  exit 1
fi

case "$AGENT" in
  claude) LAUNCH="claude --remote-control \"$NAME\"" ;;
  codex)
    # systemd starts with a minimal PATH, so prefer the managed nvm install
    # when present. This keeps persistent Codex sessions on the same Node/Codex
    # runtime as the interactive root shell and preserves js_repl availability.
    CODEX_NODE_BIN="${CODEX_NODE_BIN:-/root/.nvm/versions/node/v22.22.0/bin}"
    LAUNCH="env PATH=\"$CODEX_NODE_BIN:\$PATH\" codex"
    ;;
  *)      echo "session-supervisor[$NAME]: unknown agent '$AGENT'" >&2; exit 1 ;;
esac

write_manifest() {
  mkdir -p "$WORKSPACE_SUPERVISOR_SESSIONS_DIR"
  python3 - "$WORKSPACE_SUPERVISOR_SESSIONS_DIR/$NAME.json" "$NAME" "$DIR" "$AGENT" "$ROLE" <<'PY'
import json
import sys
from datetime import datetime, timezone

path, name, cwd, agent, role = sys.argv[1:6]
payload = {
    "session_name": name,
    "cwd": cwd,
    "agent": agent,
    "role": role,
    "kind": "persistent",
    "source": "sessions.conf",
    "desired_state": "running",
    "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
}
with open(path, "w") as fh:
    json.dump(payload, fh, indent=2, sort_keys=True)
    fh.write("\n")
PY
}

# If the session already exists (user started it manually via `ws start`),
# attach supervision to it rather than starting a second copy.
if ! tmux has-session -t "$NAME" 2>/dev/null; then
  echo "session-supervisor[$NAME]: starting tmux session at $DIR (agent: $AGENT)"
  tmux new-session -d -s "$NAME" -c "$DIR" "$LAUNCH"
  sleep 2
  # Nudge past any first-run prompt. Harmless for both agents.
  tmux send-keys -t "$NAME" "" Enter 2>/dev/null || true
else
  echo "session-supervisor[$NAME]: attaching to existing session"
fi

write_manifest

# Block while the session is alive. Poll every 15s.
while tmux has-session -t "$NAME" 2>/dev/null; do
  sleep 15
done

echo "session-supervisor[$NAME]: session exited — systemd will restart us"
exit 1
