---
from: synthesis-translator
to: general
date: 2026-06-07T03:32:57Z
priority: high
task_id: synthesis-reflect-hook-allowlist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-07T03-27-00Z.md
source_proposal: 2. P-reflect-hook-allowlist — Filter session-end hook writes from dirty-tree check
---

# P-reflect-hook-allowlist — Filter session-end hook writes from dirty-tree check

**Type:** Shared primitive update — `supervisor/scripts/lib/reflect.sh`

**Context:** The session-end hook writes files to `handoffs/` during normal operation. The dirty-tree check at lines 172–173 counts these as unexpected mutations and generates false-positive URGENT handoffs. Adding an exclusion pattern for `handoffs/ARCHIVE/` (where completed/archived handoffs live) eliminates these spurious alerts without changing the safety net's core function.

**Proposed change (lines 172–173):**

Extend the existing grep filter to exclude `handoffs/ARCHIVE/`:

```bash
BEFORE_DIRTY_FILTERED=$(echo "$BEFORE_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE/' || true)
AFTER_DIRTY_FILTERED=$(echo "$AFTER_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE/' || true)
```

**Current state (lines 172–173):**
```bash
BEFORE_DIRTY_FILTERED=$(echo "$BEFORE_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md' || true)
AFTER_DIRTY_FILTERED=$(echo "$AFTER_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md' || true)
```

**Blast radius:** Supervisor only (other projects lack `handoffs/ARCHIVE/`). Eliminates false-positive URGENT generation from session-end hook writes. Independent of P1 (destructive git clean).

**Rationale:** The safety net is correct to be suspicious of working-tree mutations, but session-end hook writes to archive directories are expected and should not trigger escalations. This is a narrowing of the filter, not a weakening of the safety net.

## Verification before action (required)

- Run `git log --oneline -20 supervisor/scripts/lib/reflect.sh` to check if this has landed via another path.
- Read `supervisor/scripts/lib/reflect.sh` lines 172–173. Verify they do NOT contain the `|handoffs/ARCHIVE/` pattern.
- If either verification fails, write a completion report stating which commit this was already landed in.

## Acceptance criteria

- Lines 172–173 are updated to filter `handoffs/ARCHIVE/` from the dirty-tree check.
- Change committed with a message explaining the synthesis source (e.g., "Filter hook-generated archive writes from dirty-tree check (synthesis C83)").
- No adversarial review required (narrowing an existing filter pattern).
- Completion report written to `/opt/workspace/supervisor/handoffs/INBOX/completion-reflect-hook-allowlist-<iso>.md` with a brief summary of the change and expected impact on false-positive URGENTs.

## Escalation

URGENT if:
- Primary verification reveals this has already landed. Record the commit hash and close.
- The proposed change conflicts with a more recent modification to the same lines. Surface the conflict with both versions.
