---
type: URGENT
created: 2026-05-12T06:47Z
source: supervisor-tick-2026-05-12T06-47-55Z
priority: critical
root_cause: atlas-strategic-deadlock-principal-decision-overdue
ages_from: 2026-05-10T16:49Z
original_handoff: runtime/.handoff/general-atlas-s3p2-principal-decision-2026-05-10T16-49Z.md
---

# URGENT: Atlas principal decision handoff 43h overdue — FR-class breach

`general-atlas-s3p2-principal-decision-2026-05-10T16-49Z.md` was filed
2026-05-10T16:49Z (43h ago). The 24h dispatch obligation threshold was
crossed at 2026-05-11T16:49Z. Cycle-31 synthesis (03:23Z) confirmed this
as a governance breach. This URGENT is required by the dispatch obligation
rule in workspace CLAUDE.md.

## What's needed

A principal decision on atlas strategic direction. Choose one:

**Option A — Expand signal universe** (continues atlas)
- Re-admit 4h timeframe, add new asset classes, or commission new signal detectors
→ Dispatch to atlas session with specific expansion scope

**Option B — Explicit park** (principled pause)
- Record a decision in `supervisor/decisions/` with resume condition
→ No session work needed immediately

**Option C — Retire atlas pod**
- Update or supersede ADR-0023; archive atlas from reflection loop
→ Attended session needed to edit `scripts/lib/projects.conf`

## Current state

- Atlas: 218+ idle cycles (~9.1 days), `consecutive_empty_count: 148+`
- 7 hypotheses stuck in TESTING (orphaned, no re-evaluation path)
- 5 FORMULATED stuck (4h off-universe or insufficient bars)
- The atlas session correctly declined the S3-P2 re-arm proposal; this
  is now a principal-class decision, not a project-session decision

## Archive when resolved

Archive `general-atlas-s3p2-principal-decision-2026-05-10T16-49Z.md` and
`general-atlas-orphaned-testing-failure-mode-2026-05-02T14-26Z.md` after
principal makes a choice and work is dispatched.

Update `system/active-issues.md` under "Pending principal".
