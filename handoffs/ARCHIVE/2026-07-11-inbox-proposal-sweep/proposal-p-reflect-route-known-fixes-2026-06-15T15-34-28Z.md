---
from: synthesis-translator
to: general
date: 2026-06-15T15:34:28Z
priority: high
task_id: synthesis-p-reflect-route-known-fixes
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-15T15-26-25Z.md
source_proposal: "Proposal 3 — P-reflect-route-known-fixes (carry from C97 — 4th cycle, PAST >3-CYCLE FLAG)"
---

# P-reflect-route-known-fixes

**Type:** Shared primitive amendment.
**File:** `supervisor/scripts/lib/reflect-prompt.md`

## Problem

Known-fix handoffs (issues with exact, unambiguous, zero-credential fixes confirmed in 3+ reflection cycles) are not being systematically routed by the reflection job. Supervisor C38 exercised this authority ad hoc, but it needs to be codified.

## Solution

Amend the reflection prompt to systematically route known-fix handoffs when all conditions are met.

Add this section to `supervisor/scripts/lib/reflect-prompt.md`:

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

## Verification before action (required)

- Read `supervisor/scripts/lib/reflect-prompt.md` and check if the "Action routing rule" section already exists.
- If it does, read the existing text and verify it matches the proposed text (allowing for minor wording variations).
- If already present, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- The "Action routing rule" section is added to `reflect-prompt.md` after the existing guidance sections.
- The rule clearly states all 4 preconditions.
- The rule specifies the handoff path and naming convention (`runtime/.handoff/general-<finding-slug>-action-<ts>.md`).
- Change committed with clear message: "Systematize known-fix routing in reflection prompt (synthesis C100, Proposal 3)".

## Escalation

URGENT if:
- Primary verification shows the rule is already in place. Write completion report stating "already landed" and close.
- The condition for routing conflicts with other guidance in the prompt (e.g., "do not create handoffs from reflection jobs"). Escalate with the conflict named.

---

## Notes from synthesis

- Carried from C97 (4th cycle) — past the >3-cycle flag.
- Low risk guidance change.
- Affects all projects via prompt guidance.
