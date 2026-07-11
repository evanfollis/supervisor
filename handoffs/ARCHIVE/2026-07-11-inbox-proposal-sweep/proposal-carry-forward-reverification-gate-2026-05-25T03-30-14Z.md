---
from: synthesis-translator
to: general
date: 2026-05-25T03:30:14Z
priority: high
task_id: synthesis-carry-forward-reverification
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-25T03-24-49Z.md
source_proposal: Proposal 3 (STRUCTURAL — new)
---

# Add carry-forward re-verification step to reflection prompt template

**Type:** Shared primitive fix (`reflect-prompt.md` or `reflect-supervisor-prompt.md`).

**What:** Add a verification gate before any carry-forward assertion. When a reflection carries forward an observation from a prior cycle, it must re-run the canonical diagnostic command (from the prior cycle's Proposals section) before asserting "still unresolved." If the command returns clean, mark the observation RESOLVED.

**Why:** 3 documented instances of reflections filing URGENTs against already-fixed issues (Pattern 2). The false URGENTs consume INBOX capacity and attended-session attention — two resources the workspace is already short on. A re-verification step eliminates stale carry-forwards as a failure class.

**Blast radius:** All reflected projects (automatic). Changes prompt template behavior only.

**Sketch (addition to reflect prompt template):**
```markdown
### Carry-forward gate
Before re-asserting any observation from the prior reflection cycle as
"unresolved," re-run the diagnostic command or check named in that
observation's Proposals section. If the diagnostic now passes, mark the
observation RESOLVED in this reflection and do NOT file an URGENT.
```

## Verification before action (required)

- Check if `reflect-prompt.md` and `reflect-supervisor-prompt.md` already contain a carry-forward re-verification section. If present in either, mark as resolved and close.
- Identify the best location to add the gate: after the "Observations" section and before the "Proposals" section is the natural spot.

## Acceptance criteria

- A "Carry-forward gate" section is added to the reflection prompt template (or both templates if both exist).
- The section clearly instructs the reflection to re-verify diagnostic commands before re-asserting carry-forward observations.
- Change committed with clear message explaining the false-URGENT elimination.
- Next reflection cycle confirm that stale carry-forwards are re-verified before re-assertion.

## Escalation

URGENT if:
- The reflection prompt has recently been refactored and the carry-forward instruction already exists under a different name or structure. If so, verify with the principal whether an additional explicit gate is still needed or if the existing structure is sufficient.
