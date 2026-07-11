---
from: synthesis-translator
to: general
date: 2026-07-10T15:28:36Z
priority: high
task_id: synthesis-p7-latest-synthesis-context
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-10T15-24-51Z.md
source_proposal: P7 (CARRY — C133, 4th cycle): Add LATEST_SYNTHESIS to always-load context
---

# P7: Add LATEST_SYNTHESIS to always-load context

**Type:** CLAUDE.md amendment — `context-always-load` block. Add at tail:

```yaml
  - runtime/.meta/LATEST_SYNTHESIS              # regenerated every synthesis (~12h)
```

**Rationale:** The always-load set describes a workspace from June 9. The synthesis describes reality. Adding the symlink ensures every cold-start session reads accurate cross-cutting diagnosis. Under the 30KB cap, this would displace stale files — which is the correct outcome.

**Blast radius:** All workspace sessions. Automatic.

## Verification before action (required)

- Location: `/opt/workspace/CLAUDE.md` lines 64-78 (context-always-load block)
- Current state: 6 items listed, LATEST_SYNTHESIS not present
- Target state: Add `- runtime/.meta/LATEST_SYNTHESIS` after line 77
- Verification: `ls -la /opt/workspace/runtime/.meta/LATEST_SYNTHESIS` confirms symlink exists and points to current synthesis

## Rationale context (from synthesis)

Pattern 3 notes that the always-load context is actively harmful to cold-start sessions:

| Surface | Claimed | Reality | Delta |
|---------|---------|---------|-------|
| INBOX count | 156 | 317 | **+161** |
| Commits ahead | 224 | 591 | **+367** |
| Phase 2b status | not mentioned | bucket 2948 permanently lost, 2949 at 5.4d | — |

The synthesis file at `LATEST_SYNTHESIS` contains the accurate cross-cutting diagnosis that the old always-load files lack. Adding it ensures new sessions start from correct state.

## Implementation notes

1. Add the line at the tail of `context-always-load` (after `verified-state.md`)
2. Add a comment: `# regenerated every synthesis (~12h)`
3. Do not remove any existing entries; the 30KB cap will apply naturally (verified-state and active-issues are most dynamic)
4. Confirm `/opt/workspace/runtime/.meta/LATEST_SYNTHESIS` symlink exists before committing (should be created by synthesize.sh)

## Acceptance criteria

- Entry added to `context-always-load` list in `/opt/workspace/CLAUDE.md`
- File order preserved (stable → volatile)
- Comment added explaining refresh cadence
- Change committed with message: "Add LATEST_SYNTHESIS to always-load context for accurate cold-start diagnosis"
- Verify: New session opens and loads LATEST_SYNTHESIS without error
- Completion report filed at `runtime/.handoff/general-latest-synthesis-load-complete-<iso>.md`

## Escalation

If the LATEST_SYNTHESIS symlink does not exist in runtime/.meta/, investigate whether synthesize.sh is creating it correctly before committing this change. The always-load will fail if the target is missing.
