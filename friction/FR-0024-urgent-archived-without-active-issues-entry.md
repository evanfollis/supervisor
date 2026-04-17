---
id: FR-0024
title: URGENT handoffs archived without corresponding active-issues entries
status: open
captured: 2026-04-17T12:48Z
source: supervisor tick 2026-04-17T12-48-47Z
---

## Observation

`URGENT-review-skill-broken-2026-04-17T02-49Z.md` was written, then archived
by a subsequent tick session, but the `/review` EROFS issue it described had
no corresponding entry in `system/active-issues.md`. The URGENT escalation
mechanism fired correctly — but archiving it without surfacing it in active-issues
created an invisible gap: the issue exists, the URGENT was acknowledged, but
the persistent pressure surface (active-issues) had no explicit item for it.

This means an attended session scanning active-issues would not see the EROFS
blocker at the top of the list unless they happened to cross-reference FR-0021.

## Root cause

The tick contract for URGENT handling says: read, act or escalate, archive.
It does not require: "if the underlying issue remains unresolved, ensure active-issues
has a corresponding entry before archiving." The active-issues update is a
separate write that ticks can miss.

## Pattern

Any URGENT handoff that is archived without the underlying issue being resolved
should leave a trace in `active-issues.md`. Otherwise the mechanism escalates
correctly but the signal disappears after one tick.

## Proposed fix

Add to the tick protocol: when archiving an URGENT item that is not fully
resolved, a corresponding entry in `system/active-issues.md` is required.
The tick must either update active-issues or explain in the tick report why
no active-issues entry is needed.

This is a playbook-level amendment to the URGENT processing protocol.
