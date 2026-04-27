---
id: FR-0039
title: Synthesis dispatch execution gap — INBOX is not execution
severity: HIGH
status: open
created: 2026-04-27
---

# FR-0039: Synthesis dispatch execution gap

## Pattern

The charter's 24h dispatch obligation is satisfied when synthesis proposals are
translated into INBOX handoffs. But "in INBOX" and "executed" are not the same
state. 0/8 synthesis proposals have landed across 2 consecutive synthesis cycles
(April 26 03:26Z and April 26 15:25Z syntheses). Each tick correctly defers
Tier-C edits to the attended session. No attended session has materialized to
execute them.

## Root cause

The dispatch obligation was designed to ensure attended-session attention within
24h. In practice, ticks satisfy the *letter* of the obligation by writing INBOX
files but cannot satisfy the *spirit* because Tier-C execution requires an
attended session. When no attended session opens within 24h, proposals cycle
indefinitely without landing.

The INBOX grows: 14 items as of this writing, 11 of which are Tier-C proposals.
The saturation suppression rule fires (correctly), suppressing new URGENT writes
for the same root cause. But suppression is a signal the queue is broken, not a
fix.

## Consequences

- Synthesis operates at high diagnostic quality but zero execution impact
- Carry-forwards accumulate (8 proposals, 2 cycles, 0 landed)
- The synthesis loop is becoming an instance of Pattern 2 (activity without epistemic advance) that it was designed to detect

## Fix direction

The dispatch obligation should require a positive signal from the attended session,
not just an INBOX write. Options:
- Charter amendment: dispatch obligation is not met until the attended session
  writes an explicit deferral or begins execution
- Monitoring: if a proposal sits in INBOX >48h with no attended-session interaction,
  escalate to principal rather than looping through ticks
