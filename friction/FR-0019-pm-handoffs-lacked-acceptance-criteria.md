# FR-0019: PM handoffs lacked acceptance criteria — PMs stalled or produced wrong artifacts

**Observed**: 2026-04-16  
**Source**: command session handoff archaeology

## What happened

Over 4+ reflection cycles, the command PM received handoffs like:
- "command-fix-broken-executive-conversation" — describes what was broken, no acceptance criteria
- "command-acknowledge-executive-surface-gap" — describes a gap, no deliverable shape
- "command-pressure-git-bootstrap-and-review-enforcement" — pressure without spec

These handoffs sat unresolved for days. When they were acted on (the executive conversation fix), the PM reported a partial implementation (build passing, service not deployed) and the executive never closed the loop.

## Root cause

Executive handoffs to PMs described the problem but not the deliverable. A capable PM receiving "this is broken" without "ship when these criteria pass" will either:
1. Stall — unclear what done looks like
2. Implement a partial solution that looks complete from the inside but doesn't satisfy the principal

## Policy correction

**Handoffs to project PMs must include:**
1. `task_id` — so the PM can report back and the executive can recognize it
2. Acceptance criteria (numbered, testable) — not "fix X" but "smoke test passes AND Y returns Z"
3. Non-goals — explicitly what is out of scope
4. Escalation conditions — when to stop and ask instead of guess
5. Deliverable format — what the PM should report back and where

**Executive must also close the loop:** When a PM reports back via handoff, the executive must acknowledge receipt within one tick cycle (2h). Unacknowledged completions are as bad as unactioned requests — the PM has no signal that the work landed.

## How to apply

When writing a handoff to a project PM session:
- Lead with the intent (why, not just what)
- Number the acceptance criteria — if you can't number them, the spec isn't complete
- Explicitly list non-goals (prevents scope creep and over-engineering)
- Provide escalation conditions (where the PM should stop and ask rather than guess)
- After the PM reports back, write a `handoff_received` event and delete the handoff file

If the handoff is longer than 80 lines, the spec probably needs to be broken up or an intermediate ADR is needed.
