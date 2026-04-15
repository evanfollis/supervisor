# FR-0003: Supervisor control plane had no remote for months

Captured: 2026-04-15
Source: session (principal asked "is GitHub up to date?")
Status: resolved (remote added + pushed 2026-04-15)

## What happened

The supervisor repo accumulated 30+ untracked files (ADRs, ideas,
skills, maintenance-agent manifests, systemd units, scripts for the
entire reflection/synthesis/server-health machinery) with no remote
configured. One disk failure on this Hetzner box would have taken the
full governance substrate. The condition went uncaught across every
reentry, including the ones that followed the documented reentry
checklist.

## Why it matters

The supervisor is the workspace control plane. Its durability is the
upper bound on the whole system's durability. A substrate with zero
redundancy is worse than one without a stated durability guarantee —
at least the latter is honest.

## Root cause / failure class

**Reentry routine has no durability checks.** The checklist in
`AGENT.md` §Reentry covers handoffs, synthesis pointers, health
status, and recent decisions. None of those detect: "is this repo
pushed somewhere I don't own?", "is the remote reachable?", or "are
there untracked files older than N days?" The blind spot extends to
every other durability condition too.

## Proposed fix

1. **`workspace.sh doctor` command** that runs on every session start
   and fails loud on durability-class issues (no remote, unpushed
   commits, large untracked-file count, notifier stalled, timers
   failing, secrets in tracked files).
2. **Reentry routine step 0**: run `doctor` before any other reentry
   work. Fail closed — broken durability surfaces to the top of the
   session, not the bottom.
3. **ADR amendment to AGENT.md** adding durability-verification as a
   named reentry responsibility.

## References

- 09987bd (commit that finally pushed everything)
- `config/slack.env` lives gitignored; reminder that secrets still
  live on this disk only.
