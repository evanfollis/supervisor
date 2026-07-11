---
from: synthesis-translator
to: general
date: 2026-07-03T15:29:41Z
priority: high
task_id: synthesis-reflect-failure-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-03T15-24-18Z.md
source_proposal: P3 (CARRY — C114, 12th cycle): Land reflection failure self-reporting
---

# P3: Land reflection failure self-reporting

**Type:** `reflect.sh:115–119` — emit handoff + telemetry on failure.

**Target file:** `/opt/workspace/supervisor/scripts/lib/reflect.sh`

## Current behavior (lines 115–119)

```bash
if [[ -f "$OUTPUT_FILE" ]]; then
  echo "reflect[$PROJECT]: wrote $OUTPUT_FILE"
else
  echo "reflect[$PROJECT]: WARNING — no output file produced" >&2
  exit 2
fi
```

When reflection fails to produce output, the script prints a warning and exits. There is no handoff created and no telemetry emitted.

## Proposed behavior

When `$OUTPUT_FILE` is not created (Claude invocation failed, disallowedTools prevented completion, or session crashed):
1. **Emit handoff** to `/opt/workspace/supervisor/handoffs/INBOX/URGENT-reflect-failure-<project>-<iso>.md` with:
   - Project name
   - Timestamp
   - Last few lines of stderr (if available)
   - Suggestion to check Claude's output log for the full error
2. **Emit telemetry** to `/opt/workspace/runtime/.telemetry/events.jsonl` with:
   - `event_type: "failure"`
   - `source: "reflect"`
   - `project: "<PROJECT>"`
   - `detail: "reflection session produced no output"`
   - `timestamp: <epoch-ms>`
   - `sourceType: "system"`
3. **Exit with code 2** (unchanged)

## Rationale (from C122 synthesis)

Reflection is part of the workspace's self-monitoring loop. When it fails silently, the synthesizer has no signal that a project's internal state is not being captured. This is the self-reporting gap that allows a stuck reflection to go unnoticed.

Effort: <5 min. This is the 12th cycle this proposal has been open (since C114).

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor/` to check if this change has already landed.
- Check lines 115–119 of `/opt/workspace/supervisor/scripts/lib/reflect.sh` — verify no handoff/telemetry is being emitted on failure.
- If already landed, write a completion report stating "already landed at commit <SHA>".

## Acceptance criteria

- When Claude fails to produce an output file, a handoff is written to `/opt/workspace/supervisor/handoffs/INBOX/URGENT-reflect-failure-<project>-<iso>.md`.
- A telemetry event with `event_type: "failure"` is appended to events.jsonl.
- The script exits with code 2 (same as before).
- Change committed with message: `Emit failure handoff and telemetry when reflection produces no output`
- Completion report written to `runtime/.handoff/general-reflect-failure-reporting-complete-<iso>.md`.

## Escalation

None anticipated. This is instrumenting an existing failure path.
