# Handoff — pending supervisor infrastructure items (2026-04-16T13:00Z)

## Context

The 12:48Z unattended tick is routing three carry-forward items from the S4 synthesis
and prior attended session that require attended-session action (scripts/lib changes, ADR
acceptance, git push). Collected here so they don't scatter across the next session start.

## Items

### 1. S3-P1 — Health escalation handoff trigger (supervisor-tick.sh)

**Status**: Accepted in dispositions (`/opt/workspace/runtime/.meta/dispositions.jsonl`),
not yet implemented.

**What**: `supervisor-tick.sh` should detect when consecutive skips have the reason
`supervisor working tree was dirty` (distinct from the session-active skip) and after
≥ 3 create an INBOX handoff to the attended session rather than just emitting an
`escalated` event. The escalated event is invisible when nobody is watching the event
log; the INBOX handoff persists visibly.

**File to edit**: `/opt/workspace/supervisor/scripts/lib/supervisor-tick.sh`

**Acceptance**: INBOX handoff appears within 3 dirty-tree consecutive skips during a
test run.

### 2. S4-P3 — Telemetry rotation script

**Status**: Accepted in dispositions, not yet implemented.

**What**: `events.jsonl` and `session-trace.jsonl` have no rotation logic. As the
workspace runs for months these files will grow without bound. The S4 synthesis
proposed a cron-driven rotation script (compress files > N MB, keep 30 days, emit
`telemetry_rotated` event).

**Location**: add to `scripts/lib/` with matching systemd timer under `systemd/`.

**Acceptance**: `workspace.sh doctor` stops seeing unbounded growth on rotation check
(once added to doctor).

### 3. ADR-0015 cross-agent review — still owed

**Status**: Acknowledged in 2+ session cycles, not yet done.

**What**: ADR-0015 requires cross-agent adversarial review before it can be flipped to
`accepted`. The session repeatedly noted it owed this but did not complete it.

**Action**: Route the ADR-0015 draft to Codex via `codex exec --skip-git-repo-check
--sandbox read-only "<review prompt>"`. Record the finding. If clean, flip to accepted.
If not, open a friction record.

### 4. Push supervisor remote

**Status**: Doctor warns 3 commits ahead of `origin/main` as of 12:48Z tick.

**Action**: `git push` in `/opt/workspace/supervisor` before detaching.

## Reference

- Dispositions: `/opt/workspace/runtime/.meta/dispositions.jsonl`
- FR-0020: supervisor remote drift
- ADR-0015: (path: `/opt/workspace/supervisor/decisions/`)
