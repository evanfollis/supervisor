---
from: synthesis-translator
to: general
date: 2026-07-10T15:28:36Z
priority: high
task_id: synthesis-p3-reflect-failure-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-10T15-24-51Z.md
source_proposal: P3 (CARRY — C114, 27th cycle): Reflection failure self-reporting
---

# P3: Reflection failure self-reporting

**Type:** `reflect.sh:115-119` — emit handoff + telemetry event on failure exit.

**Blast radius:** All reflected projects. <5 min.

## Background

Currently, when reflect.sh fails to produce an output file (line 118-119), it logs a WARNING to stderr but does not emit a structured failure signal. This means a failure silently disappears unless someone is actively monitoring the reflect.sh output stream.

Per the Architecture Governance section of CLAUDE.md, self-monitoring systems must self-report stuck states (S3-P2): "Any automated loop (supervisor tick, meta-scan, executive dispatch) must emit a named `escalated` event after N consecutive skips or silent failures."

## Verification before action (required)

- Location: `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 115-119
- Current behavior: logs warning to stderr, exits with code 2
- Target behavior: emit handoff file to `WORKSPACE_HANDOFF_DIR/URGENT-${PROJECT}-reflect-failure-*.md` AND emit telemetry event to `WORKSPACE_TELEMETRY_DIR/events.jsonl`
- Check: No existing telemetry emission in reflect.sh (verified via grep)

## Acceptance criteria

When `reflect.sh` exits with code 2 (no output file produced):

1. Write a handoff file: `URGENT-${PROJECT}-reflect-failure-${ISO_NOW}.md` with:
   - Project name
   - ISO timestamp
   - Exit code and reason
   - Brief guidance (check prompt, check session logs, escalate)

2. Emit a telemetry event to `events.jsonl` with:
   - `"eventType": "failure"`
   - `"sourceType": "system"`
   - `"project": "${PROJECT}"`
   - `"source": "reflect.sh"`
   - `"timestamp": <epoch ms>`
   - `"level": "high"`
   - One-line reason

3. Change committed with message: "Emit failure signal when reflection output missing"

4. Completion report filed at `runtime/.handoff/general-reflect-failure-complete-<iso>.md`

## Escalation

If telemetry event shape is unclear, verify against existing events in `runtime/.telemetry/events.jsonl` to match schema. If a different failure-reporting mechanism is preferred, escalate before implementing.
