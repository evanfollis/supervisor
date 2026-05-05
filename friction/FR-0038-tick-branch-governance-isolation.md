---
id: FR-0038
title: Tick branch governance isolation — Tier-A outputs never reach main
status: Open
filed: 2026-05-05T10-47-35Z
source: supervisor-tick-2026-05-05T10-47-35Z
severity: critical
---

# FR-0038: Tick branch governance isolation

## Observed failure

Every tick session writes Tier-A governance artifacts (FR files, `system/active-issues.md`
updates, `system/verified-state.md`) and commits them to a tick branch (e.g.,
`ticks/2026-05-05-04`). These tick branches are never merged to `main`. As a result:

- All FR files from FR-0038 onward (per prior tick event claims: FR-0038, FR-0039, FR-0040)
  exist only on orphan tick branches — not on `main`.
- `system/active-issues.md` on `main` is dated 2026-04-25 (10 days stale) despite multiple
  ticks claiming to update it.
- The friction directory on `main` shows FR-0037 as the latest entry; the doctor's friction
  check sees no new FRs in 7 days and reports a warn.
- The governance meta-loop writes outputs that never land in the control plane. Every tick's
  friction capture, active-issues update, and state verification is effectively dead.

## Evidence

- `git log --oneline -10` on `main`: only autocommit entries; no tick Tier-A commits
- `git show ticks/2026-05-05-04 --name-only`: contains FR-0038/0039/0040 and active-issues.md
- `ls friction/` on `main`: highest is FR-0037 (filed 2026-03-XX)
- `system/active-issues.md` frontmatter `updated: 2026-04-25` on `main`
- Autocommit picks up only `handoffs/ARCHIVE/` paths; tick wrapper commits to tick branches

## Why this slips past

Prior FRs (e.g., FR-0029 "ghost FR claimed in events") attributed the problem to event-level
dishonesty. The actual failure is structural: the tick wrapper creates a tick branch, commits,
and pushes. The attended session is supposed to merge these branches. Without merge, the
governance loop is write-only — outputs accumulate on orphan branches indefinitely.

## Required fix (Tier C — attended session)

1. Merge or cherry-pick Tier-A content from all unmerged tick branches to `main`.
2. Add a playbook step: attended session merges (or fast-forward-merges) aged tick branches
   that contain only Tier-A paths before archiving.
3. Consider: have the autocommit script also sweep Tier-A paths from the working tree on
   `main` directly, bypassing the tick branch pattern for governance files.

## How to apply

Every attended session should check `git branch -a | grep ticks/ | wc -l` and run
`workspace.sh doctor` before treating `friction/`, `system/active-issues.md`, or
`system/verified-state.md` as ground truth.
