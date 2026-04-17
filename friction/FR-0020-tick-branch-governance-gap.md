---
name: Tick branch governance gap
description: Tick sessions commit friction records and active-issues changes to tick branches, not main — governance artifacts never land in the canonical surface
type: feedback
---

Status: open

Tick sessions commit Tier A governance artifacts (friction/, system/active-issues.md, handoffs/ARCHIVE/) to `ticks/YYYY-MM-DD-HH` branches. These branches are pushed to origin but never merged to main. The result: friction records created in a tick are invisible to any subsequent session reading from main.

Confirmed at this tick: FR-0020 and FR-0021 were claimed in the events log for the 02:49Z tick, but `ls friction/` on main shows only FR-0001 through FR-0019. The tick branch `ticks/2026-04-17-02` has the files; main does not.

**Why:** The tick branch model was designed to isolate tick writes from main. But friction records and active-issues.md are governance surfaces — they need to be on main to matter. The design intent was correct (don't pollute main with scratch work), but friction and system state are not scratch work.

**How to apply:** Either:
1. Merge tick branches to main after doctor passes (attended session action, scripts/lib change), or
2. Move friction/ and system/ writes to the runtime surface (not the git repo), or
3. Have the tick wrapper cherry-pick or merge governance artifact commits to main.

This is an attended-session ADR-class decision. Record as structural friction until resolved.

**Discovered**: 2026-04-17T04:47Z (supervisor tick)
