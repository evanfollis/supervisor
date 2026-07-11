---
from: synthesis-translator
to: general
date: 2026-06-28T15:32:45Z
priority: high
task_id: synthesis-governance-interleave
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-28T15-27-10Z.md
source_proposal: P-governance-interleave (NEW)
---

# Session-start governance checklist

## Full proposal from synthesis

**Type:** CLAUDE.md amendment — addition to "Session Awareness" section.

**Purpose:** Ensure that attended sessions spend 5–10 minutes on
governance hygiene before diving into domain work, so that small
maintenance items (deleting stale URGENTs, checking branch divergence,
reading LATEST_SYNTHESIS) don't require a dedicated governance session.

**Proposed text:**
```
### Session-start governance hygiene (5 min)
When starting an attended session on any project:
1. Delete confirmed-stale URGENTs from `runtime/.handoff/` (check CURRENT_STATE.md for "DELETE: stale" markers).
2. Check `runtime/.meta/LATEST_SYNTHESIS` — if unread, skim the Questions section.
3. If the project has unpushed commits older than 7 days, push before starting new work.
These are reversible, take <5 min total, and prevent governance debt from compounding during domain-focused sessions.
```

**Blast radius:** All projects (automatic — read on session start).

## Verification before action (required)

- Verified: `/opt/workspace/CLAUDE.md` does **not** contain a "Session-start governance hygiene" section.
- Current "Session Awareness" section (lines 175-182) has no such clause.
- This is a new addition, not a replacement or update.

## Acceptance criteria

- Proposed text is added to `/opt/workspace/CLAUDE.md` under the "Session Awareness" section.
- Change committed with imperative message explaining the synthesis source and rationale.
- Completion report filed at `runtime/.handoff/general-claude-synthesis-governance-interleave-complete-<iso>.md`.

## Escalation

None anticipated. This is a low-risk documentation addition that codifies existing best practice.
