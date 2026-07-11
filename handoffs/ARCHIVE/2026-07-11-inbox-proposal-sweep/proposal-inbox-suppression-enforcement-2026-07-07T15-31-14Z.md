---
from: synthesis-translator
to: general
date: 2026-07-07T15:31:14Z
priority: high
task_id: synthesis-p3a-inbox-suppress
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-07T15-27-01Z.md
source_proposal: P3a — INBOX suppression enforcement
---

# P3a: INBOX suppression enforcement

**Type:** Synthesis translator script amendment. Before depositing a new INBOX item, count existing items with the same slug-prefix. Suppress if ≥5. Log the suppression.

**Blast radius:** Supervisor INBOX only. Reduces per-cycle growth.

**Rationale:** C128 declared INBOX saturation exception: when INBOX holds >5 items sharing the same root cause, suppress additional UIs for that root cause and record in the synthesis file. This proposal hardens that gate into the synthesis-translator job so it's enforced automatically and consistently.

## Verification before action (required)

- Check `supervisor/scripts/lib/synthesis-translator.sh` (or equivalent). Determine where it deposits INBOX files.
- Verify the slug-prefix matching logic and how to extract it from handoff titles.
- Confirm current INBOX state at `/opt/workspace/supervisor/handoffs/INBOX/` — understand what constitutes a "same root cause" cluster.

## Acceptance criteria

- Synthesis translator counts existing INBOX files with matching slug-prefix before creating a new one.
- If count ≥5, it suppresses the new INBOX file and logs the suppression in a `synthesis-suppression-log.jsonl` file at `/opt/workspace/runtime/.meta/synthesis-suppression-log.jsonl`.
- Log format: `{ timestamp, suppressedProposal, rootCause, existingCount, reason }`.
- Change committed with message: "Enforce INBOX suppression gate in synthesis translator — cap same-root-cause items at 5"
- Completion report at `/opt/workspace/supervisor/handoffs/general-p3a-inbox-suppress-complete-<iso>.md`.

## Escalation

URGENT if:
- The slug-prefix extraction is ambiguous (clarify the root-cause grouping key).
- Suppression prevents legitimate distinct proposals from being recorded (refine the grouping logic).
