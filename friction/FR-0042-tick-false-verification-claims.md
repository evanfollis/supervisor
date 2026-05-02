---
id: FR-0042
title: Tick reports emit false "verified on disk" claims for ghost-writes
status: Open
created: 2026-05-02
updated: 2026-05-02
source: cross-cutting synthesis 2026-05-02T03:23:48Z; supervisor-reflection-2026-05-02T02:37:44Z
---

# FR-0042: False verification claims in tick reports

## What happened

Starting around 2026-05-02, supervisor tick sessions began explicitly claiming
post-write verification ("FR-0038/0039/0040 written — verified on disk: ls confirms")
for file writes that did not actually land on main. The verification step ran
inside the tick's branch, where the write had occurred locally, so `ls` returned
the expected result. From main's perspective, nothing changed.

This is strictly worse than silent ghost-writes because:
- A verified claim closes the carry-forward escalation gate
- The principal and future sessions read "verified" and stop tracking the item
- The actual file never gets written, but there is no visible signal

## Why it matters

The verification pattern (write → ls to confirm) is correct in principle, but
it only works if the verification checks the same branch that future sessions
will read. A tick branch that hasn't been merged is not main. The verification
is answering "did the write land in my local branch?" not "is this on main?"

## Fix direction

Verification must be cross-branch (check main's state after write), not
intra-branch. Until the tick branch infrastructure is fixed (see FR-0038):
tick sessions should not emit "verified on disk" claims — they should emit
"written to tick branch, pending merge" to avoid false confidence.
