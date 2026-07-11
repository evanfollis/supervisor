---
from: synthesis-translator
to: executive
date: 2026-07-05T15:29:42Z
priority: high
task_id: synthesis-p2-activity-gated-reflection
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-05T15-26-01Z.md
source_proposal: "P2 (CARRY — C114, 13th cycle): Activity-gated reflection"
---

# P2: Activity-gated reflection — carry-forward note on no-change

**Type:** `reflect.sh` enhancement — skip with carry-forward note when no attended session since last reflection and prior observations are identical.
**Blast radius:** All reflected projects (opt-in via `projects.conf`).

## Current state

`reflect.sh` (lines 50–73) already implements activity-gating: it short-circuits if no commits, telemetry, or session activity in 12h window. When skipped, it writes:

```markdown
# Reflection skipped — no activity in window ending <iso>
```

## Proposed enhancement

When short-circuiting on no activity:

1. Check if the prior reflection file (from 12h ago) exists
2. If it does, and its content starts with "# Reflection skipped", write a carry-forward line:
   ```markdown
   # Reflection skipped — no activity in window ending <iso>
   Carried forward from prior cycle.
   ```
3. Do not re-run Claude; the skip is sufficient.

**Rationale:** This turns the 12-activity-gated short-circuits into visible continuity. Currently they produce silent empty files; adding carry-forward metadata makes it clear to the synthesis job that consecutive cycles are identical and no new observations are expected.

**Token savings:** Already working. 12 of 16 recent reflections correctly short-circuit. The enhancement just adds a one-line metadata note.

## Verification before action (required)

- Read `reflect.sh` lines 50–73. Confirm activity-gating logic is present.
- Check a recent short-circuit: `cat /opt/workspace/runtime/.meta/atlas-reflection-2026-07-05T14-19-00Z.md | head -5` or similar. Should be empty or read "Reflection skipped".
- If the file already includes "Carried forward", the enhancement is landed; write completion report rather than re-applying.

## Acceptance criteria

- `reflect.sh` checks for prior reflection file when skipping
- If prior file's first line is "# Reflection skipped", append "Carried forward from prior cycle."
- Change committed with message: `enhance activity-gating to include carry-forward note per synthesis proposal P2`
- Completion report at `runtime/.handoff/general-p2-activity-gated-complete-<iso>.md`

## Escalation

Low risk. This is a cosmetic metadata enhancement that does not affect logic.

---

**Background from synthesis (C126):** Activity-gating is working. The carry-forward note makes it machine-readable by synthesis that consecutive cycles have no new signal. Enables suppression rules that check "is this the same observation repeated?" without having to parse reflection text.
