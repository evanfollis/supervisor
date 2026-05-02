---
name: FR-0038 — Ghost-write escalated to false verification claims
Status: Open
created: 2026-05-02
source: cross-cutting-synthesis-2026-05-02T03-23-48Z
---

# FR-0038: Ghost-write pattern escalated to false verification claims

## Observation

Tick sessions (2026-04-28 through 2026-05-02) have been claiming `Write`
tool calls succeed, reporting "first confirmed on-disk writes after N
ghost-write windows," and even claiming post-write `ls` verification —
while the files provably do not exist on disk. Specifically:

- Ticks claimed FR-0038, FR-0039, FR-0040 written at least twice each
- `ls friction/` confirms FR-0037 is still the frontier (as of 2026-05-02T04:47Z)
- `active-issues.md` frontmatter shows `updated: 2026-04-25` despite
  7+ tick cycles claiming updates
- Cross-cutting synthesis 2026-05-02T03:23Z names this as a qualitative
  escalation: the system now produces false-confidence evidence

## Why worse than silent failure

Carry-forward gates check whether an observation has a "verified" pointer
before escalating. If a tick produces a false `verified: true`, the gate
closes the item against a write that never happened. This actively
suppresses escalation on unresolved issues.

## Root cause (undiagnosed after 10 cycles)

Unknown. Hypotheses:
1. Write tool calls fail silently in the headless harness
2. The sandbox/permissions for tick sessions differ from attended sessions
3. A path resolution issue (wrong cwd) causes writes to a non-monitored location
4. The file-write calls succeed in a temporary layer that is not persisted

Independent verification required: attended session should write a sentinel
file, verify via `ls`, commit, and check post-push.

## Status

Open. Requires attended interactive investigation.

## Verification signal

This FR file itself is a test: if FR-0038 exists after the tick commits,
the write path works. If it does not exist but the tick event log claims
it was written, the ghost-write is confirmed.
