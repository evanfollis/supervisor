---
from: synthesis-translator
to: general
date: 2026-05-14T15:33:41Z
priority: high
task_id: synthesis-reflect-live-source-instruction
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-14T15-25-54Z.md
source_proposal: Proposal 4 — Shared primitive — reflect-prompt instruction for live-source reading
---

# Live-source discipline instruction — reflect-prompt.md amendment

## Context

Complements Proposal 1 (CLAUDE.md amendment). This adds a concrete instruction in the reflection template to ensure reflection jobs read live state directly instead of citing CURRENT_STATE.md.

## Proposal

Add a new section to `/opt/workspace/supervisor/scripts/lib/reflect-prompt.md` after the "Artifacts to read" section and before "Short-circuit rule":

```markdown
## Live-source discipline

When reporting on live state (task stores, telemetry files, service status, git HEAD),
read the canonical source directly. Do NOT cite CURRENT_STATE.md for current values —
it is a derivative artifact that may be stale. Read the file, query the service,
or run `git show HEAD:path`. State which source you read and when.
```

**Rationale:** This explicit instruction prevents reflections from propagating stale data through derivative sources, directly addressing the reflection accuracy gap identified in cycle 36 Pattern 2.

## Verification before action (required)

- Run `grep -n "Live-source discipline" /opt/workspace/supervisor/scripts/lib/reflect-prompt.md` to confirm the section is not already present.
- Read `/opt/workspace/supervisor/scripts/lib/reflect-prompt.md` to identify the correct insertion point (after "Artifacts to read" section, before "Short-circuit rule").
- Verify the indentation and markdown formatting match the existing file.

## Acceptance criteria

- The "Live-source discipline" section is added to reflect-prompt.md with the exact text above.
- The section appears in the correct location (between "Artifacts to read" and "Short-circuit rule").
- A commit is created with message: "Add live-source discipline instruction to reflect-prompt.md" (imperative mood, explains why).

## Escalation

URGENT if:
- The section is already present in the file (proposal already landed; write completion report instead).
- The "Artifacts to read" or "Short-circuit rule" sections have been reorganized (may need manual placement).
