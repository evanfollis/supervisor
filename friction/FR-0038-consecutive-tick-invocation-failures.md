---
id: FR-0038
slug: consecutive-tick-invocation-failures
created: 2026-05-03T00:47Z
status: open
source: supervisor-tick-2026-05-03T00-47-24Z
---

# FR-0038: Consecutive headless tick invocation failures with intermittent recovery

## What happened

Two consecutive scheduled supervisor ticks failed immediately:
- `2026-05-02T20:47:49Z` — "tick claude invocation failed" (tick committed empty at sha=39594201b3fa)
- `2026-05-02T22:47:49Z` — "tick claude invocation failed" (tick committed empty at sha=66d7d050b5ba)

The subsequent tick at `2026-05-03T00:47:24Z` (this session) succeeded without any
operator intervention or credential rotation.

## Why this is friction

The intermittent pattern means:
1. Two 12h reflection cycles produced zero executive work (routing, escalation, grading)
2. The failure mode is not yet diagnosed — "invocation failed" is not specific enough
   to distinguish: network timeout, 401 auth, rate-limit, or harness startup failure
3. The tick wrapper emits a `session_reflected` event even on failure, providing false
   signal that the tick ran (the event says "failed" but the queue still moved)
4. The previous URGENT (FR-0039-headless-tick-401-auth-split.md) referenced a
   friction file that does not exist on disk — ghost-write pattern confirmed

## Connection to known patterns

- FR-0029 (ghost-FR claimed in events) documented the ghost-write pattern; the
  claimed FR-0039 through FR-0042 from May 2 ticks are confirmed non-existent
- URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md identified auth path divergence
  between reflection and tick invocations; this failure is consistent with that root cause

## Required fix

1. The tick wrapper script should capture and surface the specific failure reason
   (exit code, stderr first 200 chars) in both the event note and the tick report file
2. The current failure is likely context-dependent: the 20:47 and 22:47 ticks
   may have hit rate limits, not auth failures — needs diagnosis from the actual
   stderr of those invocations
3. If intermittent auth: rotate key or normalize credential path per FR-0039 root
