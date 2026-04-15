#!/usr/bin/env bash
# Invoke reflect.sh for every project listed in projects.conf.
# Each project is independent — a failure in one doesn't stop the others.

set -uo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"
CONF="$WORKSPACE_PROJECTS_CONF"

if [[ ! -f "$CONF" ]]; then
  echo "reflect-all: missing $CONF" >&2
  exit 1
fi

FAILED=()
while IFS='|' read -r name path prompt; do
  # Skip comments and blank lines
  [[ -z "${name// }" ]] && continue
  [[ "${name:0:1}" == "#" ]] && continue
  name="$(echo "$name" | xargs)"
  path="$(echo "$path" | xargs)"
  prompt="$(echo "${prompt:-}" | xargs)"

  if [[ ! -d "$path" ]]; then
    echo "reflect-all: skipping $name — $path not found"
    continue
  fi

  echo "=== reflect-all: $name ($path)${prompt:+ [prompt=$prompt]} ==="
  if ! "$LIB_DIR/reflect.sh" "$name" "$path" "$prompt"; then
    echo "reflect-all: $name FAILED" >&2
    FAILED+=("$name")
  fi
done < "$CONF"

if [[ ${#FAILED[@]} -gt 0 ]]; then
  echo "reflect-all: ${#FAILED[@]} project(s) failed: ${FAILED[*]}" >&2
  exit 2
fi
echo "reflect-all: all projects complete"
