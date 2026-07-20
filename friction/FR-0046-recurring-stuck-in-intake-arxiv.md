# FR-0046: Recurring stuck in intake/arxiv

Captured: 2026-07-20T10:08:19Z
Source: friction-classifier
Status: open
Fingerprint: `a8bbb631aeb1cdd3b06e9560a8c8a70a7a90e57bd60bfb6b0051ac9db80f6807`
Window: 7 days
Count: 4
First seen: 2026-07-13T20:19:00Z
Last seen: 2026-07-20T00:18:21Z

## What happened

The deterministic Layer-5 classifier observed a promotable recurring class.

## Root cause / failure class

- Layer: `intake`
- Source: `arxiv`
- Event type: `stuck`
- Normalized reason: `no arxiv items in 3d window (preserved <n> from prior runs)`

## Representative reasons

- no arxiv items in 3d window (preserved 100 from prior runs)
- no arxiv items in 3d window (preserved 0 from prior runs)
- no arxiv items in 3d window (preserved 89 from prior runs)
- no arxiv items in 3d window (preserved 67 from prior runs)

## Source-event references

- `/opt/workspace/runtime/friction/events.jsonl` bytes 781433-781714 (line 2836, sha256:2e758d1c82b4bde08c6ba488cc2a2ba3010f95bc143989f5a100c24ccd1f68e0)
- `/opt/workspace/runtime/friction/events.jsonl` bytes 782556-782835 (line 2840, sha256:31b873b46e56802e379147372d4949331a9a7eb4f3d332488654dae29a06e11b)
- `/opt/workspace/runtime/friction/events.jsonl` bytes 828059-828340 (line 3006, sha256:98f43bb8d8a21553a4e2b7b6b20ae6347bf84a88b92f1cd738152ac6268b44ea)
- `/opt/workspace/runtime/friction/events.jsonl` bytes 829182-829461 (line 3010, sha256:a1cd8ecb2969677c484314c9eee9aa8b5d13c601956f99835957e19d331ccffa)

## Proposed fix

Pressure-test the recurring class through the normal supervisor friction and synthesis loop.
Do not infer resolution from this automated promotion alone.
