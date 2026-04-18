---
id: FR-0031
title: Breach detector fires on concurrent attended-session activity
date: 2026-04-18
severity: medium
status: open
---

# FR-0031: Breach detector fires false URGENT on concurrent attended-session activity

## Observed

Two URGENT false positives in the same window:

1. **URGENT-tick-boundary-breach-2026-04-18T16-49-48Z.md** — tick at 16:49Z left supervisor dirty tree (Tier-A changes: `system/active-issues.md` modified, new friction/ARCHIVE files). Command HEAD advanced (`e1f23036` → `c3aac729`). Both were expected: dirty tree = uncommitted Tier-A work (autocommit cleaned it at 18:25Z); command HEAD = concurrent command PM tick doing routed work. No Tier-C violations.

2. **URGENT-supervisor-reflection-mutated-head.md** — reflection at 14:32Z reported supervisor HEAD advanced (`e4e9b7b2` → `b78795c`). Both commits were made at 14:32:15 and 14:32:45 by the attended session — the reflection session was a read-only observer and committed nothing. The breach detector recorded HEAD at session start, the attended session committed during the reflection run, breach detector reported it as the reflection session's fault.

## Root cause

The breach detection script (`supervisor-tick.sh` and/or `reflect.sh`) determines violation by comparing HEAD at start vs. end and checking dirty tree at session exit. It does not account for:
- Concurrent attended-session commits happening during the session window
- Normal Tier-A dirty tree that the autocommit job is responsible for cleaning

## Why it matters

URGENT handoffs demand principal attention. False positives train the principal to dismiss URGENTs, defeating the escalation mechanism. Two false positives in one 6h window is a meaningful noise rate.

## Rule signal

The breach detector should distinguish the session's own writes from external concurrent writes. One approach: record the author of new commits (attended sessions use `Evan Follis` author; tick/reflect sessions use a different identity or could be detected by checking `GIT_AUTHOR_EMAIL`). Alternatively, detect only if the session's own PID is in the git reflog for the window.

A softer fix: dirty tree at session exit is expected for Tier-A paths — only flag if Tier-C paths appear dirty.

**Status**: Open — structural fix requires `scripts/lib/` edit (Tier-C for tick sessions); flagged to attended session.
