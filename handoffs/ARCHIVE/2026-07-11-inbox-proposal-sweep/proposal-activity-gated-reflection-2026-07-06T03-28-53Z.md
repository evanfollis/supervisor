---
from: synthesis-translator
to: general
date: 2026-07-06T03:28:53Z
priority: high
task_id: synthesis-activity-gated-reflection
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-06T03-24-44Z.md
source_proposal: P2 — Activity-gated reflection
---

# Activity-gated reflection

## Proposal

**Type:** `reflect.sh` amendment — skip with carry-forward note when no attended session since last reflection and prior observations are identical.

**Blast radius:** All reflected projects (opt-in via `projects.conf`). Reduces token spend on dormant projects.

**Current status:** The synthesis reports "Activity-gated reflection working — 12 of 16 reflections correctly short-circuit on inactivity" (line 261). So this is already partially implemented.

## Verification before action (required)

- Check `/opt/workspace/supervisor/scripts/lib/reflect.sh` for activity-gating logic (likely a conditional before the main reflection block).
- If activity-gating is already in place, verify it:
  - Checks for attended sessions since last reflection
  - Compares prior observations for identity
  - Skips reflection + emits carry-forward note when both conditions are met
- If already implemented, write completion report stating "already landed and verified operational (12/16 reflections short-circuiting per C127 reflection output)".

## Acceptance criteria

If not already landed:
- `reflect.sh` contains activity-gating check before main reflection block
- Unattended dormant projects skip reflection and emit carry-forward note to their reflection output
- No functional change to attended projects — they continue full reflection
- Commit message: "Add activity-gating to reflect.sh — skip reflection for dormant projects with unchanged observations"
- Completion report at `runtime/.handoff/general-complete-activity-gated-reflection-<iso>.md`

## Escalation

If activity-gating is only partially implemented (e.g., checks one condition but not the other), escalate with specifics on what's missing.
