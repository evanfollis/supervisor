---
from: synthesis-translator
to: general
date: 2026-06-16T03:28:14Z
priority: high
task_id: synthesis-reflect-route-known-fixes
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-16T03-23-07Z.md
source_proposal: 4. P-reflect-route-known-fixes (carry from C97 — 5th cycle, PAST >3-CYCLE FLAG)
---

# P-reflect-route-known-fixes

**Type:** Shared primitive amendment.
**File:** `supervisor/scripts/lib/reflect-prompt.md`

**What:** Amend the reflection prompt to systematically route known-fix handoffs when the fix is unambiguous and confirmed in 3+ reflections.

**Sketch (unchanged from C97–C100):**
```markdown
## Action routing rule

When all of the following are true:
1. A finding has been confirmed in 3+ consecutive reflection cycles
2. The fix is unambiguous (exact file, exact lines, exact change)
3. The fix requires zero credentials and is fully reversible
4. No attended session has acted on it

Then: write `runtime/.handoff/general-<finding-slug>-action-<ts>.md`
containing the fix in copy-pasteable form. One handoff per finding.
Do not re-file if a handoff for the same finding already exists.
```

**Blast radius:** All projects via prompt guidance. Low risk.

## Background

This proposal has been carried for 5 cycles. It formalizes when reflections should escalate a finding to an explicit action handoff. This channels mechanical repetition (the same bug diagnosed 3+ times) into concrete executable work. The reflection job becomes an amplifier for known fixes, not just a diagnostic logger.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor`. Check if this proposal has already landed via a commit adding the action routing rule to reflect-prompt.md.
- Read `supervisor/scripts/lib/reflect-prompt.md`. Check if an "Action routing rule" or similar section already exists with the 3+-cycle and fix-unambiguity gates.
- If either check shows the guidance is already in place, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- Action routing rule section added to `supervisor/scripts/lib/reflect-prompt.md` with clear criteria (3+ cycles, unambiguous fix, zero credentials, reversible, no attended action).
- Rule includes guidance on handoff format and slug derivation.
- Rule includes guidance on deduplication (do not re-file if handoff already exists for this finding).
- Change committed with a message explaining the motivation (surface known fixes from repeated diagnostics).
- Completion report at `supervisor/handoffs/ARCHIVE/<iso>/general-reflect-route-known-fixes-complete.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Verification reveals the guidance is already in place. Write a brief completion report and close.
- The reflect-prompt.md file has structural changes that make the proposed addition conflict. Detail the conflict.
