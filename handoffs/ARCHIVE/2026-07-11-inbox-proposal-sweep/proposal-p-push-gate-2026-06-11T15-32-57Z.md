---
from: synthesis-translator
to: general
date: 2026-06-11T15:32:57Z
priority: medium
task_id: synthesis-p-push-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-11T15-25-11Z.md
source_proposal: P-push-gate (carry from C91 — 2nd cycle)
---

# P-push-gate — Add conditional push to supervisor-autocommit.sh

## Summary

Add a push step to `supervisor/scripts/lib/supervisor-autocommit.sh` that runs `git push` after a successful Tier-A commit, gated on a `SUPERVISOR_AUTOPUSH=true` env var (defaulting to `false`).

## Why

Supervisor is 241 commits ahead of origin. Unpushed commits are invisible to remote consumers and accumulate risk. An opt-in gate (enabled via env var) avoids accidental pushes while enabling automated resolution once the principal authorizes it. The default is `false`, so no unintended pushes occur.

## Proposed change

Add this code block after the successful commit section in `supervisor/scripts/lib/supervisor-autocommit.sh`:

```bash
# After successful commit:
if [[ "${SUPERVISOR_AUTOPUSH:-false}" == "true" ]]; then
  git -C "$SUP" push origin main 2>/dev/null || true
fi
```

(Suggested insertion point: after line 85, before or after the final `log` statement, depending on desired sequence.)

## Verification before action (required)

- Run `git log --oneline -10 supervisor/scripts/lib/supervisor-autocommit.sh` to check if this has landed.
- Search the script for `SUPERVISOR_AUTOPUSH` or `git push` to verify this mechanism doesn't already exist.
- If already present, write a completion report stating "already present" with the commit SHA.

## Acceptance criteria

- The conditional push block is added to `supervisor-autocommit.sh`.
- The env var defaults to `false` (no automatic pushes until principal explicitly enables via env var).
- Change committed with message: "Add conditional autopush mechanism to supervisor-autocommit.sh (P-push-gate, C92)"
- No adversarial review needed (mechanism change, opt-in by default, low risk).
- Completion report references this handoff.

## Note on enablement

This handoff adds the **mechanism**. The principal's decision to enable autopush (`SUPERVISOR_AUTOPUSH=true`) is a separate, future decision—it requires principal authorization but is not blocking this code landing.

## Escalation

URGENT if:
- Verification shows this already landed.
- The script structure has changed significantly and the insertion point is unclear — note the ambiguity in the commit message.
