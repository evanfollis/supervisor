# FR-0050: Recurring stuck in intake/digest

Captured: 2026-09-14T07:02:41Z
Source: friction-classifier
Status: open
Fingerprint: `68e6167280aa359db87460b15f200891a518ba5018cd75d2e63fdf340435409a`
Window: 7 days
Count: 1
First seen: 2026-09-14T06:59:07Z
Last seen: 2026-09-14T06:59:07Z

## What happened

The deterministic Layer-5 classifier observed a promotable recurring class.

## Root cause / failure class

- Layer: `intake`
- Source: `digest`
- Event type: `stuck`
- Normalized reason: `<n> items cleared cutoff for agent-platforms <time>`

## Representative reasons

- 0 items cleared cutoff for agent-platforms 2026-09-14

## Source-event references

- `/opt/workspace/runtime/friction/events.jsonl` bytes 1823288-1823575 (line 5848, sha256:034f9cb00d85b91b38a4dd5979cbae4fc231cea297a2cd2966886169cc6910fc)

## Proposed fix

Pressure-test the recurring class through the normal supervisor friction and synthesis loop.
Do not infer resolution from this automated promotion alone.
