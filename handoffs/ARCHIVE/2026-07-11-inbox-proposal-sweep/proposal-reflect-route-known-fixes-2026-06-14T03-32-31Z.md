---
from: synthesis-translator
to: general
date: 2026-06-14T03:32:31Z
priority: high
task_id: synthesis-reflect-route-known-fixes
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-14T03-27-39Z.md
source_proposal: 2. P-reflect-route-known-fixes (NEW — from supervisor C37)
---

# P-reflect-route-known-fixes — Route known fixes from reflection sessions

## Proposal

**Type:** Shared primitive amendment.  
**File:** `supervisor/scripts/lib/reflect-prompt.md` (or equivalent prompt source used by `reflect.sh`)

**What:** Amend the reflection prompt to route known-fix handoffs to the executive queue when the fix is unambiguous and has been confirmed in 3+ prior reflections.

**Proposed amendment:**

Add a new section to `reflect-prompt.md` after the "Short-circuit rule" section:

```markdown
## Action routing rule

When all of the following are true:
1. A finding has been confirmed in 3+ consecutive reflection cycles
2. The fix is unambiguous (exact file, exact lines, exact change)
3. The fix requires zero credentials and is fully reversible
4. No attended session has acted on it

Then: write `runtime/.handoff/general-<finding-slug>-action-<ts>.md`
containing the fix in copy-pasteable form. One handoff per finding.
Do not re-file if a handoff for the same finding already exists on disk.

This converts reflection from a passive observer to an active router
for the subset of findings where diagnosis is complete and action is
known.
```

**Blast radius:** All projects. Behavioral guidance in prompt, not enforcement. Low risk. Addresses the structural gap identified in the synthesis as Pattern 5. The first concrete use case is FR-D: the fix has been confirmed in 35+ reflection cycles and 5 synthesis cycles.

## Rationale

Supervisor C37 observed that reflection sessions have standing charter authority to write `runtime/.handoff/general-*.md` handoffs but have never exercised it. This amendment makes diagnosis-to-execution routing explicit and automatic for known fixes, reducing the dependency on attended sessions to observe and act on repeated patterns.

## Verification before action (required)

- [VERIFIED] `supervisor/scripts/lib/reflect-prompt.md` does not contain an "Action routing rule" section.
- This proposal has not been landed by another path.

## Acceptance criteria

- A new "## Action routing rule" section is added to `reflect-prompt.md` with the sketch above (or a functionally equivalent version).
- The section appears after the "Short-circuit rule" section.
- Change committed with a message citing the synthesis source and Pattern 5.
- No adversarial review needed (prompt guidance only, no code logic change).
- Completion report at `runtime/.handoff/general-supervisor-synthesis-routing-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- The amendment appears to have already landed by another path.
- The current state of the file contradicts what is described here.
