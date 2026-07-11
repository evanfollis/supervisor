---
from: synthesis-translator
to: general
date: 2026-06-12T15:33:01Z
priority: high
task_id: synthesis-autocommit-event-order
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-12T15-27-51Z.md
source_proposal: Proposal 1 — P-autocommit-event-order (carry from C93 — 2nd cycle, HIGHEST PRIORITY)
---

# P-autocommit-event-order — Fix autocommit event emission order (FR-D)

## Synthesis proposal (verbatim)

**Type:** Shared primitive fix.
**File:** `supervisor/scripts/lib/supervisor-autocommit.sh`, lines 79–84.

**What:** Reorder so the completion event is emitted and staged BEFORE the `git commit`, not after:

```bash
# Fixed: emit → stage → commit (event included in commit payload)
emit_event "session_reflected" "autocommit: committed Tier-A on current branch"
git -C "$SUP" add events/ 2>/dev/null || true
git -C "$SUP" commit ...  # event is now part of the committed state
NEW_SHA=$(git -C "$SUP" rev-parse HEAD)
git -C "$SUP" branch -f "$BRANCH" "$NEW_SHA"
emit_event "session_reflected" "autocommit: committed Tier-A on current branch and marked $BRANCH (sha=${NEW_SHA:0:12})"
log "committed Tier-A writes on current branch and marked $BRANCH (sha=${NEW_SHA:0:12})"
```

Note: the SHA in the note references the just-created commit, so the event emitted before commit cannot include it. Options: (a) emit a generic pre-commit event, do the commit, then emit the sha-carrying event (but stage the second event too or it re-dirties); (b) emit only the pre-commit event and log the SHA without an event; (c) compute the tree SHA pre-commit. Option (b) is simplest and sufficient.

**Blast radius:** Supervisor only. Automatic (takes effect next autocommit cycle). No other project affected.

**Status:** This is the single highest-leverage item in the workspace for the 2nd consecutive synthesis cycle. <10 min, zero credentials.

---

## Context (from synthesis)

This fix resolves FR-D (autocommit self-pollution), the sole remaining tick blocker. Current behavior: autocommit commits Tier-A → post-commit event fires → event dirties `events/` → next tick finds `events/` dirty and skips. Synthesis documents 6 confirmed skip cycles in this window alone. The workspace governance clock has not advanced in 70 hours. No automated dispatch can fire until this lands.

---

## Verification before action (required)

- Check `git log -10 --oneline supervisor/scripts/lib/supervisor-autocommit.sh` — has this already been fixed?
- Read lines 60–85 of the current file — is the event already being emitted and staged BEFORE the commit?
- If either is true, write completion report "already landed" and close.

---

## Acceptance criteria

- Event emission reordered so `events/` changes are staged BEFORE `git commit`, not after.
- The commit includes the event in its payload (no post-commit dirt).
- Next autocommit cycle produces a clean → commit → clean sequence (no subsequent skip).
- Commit message explains the fix (e.g., "Fix autocommit event order — emit and stage before commit to prevent post-commit dirty-tree deadlock").
- Escalate if verification surfaces ambiguity about which option (a/b/c above) the principal prefers — synthesis recommends (b) but leaves choice open.

---

## Escalation

URGENT if:
- The fix has already landed on another branch or via another path. Report the SHA and close.
- Verification reveals uncertainty about whether pre-commit or post-commit event is safer. The synthesis frames this as a design choice; seek clarification if needed.
