# FR-0001: `active-issues.md` drifted from repo reality

Captured: 2026-04-15
Source: session (2026-04-14/15 general)
Status: mitigated (swept + pruned); structural fix in progress

## What happened

On reentry I treated `system/active-issues.md` as an authoritative list
of open items. While processing the "highest-leverage self-alignment"
task, three of the listed items turned out to already be resolved in
the repo (`docs/README.md` retention rule, `projects/README.md`
retention rule, `sessions/README.md` retention rule). The surface was
stale.

## Why it matters

A current-state surface that lies is worse than no surface at all. It
causes the supervisor to spend work on solved problems and, more
importantly, lose trust in the rest of the file. If one item is stale,
are the others real?

## Root cause / failure class

**Hand-maintained state surfaces drift.** `active-issues.md` is
maintained by whoever last edited it; there is no loop that verifies
its claims against the repo on a cadence. The same failure class will
repeat for `active-ideas.md`, `projects/*.md`, and any other
narrative surface the supervisor maintains by hand.

## Proposed fix

1. **Auto-derive these surfaces from authoritative sources.**
   `active-ideas.md` should be generated from `ideas/*.json` status
   fields. `active-issues.md` should be generated from a combination
   of open ADRs, open handoffs, and explicit issue records. On every
   session start, regenerate and diff.
2. **Staleness audit as maintenance-agent.** The
   `analyze-recurring-friction` skill already exists — wire it into a
   job that scans the narrative surfaces for claims and flags the
   ones the repo no longer supports.
3. **Short-term**: every session end runs a sweep pass on
   `active-issues.md` to close anything handled.

## References

- `decisions/0012-runtime-vs-repo-state-location.md` — adjacent
  structural cleanup
- `system/active-issues.md` — the drifted surface itself (swept this
  session)
