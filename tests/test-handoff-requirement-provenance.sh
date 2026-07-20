#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DISPATCHER="$ROOT/scripts/lib/dispatch-handoffs.sh"
CHECKER="$ROOT/scripts/lib/check-handoff-provenance.py"
WRITER="$ROOT/scripts/lib/write-handoff.sh"

# Keep the test coupled to the actual dispatcher contract without invoking its
# fixed runtime paths or tmux side effects.
for required in \
  'PROVENANCE_GATE_CUTOFF=' \
  'check-handoff-provenance.py' \
  'handoff.dispatch_rejected' \
  'URGENT-requirement-provenance-'; do
  grep -Fq "$required" "$DISPATCHER"
done

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

printf '%s\n' \
  '---' \
  'authority: ADR-0047' \
  'external_dependencies: none' \
  'policy_compatibility: ADR-0036 checked' \
  '---' > "$tmp/valid.md"

printf '%s\n' \
  '---' \
  'authority: ADR-0047' \
  'external_dependencies:' \
  '---' > "$tmp/invalid.md"

printf '%s\n' \
  '---' \
  'authority: ADR-0047' \
  'external_dependencies: none' \
  'policy_compatibility: ADR-0036 checked' > "$tmp/unclosed.md"

printf '%s\n' \
  '---' \
  'authority: TBD' \
  'external_dependencies: none' \
  'policy_compatibility: null' \
  '---' > "$tmp/placeholders.md"

printf '%s\n' \
  '---' \
  'authority: principal directive' \
  'external_dependencies: authorized' \
  'policy_compatibility: ADR-0036 checked' \
  '---' > "$tmp/authorized-incomplete.md"

"$CHECKER" "$tmp/valid.md" '1970-01-01T00:00:00Z'
error=$("$CHECKER" "$tmp/invalid.md" '1970-01-01T00:00:00Z' 2>&1) && exit 1
[[ "$error" == 'missing required provenance fields: external_dependencies policy_compatibility' ]]
error=$("$CHECKER" "$tmp/unclosed.md" '1970-01-01T00:00:00Z' 2>&1) && exit 1
[[ "$error" == 'missing or unclosed YAML frontmatter' ]]
error=$("$CHECKER" "$tmp/placeholders.md" '1970-01-01T00:00:00Z' 2>&1) && exit 1
[[ "$error" == 'missing required provenance fields: authority policy_compatibility' ]]
error=$("$CHECKER" "$tmp/authorized-incomplete.md" '1970-01-01T00:00:00Z' 2>&1) && exit 1
[[ "$error" == 'authorized external dependency missing fields: dependency_authority dependency_details' ]]

# Pre-cutover handoffs are historical and remain dispatchable without mutation.
"$CHECKER" "$tmp/invalid.md" '2999-01-01T00:00:00Z'

# The canonical writer must reject a provenance-only handoff. Missing stdin was
# previously publishable and left project agents with a valid header but no
# task or acceptance criteria.
writer_handoffs="$tmp/writer-handoffs"
mkdir -p "$writer_handoffs"
error=$(HANDOFF_DIR="$writer_handoffs" "$WRITER" \
  --to command --slug empty-body \
  --authority "ADR-0047 test" \
  --external-dependencies none \
  --policy-compatibility "test fixture" </dev/null 2>&1) && exit 1
[[ "$error" == 'write-handoff: REFUSED to publish empty handoff body' ]]
[[ $(find "$writer_handoffs" -maxdepth 1 -type f | wc -l) -eq 0 ]]

published=$(printf '%s\n' '# Concrete task' 'Ship and verify it.' | \
  HANDOFF_DIR="$writer_handoffs" "$WRITER" \
    --to command --slug nonempty-body \
    --authority "ADR-0047 test" \
    --external-dependencies none \
    --policy-compatibility "test fixture")
[[ -f "$published" ]]
grep -Fq '# Concrete task' "$published"

# End-to-end: the dispatcher moves a malformed new project handoff out of the
# PM's direct-scan path, preserves it, emits telemetry, and escalates once.
handoffs="$tmp/handoffs"
inbox="$tmp/inbox"
telemetry="$tmp/telemetry/events.jsonl"
mkdir -p "$handoffs" "$inbox"
cp "$tmp/invalid.md" "$handoffs/command-malformed.md"
HANDOFF_DIR="$handoffs" \
TELEMETRY_LOG="$telemetry" \
PROVENANCE_INBOX="$inbox" \
PROVENANCE_GATE_CUTOFF='1970-01-01T00:00:00Z' \
  "$DISPATCHER"

[[ ! -e "$handoffs/command-malformed.md" ]]
[[ $(find "$handoffs/REJECTED" -type f -name '*-command-malformed.md' | wc -l) -eq 1 ]]
[[ $(find "$inbox" -type f -name 'URGENT-requirement-provenance-*.md' | wc -l) -eq 1 ]]
grep -Fq 'handoff.dispatch_rejected' "$telemetry"
grep -Fq 'Quarantined intact at' "$inbox"/URGENT-requirement-provenance-*.md

# Internal checker diagnostics remain explicit and machine-distinguishable.
error=$("$CHECKER" "$tmp/does-not-exist.md" '1970-01-01T00:00:00Z' 2>&1) && exit 1
[[ "$error" == provenance\ checker\ internal\ error:* ]]

echo "test-handoff-requirement-provenance: PASS"
