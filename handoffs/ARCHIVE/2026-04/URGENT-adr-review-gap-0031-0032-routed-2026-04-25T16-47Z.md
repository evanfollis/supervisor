---
priority: urgent
created: 2026-04-25T16:47Z
source: runtime/.handoff/URGENT-adr-review-gap-0031-0032.md
routed-by: supervisor-tick-2026-04-25T16-47-24Z
---

# URGENT — ADR-0031 and ADR-0032 missing cross-agent review artifacts

Routed from `runtime/.handoff/URGENT-adr-review-gap-0031-0032.md` (created by synthesis-translator 2026-04-25T15:42Z).

## Status

- ADR-0031: 5 reflection windows without cross-agent review (threshold: 3)
- ADR-0032: 3 reflection windows without cross-agent review (threshold: 3)
- FR-0025 resolution (automated URGENT after 3 cycles) never fired mechanically — the check was aspirational, not wired.

## Action required

Attended session must:
1. Read `supervisor/decisions/0031-*.md` and `supervisor/decisions/0032-*.md`.
2. Write `.reviews/adr-0031-<iso>.md` and `.reviews/adr-0032-<iso>.md` with adversarial review findings.
3. Emit `decision_recorded` events for each.

If either ADR is no longer sound, supersede it with a new ADR rather than just reviewing it.

## Note

The workspace-doctor ADR-review-check proposal in INBOX (proposal-workspace-doctor-adr-review-check-2026-04-25T15-42-22Z.md) would automate detection of this going forward — consider implementing it in the same attended session.
