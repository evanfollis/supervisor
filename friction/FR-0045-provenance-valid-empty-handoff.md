---
id: FR-0045
title: Provenance-valid handoff could publish without an operational body
class: substrate
first-observed: 2026-07-20
recurrences: 1
status: resolved
---

# FR-0045 — Provenance-valid empty handoff

Captured: 2026-07-20T09:50:00Z
Source: attended executive session
Status: resolved

## What happened

The executive used the canonical `write-handoff.sh` path to dispatch the
missing Synaplex friction classifier. The invocation omitted the body stream,
but the writer accepted and published a file containing only valid YAML
frontmatter. The Synaplex project session correctly refused to invent the
missing task and stopped before implementation.

## Why it matters

Provenance is necessary but not sufficient for an executable handoff. A
header-only artifact looks valid to the dispatcher while carrying no task,
acceptance criteria, or evidence contract. That turns an automated dispatch
into reverse-engineering work and can silently stall the diagnosis-to-execution
loop.

## Root cause / failure class

The canonical writer validated required provenance fields but did not validate
that stdin contained a non-whitespace operational body. Its schema gate
therefore protected authorship and authority while permitting an empty primary
object.

## Resolution

Commit `401598e` makes `write-handoff.sh` buffer and reject an empty body
before publication. The regression test proves an empty artifact leaves no
published file and a nonempty artifact remains valid. The malformed runtime
handoff was restored, revalidated, and explicitly re-dispatched.

## References

- `scripts/lib/write-handoff.sh`
- `tests/test-handoff-requirement-provenance.sh`
- `runtime/.handoff/synaplex-close-friction-promotion-loop-2026-07-20T09-46-37Z.md`
