---
id: FR-0030
title: Supervisor repo drifts ahead of remote without push
date: 2026-04-16
severity: low
status: open
---

## Observed

`workspace.sh doctor` consistently warns: "branch 'main' is N commit(s) ahead of
origin/main (unpushed work)". As of 2026-04-16T12:48Z tick, 3 commits are
unpushed including S3-P3 autocommit implementation and FR-0019.

## Why it matters

The remote is the durability backstop for the supervisor repo. Unpushed commits
mean a host failure or accidental repo reset loses governance artifacts. The
durability check in `doctor` exists precisely to catch this, but the gap between
"caught" and "resolved" is still the attended session manually running `git push`.

## Root cause

The wrapper blocks unattended push (intentional security constraint). The
attended session sometimes forgets to push before detaching, especially at
session end after a long run.

## Proposed remediation

Add a reminder at session-end (in the next attended session's INBOX handoff) to
push. Consider whether `workspace.sh doctor` should emit a stricter FAIL (vs.
WARN) after 24h of drift, so the escalation path is more automatic.

## Evidence

- `workspace.sh doctor` output 2026-04-16T12:48Z: `⚠ branch 'main' is 3 commit(s) ahead of origin/main`
- Prior ticks also showed warning but no automated remediation

**Status**: Open — renamed from FR-0020 collision on 2026-04-18; no fix yet for unpushed-commits reminder gap.
