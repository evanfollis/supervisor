---
name: FR-0044 — test telemetry sink pollution
description: Test code emitted production-tagged events to shared events.jsonl, violating S1-P2 sourceType rule
type: friction
status: Open
created: 2026-05-03T18:49Z
source: cross-cutting synthesis 2026-05-03T15:23Z + supervisor-tick-2026-05-03T18-49Z
project: skillfoundry-harness
---

# FR-0044 — Test telemetry sink pollution

## What happened

Commit 531946f (sf-harness migrate.py telemetry) triggered test execution
that wrote 2 events to the workspace production telemetry sink
(`events.jsonl`) with:
- `sourceType: user` (should be `sourceType: smoke`)
- `venture_root: /tmp/pytest-of-root/pytest-NNN/...` (clear pytest tmp path)
- Timestamps: 1777775272667, 1777775280921 (confirmed in events.jsonl)

## Why it matters

ADR-0019 mandates co-located measurement discrimination. CLAUDE.md S1-P2
requires `sourceType: smoke` for test/smoke runs. Both rules exist; neither
is enforced at the boundary where violations originate — the test fixture.
Any meta-scan or S3-P2 monitor that trusts `sourceType: user` events is now
processing false signals for those two timestamps.

## Pattern

This is the same class as the "loopback session as REAL-USER" incident that
drove ADR-0019. The enforcement gap is at test execution boundaries, not in
the event schema itself.

## Fix

1. Add a `conftest.py` autouse fixture in sf-harness tests that redirects
   `*_TELEMETRY_PATH` (or equivalent env var) to a temp dir before any test
   that exercises telemetry-emitting code.
2. Write a CLAUDE.md amendment (Proposal 4 in synthesis 2026-05-03T15:23Z):
   "Test suites must not write to the shared telemetry sink. Any project
   whose tests invoke telemetry-emitting code must redirect the sink path
   to a temp dir via a conftest autouse fixture."

## Status

Open — fix not yet dispatched. Synthesis Proposal 4 targets sf-harness as
immediate instance; atlas runner tests already redirect correctly (no
violation observed).
