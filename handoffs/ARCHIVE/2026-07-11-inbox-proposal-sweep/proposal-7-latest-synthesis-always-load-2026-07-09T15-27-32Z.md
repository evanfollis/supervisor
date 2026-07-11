---
from: synthesis-translator
to: general
date: 2026-07-09T15:27:32Z
priority: high
task_id: synthesis-latest-synthesis-always-load
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-09T15-23-51Z.md
source_proposal: P7 — Add LATEST_SYNTHESIS pointer to always-load context
---

# P7 — Add LATEST_SYNTHESIS pointer to always-load context

**Type:** CLAUDE.md amendment — `context-always-load` block.

**Proposed addition (at tail of the list, after `verified-state.md`):**
```yaml
  - runtime/.meta/LATEST_SYNTHESIS              # regenerated every synthesis (~12h)
```

**Rationale:** The always-load set describes a workspace from June 9. The synthesis describes reality. Adding the symlink ensures every new session reads current cross-cutting diagnosis. The 30KB cap collision means this would likely displace the stale files — which is the correct outcome, since the synthesis IS the accurate state surface.

**Blast radius:** All workspace sessions. Automatic once CLAUDE.md is amended.

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md` under "Session-start context load (M4 / ADR-0021)" section.
- Verify the `context-always-load:` block exists and contains the listed files.
- Check if `runtime/.meta/LATEST_SYNTHESIS` is already present in the list.
- Verify that `runtime/.meta/LATEST_SYNTHESIS` is a valid symlink pointing to a recent synthesis file.
- If the amendment is already in place, write a completion report stating "already landed — verified in-file" rather than re-applying.

## Acceptance criteria

- The `context-always-load:` list in `/opt/workspace/CLAUDE.md` is amended to include `- runtime/.meta/LATEST_SYNTHESIS` at the tail (after `verified-state.md`).
- The symlink `/opt/workspace/runtime/.meta/LATEST_SYNTHESIS` exists and points to a valid synthesis file.
- Change committed with message: "Add LATEST_SYNTHESIS to always-load context per synthesis C134"
- No adversarial review required (configuration amendment).
- Completion report at `/opt/workspace/runtime/.handoff/general-synthesis-latest-synthesis-always-load-complete-<iso>.md` pointing back to this handoff and source synthesis.

## Escalation

URGENT if:
- The `context-always-load:` block cannot be located in CLAUDE.md (verify the file exists and contains the section).
- The `LATEST_SYNTHESIS` symlink does not exist or points to an invalid/stale file. Verify the symlink setup in the synthesis job.
- Adding this file causes the 30KB cap to be exceeded unexpectedly. Note the current size and impact.
