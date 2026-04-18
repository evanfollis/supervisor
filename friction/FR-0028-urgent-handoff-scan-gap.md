---
FR: 0028
Title: Tick URGENT handoff scan misses non-general-prefixed escalations
Status: open
Date: 2026-04-18
---

# FR-0028 — Tick URGENT handoff scan misses non-general-prefixed escalations

## What happened

Two URGENT escalations written by the reflection job at 02:26Z (`runtime/.handoff/URGENT-atlas-claim-hash-decision-needed.md` and `runtime/.handoff/URGENT-atlas-live-path-unvalidated.md`) sat unconsumed for 6.5h across at least one full tick cycle (06:48Z tick).

The 06:48Z tick report explicitly stated "No new general runtime handoffs found" — which was technically correct for `general-*` prefix but missed both URGENT items.

## Root cause

The tick's handoff scan step uses:
```
ls /opt/workspace/runtime/.handoff/general-* 2>/dev/null
```

The reflection job escalation policy writes files named `URGENT-<project>-<slug>.md`, not `general-*.md`. The naming contract between the reflection job output and the tick scan input is mismatched.

## Failure class

Routing gap: a defined carry-forward escalation mechanism (3rd-cycle URGENT) has a naming convention that makes it invisible to the tick's handoff scan. Any URGENT escalation from a non-general source (reflection job, project sessions writing directly to runtime/.handoff/) will be silently skipped unless it uses the `general-*` prefix.

## Proposed fix

Attended session should update the tick prompt's handoff scan step to also check for any `URGENT-*` files in `runtime/.handoff/`, regardless of prefix. Proposed addition to step 1:

> Also check `ls /opt/workspace/runtime/.handoff/URGENT-* 2>/dev/null` — these are 3rd-cycle reflection escalations that require attended-session or principal action regardless of their project prefix.

This is a Tier B change (tick prompt is a playbook) — write a handoff proposing the change rather than editing directly.
