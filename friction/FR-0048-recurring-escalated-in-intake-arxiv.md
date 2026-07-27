# FR-0048: Recurring escalated in intake/arxiv

Captured: 2026-07-27T05:01:33Z
Source: friction-classifier
Status: open
Fingerprint: `f02e2410a6d2b7f6146f23c6943319b22fa68d8b85363b1b825449a1960a9e68`
Window: 7 days
Count: 1
First seen: 2026-07-27T04:20:00Z
Last seen: 2026-07-27T04:20:00Z

## What happened

The deterministic Layer-5 classifier observed a promotable recurring class.

## Root cause / failure class

- Layer: `intake`
- Source: `arxiv`
- Event type: `escalated`
- Normalized reason: `consecutive stuck/failure count <n> crossed s3-p2 threshold`

## Representative reasons

- consecutive stuck/failure count 3 crossed S3-P2 threshold

## Source-event references

- `/opt/workspace/runtime/friction/events.jsonl` bytes 953490-953813 (line 3367, sha256:dd6e2ac516385ad14a5abd4c9b0d5e085261b7d37e98720ec4ce06dd334ab2cb)

## Proposed fix

Pressure-test the recurring class through the normal supervisor friction and synthesis loop.
Do not infer resolution from this automated promotion alone.
