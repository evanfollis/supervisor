# FR-0047: Recurring failure in intake/arxiv

Captured: 2026-07-26T17:03:13Z
Source: friction-classifier
Status: open
Fingerprint: `4e3ec8fbc8edc15b03759ecd7179bf5d78b9fe126b2eb8a3a38ea62b91aa2cfe`
Window: 7 days
Count: 3
First seen: 2026-07-23T16:18:47Z
Last seen: 2026-07-26T16:19:10Z

## What happened

The deterministic Layer-5 classifier observed a promotable recurring class.

## Root cause / failure class

- Layer: `intake`
- Source: `arxiv`
- Event type: `failure`
- Normalized reason: `fetch failed: timeouterror: the read operation timed out`

## Representative reasons

- fetch failed: TimeoutError: The read operation timed out

## Source-event references

- `/opt/workspace/runtime/friction/events.jsonl` bytes 891741-892021 (line 3191, sha256:59af4b648674864160cd5c74660cb007939162e3e64be239db3708fa9d045cf6)
- `/opt/workspace/runtime/friction/events.jsonl` bytes 909317-909597 (line 3241, sha256:c73454a786ec8e91c21a7f08c8bc10df14d43b1d7d2508b346d3d0006b852d3a)
- `/opt/workspace/runtime/friction/events.jsonl` bytes 944691-944971 (line 3342, sha256:679c2269282fa6b9ece7e7b2f5290dd541f430d873eb9eb00fcb59a6f76ac31f)

## Proposed fix

Pressure-test the recurring class through the normal supervisor friction and synthesis loop.
Do not infer resolution from this automated promotion alone.
