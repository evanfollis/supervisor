---
from: synthesis-translator
to: general
date: 2026-06-16T15:28:19Z
priority: high
task_id: synthesis-reflect-route-known-fixes
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-16T15-24-30Z.md
source_proposal: 4. P-reflect-route-known-fixes (carry from C97 — 6th cycle, PAST >3-CYCLE FLAG)
---

# P-reflect-route-known-fixes: Systematic handoff routing for confirmed fixes

## Full proposal from synthesis

**Type:** Shared primitive amendment.
**File:** `supervisor/scripts/lib/reflect-prompt.md`

**What:** Amend the reflection prompt to systematically route known-fix
handoffs when the fix is unambiguous and confirmed in 3+ reflections.

**Blast radius:** All projects via prompt guidance. Low risk.

## Context

When a reflection identifies an issue that has:
1. A concrete, unambiguous fix
2. Confirmation across 3+ independent reflection cycles
3. Clear owner (which session should execute the fix)

...it should automatically route to a handoff rather than just listing it as an
open observation. This moves from "problem surfaced" to "problem + solution
routed for execution."

The synthesis has been carrying several recommendations (P-autocommit-event-order,
P-reflect-route-known-fixes, etc.) for 6-10 cycles, and the reflection system
keeps re-reporting them without action. This amendment ensures that once a fix
is confirmed, it goes to an executable handoff instead of staying in the
observation list.

## Verification before action (required)

- Read recent reflections (last 3 cycles): `ls -1 /opt/workspace/runtime/.meta/*-reflection-*.md | tail -3`
- Identify which observations appear in multiple consecutive reflections with the same "fix available" annotation.
- Confirm that the synthesis is already carrying these as standing recommendations (check synthesis file for `### Proposal` entries).

## Acceptance criteria

1. Open `supervisor/scripts/lib/reflect-prompt.md`.
2. Add a new section `## Known-fix routing rule` with guidance like:
   ```markdown
   ### Known-fix routing
   
   If an observation meets all three criteria:
   - Concrete fix is documented (in a handoff, decision, or prior synthesis proposal)
   - Fix has been confirmed/mentioned in 3+ consecutive reflection cycles
   - Target session/executor is unambiguous
   
   Then: Create a handoff to that session (instead of listing as open observation)
   with the fix details and escalation instructions. Include a pointer to the
   source synthesis or decision. Do not duplicate in the observation list once
   routed.
   ```
3. Provide examples: reference P-autocommit-event-order (fix available, 10 cycles, route to general).
4. Commit with message: "Add known-fix routing rule to reflect-prompt; route confirmed fixes to handoffs"
5. Verify: Next reflection run should detect known-fix candidates and route them instead of re-listing.

## Escalation

URGENT if:
- The routing criteria ("3+ cycles") creates too much noise (false-positive handoffs for issues that are actually blocked or deferred). Adjust the threshold or criteria.
- A reflection routes a fix that was explicitly deferred by a decision. Confirm the decision is current and suspend routing for that item.

