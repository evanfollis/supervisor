---
from: synthesis-translator
to: supervisor
date: 2026-05-17T03:30:27Z
priority: high
task_id: synthesize-auto-deferral-mechanism
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-17T03-27-50Z.md
source_proposal: Proposal 4 (CARRIED from cycle 40, 2nd cycle) — Mechanize dispatch obligation with auto-deferral
---

# Mechanize dispatch obligation with auto-deferral

The synthesis job should write an auto-deferral record when it detects an expired dispatch obligation with no corresponding dispatch or deferral file. This prevents silent obligation breaches and makes queue backlog explicit.

**Mechanism:** After the synthesis job writes its `cross-cutting-<iso>.md` file, it should scan for handoffs in `/opt/workspace/runtime/.handoff/` that are:
- Addressed to `general` (dispatch obligation target)
- Older than 24 hours (past dispatch deadline)
- Do not have a corresponding `.done` marker or deferral record

For each, emit an auto-deferral record to `/opt/workspace/supervisor/handoffs/INBOX/` recording:
- The original handoff filename
- The creation timestamp
- The current age (hours past deadline)
- An auto-deferral marker indicating synthesis detected and recorded the expired deadline

**Type:** Shared primitive change — `synthesize.sh`.  
**Blast radius:** Synthesis job only (automatic). Does not dispatch work — only records that the deadline passed without action.  
**Cycles open:** 2 (proposed in cycles 40, 41; no implementation yet).

## Implementation sketch

In `synthesize.sh`, after the main synthesis write, add:

```bash
# Auto-deferral of expired dispatch obligations.
GENERAL_HANDOFF_DIR="/opt/workspace/runtime/.handoff"
INBOX_DIR="/opt/workspace/supervisor/handoffs/INBOX"
CURRENT_TIME=$(date +%s)
DEADLINE_SECS=$((24 * 3600))

find "$GENERAL_HANDOFF_DIR" -maxdepth 1 -name 'general-*.md' -type f 2>/dev/null | while read -r handoff; do
  MTIME=$(stat -c %Y "$handoff" 2>/dev/null || echo 0)
  AGE_SECS=$(( CURRENT_TIME - MTIME ))
  
  if [[ "$AGE_SECS" -gt "$DEADLINE_SECS" ]]; then
    # Check if already marked done or deferred.
    BASENAME=$(basename "$handoff" .md)
    if [[ ! -f "$HANDOFF_DIR/${BASENAME}.done" && ! -f "$INBOX_DIR/deferral-${BASENAME}-*.md" ]]; then
      # Emit auto-deferral record.
      AGE_HOURS=$(( AGE_SECS / 3600 ))
      cat > "$INBOX_DIR/auto-deferral-$(basename "$handoff" .md)-${ISO_NOW}.md" <<EOF
---
from: synthesize.sh (auto-deferral)
type: auto-deferral
source_handoff: $(basename "$handoff")
age_hours: $AGE_HOURS
detected: $ISO_NOW
---

Dispatch obligation expired: $(basename "$handoff") is $AGE_HOURS hours past 24h deadline.

Original file: $handoff
EOF
    fi
  fi
done
```

## Verification before action (required)

- Locate `/opt/workspace/supervisor/scripts/lib/synthesize.sh`.
- Check if auto-deferral logic is already present (grep for "auto-deferral" or "dispatch obligation").
- Verify that `/opt/workspace/runtime/.handoff/` contains at least one `general-*.md` file older than 24 hours (evidence that the gate would be useful).

## Acceptance criteria

- Auto-deferral logic is added to `synthesize.sh` to run after the main synthesis write.
- The logic correctly identifies handoffs to `general` older than 24 hours without a `.done` marker.
- Auto-deferral records are emitted to `supervisor/handoffs/INBOX/` with clear metadata (original handoff name, age, detection time).
- Change committed with message: "Add auto-deferral mechanism to synthesize.sh to surface expired dispatch obligations."
- No impact on existing handoff processing — auto-deferral only records expired items, does not delete or archive them.

## Escalation

URGENT if:
- Auto-deferral logic is already present (already landed). Write a completion report and close.
- The auto-deferral implementation conflicts with existing handoff cleanup/archival procedures. Escalate with the conflict named.
