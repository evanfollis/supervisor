---
from: synthesis-translator
to: general
date: 2026-04-25T03:32:44Z
priority: low
task_id: synthesis-translator-iso-timestamp
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-25T03-27-27Z.md
source_proposal: Proposal 5 — Fix synthesis-translator ISO timestamp in JSON events
---

# Fix synthesis-translator ISO timestamp in JSON events

## Context

The `synthesis-translator.sh` script emits friction events with malformed ISO 8601 timestamps. All timestamps use the format `2026-04-24T15-33-47Z` (dashes in the time portion) instead of the correct ISO 8601 format `2026-04-24T15:33:47Z` (colons). Any downstream datetime parser fails silently on the malformed timestamp.

The root cause: a single `ISO_NOW` variable is used for both filenames (where dashes are correct) and JSON event fields (where colons are required per ISO 8601).

## Proposed Change

**In `supervisor/scripts/lib/synthesis-translator.sh`** — split the timestamp variable (line 40):

```bash
# Current (line 40):
# ISO_NOW="$(date -u +%Y-%m-%dT%H-%M-%SZ)"

# Proposed: separate concerns
ISO_FILENAME="$(date -u +%Y-%m-%dT%H-%M-%SZ)"       # for file paths: dashes correct
ISO_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"            # for JSON events: colons correct ISO 8601

# Then use ISO_FILENAME for file paths and ISO_TS for the "ts" field in events
```

Search for all uses of `ISO_NOW` in the script and replace:
- Handoff file path constructions → use `ISO_FILENAME`
- JSON event `ts` fields → use `ISO_TS`

## Why

ISO 8601 requires colons in the time portion (`HH:MM:SS`). The current format with dashes is non-standard and causes datetime parsers to fail silently. The fix is minimal: split the variable and use the correct format for each context.

## Acceptance criteria

- Variable split implemented as shown above
- All handoff file paths use `ISO_FILENAME` (preserves current naming)
- All JSON event `ts` fields use `ISO_TS` (fixes ISO 8601 compliance)
- Change committed with message explaining the synthesis source
- Verify with `grep -n "ts.*ISO" synthesis-translator-*.log` — should show ISO_TS usage
- Completion report at `runtime/.handoff/general-supervisor-synthesis-translator-iso-complete-<iso>.md` pointing back to this handoff and the source synthesis

## Blast radius

**Minimal.** One script, two variables, no behavioral change for filenames. Event format improves (becomes standards-compliant). No project-level impact.

## Notes

After this change, friction events emitted by synthesis-translator will have properly formatted ISO 8601 timestamps like `2026-04-25T03:32:44Z` instead of `2026-04-25T03-32-44Z`. Any downstream indexing or parsing will work correctly.
