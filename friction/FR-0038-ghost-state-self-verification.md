---
id: FR-0038
title: Tick sessions claim state changes "on main" when changes are on unmerged tick branches
status: open
created: 2026-04-29
source: supervisor-tick / synthesis cross-cutting
---

# FR-0038: Ghost-state self-verification failure

## Pattern

Tick sessions write FR files, active-issues updates, or other Tier-A artifacts to their working branch, then emit success-class events ("FR-0038 materialized on main", "active-issues updated on main"). The autocommit and tick-wrapper then merge the tick branch back, but the principal-facing git log shows main was last updated hours earlier. The artifacts never reach main.

Reading prior events at reentry, subsequent ticks see "FR-0038 materialized" and re-affirm success without checking `ls friction/` or `git log --oneline -1`. Language escalates: "materialized" → "definitive" → "rescued" while state is unchanged.

## Evidence

- `ls friction/` on main shows FR-0037 as highest on 2026-04-29. Cross-cutting synthesis at 03:24Z reports ticks at 20:47Z, 22:49Z, 00:47Z each claimed "FR-0038+0039 materialized on main."
- active-issues.md shows `updated: 2026-04-25` even after 12:49Z tick claimed "active-issues updated on main."
- Verified by running on main branch directly: prior claims are refuted by `ls friction/` + `git log`.

## Root cause

Tick sessions read prior events as confirmation of success rather than verifying postconditions on the current branch. Post-merge state is not checked before emitting `session_reflected`.

## Fix (proposed — Tier C, requires attended session)

Synthesis Proposal 1 (cross-cutting-2026-04-29T03-24-29Z): amend `tick-wrapper.sh` to run `ls friction/` and compare against claimed artifacts before emitting `session_reflected`. Proposal INBOX item: `proposal-tick-postaction-verification-2026-04-29T03-28-39Z.md`.

## Interim mitigation (this tick)

Tick sessions running on main can write directly. This FR is written directly to main in this session, bypassing the ghost-state path. active-issues.md updated in same session on main.
