#!/usr/bin/env bash
# write-handoff.sh — the canonical handoff writer (ADR-0047).
#
# Every non-LLM handoff writer should call this instead of hand-assembling a
# file. It guarantees the three ADR-0047 provenance fields are present and
# SCALAR (newlines are flattened so a value can never become a YAML block/list),
# and it VALIDATES the assembled file with check-handoff-provenance.py BEFORE
# moving it into the dispatch dir. An invalid handoff is refused, not published —
# closing the "gate landed without a pre-publication check" gap.
#
# Body is read from stdin.
#
#   write-handoff.sh --to <session> --slug <slug> [--from X] [--priority high] \
#     [--authority "…"] [--external-dependencies none|authorized] \
#     [--policy-compatibility "…"] [--extra 'key: value']… < body.md
#
# Prints the published path on success; exits non-zero (nothing published) on
# any validation failure.
set -euo pipefail

HANDOFF_DIR="${HANDOFF_DIR:-/opt/workspace/runtime/.handoff}"
CHECK="$(cd "$(dirname "$0")" && pwd)/check-handoff-provenance.py"

from="unspecified"; to=""; slug=""; priority="high"
authority="reversible-action scope under ADR-0020"
external_dependencies="none"
policy_compatibility="verified against matching accepted Decisions; no conflict found"
declare -a extra=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --to) to="$2"; shift 2;;
    --slug) slug="$2"; shift 2;;
    --from) from="$2"; shift 2;;
    --priority) priority="$2"; shift 2;;
    --authority) authority="$2"; shift 2;;
    --external-dependencies) external_dependencies="$2"; shift 2;;
    --policy-compatibility) policy_compatibility="$2"; shift 2;;
    --extra) extra+=("$2"); shift 2;;
    *) echo "write-handoff: unknown arg $1" >&2; exit 2;;
  esac
done

[[ -n "$to" && -n "$slug" ]] || { echo "write-handoff: --to and --slug required" >&2; exit 2; }

# Flatten any newlines/CRs so a supplied value can never become a block/list.
scalarize() { printf '%s' "$1" | tr '\n\r' '  '; }

iso="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
mkdir -p "$HANDOFF_DIR"
target="$HANDOFF_DIR/${to}-${slug}-${iso}.md"
tmp="$(mktemp "${HANDOFF_DIR}/.write-handoff.XXXXXX")"
trap 'rm -f "$tmp"' EXIT

{
  echo "---"
  echo "from: $(scalarize "$from")"
  echo "to: $(scalarize "$to")"
  echo "date: ${iso}"
  echo "priority: $(scalarize "$priority")"
  echo "authority: $(scalarize "$authority")"
  echo "external_dependencies: $(scalarize "$external_dependencies")"
  echo "policy_compatibility: $(scalarize "$policy_compatibility")"
  for kv in "${extra[@]:-}"; do
    [[ -n "$kv" ]] && echo "$(scalarize "$kv")"
  done
  echo "---"
  echo
  cat
} > "$tmp"

# Validate BEFORE publication. Force validation regardless of ctime cutoff by
# passing an ancient cutoff, so the gate always runs on new writes.
if ! err="$(python3 "$CHECK" "$tmp" "2000-01-01T00:00:00Z" 2>&1)"; then
  echo "write-handoff: REFUSED to publish invalid handoff: $err" >&2
  exit 1
fi

mv -- "$tmp" "$target"
trap - EXIT
echo "$target"
