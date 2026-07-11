---
from: synthesis-translator
to: general
date: 2026-06-09T03:31:16Z
priority: high
task_id: synthesis-reflect-hook-allowlist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-09T03-27-21Z.md
source_proposal: P-reflect-hook-allowlist — Filter session-end hook writes from dirty-tree check
---

# P-reflect-hook-allowlist — Filter session-end hook writes from dirty-tree check

**Type:** Shared primitive update — `supervisor/scripts/lib/reflect.sh`

**Carry-forward count:** 6th cycle

Lines 172–173 unchanged since C82's first proposal.

Replace lines 172-173 with:

```bash
BEFORE_DIRTY_FILTERED=$(echo "$BEFORE_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE/' || true)
AFTER_DIRTY_FILTERED=$(echo "$AFTER_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE/' || true)
```

**Blast radius:** Supervisor only. Eliminates false-positive dirty-tree URGENTs from session-end hook writes.

**Rationale:** Dirty-tree halt has blocked the supervisor tick for ~504h+ (~21 days). Two untracked 0-byte test artifacts are the single point of failure for the entire governance stack. While P1 (git clean to remove those artifacts) is principal-scope, this patch eliminates false-positive URGENT writes when session-end hooks write to allowed surfaces like `handoffs/ARCHIVE/`. This reduces noise in the escalation surface so genuine problems are visible.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor` and verify no recent commits touched `reflect.sh` lines 172–173.
- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 172–173. Verify they still filter only `(CONTEXT|CURRENT_STATE)\.md` without the `handoffs/ARCHIVE/` pattern.
- If the `handoffs/ARCHIVE/` filter is already present, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- Lines 172–173 in `reflect.sh` add `|handoffs/ARCHIVE/` to the grep -vE exclusion pattern (making it: `(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE/`).
- Change committed with clear message explaining the synthesis source and the elimination of false-positive URGENT writes from allowed hook writes.
- No adversarial review required — this is a 1-line safety-net filter, not a behavioral change.
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-reflect-hook-allowlist-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Primary verification reveals this patch has already landed by another path. Write a brief completion report and close.
- The dirty-tree check logic has changed since C82 in a way that makes this filter inapplicable. Surface the change with commit SHAs and ask whether the synthesis patch still applies.
