---
from: synthesis-translator
to: general
date: 2026-07-03T15:29:41Z
priority: medium
task_id: synthesis-activity-gated-reflection
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-03T15-24-18Z.md
source_proposal: P2 (CARRY — C114, 9th cycle): Reflection cadence gating for automated-only windows
---

# P2: Reflection cadence gating for automated-only windows

**Type:** `reflect.sh` change — skip reflection and emit a one-line carry-forward note when:
- No attended session has occurred since the last reflection, AND
- The prior reflection's observations are materially identical to what would be produced now

**Target file:** `/opt/workspace/supervisor/scripts/lib/reflect.sh`

## Rationale (from C122 synthesis)

The reflection loop is producing faster than it is consumed. When an attended session does not occur, the next reflection cycle produces identical observations to the previous one. Emitting a carry-forward note instead of a full reflection saves tokens and signals continuity without adding noise.

Token savings are real and compounding (per C122: "Activity-gated reflection works. 12 of 16 reflections correctly short-circuit. Token savings remain real and compounding.").

This is the 9th consecutive synthesis request for this fix (since C114).

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor/` to check if this change has already landed.
- Search `/opt/workspace/supervisor/scripts/lib/reflect.sh` for any logic comparing the current observations against prior reflection files.
- If already landed, write a completion report stating "already landed at commit <SHA>".

## Implementation sketch

The logic should:
1. After the activity check (lines 69–73), add a gate that checks whether an attended session has occurred since the most recent reflection file for this project.
2. If no attended session has occurred AND the prior reflection would be identical (heuristic: same project state, same stale-artifact count, no new URGENT files), emit a one-line note:
   ```
   # Reflection carried forward — no attended session, observations identical (see <previous-iso>)
   ```
3. Exit early before spawning Claude.

Definition of "attended session": a non-reflection, non-auto-tick session session involving real user interaction at the project, detected via git commits authored by a human (not reflection autocommit pattern) or user-generated handoffs in the project session JSONL.

## Acceptance criteria

- Reflection skips are measurable: output file contains only a one-line carry-forward note (pattern: `# Reflection carried forward`).
- Consecutive identical-observation skips are counted and reported (heuristic ok; precision not required).
- Token savings from skips are reflected in next synthesis cycle's reflection metrics.
- Change committed with message: `Add activity-gated reflection cadence to skip identical observations on automated-only windows`
- Completion report written to `runtime/.handoff/general-reflect-activity-gated-complete-<iso>.md`.

## Escalation

None anticipated. This is an optimization that tightens reflection behavior.
