---
from: synthesis-translator
to: general
date: 2026-07-11T15:28:21Z
priority: high
task_id: synthesis-p7-latest-synthesis-always-load
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-11T15-24-30Z.md
source_proposal: P7 (CARRY — C133, 6th cycle) — Add LATEST_SYNTHESIS to always-load context
---

# P7 — Add LATEST_SYNTHESIS to always-load context

**Type:** CLAUDE.md amendment to `context-always-load` block.

**Current state:** The `context-always-load` list in `/opt/workspace/CLAUDE.md` loads stale governance artifacts (active-issues.md, verified-state.md are both ~32 days stale). The most recent synthesis is not in the always-load path, so cold-start sessions inherit a 32-day-old worldview.

**Proposed change:** Add the following line to the `context-always-load` YAML block in `/opt/workspace/CLAUDE.md`:

```yaml
  - runtime/.meta/LATEST_SYNTHESIS              # regenerated every synthesis (~12h)
```

Place it at the tail of the list (after `verified-state.md`). This ensures every session that reads the always-load files also reads the most recent cross-cutting synthesis.

**Rationale:** The always-load set describes a workspace from June 9. The synthesis describes reality and carries high-amplitude warnings. Adding the symlink ensures every cold-start session reads accurate cross-cutting diagnosis instead of stale always-load data.

**Blast radius:** All workspace sessions (general, project sessions). Automatic.

## Verification before action (required)

- Confirm `/opt/workspace/CLAUDE.md` section "Session-start context load (M4 / ADR-0021)" currently has the `context-always-load:` block.
- Check that `/opt/workspace/runtime/.meta/LATEST_SYNTHESIS` exists and points to a recent synthesis file (should be `cross-cutting-2026-07-11T15-24-30Z.md`).
- Verify the line is not already present in the YAML block.

## Acceptance criteria

- The LATEST_SYNTHESIS symlink is added to the context-always-load list in CLAUDE.md.
- Change is committed with message: "Add LATEST_SYNTHESIS to always-load context — ensure cold-start sessions read current cross-cutting diagnosis (P7 from synthesis C138)".
- Next session start verifies that the synthesis file is loaded (check session context output).
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` (not strictly required; low complexity change).

## Escalation

If `/opt/workspace/runtime/.meta/LATEST_SYNTHESIS` does not exist or is stale (older than 12 hours), escalate with pointer to the most recent synthesis file and ask whether to update the symlink manually.
