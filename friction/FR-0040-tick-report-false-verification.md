---
id: FR-0040
slug: tick-report-false-verification
status: open
created: 2026-05-02
discovered-by: supervisor-tick-2026-05-02T12-49-17Z
---

# FR-0040: Tick reports claim file writes as "verified on disk" when writes failed

## Symptom

Supervisor ticks repeatedly emit events and write reports claiming that files
were "written and verified on disk" (FR records, active-issues.md updates,
etc.) when those files do not actually exist on disk. Example: ticks from
2026-04-25 through 2026-05-02 claimed FR-0038 through FR-0042 were written;
`ls friction/` confirmed only FR-0037 existed — a gap of 8+ files claimed
but not written across 10+ tick cycles.

## Impact

Event stream is corrupted: `supervisor-events.jsonl` contains successful-write
claims that are false. Downstream synthesis and supervisor sessions base
diagnosis on the claimed state and fail to re-file the missing records.
The INBOX grows with proposals to fix a problem that existing records claim
is already addressed.

## Root cause

Headless tick sessions (systemd-spawned, or running with `--dangerously-skip-permissions`)
may write to a shadow filesystem path that is discarded after the session exits,
OR the Write tool call appears to succeed inside the session but the file is
written to a transient worktree that is never committed. The session reports
success based on the tool call return value, not based on an independent
verification.

## Fix required

Proposal `proposal-post-action-state-verify-2026-05-02T15-31-58Z.md` in INBOX
describes a wrapper-level verification step: after the tick session exits,
the wrapper script should check each claimed write by path and emit a
`ghost_write_detected` event if the file is missing.
