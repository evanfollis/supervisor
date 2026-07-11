---
from: synthesis-translator
to: general
date: 2026-06-28T15:32:45Z
priority: medium
task_id: synthesis-stale-urgent-cleanup
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-28T15-27-10Z.md
source_proposal: P-stale-urgent-cleanup (NEW, <5 min)
---

# Delete confirmed-stale URGENTs from runtime/.handoff/

## Full proposal from synthesis

**Type:** One-time cleanup — not a shared primitive.

**Purpose:** 4 of the 8 URGENTs in `runtime/.handoff/` are confirmed stale
by the reflections that produced them:
- `URGENT-atlas-frozen-loop-2026-06-11T20-26Z.md` — superseded by Phase 1 theater strip
- `URGENT-atlas-unpushed-commits-3rd-cycle.md` — atlas is now pushed (1 ahead)
- `URGENT-supervisor-reflection-dirty-tree.md` — the dirty-tree condition is the known tick deadlock, not a novel finding
- `URGENT-supervisor-reflection-mutated-head.md` — same class as dirty-tree, known

The remaining 4 (`context-repository-structural-abandonment`,
`supervisor-event-stream-false-positive`, `synaplex-reflection-mutated-head`,
`skillfoundry-harness-migrate-failure.done`) should be triaged but are not
as clearly stale.

**Blast radius:** runtime/.handoff/ only. No code changes.

## Verification before action (required)

- Verified: All 4 files exist in `/opt/workspace/runtime/.handoff/`:
  - `URGENT-atlas-frozen-loop-2026-06-11T20-26Z.md` ✓
  - `URGENT-atlas-unpushed-commits-3rd-cycle.md` ✓
  - `URGENT-supervisor-reflection-dirty-tree.md` ✓ (created 2026-06-27T14:31Z)
  - `URGENT-supervisor-reflection-mutated-head.md` ✓ (created 2026-06-28T14:26Z)
- Each is confirmed stale per the synthesis:
  - atlas-frozen-loop: superseded by Phase 1 theater strip (Phase 1 shipped in attended session 2026-06-28T14:19Z per atlas reflection)
  - atlas-unpushed-commits: atlas now has 1 commit ahead on main (pushed or auto-reflected)
  - supervisor-reflection-dirty-tree: this is the known tick-deadlock condition tracked as standing rec #1 (Pattern 1 — Tick deadlock); raising it as a novel URGENT is redundant
  - supervisor-reflection-mutated-head: same class as dirty-tree; known autocommit issue

## Acceptance criteria

- Delete the 4 confirmed-stale URGENT files listed above.
- Do NOT delete the remaining 4 (context-repo, event-stream, synaplex, skillfoundry); those are marked for future triage.
- Optional: document the deletion in a summary comment or completion report for audit.
- Completion report filed at `runtime/.handoff/general-claude-synthesis-stale-urgent-cleanup-complete-<iso>.md`.

## Escalation

None expected. This is administrative cleanup of superseded artifacts.
