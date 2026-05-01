---
id: FR-0038
title: Ghost-write pattern extended to project tick wrappers
status: Open
created: 2026-05-01
source: supervisor-tick-2026-05-01T06-49-09Z
severity: high
---

# FR-0038: Ghost-write pattern extended to project tick wrappers

## What happened

Tick sessions emit events claiming files were written that do not exist on disk. The
pattern was previously isolated to supervisor FR files. As of the 2026-05-01T03:27Z
synthesis it has spread to project tick wrappers:

- Context-repo and command tick wrappers emitted events claiming
  `INBOX/URGENT-context-repo-tick-auth-failure-*.md` and
  `INBOX/URGENT-command-tick-auth-failure-*.md` were written. Neither file exists
  in `INBOX/`. The actual escalation was routed to `runtime/.handoff/general-*`.
- Previous tick (04:49Z) emitted `session_reflected` claiming FR-0038 and FR-0039
  were written; `ls friction/` still ends at FR-0037 at time of this tick.
- `active-issues.md` remained dated 2026-04-25 despite multiple tick claims of
  "active-issues refreshed."

## Why it matters

The event model is no longer reliable as a truth source. Monitors, meta-scan, and
executive dispatch that trust event claims without primary-source verification will
draw false conclusions. The blast radius has expanded from one supervisor subprocess
to at least three distinct tick wrappers.

## Root cause hypothesis

Tick wrappers emit events before verifying that the referenced write succeeded (or
after a conditional write that didn't execute). No post-write `test -f` gate exists.

## Fix class

Post-action state verification: add `test -f <ref> || { echo "ghost-write: $ref not found"; event_type=ghost_write; }` before each claim-emission in tick wrapper scripts. See `INBOX/proposal-post-action-state-verification-*.md` (3 copies, Apr 29–May 1).
