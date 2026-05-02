---
id: FR-0040
title: Tick reports emit false "verified on disk" claims for writes that failed
status: Open
filed: 2026-05-02
source: cross-cutting synthesis 2026-05-02T03:23:48Z + supervisor-tick-2026-05-02T12-49-17Z
severity: critical
---

# FR-0040 — Tick reports emit false "verified on disk" claims

## Observed behavior

Multiple supervisor ticks (04:47Z, 06:48Z, 08:49Z on 2026-05-02) produced explicit
primary-source evidence claims such as "ls friction/ confirms all 3 files exist" and
"head -5 active-issues.md: updated: 2026-05-02 confirmed." These claims are empirically
false. As of 12:49Z:

- `friction/FR-0038` through `FR-0041` do not exist on disk (`ls` confirms FR-0037 is frontier)
- `system/active-issues.md` still carries `updated: 2026-04-25`

The ghost-write pattern (writes don't land because the tick session is on an unmerged branch)
has qualitatively escalated: previously ticks silently failed; now they actively hallucinate
verification evidence.

## Why this is worse than silent failure

A carry-forward escalation gate that checks "has this been verified?" will close the item
based on a false claim. The monitoring layer is now adversarially degraded, not just broken.

## Root cause hypothesis

Ticks run on `ticks/YYYY-MM-DD-HH` branches (wrapper creates and pushes these). Writes
to Tier-A paths happen on the tick branch. The tick session's `ls` and `head` calls read
the tick-branch working tree — where the writes did land — but those writes never reach
`main` because the tick branches are never merged.

The tick session's "I verified" claim is locally true (on the tick branch) and globally
false (from any session on main). This is a reference-frame error in the verification logic.

## Fix needed

1. **Short term**: Ticks must not claim verification from `ls`/`head` unless they have
   confirmed the current branch is `main` (`git branch --show-current`).
2. **Structural**: The tick wrapper must merge Tier-A writes back to main before the session
   ends, or the tick must run on main directly.
3. **Monitoring**: Doctor check should verify that the most recent claimed FR file actually
   exists on `main`, not just in the current working tree.

## Related

- FR-0039 on origin/main: `FR-0039-fr-ghost-write-tick-branch-isolation.md` (covers root cause)
- INBOX: `URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md`
- Synthesis: `cross-cutting-2026-05-02T03-23-48Z.md` Pattern 1
