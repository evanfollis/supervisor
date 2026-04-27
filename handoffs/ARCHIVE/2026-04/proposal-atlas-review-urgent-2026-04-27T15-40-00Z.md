---
from: synthesis-translator
to: general
date: 2026-04-27T15:40:00Z
priority: URGENT
task_id: synthesis-atlas-review-urgent
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-27T15-27-30Z.md
source_proposal: Proposal 1 [HIGH] — INBOX item for atlas runner.py adversarial review (URGENT-class)
---

# Atlas runner.py adversarial review (URGENT-class)

## Summary

The atlas reflection has been flagging `/review` debt on `runner.py:1086–1196` for 4 consecutive cycles — past the 3-cycle URGENT threshold. The code has had 2 bugs in 2 weeks. No existing INBOX item covers this specific review debt (URGENT-adr-review-gap covers supervisor ADRs, not project code reviews).

## Proposed action

Run adversarial review on atlas `runner.py:1086–1196` (escalation gate code, commits 90bd5fc, 34f4a83, ee9beaf).

**Command to execute (from workspace root or via atlas session):**

```bash
supervisor/scripts/lib/adversarial-review.sh src/atlas/runner.py:1086–1196
```

## Focus areas (per atlas reflection P1)

1. Edge cases in streak walk-back beyond the fixed drift
2. Behavior when max_events=200 truncates older escalation events
3. Concurrent runner process safety
4. State file seed inconsistency (last_emitted_ts at 07:30Z with no corresponding telemetry event)

## Evidence

- **4-cycle carry-forward**: atlas-reflection-2026-04-27T14-20-55Z flags this as 4th consecutive window (commits 90bd5fc, 34f4a83, ee9beaf)
- **2 bugs in 2 weeks**: 
  - `34f4a83` — original `streak_start_ts` walk-back bug
  - `ee9beaf` — midnight rotation bug
- **Pattern 2 in synthesis**: Adversarial review debt crosses URGENT threshold across 3 projects; atlas is the most specific call
- **Carry-forward escalation rule applied**: 3+ cycles → URGENT; this is the 4th

## Verification before action

- Confirm atlas session has current `runner.py` with the referenced commits
- Confirm `supervisor/scripts/lib/adversarial-review.sh` exists and is executable
- Review the code in the specified range (commits 90bd5fc, 34f4a83, ee9beaf context) to ensure the focus areas make sense

## Acceptance criteria

- Adversarial review runs via `adversarial-review.sh` (the workaround for EROFS-blocked `/review` skill)
- Review output captured or summarized
- If material issues are found, file them as project-session follow-up work (commits, improvements)
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-atlas-review-urgent-complete-<iso>.md` pointing back to this handoff with results summary

## Blast radius

Atlas project only. Requires either an attended atlas session or an attended general/operator session with access to the atlas repo.

## Rationale

The escalation-gate code controls a critical safety boundary for systematic trading (backpressure, hypothesis validation, evidence truncation). Two recent bugs in tight succession suggest latent complexity or insufficient vetting. A third bug is plausible. Adversarial review is the designed mechanism for catching these; it's overdue.
