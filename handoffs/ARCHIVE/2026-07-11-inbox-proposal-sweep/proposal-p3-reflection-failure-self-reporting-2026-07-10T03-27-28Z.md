---
from: synthesis-translator
to: general
date: 2026-07-10T03:27:28Z
priority: medium
task_id: synthesis-p3-reflect-failure-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-10T03-23-34Z.md
source_proposal: P3 (CARRY — C114, 26th cycle) — Reflection failure self-reporting
---

# P3: Reflection failure self-reporting

**Type:** `reflect.sh:115-119` — emit handoff + telemetry event on failure exit.

**Blast radius:** All reflected projects. <5 min.

## Rationale

The architectural principle is that self-monitoring systems must self-report stuck states (S3-P2 mandate in CLAUDE.md). A reflection that fails silently is indistinguishable from a reflection that succeeded with zero findings. This amendment ensures failed reflection attempts surface in both the handoff queue and telemetry.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 115-119 (failure exit path)
- Check if handoff emission already exists (pattern like `emit_handoff` or similar)
- If already implemented, write a completion report stating "already landed"

## Acceptance criteria

- `reflect.sh` failure exits (around lines 115-119) amended to emit:
  - A handoff file to `/opt/workspace/supervisor/handoffs/INBOX/` with format `reflect-<project>-failure-<iso>.md`
  - A telemetry event to `events/supervisor-events.jsonl` with `eventType: "failure"` and `sourceType: "system"`
- Handoff includes: project name, failure reason, last-known project state
- Single commit with message: "Add reflection failure self-reporting — emit handoff + telemetry on error exits (synthesis C135)"
- Completion report filed to `runtime/.handoff/general-supervisor-synthesis-p3-complete-<iso>.md`
