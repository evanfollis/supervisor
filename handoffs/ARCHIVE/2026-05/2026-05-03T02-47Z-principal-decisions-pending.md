---
type: principal-summary
created: 2026-05-03T02:47Z
source: supervisor-tick-2026-05-03T02-47-25Z
priority: high
---

# Principal decisions pending — 2026-05-03

Four items require principal action. Listed in order of urgency.

---

## 1. Atlas runner restart (operator, 1 command)

`sudo systemctl restart atlas-runner.service`

**Why now**: P1 (TESTING orphan re-evaluation, commit `71224e9`) is in `main` but the service
was last restarted at 14:25Z May 2 before P1 landed. After restart, 7 orphaned TESTING
hypotheses with expired freshness are immediately re-evaluated — this is what restarts the
scientific output loop. The S3-P2 counter gate (39b6d2f) is already deployed and verified
firing. Evidence: `cycle.escalated consecutive_cycles=3` in telemetry confirms frozen loop.

---

## 2. Synaplex cap policy (principal, 5 min)

**Recommendation: Option C** — ratify per-fetch semantic, amend ADR-0029 §6 wording. Zero
code change. This closes the doc/code divergence and ends the 4-cycle carry-forward loop.

ADR-0029 §6 says "max 200 per source per day"; implementation does "max 200 per fetch" with
union accumulation. HN now reaches ~400/day. No data corruption. Layer 2 will filter anyway.

Secondary: the score cron runs 12× per day but intake only runs 3× — 9 of 12 runs re-score
an unchanged corpus. With heuristic scoring this is free; with Sonnet scoring (when API key
lands) this is ~9 wasted API calls/day. May want to align cron cadence to intake cadence.

If C: amend `decisions/0029-*.md` §6 directly (Tier-A write). INBOX: `URGENT-synaplex-cap-policy-3rd-cycle-2026-05-01T14-42Z.md`.

---

## 3. LCI outreach decision (principal, 5 min)

10 outreach drafts at `drafted` status since 2026-04-11 (22+ days). The LCI commercial
assumption has zero external evidence. Three options:

A. **Unblock**: decide Tally form questions + outreach channel → foundry sends 10 drafted messages
B. **Park explicitly**: record ADR in `decisions/`, update researcher CURRENT_STATE.md
C. **Kill**: mark LCI as deprioritized; remove from active tracking

Without a decision, reflection will continue escalating every 12h. INBOX: `URGENT-lci-outreach-blocked-22-days-2026-05-02.md`.

---

## 4. Tier-B-auto authority for workspace infrastructure (principal, 10 min)

11 synthesis cycles have produced 19 proposals, 0 implemented. The reflect.sh Write-bypass
fix (add `"Write"` to one disallowedTools list) has been proposed in 7 cycles, filed in INBOX,
and consumed by the general tick session — but never applied, because `scripts/lib/` is Tier-C
from all autonomous sessions.

**Proposed**: Approve "Tier-B-auto" classification for changes to `scripts/lib/` that are:
additive only, proposed in 2+ synthesis cycles, modify only workspace infrastructure, require
no ADR. Such changes could be applied by attended tick sessions without confirmation.

Immediate unlocks: reflect.sh Write fix (FR-0040), synthesize.sh size gate (FR-0038 class),
synthesis-translator dedup gate, tick post-action state verification.

If approved: one-line CLAUDE.md amendment to the Boundaries section, or an ADR accepting
this classification. INBOX: `proposal-tier-b-auto-authority-2026-05-02T18-50Z.md`.

---

## Background: what worked this tick

- FR-0038 through FR-0042 confirmed written to disk for the first time (ghost-write pattern
  was specific to headless `claude -p` invocations, not attended sessions).
- INBOX down from 50 → 30 items (superseded proposal duplicates archived).
- All 8 project reflections current (all <1h old).
- Atlas P1 verified implemented; skillfoundry migrate telemetry landed (commit `531946f`).
- 401 auth recovered (URGENT archived; ticks running since 2026-05-03T00:47Z).
