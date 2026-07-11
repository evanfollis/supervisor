---
type: URGENT
created: 2026-05-14T04:49Z
source: supervisor-tick-2026-05-14T04-49-09Z
priority: high
root_cause: tier-c-proposals-unconsumed-over-24h
aged_items:
  - proposal-dead-letter-close-mechanism-2026-05-13T03-31-49Z.md (25h)
  - proposal-infrastructure-handoff-priority-signal-2026-05-13T03-31-49Z.md (25h)
  - proposal-synthesis-carry-forward-acknowledgment-rule-2026-05-13T03-31-49Z.md (25h)
---

# URGENT: 3 synthesis proposals >24h in INBOX — Tier-C attended action needed

Three proposals filed 2026-05-13T03:31Z (now 25h+ old) require attended-session action on Tier-C surfaces (CLAUDE.md charter or scripts/lib/). Ticks cannot consume them.

## Aged proposals requiring attended action

### 1. Dead-letter close mechanism (CLAUDE.md amendment)
`proposal-dead-letter-close-mechanism-2026-05-13T03-31-49Z.md`
- Add carry-forward force-close rule to `/opt/workspace/CLAUDE.md` § Quality: Radical Truth
- 5-cycle source; command and context-repo carry-forwards driving the proposal

### 2. Infrastructure handoff priority signal (CLAUDE.md amendment)
`proposal-infrastructure-handoff-priority-signal-2026-05-13T03-31-49Z.md`
- Add ordering constraint to executive reentry: infrastructure-repair handoffs >24h float to top
- Addresses 0-of-7 infrastructure handoffs consumed vs 4-of-4 product handoffs (empirical)

### 3. Synthesis carry-forward acknowledgment rule (synthesize-prompt.md edit)
`proposal-synthesis-carry-forward-acknowledgment-rule-2026-05-13T03-31-49Z.md`
- Add "Standing proposals" section to `/opt/workspace/supervisor/scripts/lib/synthesize-prompt.md`
- Prevents synthesis from restating same top-3 proposals every cycle without new evidence

## How to consume

Open an attended session at `/opt/workspace` and process each INBOX file per its
Verification + Acceptance criteria. Each proposal includes pre-flight verification steps.

## Archive when resolved

- Archive each proposal file to `handoffs/ARCHIVE/2026-05/`
- Update `system/active-issues.md` to reflect resolved items
- Archive this URGENT file
