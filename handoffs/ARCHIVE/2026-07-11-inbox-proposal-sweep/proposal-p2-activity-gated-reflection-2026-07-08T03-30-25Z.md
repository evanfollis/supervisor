---
from: synthesis-translator
to: general
date: 2026-07-08T03:30:25Z
priority: high
task_id: synthesis-p2-activity-gated-reflection
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-08T03-24-41Z.md
source_proposal: P2 — Activity-gated reflection
---

# P2: Activity-gated reflection

**Type:** `reflect.sh` amendment — skip with carry-forward note when no attended session since last reflection and prior observations are identical.

**Rationale:** 12 of 16 reflections already short-circuit correctly on no activity. The remaining 4 (atlas, supervisor) produce increasingly repetitive diagnostics in idle windows. Activity-gating would not suppress novel findings (T20's `skipped_unreplayable` discovery proves the current system can still extract new signal), but would suppress structurally identical re-reports.

**Blast radius:** All reflected projects (opt-in via `projects.conf`).

---

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 69-72. Confirm activity-check logic is already present.
- Check recent reflection files (e.g., `/opt/workspace/runtime/.meta/atlas-reflection-2026-07-08T02-20-26Z.md` and supervisor reflections). Confirm whether they already have carry-forward notes or are still emitting identical re-reports.
- If carry-forward logic is already in place, write completion report stating "already landed".

## Acceptance criteria

- **New logic added to `reflect.sh`:** After the activity check (lines 69-72), when short-circuiting due to inactivity, compare the proposed output against the prior reflection file (if it exists). If the content is substantively identical to the prior reflection, emit a carry-forward note instead of a full reflection.
- **Carry-forward note format:** Output file contains: `# Reflection short-circuit — no activity since <prior-iso>, prior findings unchanged`
- **Novel finding gate:** If the reflection detects genuinely new signal (e.g., a new error pattern, new metric change, new handoff), emit the full reflection regardless of activity status.
- Commit message: "Add carry-forward notes to reflect.sh for idle-window dedup (synthesis-p2)".
- Test by running atlas and supervisor reflections in an idle window and confirming carry-forward logic fires.
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-synthesis-p2-activity-gated-complete-<iso>.md`.

## Non-goals

- No changes to the core activity-check logic (commits, telemetry, JSONL activity).
- Do not suppress reflections that detect novel findings.
