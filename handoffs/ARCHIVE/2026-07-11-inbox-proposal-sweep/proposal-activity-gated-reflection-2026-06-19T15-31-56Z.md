---
from: synthesis-translator
to: general
date: 2026-06-19T15:31:56Z
priority: high
task_id: synthesis-activity-gated-reflection
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-19T15-27-31Z.md
source_proposal: 3. P-activity-gated-reflection
---

# P-activity-gated-reflection — Short-circuit reflections on stalled windows

**Carried from C104. 15 cycles open. Combined cost ~$8-12/day for zero epistemic output.**

## Problem

Atlas runner, context-repository reflection, and this synthesis loop self-diagnose as waste-generating. Three systems independently request self-throttle: when N consecutive windows produce identical skip/counter-only output, short-circuit and stop emitting.

**Current cost:** ~$8-12/day for counter increments that no one reads until an attended session occurs.

## Solution

1. Amendment to `reflect.sh` — add activity-gating logic to short-circuit when N consecutive windows produce zero new structural patterns.
2. Amendment to synthesis prompt — enable self-suppression mode when the same recommendations carry unchanged for M consecutive cycles.

**Location:** 
- `supervisor/scripts/lib/reflect.sh` — add short-circuit condition
- synthesis prompt (in `synthesize.sh` or its invocation) — add threshold for self-suppression

## Specification

The condition is already specified in the synthesis file (C108):

> C109 and subsequent cycles will emit a 3-line skip file:
> ```
> # Synthesis skipped — no attended action since C108 (2026-06-19).
> # Canonical reference: cross-cutting-2026-06-19T15-27-31Z.md
> # 25 open / 0 resolved. Critical path: ~60 min attended.
> ```

This logic should be applied to `reflect.sh` as well: when N consecutive reflections show only counter increments and zero new findings, emit a 3-line skip file instead of a full reflection.

## Blast radius

atlas, context-repository, supervisor, synthesis. Eliminates ~$8-12/day waste by short-circuiting unproductive reflection windows.

## Verification before action (required)

- Read `supervisor/scripts/lib/reflect.sh`. Check if activity-gating logic is already present.
- Check the synthesis prompt in `synthesize.sh`. Check if self-suppression threshold is already configured.
- If both are true, write a completion report saying "already landed in reflect.sh and synthesis prompt" and close.

## Acceptance criteria

- `reflect.sh` amended to short-circuit when N consecutive windows produce zero new findings (counter increments only).
- Synthesis prompt amended to enable self-suppression when recommendations carry unchanged for M consecutive cycles.
- Both changes committed with message explaining the synthesis source and cost savings (~$8-12/day).
- Completion report at `runtime/.handoff/general-supervisor-synthesis-activity-gated-reflection-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Why this matters

Once attended action resolves standing recommendations or lands substantive commits in 2+ projects, the synthesis will resume full cycles. Until then, this gates unnecessary token spend.

## Escalation

URGENT if:
- The activity-gating fix has already landed by another path.
- The proposal conflicts with a decision to continue full synthesis cycles regardless of productive output.
