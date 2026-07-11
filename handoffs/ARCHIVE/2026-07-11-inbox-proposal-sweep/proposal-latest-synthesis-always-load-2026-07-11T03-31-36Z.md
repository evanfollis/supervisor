---
from: synthesis-translator
to: general
date: 2026-07-11T03:31:36Z
priority: high
task_id: synthesis-latest-synthesis-always-load
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-11T03-27-25Z.md
source_proposal: P7 — Add LATEST_SYNTHESIS to always-load context
---

# P7 — Add LATEST_SYNTHESIS to always-load context

## Proposal

**Type:** CLAUDE.md amendment — `context-always-load` block. Add at tail:
```yaml
  - runtime/.meta/LATEST_SYNTHESIS              # regenerated every synthesis (~12h)
```

**Rationale:** The always-load set describes a workspace from June 9. The synthesis describes reality. Adding the symlink ensures every cold-start session reads accurate cross-cutting diagnosis. Currently, the always-load set includes state surfaces (active-issues.md, verified-state.md) that are 31+ days stale, actively misdirecting any cold-start session. Adding LATEST_SYNTHESIS makes the accurate diagnosis immediately available.

**Blast radius:** All workspace sessions. Automatic.

## Verification before action (required)

- Check `/opt/workspace/CLAUDE.md` lines 64-78 (the `context-always-load` block).
- Search for `LATEST_SYNTHESIS` in the list.
- If it is already present, this proposal is landed — write a completion report and close.
- If absent, proceed with the amendment.

## Acceptance criteria

- `/opt/workspace/CLAUDE.md` is amended to include `- runtime/.meta/LATEST_SYNTHESIS` in the `context-always-load` block.
- It should be added at the tail of the list to maintain cache-prefix stability (keep stable files first, volatile files last).
- The comment should match the pattern: `# regenerated every synthesis (~12h)`.
- Commit with message explaining the addition (synthesis C137, P7).
- Completion report at `runtime/.handoff/general-proposal-latest-synthesis-always-load-complete-2026-07-11T03-31-36Z.md`.

## Escalation

None anticipated. This is a direct file amendment with no dependencies.
