# FR-0049: Recurring escalated in intake/arxiv

Captured: 2026-09-08T05:02:03Z
Source: friction-classifier
Status: open
Fingerprint: `4e43d0b25ac67ba535f285cb40fdd230cae5f36d6083eb6350e008810c357f78`
Window: 7 days
Count: 1
First seen: 2026-09-08T04:18:44Z
Last seen: 2026-09-08T04:18:44Z

## What happened

The deterministic Layer-5 classifier observed a promotable recurring class.

## Root cause / failure class

- Layer: `intake`
- Source: `arxiv`
- Event type: `escalated`
- Normalized reason: `consecutive stuck count <n> crossed s3-p2 threshold`

## Representative reasons

- consecutive stuck count 3 crossed S3-P2 threshold

## Source-event references

- `/opt/workspace/runtime/friction/events.jsonl` bytes 1712685-1713000 (line 5532, sha256:089f7a579be365b0e3b8f6c22e3b59b3500452d1d83dda277cb4254b6fc3cb89)

## Proposed fix

Pressure-test the recurring class through the normal supervisor friction and synthesis loop.
Do not infer resolution from this automated promotion alone.
