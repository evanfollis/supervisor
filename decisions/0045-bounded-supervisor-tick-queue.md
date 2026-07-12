# ADR-0045: Bounded supervisor tick queue

Date: 2026-07-12
Status: accepted
Supersedes: the branch-lifecycle and push provisions of ADR-0014 only

## Context

ADR-0014 correctly kept unattended commits off `main`, but its hourly
`ticks/<date>-<hour>` branches and push behavior created an unbounded review
queue. The accumulated refs were not consumed reliably and remote copies
made the queue harder to reason about.

## Decision

The supervisor tick has one bounded durable queue slot: `refs/heads/ticks/pending`.

- Before interlocks complete or the headless model starts, the wrapper checks
  every local `refs/heads/ticks/*` ref. Any existing ref causes a clean runtime
  skip report and `session_reflected` event with the blocking count and refs.
- With no tick ref, the wrapper reserves `ticks/pending` using non-forcing
  branch creation. A race or existing ref fails closed.
- Tier-A work is committed locally to `ticks/pending`; `main` is restored to
  its captured SHA. The wrapper never pushes tick refs.
- A run with no tracked work releases the empty pending slot. A run with a
  commit leaves the slot for attended review.
- Reentry must review `ticks/pending`, record promotion, refusal, or no-useful-
  work evidence, and then delete the ref. Historical refs are retained in
  runtime cold storage and are not merged wholesale or blindly cherry-picked.
- Doctor is healthy at zero refs, reports one pending ref with age and tip,
  warns after 24 hours, fails after 72 hours, and fails immediately for
  multiple or unexpected local refs. Remote-tracking refs are reported as
  drift after fetch/prune.

This decision intentionally preserves the tick's routing, telemetry, and
reflection capabilities. A runtime-only mode was considered but rejected for
now because it would remove the existing governance-artifact routing path;
the bounded queue removes the recurrence class with a smaller behavioral
change.

## Supersession boundary

This ADR supersedes ADR-0014 §Push discipline's per-run branch naming,
attended merge/delete workflow, and any permission to push a tick branch. It
also supersedes the corresponding per-branch age checks and reentry examples.
ADR-0014's cadence, interlocks, writable-surface tiers, project boundary,
and no-write-to-`main` invariant remain in force.

## Consequences

The queue can hold at most one unreviewed tick commit, so backpressure is
visible and bounded. If attended review is absent, future ticks skip rather
than silently accumulating or overwriting work. The cold archive and
machine-readable reconciliation inventory preserve the abandoned corpus
without keeping it in the active ref namespace.
