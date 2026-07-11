---
from: synthesis-translator
to: general
date: 2026-05-14T15:33:41Z
priority: high
task_id: synthesis-reflection-accuracy-discipline
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-14T15-25-54Z.md
source_proposal: Proposal 1 — CLAUDE.md amendment — reflection accuracy discipline
---

# Reflection accuracy discipline — CLAUDE.md amendment

## Context

Reflections in command, supervisor, and context-repository are reading stale derivative sources (CURRENT_STATE.md) instead of live canonical sources, propagating errors across cycles. Command's reflection has been reporting "1 task" for multiple cycles when the live Symphony task store contains 11 tasks.

## Proposal

Add a new entry to `/opt/workspace/CLAUDE.md` under **Active Decisions → Quality: Root-Cause Discipline**:

```markdown
**Reflections must read live sources, not derivative summaries.** CURRENT_STATE.md is a derivative artifact updated by reflection jobs; it is not a source of truth for live state (task stores, telemetry files, git HEAD, service status). When a reflection job needs to report the current value of a live resource, it must read the resource directly (e.g., `runtime/symphony/tasks.json`, `git show HEAD:path`, `systemctl status`). Citing CURRENT_STATE.md for live state propagates stale data across cycles. Source: cycle 36 Pattern 2 (command 11→1 task error, supervisor working-tree/HEAD divergence, context-repo 10-pass drift).
```

## Verification before action (required)

- Run `grep -n "Reflections must read live sources" /opt/workspace/CLAUDE.md` to confirm the rule is not already present.
- Read `/opt/workspace/CLAUDE.md` and locate the "Active Decisions" section and the "Quality: Root-Cause Discipline" subsection to understand where to insert this rule.
- Verify the insertion point is after the "No bandaid fixes" rule in that section.

## Acceptance criteria

- The rule is added to CLAUDE.md in the correct section with the exact text above.
- A commit is created with message: "Add reflection accuracy discipline rule to CLAUDE.md" (imperative mood, explains why).
- The corresponding update to `supervisor/scripts/lib/reflect-prompt.md` (Proposal 4) should be completed in the same session if both are targeted.

## Escalation

URGENT if:
- The text already exists in CLAUDE.md (this proposal is already landed; write completion report instead).
- The "Active Decisions → Quality: Root-Cause Discipline" section does not exist (need structural amendment first).
