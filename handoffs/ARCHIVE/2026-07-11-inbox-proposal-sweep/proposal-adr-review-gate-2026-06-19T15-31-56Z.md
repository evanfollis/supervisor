---
from: synthesis-translator
to: general
date: 2026-06-19T15:31:56Z
priority: medium
task_id: synthesis-adr-review-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-19T15-27-31Z.md
source_proposal: 5. P-adr-review-gate
---

# P-adr-review-gate — Pre-commit hook for ADR review artifacts

**Carried from C104. 5 cycles open. ADR-0034/35/36 without required review.**

## Problem

ADR-0034 at 19+ cycles, ADR-0035/36 at 6 cycles without charter-required adversarial review. Compliance is currently honor-system; there is no enforcement.

## Solution

Implement a pre-commit hook that:
1. Detects when an ADR file is being committed
2. Checks if a corresponding `*.review.md` artifact exists in the same directory
3. Rejects the commit if the review artifact is missing (unless the ADR is marked as exempt)

This turns the honor-system ADR review requirement into a hard check.

## Blast radius

Supervisor only. Enforces ADR review compliance at commit time.

## Implementation

**Location:** `supervisor/.git/hooks/pre-commit` (or integrate into existing pre-commit if one exists)

**Logic:**
```
For each ADR file (adr-*.md) being staged:
  If the ADR was created in this same commit (new file):
    Check for adr-*.review.md with matching number
    If missing:
      Exit 1 with message: "ADR review required. Create adr-NNNN.review.md before committing."
  (Existing ADRs can be updated without new review unless marked as requires-review-on-update)
```

## Verification before action (required)

- Read `supervisor/.git/hooks/pre-commit`. Check if an ADR review check is already present.
- Check the charter or CLAUDE.md for documented ADR review requirements.
- If the hook is already present and functional, write a completion report saying "already landed" and close.

## Acceptance criteria

- Pre-commit hook added to supervisor/.git/hooks/pre-commit
- Hook correctly detects new ADRs and requires review artifacts
- Change committed with message explaining the synthesis source
- Completion report at `runtime/.handoff/general-supervisor-synthesis-adr-review-gate-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Note

This is part of the standing recommendations (#27 in synthesis). It complements the "ADRs without review" tracking pattern (Pattern #5).

## Escalation

URGENT if:
- The pre-commit hook is already present and functional.
- The ADR review policy has changed since this proposal was written.
