---
id: FR-0039
title: Synthesis proposals not dispatched within the 24h charter window
severity: HIGH
created: 2026-04-27T02-49Z
status: open
source: supervisor-tick-2026-04-27T02-49-05Z
---

# FR-0039 — Synthesis dispatch obligation not met

## Observation

The charter (supervisor/CLAUDE.md) requires: "the executive must dispatch a
delegated project session within 24h — via `runtime/.handoff/<project>-*.md`
handoff — or record an explicit deferral reason in `supervisor/decisions/` or
`runtime/.meta/`."

The most recent synthesis (2026-04-26T15:25Z) produced 3 proposals. As of
2026-04-27T02:49Z (11.5h later), no `delegated` events for these proposals
appear in events.jsonl, and `runtime/.handoff/` contains no dispatch files
for the synthesis proposals. The deadline is 2026-04-27T15:25Z (~12.5h from now).

## Evidence

- events.jsonl: `synthesis_reviewed` emitted at 20:48Z and 22:47Z by tick
  sessions; no `delegated` event follows for any synthesis proposal.
- `runtime/.handoff/`: Only `URGENT-supervisor-reflection-dirty-tree.md`,
  `ARCHIVE/`, and `README.md`. No synthesis dispatch files.
- Proposals 1-3 in 2026-04-26T15:25Z synthesis all target Tier-C files
  (supervisor-tick.sh, reflect.sh, reflect-prompt.md) — not dispatchable by
  unattended ticks but dispatchable to the attended executive session.

## Root cause

Tick sessions correctly flag synthesis as "reviewed" but do not write dispatch
handoffs. Tier-C proposals can only be executed by attended sessions. Ticks have
no mechanism to create `runtime/.handoff/general-*.md` for supervisor-level
synthesis proposals — the dispatch to the executive is also Tier-A but was
never done.

## Required action

The attended executive session at next open must implement or record a deferral
for all 3 synthesis proposals before 2026-04-27T15:25Z. This tick has written
`runtime/.handoff/general-synthesis-dispatch-2026-04-27T02-49Z.md` to surface
this for the next attended session.

## Pattern note

This is a recurring gap: synthesis produces Tier-C proposals → ticks review
and emit `synthesis_reviewed` → no dispatch happens → proposals age past 24h
→ executive must be escalated. The `synthesis_reviewed` event being emitted
by an unattended tick should not count as "dispatch" for Tier-C proposals.
