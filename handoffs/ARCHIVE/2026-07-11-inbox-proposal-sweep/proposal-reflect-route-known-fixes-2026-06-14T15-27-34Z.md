---
from: synthesis-translator
to: general
date: 2026-06-14T15:27:34Z
priority: high
task_id: synthesis-reflect-route-known-fixes
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-14T15-23-48Z.md
source_proposal: 2. P-reflect-route-known-fixes (carry from C97 — 2nd cycle)
---

# P-reflect-route-known-fixes — Systematize reflection-routed action handoffs

## Proposal

Amend the reflection prompt (`supervisor/scripts/lib/reflect-prompt.md`) to formalize the authority for reflection sessions to route known-fix handoffs to the executive queue when the fix is unambiguous and confirmed in 3+ prior reflections.

Supervisor C38 exercised this authority ad hoc on 2026-06-14 by writing the first-ever reflection-routed action handoff for FR-D. This proposal systematizes that behavior so future reflections can route other known fixes (atlas P2, context-repo push, etc.) without rediscovering the authority each time.

## Full proposal text from synthesis

**Type:** Shared primitive amendment.
**File:** `supervisor/scripts/lib/reflect-prompt.md`

**What:** Amend the reflection prompt to route known-fix handoffs to
the executive queue when the fix is unambiguous and confirmed in 3+
prior reflections. Supervisor C38 exercised this authority ad hoc for
FR-D — this proposal systematizes it.

**Sketch (unchanged from C97):**
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

## Verification before action (required)

- Check `supervisor/scripts/lib/reflect-prompt.md` for any existing "action routing" or "known fix" section.
- Review the FR-D action handoff at `runtime/.handoff/general-frd-action-2026-06-14T14-26-40Z.md` as a reference for what the output format should be.
- Confirm no existing guidance in the prompt would conflict with this amendment.

## Acceptance criteria

- The action routing rule is added to `supervisor/scripts/lib/reflect-prompt.md` under a new `## Action routing rule` section.
- The rule is clear enough that future reflection sessions can apply it without re-deriving the authority.
- A commit is created explaining that this formalizes the ad hoc pattern supervisor C38 established on 2026-06-14.
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` is recommended to verify the wording is unambiguous.

## Escalation

URGENT if:
- The prompt has already been amended with a similar rule (already landed).
- The reflection prompt structure makes this addition impossible (e.g., hardcoded template that doesn't allow new sections). If so, escalate with a structural constraint note.
