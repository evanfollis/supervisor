---
from: synthesis-translator
to: general
date: 2026-06-17T15:30:11Z
priority: medium
task_id: synthesis-translator-idempotent
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-17T15-26-36Z.md
source_proposal: Proposal 4 — P-synthesis-translator-idempotent (carry from C101 — 4th cycle, PAST >3-CYCLE FLAG)
---

# P-synthesis-translator-idempotent (Workspace process hygiene)

**Type:** Shared primitive fix.
**File:** `supervisor/scripts/lib/synthesis-translator.sh`
**Change:** Add slug-existence check before deposit.
**Blast radius:** Supervisor only. Low risk.
**Status:** Carried 4 cycles. Past 3-cycle flag.

The synthesis-translator script (the same script running now to emit these handoffs) should check whether a handoff file with the same slug already exists before depositing a new one. If a synthesis is re-run and the translator runs again, it would re-emit all the same handoffs with the same timestamp and slug, creating duplicates.

The fix is a simple existence check: if `proposal-<slug>-<timestamp>.md` already exists in the target directory, skip deposit and log "already exists."

## Verification before action (required)

- Read `supervisor/scripts/lib/synthesis-translator.sh` and check if a slug-existence check is already implemented.
- Look for patterns like `[ -f ... ] &&` or `if ... exists` before writing handoff files.
- If the check is present, write a completion report "already in place" rather than re-implementing.

## Acceptance criteria

- The synthesis-translator script checks if the target handoff file already exists (by slug + timestamp).
- If it exists, the script skips deposit and logs a message (does not error, just skips).
- Change committed with message: "Make synthesis-translator idempotent: skip if slug already exists"
- No adversarial review required (conditional skip, low complexity).
- Completion report at `runtime/.handoff/general-supervisor-synthesis-translator-idempotent-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Verification reveals the check is already implemented. Write "already in place" completion report and close.
- The script is running under a newer framework that already handles dedup at a higher level. Do not force-apply; escalate with the new framework detail.

---

**Pattern context:** This is a workspace process hygiene fix to prevent duplicate handoffs from re-runs of the synthesis-translator (this tool). It's a defensive measure that prevents noise in the INBOX when synthesis is re-invoked with the same findings.
