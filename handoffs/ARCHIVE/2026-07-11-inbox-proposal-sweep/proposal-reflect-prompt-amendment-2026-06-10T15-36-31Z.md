---
from: synthesis-translator
to: general
date: 2026-06-10T15:36:31Z
priority: high
task_id: synthesis-reflect-prompt-amendment
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-10T15-26-21Z.md
source_proposal: "Proposal 1 — reflect.sh prompt amendment — inform reflections about the auto-commit gate (highest leverage for diagnostic quality)"
---

# Reflect.sh prompt amendment — inform reflections about the auto-commit gate

## Proposal

The reflect prompt (`supervisor/scripts/lib/reflect-prompt.md`) does not mention the CURRENT_STATE auto-commit gate that was added to `reflect.sh` (lines 186-205). Reflections don't know the gate exists, so they misdiagnose its commits as constraint violations. Add to the reflect prompt:

```
## Context: CURRENT_STATE.md auto-commit gate

After each reflection session ends, the `reflect.sh` wrapper checks if
CURRENT_STATE.md is dirty and commits it automatically (lines 186-205).
This is by design (cross-cutting 2026-04-20 Proposal 2 Option A). Commits
with the message "reflect: auto-update CURRENT_STATE.md <ISO>" are produced
by this shell mechanism, NOT by the Claude session itself. Do not diagnose
these commits as Write bypass exploitations — the `Write` tool is correctly
blocked in --disallowedTools.
```

**Impact**: This eliminates the false "Write bypass" carry-forward in skillfoundry-harness (100+ days of stale alarm) and prevents future misdiagnosis in all projects. Zero code change; prompt-only edit.

**Blast radius**: All 8 projects (automatic — reflects via the shared prompt template).

## Verification before action (required)

- Read `supervisor/scripts/lib/reflect-prompt.md` and confirm the "Context: CURRENT_STATE.md auto-commit gate" section is not already present.
- Confirm the auto-commit gate code exists at `reflect.sh` lines 186-205.

## Acceptance criteria

- The specified context section is added to `supervisor/scripts/lib/reflect-prompt.md`
- The addition is committed with a message explaining it informs reflections about the auto-commit mechanism
- Completion report at `runtime/.handoff/general-supervisor-synthesis-reflect-prompt-amendment-complete-<iso>.md` referencing this handoff

## Escalation

URGENT if:
- The prompt has been reworded in a way that makes adding this context awkward or contradictory. If so, surface the conflict and ask how to harmonize.
