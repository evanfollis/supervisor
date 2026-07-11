---
from: synthesis-translator
to: general
date: 2026-07-02T15:26:24Z
priority: medium
task_id: synthesis-reflection-cadence-gating
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-02T15-23-04Z.md
source_proposal: P2 (CARRY — C114, 7th cycle)
---

# P2: Reflection cadence gating for automated-only windows

**Type:** `reflect.sh` change.

**Context:** C120 evaluation notes "10th consecutive 12h window with no substantive attended session" and assesses that suppression criteria are met. Reflection cadence gating would short-circuit reflection runs during windows with no attended activity, reducing token waste on counter-increment cycles.

**Synthesis text (as written):**

> **Type:** `reflect.sh` change.
> **Blast radius:** All reflected projects (opt-in via `projects.conf`).

## Implementation guidance (from context)

The synthesis carries this proposal through 7 cycles (C114 → C120) with minimal elaboration. The expected behavior:

- If the current 12h reflection window contains no attended sessions (only counter increments, no substantive code changes, no governance output), skip the reflection run.
- Preserve the counter-increment tracking for C120+ evaluation of carry-forward depth.
- This is an opt-in gating mechanism; should not affect projects without active reflection registration in `projects.conf`.

The synthesis demonstrates this is working: "12 of 16 reflections short-circuit correctly. Token savings remain real." This suggests the gating mechanism may already be partially present or the proposal is a formal codification of existing behavior.

## Verification before action (required)

- Check `reflect.sh` for existing window-activity gates or "substantive session" detection logic.
- If gating already exists, check its implementation against the proposal intent and file a completion report: "already gated at [line range]" with an explanation of the existing mechanism.
- Check `projects.conf` to understand which projects are opt-in to reflection.

## Acceptance criteria

- A check in `reflect.sh` that evaluates window activity (attended session indicator or dirty-tree state change).
- Conditional logic that skips the full reflection run if the window contains only counter increments.
- Preservation of counter tracking or a logged reason why the window was skipped.
- One commit with message: "gate reflection cadence for automated-only windows per C120 P2"
- Completion report pointing back to this handoff.

## Escalation

URGENT if:
- The mechanism is already implemented and the proposal is redundant (move to archive with evidence).
- The implementation is ambiguous or conflicts with existing short-circuit logic in reflect.sh.
