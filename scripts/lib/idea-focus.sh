#!/usr/bin/env bash
set -euo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"

python3 "$LIB_DIR/idea-focus.py" \
  --ideas-dir "$SUPERVISOR_ROOT/ideas" \
  --meta-dir "$WORKSPACE_META_DIR" \
  --latest-pointer "$WORKSPACE_META_DIR/LATEST_IDEA_FOCUS"
