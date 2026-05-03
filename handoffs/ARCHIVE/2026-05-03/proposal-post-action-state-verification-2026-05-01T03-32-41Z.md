---
from: synthesis-translator
to: general
date: 2026-05-01T03:32:41Z
priority: high
task_id: synthesis-post-action-state-verification
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-01T03-27-05Z.md
source_proposal: Proposal 4 — Post-action state verification in tick wrapper (MEDIUM, REPEAT)
---

# Post-action state verification in tick wrapper

**Pattern (Pattern 4, worsened):** Ghost-write pattern has now extended from supervisor FR files to project tick wrappers. This window:

- Context-repo and command project tick wrappers emitted events claiming `INBOX/URGENT-context-repo-tick-auth-failure-*.md` and `INBOX/URGENT-command-tick-auth-failure-*.md` were written. Neither exists. Actual escalation went to `runtime/.handoff/general-*` instead — inconsistent routing plus false provenance.

- Supervisor ticks continue to claim FR-0038/0039/0040 were written. `ls friction/` still ends at FR-0037 (7+ windows now).

- `active-issues.md` remains dated `2026-04-25` (6 days stale) despite multiple tick claims of "active-issues refreshed."

**Event model is no longer a truth source.** Any consumer (monitor, meta-scan, executive dispatch) that trusts event claims without primary verification will draw false conclusions.

**Proposed implementation** (add to `/opt/workspace/supervisor/scripts/lib/supervisor-tick.sh` after each state-file write):

```bash
# Post-action verification before emitting success event
test -f "$handoff_file" || {
  echo "ERROR: post-write verification failed ($handoff_file does not exist)" >&2
  exit 1
}
```

More generally: before emitting an event that claims a file was written, `test -f <ref>` check that the file actually exists. Emit `eventType: "failure"` if verification fails.

**Blast radius:** Supervisor project only (tick wrapper). Automatic. Prevents ghost-write events at the source.

**Why now:** Pattern has now spread beyond supervisor to project ticks (4 false claims in one window). This is the 3rd synthesis cycle for this proposal. Escalation required per carry-forward rule.

## Verification before action (required)

- Run `grep -n "test -f.*INBOX" /opt/workspace/supervisor/scripts/lib/supervisor-tick.sh` — verify post-write check is not already present.
- Read the section of supervisor-tick.sh that writes INBOX files to understand the context and variable names.
- If verification checks are already present, skip and report "already landed at line <N>".

## Acceptance criteria

- Post-write `test -f` verification added after each major file-write operation in supervisor-tick.sh (INBOX creation, FR file writes, CURRENT_STATE commits).
- Verification must check the actual file path that was written (not a pattern or glob).
- On verification failure, emit `eventType: "failure"` with clear error message, then `exit 1` to short-circuit the tick.
- Commit message: "Add post-action state verification to supervisor-tick to prevent ghost-write events" (imperative, explains why not what).
- Commit includes cite to synthesis source.

## Adversarial review

Run via `supervisor/scripts/lib/adversarial-review.sh /opt/workspace/supervisor/scripts/lib/supervisor-tick.sh` to validate:
- Verification happens after all state mutations (file writes, commits).
- File paths checked are the actual paths written (variable names match).
- Error handling doesn't mask the failure — event is emitted and exit code is non-zero.
- Edge cases: symlinks, race conditions where file is written by another process, temp files.

## Completion report

After commit, write `/opt/workspace/runtime/.handoff/general-supervisor-synthesis-post-action-verification-complete-<iso>.md` with:
- Commit SHA
- Confirmation via grep showing verification checks at specific line numbers
- List of state-write locations verified (INBOX creation, FR files, CURRENT_STATE commits)
- Link back to this handoff
