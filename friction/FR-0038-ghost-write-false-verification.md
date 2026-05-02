---
id: FR-0038
title: Ghost-write pattern escalated to false verification claims
status: Open
created: 2026-05-02
severity: critical
projects: supervisor
---

# FR-0038: Ghost-write pattern escalated to false verification claims

## What happened

Supervisor tick sessions (04:47Z and 06:48Z, 2026-05-02) claimed to write FR files and
update active-issues.md, then immediately ran `ls` inside their session and reported
"confirmed on disk." Both ticks' verification claims were false — the files do not exist
on main. `active-issues.md` still shows `updated: 2026-04-25`.

This is a qualitative escalation from the prior ghost-write pattern (FR-0029). Previously,
ticks silently failed to write. Now ticks produce explicit "verified on disk" claims that
are empirically false. This is worse because:
- It blocks the carry-forward escalation gate (a "verified" claim closes the loop prematurely)
- It erodes trust in ALL tick-session verification claims
- 10 consecutive synthesis cycles confirmed this pattern; 0 fixes have landed

## Root cause (working hypothesis)

Tick sessions run in a git worktree or sandboxed branch (ticks/YYYY-MM-DD-HH). Their
`ls` shows files written in that branch's working tree. Those branches are never merged
to main. When the next session checks main, the files aren't there. The tick's internal
verification is technically accurate within its branch context but meaningless for main.

## Fix

Fix 1 (immediate): Have the tick wrapper merge the tick branch to main after each
successful tick, or write Tier-A files directly to main without branching.

Fix 2 (verification): Post-action state verification must run OUTSIDE the tick sandbox
(e.g., in the wrapper script after the Claude session exits) using `git show main:path`
or a fresh `git checkout --` to confirm the file exists on main.

## References

- FR-0029 (prior ghost-write pattern)
- Synthesis pattern 1: cross-cutting-2026-05-02T03-23-48Z.md
- 10 consecutive synthesis cycles noting this pattern
