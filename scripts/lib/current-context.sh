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
print_file "$ROOT/AGENT.md"
print_file "$ROOT/system/status.md"
print_file "$ROOT/system/active-issues.md"
print_file "$ROOT/system/active-ideas.md"

for path in "$ROOT"/projects/*.md; do
  [[ "$(basename "$path")" == "README.md" ]] && continue
  print_file "$path"
done

for path in "$ROOT"/roles/*.md; do
  [[ "$(basename "$path")" == "README.md" ]] && continue
  print_file "$path"
done
