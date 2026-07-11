---
from: synthesis-translator
to: general
date: 2026-05-25T03:30:14Z
priority: high
task_id: synthesis-synthesis-reviewed-event
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-25T03-24-49Z.md
source_proposal: Proposal 1 (CONCRETE — regression fix)
---

# Add explicit `synthesis_reviewed` instruction to tick prompt template

**Type:** Shared primitive fix (`supervisor-tick-prompt.md`).

**What:** Add to step 6 ("Route open items from recent synthesis"):
```markdown
6. **Route open items from recent synthesis**. Read the most recent
   `/opt/workspace/runtime/.meta/cross-cutting-*.md`. For each
   proposal not yet in `system/active-issues.md` or a handoff, add a
   line to `system/active-issues.md` **or** open a handoff to the
   relevant project. Do not accept ADRs unilaterally.
   **After processing**, emit a `synthesis_reviewed` event in
   `supervisor-events.jsonl` with the synthesis file ref and a one-line
   summary of actions taken.
```

**Why:** The `synthesis_reviewed` event was reliably emitted through cycle-54 by model inference. When the tick's behavioral load increased (question-promotion at 16:47Z), the model dropped the implicit emit. Making it explicit in the prompt template eliminates the dependency on model inference. Zero-risk: adds one event emission instruction to an existing step.

**Blast radius:** Supervisor tick only (automatic). No project impact.

## Verification before action (required)

- Check `/opt/workspace/supervisor/scripts/lib/supervisor-tick-prompt.md` step 6. If the `synthesis_reviewed` event instruction is already present, mark as resolved and close.
- If not present, apply the patch.

## Acceptance criteria

- The `synthesis_reviewed` event emission instruction is added to step 6 of supervisor-tick-prompt.md.
- Change committed with clear message explaining the regression fix.
- Next supervisor tick (or current tick if running before application) emits the event successfully.

## Escalation

URGENT if:
- The event emission logic is already present under a different instruction or elsewhere in the prompt — before applying, verify the state to avoid duplication.
