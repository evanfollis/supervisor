# ADR-0012: Relocate append-only logs from supervisor repo to runtime

Date: 2026-04-15
Status: accepted

## Context

Two surfaces inside the supervisor repo drift from the current-state-first
model articulated in `system/status.md`:

- `events/supervisor-events.jsonl` — append-only telemetry in the repo.
  Charter (`AGENT.md` §Event model) currently locates it here.
- `handoffs/ARCHIVE/YYYY-MM/` — resolved inbox items moved here by
  `AGENT.md` §Reentry step 3.

Both are logs. Logs belong under `/opt/workspace/runtime/.telemetry/` and
`/opt/workspace/runtime/.meta/` alongside reflections, syntheses, and
server-health snapshots. Keeping them in the governance repo:

1. Dilutes the working-context bundle.
2. Duplicates durability surface — git already captures every
   state-changing commit; the JSONL is a second copy.
3. Creates `archive vs. git history` ambiguity for handoff resolution.

## Decision

1. `events/supervisor-events.jsonl` → `/opt/workspace/runtime/.telemetry/supervisor-events.jsonl`.
   A one-line pointer file `system/events-pointer.md` stays in-repo so
   reentry still has one place to look.
2. `handoffs/ARCHIVE/` removed. Resolution is recorded by
   INBOX-delete commit + `handoff_received` event. Any historical
   content moves to `/opt/workspace/runtime/.meta/handoff-archive/`.
3. `AGENT.md` §Event model and §Reentry amended to reference the new
   locations.
4. All writers updated in one commit series:
   `scripts/slack/notifier.py`, `scripts/lib/idea-ledger.py`,
   `scripts/lib/workspace-paths.sh`, plus any reflect/synthesize hooks.

This is **accepted** (not proposed) because the principal explicitly
authorized ADR authority to the supervisor without per-decision approval
and the drift has stood across multiple synthesis cycles. Execution is
tracked as a separate task, not bundled here.

## Execution

Executed 2026-07-12. All live writers and readers now use runtime paths;
the installed SessionEnd hook writes directly to
`runtime/.meta/handoff-archive/`; and the historical Git-resident corpus was
checksum-verified after copying to runtime before its repository copies were
removed. ADR-0043 supersedes the original delete-on-resolution detail:
processed handoffs remain retained as empirical evidence, but only on the
cold runtime surface. Both event streams rotate into immutable compressed
segments without blocking writers.

## Consequences

- Working-context bundle shrinks.
- Single source of truth per telemetry stream.
- Handoff resolution is inspectable through git alone.
- Migration is reversible: paths are append-only, rollback is symmetric.

## Alternatives considered

- Leave both in-repo. Rejected: perpetuates the flagged drift.
- Move events but keep ARCHIVE. Rejected: splitting the fix muddies the
  model without reducing risk.
- Version-control runtime artifacts. Rejected: runtime is intentionally
  not tracked.
