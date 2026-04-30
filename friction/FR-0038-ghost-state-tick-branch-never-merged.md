---
id: FR-0038
title: Ghost-state — tick branches never merge to main
status: Open
created: 2026-04-30
severity: high
---

# FR-0038: Ghost-state — tick branches never merge to main

## Observed failure

The tick wrapper (`scripts/lib/supervisor-tick.sh`) creates a fresh `ticks/YYYY-MM-DD-HH`
branch for each run, then the Claude session writes Tier-A artifacts to that branch. The
branch is pushed but never merged to main. This produces:

1. **Ghost writes**: tick completion reports claim "FR-0038 written", "active-issues updated",
   etc., but those files never appear on main. At least 4 consecutive ticks (2026-04-29T22Z,
   2026-04-30T00Z, 2026-04-30T02Z, 2026-04-30T04Z) claimed FR-0038 was written; it was absent
   from main on each subsequent verification.
2. **False events**: `session_reflected` events in `supervisor-events.jsonl` record artifact
   paths that do not exist at those paths on main, making the event log unreliable as a
   truth source.
3. **Stale governance surfaces**: `active-issues.md`, `system/verified-state.md`, and
   `friction/` only reflect the state of the last autocommit cycle, not tick sessions —
   because tick sessions write to unmerged branches.
4. **Growing branch debt**: 49+ tick branches unmerged as of 2026-04-30T06Z, growing ~3/12h.

## Root cause

The tick wrapper design assumes that Claude sessions should run in isolation branches for
safety, but never implements the merge step. The Claude session running within the branch
does not know it's isolated — it reports success based on local file state. The wrapper
records "committed + pushed ticks/YYYY-MM-DD-HH" but this SHA is on the branch, not main.

## Impact

Every tick session's writes are invisible to the next session unless the next session
explicitly checks out the branch or the autocommit cycle happens to pick up the same files.
This creates a systematic disconnect between claimed state and actual main-branch state.

## Fix path

The tick wrapper needs one of:
- Merge the tick branch to main after a successful tick (`git merge --no-ff ticks/<name>`)
- Run the session directly on main (no branch creation for tick sessions)

Proposal `proposal-merge-tick-branches-playbook-2026-04-26T03-37-07Z.md` has been in INBOX
for 7+ synthesis cycles. Requires `scripts/lib/` write access (Tier-C/attended session).

## This file's own provenance

This FR was written on main directly in an interactive session (not a tick branch), which
is why it will persist. Prior claims by ticks to have written this FR were themselves ghost-writes.
