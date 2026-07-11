---
from: synthesis-translator
to: general
date: 2026-07-08T03:30:25Z
priority: low
task_id: synthesis-p6-cycle-count-guidance
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-08T03-24-41Z.md
source_proposal: P6 — Add rotation-aware cycle-count guidance
---

# P6: Add rotation-aware cycle-count guidance

**Type:** CLAUDE.md amendment or reflection template note: "use `consecutive_empty_count` delta from state file, not events.jsonl line count, to verify atlas cycle activity across midnight UTC boundary."

**Rationale:** Atlas reflection logic currently uses events.jsonl line count to verify cycle activity, but this breaks across UTC midnight boundaries (the telemetry file rolls and line count resets). The `consecutive_empty_count` field in verified-state.md is rotation-aware and provides accurate cycle counting regardless of time-of-day.

**Blast radius:** Atlas reflections. Low-risk, informational.

---

## Verification before action (required)

- Check `/opt/workspace/CLAUDE.md` to see if guidance about `consecutive_empty_count` already exists.
- Check the atlas reflection prompt template (if separate) for similar guidance.
- Check recent atlas reflection files (e.g., `/opt/workspace/runtime/.meta/atlas-reflection-*.md`) to see if they already reference `consecutive_empty_count` for cycle counting.
- If guidance is already present, write completion report stating "already landed".

## Acceptance criteria

- **Guidance added to appropriate file** (either `/opt/workspace/CLAUDE.md` "Automated Self-Reflection Loop" section or atlas-specific reflection prompt):
  > For cycle counting across UTC midnight boundaries, use the `consecutive_empty_count` delta from `supervisor/system/verified-state.md` rather than events.jsonl line count. This field tracks runner cycles independent of telemetry rotation.

- Alternatively, if atlas has a dedicated reflection prompt, add this note to the template:
  > When comparing this reflection against the prior one, use `consecutive_empty_count` to measure elapsed cycles, not line-count diffs in events.jsonl (which resets at midnight UTC).

- Commit message: "Add rotation-aware cycle-count guidance for atlas reflection (synthesis-p6)".
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-synthesis-p6-cycle-guidance-complete-<iso>.md`.

## Non-goals

- No changes to verified-state.md generation or the `consecutive_empty_count` logic itself.
- This is documentation/guidance only; no code changes required.
