---
from: synthesis-translator
to: general
date: 2026-06-10T03:31:35Z
priority: high
task_id: synthesis-p-self-sustaining-inactivity
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-10T03-23-06Z.md
source_proposal: "Proposal 3: P-self-sustaining-fix — Exclude automation from inactivity check (CARRY-FORWARD, 8th cycle — remaining piece)"
---

# P-self-sustaining-fix — Exclude automation from inactivity check (remaining piece)

**Type:** Shared primitive update — `supervisor/scripts/lib/reflect.sh`

This is the **third and final piece** of a triple-fix. The previous patch `be5ec96` landed 2 of 3 parts:
- **Write block**: LANDED (line 112 — `Write` added to `--disallowedTools`) ✓
- **Dirty-tree filter**: LANDED (lines 172-173 — `CONTEXT|CURRENT_STATE` excluded) ✓
- **Automation exclusion from inactivity check**: NOT LANDED (lines 56-66 still count all telemetry and JSONL activity) ⚠️

The remaining fix excludes automation-generated events from the inactivity count. This prevents supervisor from appearing "active" when only its own background jobs (autocommit, reflection, etc.) are running.

Implement the automation-exclusion filters:

```bash
# Line 60 — filter automation sources:
TELEMETRY_COUNT=$(tail -n 5000 "$WORKSPACE_TELEMETRY_DIR/events.jsonl" 2>/dev/null \
  | grep -F "\"$PROJECT\"" \
  | grep -v '"source":"session-end-auto-summary"' \
  | grep -v '"source":"reflect"' \
  | grep -v '"source":"autocommit"' \
  | wc -l || true)

# Line 66 — exclude reflect transcripts:
JSONL_RECENT=$(find "$SESSION_DIR" -maxdepth 1 -name '*.jsonl' \
  -not -name '*reflect*' -newermt "12 hours ago" 2>/dev/null | wc -l)
```

**Blast radius:** All 8 projects (automatic). Supervisor is the main beneficiary — it currently never short-circuits because its own automation generates enough telemetry to pass the threshold. Dormant projects already short-circuit correctly. This change does not affect skip behavior — only inactivity detection.

**Impact:** Reduces false-positive activity signals on supervisor and prevents projects from appearing "active" due to only internal automation. Works in conjunction with P-skip-escalation to properly distinguish dormant projects from genuinely paused ones.

## Verification before action (required)

- Run `git log --oneline -10` on `/opt/workspace/supervisor`. Check if this change has already landed (look for changes to lines 60, 66 after `be5ec96`).
- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 56-66. Check if automation filters are already present (grep for `"source":"reflect"` or `"source":"autocommit"`).
- If either is true, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- Line 60: TELEMETRY_COUNT grep chain excludes `session-end-auto-summary`, `reflect`, and `autocommit` sources
- Line 66: JSONL_RECENT find command uses `-not -name '*reflect*'` to exclude reflection transcripts
- Change committed with clear message explaining the synthesis source and the triple-fix completion
- Inactivity detection on supervisor now properly ignores its own background automation
- Reflection skip behavior on dormant projects remains correct (short-circuits as before)
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p-self-sustaining-inactivity-complete-<iso>.md` pointing back to this handoff

## Escalation

URGENT if:
- Primary verification reveals the change is already landed. Write completion report "already landed" and close.
- The filters cause grep/find to fail or produce syntax errors. Include full error output.
- After this change, supervisor begins short-circuiting incorrectly (should only short-circuit on true inactivity). Verify the filters are working as intended and adjust thresholds if needed.
