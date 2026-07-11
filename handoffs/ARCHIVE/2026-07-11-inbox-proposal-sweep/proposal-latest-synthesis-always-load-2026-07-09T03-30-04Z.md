---
from: synthesis-translator
to: general
date: 2026-07-09T03:30:04Z
priority: high
task_id: synthesis-latest-synthesis-always-load
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-09T03-26-11Z.md
source_proposal: P7 — Add LATEST_SYNTHESIS pointer to always-load context
---

# P7: Add LATEST_SYNTHESIS pointer to always-load context

**Type:** CLAUDE.md amendment — `context-always-load` block.

**Proposed addition (at tail of the list, after `verified-state.md`):**
```yaml
  - runtime/.meta/LATEST_SYNTHESIS              # regenerated every synthesis (~12h)
```

**Rationale:** Supervisor C73 identifies that the always-load set describes a workspace state from June 9, while synthesis files describe reality. Adding the symlink pointer (72 bytes → ~19KB target) would ensure every new session reads current cross-cutting diagnosis on load. The target file's `updated:` date would be synthesis-generated, so the 7-day stale banner applies automatically if synthesis stops running.

**Tradeoff:** The 30KB aggregate cap is already exceeded (active-issues.md alone is ~24KB). Adding LATEST_SYNTHESIS (~19KB) makes truncation more aggressive. Two mitigation paths: 
  - (a) accept truncation of the oldest stale files (active-issues.md, verified-state.md) in favor of the current synthesis — arguably correct, since the synthesis IS the accurate state surface; or 
  - (b) replace the stale files with lightweight pointers and let sessions read on demand.

**Blast radius:** All workspace sessions. Automatic once CLAUDE.md is amended. The cap collision must be addressed concurrently or the new file will truncate existing entries.

---

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md` "Session-start context load (M4 / ADR-0021)" section (around line 68 in the workspace CLAUDE.md).
- Check if `runtime/.meta/LATEST_SYNTHESIS` is already listed in the `context-always-load:` block. If yes, write completion report "already landed in-file" and close.
- Verify that `/opt/workspace/runtime/.meta/LATEST_SYNTHESIS` exists as a symlink and points to the most recent `cross-cutting-*.md` file.
- Understand the cap collision (synthesis notes the 30KB aggregate limit and current state). Decide on mitigation: (a) accept truncation, or (b) replace stale files with pointers.

## Acceptance criteria

- `LATEST_SYNTHESIS` pointer added to the `context-always-load:` list in `context-always-load` CLAUDE.md section.
- Addition includes the comment `# regenerated every synthesis (~12h)` on the same line.
- A symlink `/opt/workspace/runtime/.meta/LATEST_SYNTHESIS` exists and is automatically updated by the synthesis job to point to the latest `cross-cutting-*.md` file.
- If mitigation path (b) is chosen: stale files (active-issues.md, verified-state.md) are replaced with lightweight pointers (or removed from always-load) to stay within the 30KB cap.
- Change committed with clear message: "Add LATEST_SYNTHESIS to always-load context per synthesis #133"
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-supervisor-synthesis-latest-synthesis-always-load-complete-<iso>.md` documenting which mitigation path was chosen.

## Escalation

URGENT if:
- The symlink `/opt/workspace/runtime/.meta/LATEST_SYNTHESIS` does not exist or is not maintained by the synthesis job. Escalate the missing automation.
- Cap collision resolution is ambiguous (should stale files be removed or replaced with pointers?). Escalate for principal decision on policy.
