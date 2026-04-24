#!/bin/bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

print_file() {
  local path="$1"
  [[ -f "$path" ]] || return 0
  printf '## %s\n\n' "${path#$ROOT/}"
  cat "$path"
  printf '\n\n'
}

print_capabilities() {
  local probe="$ROOT/scripts/lib/capability-attestation.sh"
  [[ -x "$probe" ]] || return 0
  printf '## capability-attestation\n\n'
  "$probe" --markdown
  printf '\n\n'
}

print_capabilities

# Reentry hygiene: keep low-priority session summaries out of the active queue
# before we refresh verified state and print the current context bundle.
if [[ -x "$ROOT/scripts/lib/archive-inbox-session-summaries.sh" ]]; then
  "$ROOT/scripts/lib/archive-inbox-session-summaries.sh" >/dev/null 2>&1 || true
fi

# Refresh verified-state.md before emitting. Best-effort; never blocks.
if [[ -x "$ROOT/scripts/lib/verify-state.sh" ]]; then
  "$ROOT/scripts/lib/verify-state.sh" >/dev/null 2>&1 || true
fi

print_file "$ROOT/AGENT.md"
print_file "$ROOT/system/verified-state.md"
print_file "$ROOT/system/status.md"
print_file "$ROOT/system/active-issues.md"
print_file "$ROOT/system/paid-services.md"
print_file "$ROOT/system/active-ideas.md"

for path in "$ROOT"/projects/*.md; do
  [[ "$(basename "$path")" == "README.md" ]] && continue
  print_file "$path"
done

for path in "$ROOT"/roles/*.md; do
  [[ "$(basename "$path")" == "README.md" ]] && continue
  print_file "$path"
done
