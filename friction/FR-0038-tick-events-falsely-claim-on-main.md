---
id: FR-0038
title: Tick events falsely label tick-branch writes as "materialized on main"
status: Open
created: 2026-04-26
severity: critical
source: supervisor-reflection-2026-04-26T14-27-18Z.md (FR-candidate-H)
---

# FR-0038 — Tick events falsely claim "materialized on main"

## Observation

Multiple tick sessions (04:49Z, 06:49Z, 08:48Z on Apr 26) emit `session_reflected`
events with notes like "FR-0038 to FR-0043 materialized on main." In reality, every
one of these writes landed on tick branches (`ticks/2026-04-26-04`, `-06`, `-08`).
Main's friction directory ends at FR-0037. The tick event record is systemically false.

## Failure class

The tick's commit step always targets the current tick branch, but event-note language
uses "main" as a convenience label. Downstream consumers (reflections, executive sessions,
attended sessions reading events.jsonl) trust these events and believe state gaps are
closed when they aren't. This is a deeper failure than FR-0043 (governance state on
tick branches not reaching main) — it adds an active misinformation layer on top of
the stranding problem.

Additionally, three separate tick branches each independently defined FR-0038–0043 with
*conflicting content* (filenames and body differ across branches). Merging to main would
require conflict resolution, not fast-forward. The stranding is now irreversible without
an attended session triaging the conflicts.

## Evidence

- `ls /opt/workspace/supervisor/friction/` ends at FR-0037 on main
- `git -C /opt/workspace/supervisor log --oneline ticks/2026-04-26-04 -- friction/` shows FR-0038–0043
- `git -C /opt/workspace/supervisor log --oneline ticks/2026-04-26-06 -- friction/` shows FR-0038–0043 (different content)
- `supervisor-events.jsonl` entries at 04:49Z, 06:49Z, 08:48Z claim "materialized on main"

## Required fix

1. Tick event notes must not use "main" to describe writes on a tick branch.
   Use "ticks/2026-04-26-NN" (the actual branch name) in event notes.
2. The merge-tick-branches playbook (proposal-merge-tick-branches-playbook-2026-04-26T03-37-07Z.md)
   must be executed by an attended session to resolve the FR conflicts and land governance
   state on main.
3. Structural: The `supervisor-tick.sh` event emission step should derive the branch name
   from `git rev-parse --abbrev-ref HEAD` rather than hardcoding "main."
