---
id: FR-0030
title: Supervisor repo drifts ahead of remote without push
date: 2026-04-16
severity: low
status: resolved
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

## Resolution (2026-07-12)

`scripts/lib/remote-durability.sh` now audits every Git repository in the
managed workspace, publishes only strict fast-forwards from `main` to
`origin/main`, screens the committed range for high-signal credential patterns,
and verifies the remote SHA after every push. A 15-minute systemd timer runs the
repair path without staging or otherwise touching working-tree changes.

`workspace.sh doctor` now fails when any managed repository is ahead, behind,
diverged, ambiguously configured, or unreachable. Every result is appended to
structured runtime telemetry with local/remote heads and publication state.

## Evidence

- `workspace.sh doctor` output 2026-04-16T12:48Z: `⚠ branch 'main' is 3 commit(s) ahead of origin/main`
- Prior ticks also showed warning but no automated remediation

**Status**: Resolved — closure no longer depends on an attended reminder.
