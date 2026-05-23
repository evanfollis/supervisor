---
name: FR-0038
slug: false-ghost-write-resolution-claims
status: Open
filed: 2026-05-07T02:48Z
source: supervisor-tick-2026-05-07T02-48-05Z
severity: high
---

# FR-0038: Tick event stream carries false "ghost-write broken" claims

Captured: 2026-05-07T02:48Z
Source: supervisor-tick-2026-05-07T02-48-05Z
Status: open

## Observed behavior

Tick sessions (14:49Z and 20:47Z on 2026-05-06) emit `session_reflected` events
claiming "FR-0038 through FR-0041 written on main" and "ghost-write cascade broken."
The wrapper events for those same ticks confirm they committed to `ticks/2026-05-06-14`
and `ticks/2026-05-06-20` respectively. The friction records do not exist on main.

The event stream — the primary source of truth for what the supervisor has done —
now carries false positive signals about the most persistent structural issue in
the workspace.

## Root cause

Tick sessions write Tier-A files to the working tree (on main). The tick wrapper
script commits those changes to a tick branch, not to main. Sessions cannot observe
this distinction from inside their execution — they report what they wrote as if the
write landed on the active branch (main), but the wrapper redirects the commit.

## Failure class

Any reader relying on the event stream to assess whether ghost-write was resolved
would conclude it was (multiple events claim "broken"). The actual state is:
- `friction/` ceiling on main: FR-0037
- FR-0038+ exist only on tick branches
- active-issues.md on main last updated ~6 weeks ago

This degrades the escalation surface. False completion signals are worse than
silence because they suppress further escalation.

## What would fix it

The tick wrapper should either:
1. Emit a correcting event after commit, noting the branch name (not main), OR
2. Merge tick branches to main automatically after each tick succeeds (see synthesis
   Proposal #5: merge playbook for tick branches), OR
3. Grant ticks operator authority to commit directly to main

None of these are within Tier-A scope for ticks. Fixing requires attended session
or Tier-B-auto authority decision.

## Related

- Ghost-write cascade root: tick wrapper commits to `ticks/<iso>` not main
- INBOX: `URGENT-inbox-proposal-saturation` (April 28)
- Synthesis Proposal #5 (cycle 4): merge playbook for tick branches (20+ cycles open)
- Synthesis Proposal #18: Tier-B-auto authority decision
