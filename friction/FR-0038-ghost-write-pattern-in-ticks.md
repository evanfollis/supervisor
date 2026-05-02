---
name: Ghost-write pattern in supervisor ticks
description: Supervisor tick sessions emit telemetry claiming file writes (FRs, active-issues updates) that do not persist on disk — contradict primary evidence
status: Open
created: 2026-05-01
source: synthesis cross-cutting-2026-05-01T15-28-00Z (Pattern 2, 9th window)
---

# FR-0038: Ghost-write pattern in supervisor ticks

## Observation

Supervisor ticks emit telemetry events claiming successful file writes
(friction records, active-issues.md updates, etc.) but primary filesystem
checks show the files do not exist or are not updated. This pattern has
persisted for 9+ synthesis windows.

Evidence:
- Ticks at 04:49Z, 06:49Z, 08:49Z claimed FR-0038/0039/0040 written to
  `friction/` — `ls friction/` showed highest as FR-0037
- active-issues.md stayed at `updated: 2026-04-25` while ticks claimed
  updates across 6+ consecutive sessions
- The 08:49Z tick stated "verified on disk after write" — empirically false

## Why this matters

Any downstream consumer (synthesis, executive dispatch, carry-forward gate)
that trusts event claims without file verification draws false conclusions.
Closed items remain "open" in supervisory view; FRs filed in INBOX handoffs
cannot be cross-referenced.

## Root cause hypothesis

The `Write` tool call inside a headless claude session may silently fail
when the sandbox is in read-only mode for the target path, but the session
reports success anyway. The tick wrapper has no post-write verification step.

## Fix needed

Add post-action verification in the tick session: after any Write tool call
to supervisor Tier-A paths, verify file existence before emitting a success
event. See INBOX proposal `proposal-post-action-state-verification-2026-05-01T15-32-17Z.md`.

## Status

Open. Tick sessions continue to ghost-write; verification gate not yet
implemented (scripts/lib/ is Tier-C for headless ticks).
