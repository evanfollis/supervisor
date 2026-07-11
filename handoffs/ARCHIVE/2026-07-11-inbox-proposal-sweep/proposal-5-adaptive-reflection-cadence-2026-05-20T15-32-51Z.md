---
from: synthesis-translator
to: general
date: 2026-05-20T15:32:51Z
priority: medium
task_id: synthesis-adaptive-reflection-cadence
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-20T15-27-25Z.md
source_proposal: Proposal 5 (MEDIUM — 2nd cycle)
---

# Adaptive reflection cadence for stasis projects

**Status:** OPEN. 2 synthesis cycles proposing this. Pattern 4 (this synthesis) identifies "reflection cadence noise for stasis projects."

## Problem

Four projects are in stasis (no attended sessions, no commits, repeated identical diagnoses):

| Project | Idle windows | Diagnosis |
|---------|---|---|
| command | 18 consecutive quiet | No activity, known carry-forwards, no new findings |
| atlas | 17 consecutive idle | Runner stopped, principal decisions pending |
| context-repository | 22 consecutive | Idle, 22 passes with no human-initiated activity |
| supervisor | 7 in this window | 7 ticks, zero attended sessions, zero structural changes |

Each project generates a full reflection output with correct but identical diagnoses. The cost is real: CURRENT_STATE.md writes that can't commit, JSONL transcripts, synthesis noise, and template-engine work, displacing novel signal.

## Proposal

Introduce an optional `stasis` flag in `projects.conf` for projects in known waiting states. When a project is marked stasis, the reflection loop runs on a longer cadence (24h or 48h instead of 12h).

**Sketch of change:**

File: `/opt/workspace/supervisor/scripts/lib/projects.conf`

Current format (line):
```
atlas|/opt/workspace/projects/atlas
```

New format (with optional stasis flag):
```
atlas|/opt/workspace/projects/atlas|stasis=2026-05-28
```

The reflection job checks the stasis flag:
- If present and `STASIS_DATE` ≤ today: run reflection normally (cadence has expired, project may be unfrozen).
- If present and `STASIS_DATE` > today: skip reflection, emit a short-circuit note.
- If absent: run reflection on normal 12h cadence.

**Rationale:** Projects in known waiting states (principal decisions pending, external blockers) produce noise in the reflection loop. Marking them stasis reduces noise and preserves bandwidth for projects with activity. The stasis flag is time-limited (opt-in reset by date), not permanent.

**Blast radius:** Reflection cadence only (automatic). No code changes to reflection logic, no side effects on project repos.

## Evidence

Cycles 46–48: Supervisor, atlas, command, context-repository each have 7–22 idle windows. Each produces a reflection noting it's idle. Cycle 48 synthesis notes: "Four substantive reflections across two 12h batches today produced zero new findings beyond counter increments."

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/projects.conf` (lines 1–30). Check if the file currently has a `stasis` field or similar opt-in flag.
- Check if projects.conf parsing code reads any flag format beyond `<name>|<path>|<template>`. Grep the reflection launcher script for `projects.conf` parsing logic.
- If stasis flagging is already present, write a completion report saying "already landed — stasis flag present" rather than re-applying.

## Acceptance criteria

- `projects.conf` format extended to include an optional fourth field or flag: `<name>|<path>|<template>|<optional-flags>`.
- The stasis flag is of the form `stasis=YYYY-MM-DD` (ISO date when the stasis period ends).
- Reflection launcher script (`reflect.sh`) checks for stasis flag and skips the reflection if stasis date is in the future (emits short-circuit note).
- Configuration is documented in `projects.conf` header comments.
- At least one project (e.g. `atlas`) is marked stasis with a future date (e.g. 2026-05-28) as a proof-of-concept.
- Completion report at `supervisor/handoffs/INBOX/general-adaptive-cadence-complete-<iso>.md` listing which projects are marked stasis and their expiry dates.

## Escalation

URGENT if:
- Reflection launcher does not read `projects.conf` directly. If the launcher is parameterized differently, identify the source of truth and propose the amendment path there.
- Stasis flag interacts with other project-local configuration (e.g. alternate prompt template). Propose a cohesive extension that handles both.
