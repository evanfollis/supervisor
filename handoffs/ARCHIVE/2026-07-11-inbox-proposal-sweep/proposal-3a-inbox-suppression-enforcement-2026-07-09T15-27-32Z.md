---
from: synthesis-translator
to: general
date: 2026-07-09T15:27:32Z
priority: high
task_id: synthesis-inbox-suppression-enforcement
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-09T15-23-51Z.md
source_proposal: P3a — INBOX suppression enforcement
---

# P3a — INBOX suppression enforcement

**Type:** Synthesis translator script amendment. Before depositing a new INBOX item, count existing items with the same slug-prefix. Suppress if ≥5. Log the suppression.

**Rationale:** INBOX at 303 and growing ~16/day. CLAUDE.md policy stated but unimplemented.

**Blast radius:** Supervisor INBOX only. Reduces per-cycle growth. Does not address existing 303-item backlog.

## Verification before action (required)

- Locate the synthesis translator script (likely `/opt/workspace/supervisor/scripts/lib/translate-synthesis.sh` or similar).
- Check if suppression logic already exists (grep for slug-prefix dedup or suppression patterns).
- If already implemented, write a completion report stating "already landed — verified in-code" rather than re-applying.

## Acceptance criteria

- The synthesis translator script is amended to:
  1. Count existing items in `/opt/workspace/supervisor/handoffs/INBOX/` with the same slug-prefix.
  2. Suppress new INBOX items if ≥5 with the same slug-prefix already exist.
  3. Log suppressions to a suppression ledger or telemetry.
- Change committed with message: "Implement INBOX suppression enforcement per synthesis C134"
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` (dedup logic must be correct; off-by-one in counting is a common error).
- Completion report at `/opt/workspace/runtime/.handoff/general-synthesis-inbox-suppression-complete-<iso>.md` pointing back to this handoff and source synthesis.

## Escalation

URGENT if:
- Translator script cannot be located. Escalate with file path needed.
- The dedup slug-prefix logic is ambiguous (what counts as a "match"?). Clarify before implementing.
- The proposal requires a new telemetry schema or ledger location. Note the location and coordinate with supervisor telemetry.
