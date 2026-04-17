# URGENT: INBOX item >40h — ADR-0015 review and S4-P3 shared primitive still open

**Written**: 2026-04-17T02:49Z (supervisor tick, age-check gate)
**Priority**: High — SLA breach, attended judgment required

## The aged item

`supervisor/handoffs/INBOX/2026-04-16T13-00Z-pending-supervisor-items.md` (written 2026-04-16T13:00Z, now ~40h old).

## Status of its 4 items

| Item | Status |
|------|--------|
| 1. S3-P1 — health escalation INBOX write | **DONE** — supervisor-tick.sh patched in bd5a854 |
| 2. S4-P3 — telemetry rotation shared primitive | **PARTIAL** — command shipped `scripts/rotate-telemetry.sh` (eb18e35) as a project-specific script; no shared workspace primitive or systemd timer |
| 3. ADR-0015 cross-agent review | **NOT DONE** — `/review` broken (EROFS); `codex exec` fallback untested |
| 4. Push supervisor remote | **DONE** — bd5a854 pushed to origin |

## What the attended session must do

1. **Archive the aged INBOX item** (it's been processed here; items 1 and 4 are done).
2. **ADR-0015 review**: now blocked on `/review` EROFS. See `URGENT-review-skill-broken-2026-04-17T02-49Z.md` — that URGENT covers this. Do not duplicate effort.
3. **S4-P3 shared primitive**: command's `rotate-telemetry.sh` needs to be moved or symlinked as a workspace-level script under `supervisor/scripts/lib/` with a matching systemd timer. This is a scripts/lib edit (Tier C for ticks) — attended session only.

## Reference

- Aged INBOX: `supervisor/handoffs/INBOX/2026-04-16T13-00Z-pending-supervisor-items.md`
- S4-P3 rotation script (project-specific): `command/scripts/rotate-telemetry.sh` (eb18e35)
- ADR-0015: `supervisor/decisions/0015-executive-supervisor-operator-split.md`
