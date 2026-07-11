---
from: synthesis-translator
to: general
date: 2026-06-15T03:30:46Z
priority: high
task_id: synthesis-p-reflect-route-known-fixes
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-15T03-27-01Z.md
source_proposal: Proposal 2 — P-reflect-route-known-fixes
---

# P-reflect-route-known-fixes (carry from C97 — 3rd cycle, AT >3-CYCLE FLAG)

**Type:** Shared primitive amendment.
**File:** `supervisor/scripts/lib/reflect-prompt.md`

## What

Amend the reflection prompt to systematically route known-fix handoffs when fix is unambiguous and confirmed in 3+ reflections. Supervisor C38 exercised this authority ad hoc; this systematizes it.

## Proposed amendment to reflect-prompt.md

Add this section after the "Short-circuit rule" section:

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

## Blast radius

All projects via prompt guidance. Low risk.

## Verification before action (required)

- Check if this section already exists in `supervisor/scripts/lib/reflect-prompt.md`
- Supervisor C38 already created a handoff following this authority; verify the handoff exists and was the first use of this pattern

## Acceptance criteria

- The "Action routing rule" section is added to reflect-prompt.md after the existing "Short-circuit rule"
- Change committed with clear message referencing the synthesis source and C38 precedent
- Completion report at `runtime/.handoff/general-synthesis-p-reflect-route-known-fixes-complete-<iso>.md`

## Escalation

URGENT if:
- The section already exists in reflect-prompt.md (verify content matches the proposal)
