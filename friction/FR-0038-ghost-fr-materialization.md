---
id: FR-0038
title: Ghost FR materialization — tick events claim FR writes that don't land on main
status: Open
created: 2026-04-28
severity: high
---

# FR-0038: Ghost FR materialization

## Pattern

Tick sessions emit `fr_captured` events referencing friction files (e.g. `friction/FR-0038-ghost-fr-materialization.md`) that never appear on main branch. Events claim "materialized on disk" but git history and filesystem show the file absent. This has recurred for 5+ consecutive cycles.

## Root cause

Tick sessions run in worktrees. Writes to `friction/` in the worktree land on the tick branch (e.g. `ticks/2026-04-28-12`), not on main. The tick branch is never merged by an attended session, so the friction files stay stranded in unmerged branches. Autocommit runs on main and never sees the worktree's changes.

The 12:49Z tick session event claimed "non-worktree session succeeds" but that session also ran in a worktree (evidenced by the tick branch it created). The event note was misleading.

## Evidence

- `ls /opt/workspace/supervisor/friction/` shows highest as FR-0037 on main
- `grep fr_captured /opt/workspace/supervisor/events/supervisor-events.jsonl` shows multiple events for FR-0038/FR-0039 with no corresponding files on main
- `git log --all --oneline --follow friction/FR-0038-*` would show the file in tick branches if they are checked

## Fix path

1. Short-term: Non-worktree sessions (attended or direct tick invocations) must write FRs directly on main, not in a worktree context. This instance (2026-04-28T20:47Z) is writing FR-0038 on main.
2. Structural: The tick-branch-to-main merge workflow needs an attended session playbook. The `proposal-merge-tick-branches-playbook-2026-04-26T03-37-07Z.md` INBOX item addresses this.

## Impact

Friction signals accumulate in event log but never reach main. The policy-search loop (friction → policy refinement) is severed. Each tick wastes time "discovering" FRs already nominally captured.
