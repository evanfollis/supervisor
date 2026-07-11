---
from: synthesis-translator
to: general
date: 2026-06-15T15:34:28Z
priority: medium
task_id: synthesis-p-synthesis-mtime-verification
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-15T15-26-25Z.md
source_proposal: "Proposal 6 — P-synthesis-mtime-verification (NEW — from Pattern 5 correction)"
---

# P-synthesis-mtime-verification

**Type:** `supervisor/scripts/lib/synthesize-prompt.md` amendment.

## Problem

C99 synthesis overstated the age of the FR-D action handoff by ~24 hours, classifying it as "structurally threatened" when it still had ~23h before the 48h threshold. The error arose from carrying forward age estimates from prior synthesis cycles instead of verifying from file mtimes.

This creates synthetic urgency and violates the workspace radical-truth standard.

## Solution

Add a verification instruction to the synthesis prompt requiring it to check artifact ages via file mtime (stat) rather than carrying forward estimates.

Add this section to `supervisor/scripts/lib/synthesize-prompt.md`:

```markdown
## Age verification rule

When reporting the age of a file-based artifact (handoff, URGENT, etc.),
verify the age from the file's mtime via `stat -c '%Y'`, not by
carrying forward an estimate from a prior synthesis or reflection.
State the mtime and current epoch in the citation.
```

## Verification before action (required)

- Read `supervisor/scripts/lib/synthesize-prompt.md` and check if an "Age verification rule" section already exists.
- If it does, verify the rule requires mtime-based verification rather than estimates.
- If already present, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- The "Age verification rule" section is added to `synthesize-prompt.md`.
- The rule explicitly requires stat-based verification (or equivalent mtime-checking tool).
- The rule explicitly forbids carrying forward age estimates from prior synthesis cycles.
- Change committed with clear message: "Require mtime-based age verification in synthesis job (synthesis C100, Pattern 5)".

## Escalation

URGENT if:
- Primary verification shows the rule is already in place. Write completion report stating "already landed" and close.

---

## Notes from synthesis

- NEW finding from Pattern 5 (radical-truth correction).
- Synthesis job only — no projects affected.
- Eliminates age-estimation drift in the governance diagnostic layer.
