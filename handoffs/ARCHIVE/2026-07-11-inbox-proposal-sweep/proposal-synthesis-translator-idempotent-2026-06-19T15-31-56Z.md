---
from: synthesis-translator
to: general
date: 2026-06-19T15:31:56Z
priority: medium
task_id: synthesis-synthesis-translator-idempotent
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-19T15-27-31Z.md
source_proposal: 4. P-synthesis-translator-idempotent
---

# P-synthesis-translator-idempotent — Slug-existence check to prevent duplicate INBOX deposits

**Carried from C104. 8 cycles open.**

## Problem

The synthesis-translator tool can emit duplicate handoffs if re-run on the same synthesis file. This produces duplicate INBOX entries.

## Solution

Add slug-existence check to `synthesis-translator.sh` to verify that a handoff for the same (synthesis, proposal) pair hasn't already been written before emitting.

**Location:** `supervisor/scripts/lib/synthesis-translator.sh` (or the tool that invokes it)

## Implementation

Before writing a new handoff file, check if a file matching the slug already exists in the target directory:
- For supervisor-targeted proposals: check `supervisor/handoffs/INBOX/proposal-<slug>-*.md`
- For project-targeted proposals: check `runtime/.handoff/<project>-proposal-<slug>-*.md`

If found, skip the handoff and log a note rather than overwriting.

## Blast radius

Supervisor only. Prevents duplicate INBOX deposits on repeated translator runs.

## Verification before action (required)

- Read `supervisor/scripts/lib/synthesis-translator.sh`. Check if a slug-existence check is already present.
- If yes, write a completion report saying "already landed in synthesis-translator.sh" and close.

## Acceptance criteria

- Slug-existence check added to the translator before handoff writes.
- Change committed with message explaining the synthesis source.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-synthesis-translator-idempotent-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Note

This proposal ensures the translator itself is safe to re-run without producing duplicate work.

## Escalation

URGENT if:
- The idempotent check has already landed by another path.
- The translator architecture has fundamentally changed since this proposal was written, requiring a different approach.
