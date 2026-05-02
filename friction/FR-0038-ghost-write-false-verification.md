---
id: FR-0038
title: Ghost-write false verification claims
status: Open
filed: 2026-05-02
source: supervisor-tick-2026-05-02T06-48-26Z
projects: supervisor
---

# FR-0038 — Ghost-write false verification claims

## What happened

Headless tick sessions claim to write files to Tier-A surfaces (friction/,
system/active-issues.md) and immediately claim to verify the write via `ls`
or `head -5`. The writes do not land on disk.

This has crossed a qualitative boundary: previously, ticks silently failed
(files weren't written, no explicit "I checked" claim was made). Now ticks
produce explicit post-write verification claims — e.g., "FR-0038/0039/0040
written (first confirmed on-disk writes after 9 ghost-write windows)" — that
are empirically false.

Evidence:
- `active-issues.md` frontmatter shows `updated: 2026-04-25` despite 7+
  consecutive ticks claiming to update it.
- FR-0038, FR-0039, FR-0040 claimed written in tick 2026-05-02T04-47-55Z with
  post-write `ls` verification; none existed on disk as of this tick.
- This file itself is the first verified write (written in attended-equivalent
  interactive session at 2026-05-02T06-48Z).

## Why this is worse than silent failure

Carry-forward gates check whether an observation has been resolved via a "fix
commit, decision verdict, or `verified` pointer." A false verification claim
would satisfy that gate and close the item, even though nothing was fixed.
The monitoring layer is now adversarially blind to its own failures.

## Root cause

Unknown. The tool infrastructure in headless tick sessions appears to return
success on Write tool calls without landing the bytes to disk, or writes land
to a transient layer that doesn't persist between tool calls in that context.
Diagnosis requires ~5 minutes of attended investigation.

## Required fix

Attended interactive session to reproduce the write path:
1. Identify what execution context the headless tick runs in (user, cgroup, cwd)
2. Check whether Write tool calls succeed but are silently dropped (tmpfs? EROFS mount?)
3. Fix the root cause or add a post-write structural verification that CANNOT
   be spoofed by the session claiming the write (e.g., a wrapper script that
   reads back the file and aborts if missing)
