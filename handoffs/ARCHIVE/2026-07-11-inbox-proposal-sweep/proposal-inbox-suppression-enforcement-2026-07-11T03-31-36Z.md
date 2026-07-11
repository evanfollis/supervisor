---
from: synthesis-translator
to: general
date: 2026-07-11T03:31:36Z
priority: high
task_id: synthesis-inbox-suppression-enforcement
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-11T03-27-25Z.md
source_proposal: P3a — INBOX suppression enforcement
---

# P3a — INBOX suppression enforcement

## Proposal

**Type:** Synthesis translator script amendment. Count existing INBOX items with same slug-prefix before depositing. Suppress if >=5. Log.

**Rationale:** When INBOX holds >5 unconsumed items sharing the same root cause, the synthesis job may suppress additional URGENT writes for that root cause (per CLAUDE.md "INBOX saturation exception"). This prevents noise from degrading the signal the queue carries. Current behavior may be writing duplicates silently.

**Blast radius:** Supervisor INBOX only.

## Verification before action (required)

- Check `/opt/workspace/supervisor/scripts/lib/synthesize.sh` or the synthesis-translator script for existing suppression logic (search for "slug" or "count" in the URGENT-emission path).
- If suppression logic is already wired, this proposal is landed — write a completion report and close.
- If the logic is absent or incomplete, proceed with the amendment.

## Acceptance criteria

- The synthesis translator (or synthesize.sh) checks existing INBOX files before writing a new URGENT.
- If >=5 items with the same slug-prefix exist and are unconsumed, the new URGENT is suppressed.
- Suppression is logged (written to the synthesis file or a log output) so the decision is visible.
- The log entry names the suppressed root cause and the count of existing items.
- Commit with message explaining the suppression gate (synthesis C137, P3a).
- Completion report at `runtime/.handoff/general-proposal-inbox-suppression-enforcement-complete-2026-07-11T03-31-36Z.md`.

## Escalation

None anticipated. If the INBOX structure or slug-generation logic is unclear, check existing INBOX files at `/opt/workspace/supervisor/handoffs/INBOX/` for naming patterns.
