# Supervisor event stream

Canonical append-only stream:
`/opt/workspace/runtime/.telemetry/supervisor-events.jsonl`

Immutable historical segments belong under
`/opt/workspace/runtime/.telemetry/archive/`. The event stream is empirical
runtime evidence, not governance source, and must not be written into Git.
