---
from: synthesis-translator
to: general
date: 2026-07-10T03:27:28Z
priority: medium
task_id: synthesis-p3a-inbox-suppression
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-10T03-23-34Z.md
source_proposal: P3a (CARRY — C126, 10th cycle) — INBOX suppression enforcement
---

# P3a: INBOX suppression enforcement

**Type:** Synthesis translator script amendment. Count existing INBOX items with same slug-prefix before depositing. Suppress if >=5. Log.

**Blast radius:** Supervisor INBOX only.

## Rationale

INBOX saturation exception (ADR-0021 amendment): When INBOX holds >5 unconsumed items sharing the same root cause, the synthesis job may suppress additional URGENT writes for that root cause and record the suppression in the synthesis file itself. This amendment extends that pattern to the synthesis-translator script itself — dedup before emitting INBOX files.

## Verification before action (required)

- Locate the synthesis translator script (likely `/opt/workspace/supervisor/scripts/lib/synthesis-translator.sh` or similar)
- Check if suppression logic already exists (grep for "slug-prefix" or similar dedup pattern)
- If already implemented, write a completion report stating "already landed"

## Acceptance criteria

- Synthesis translator script amended to count existing INBOX items by slug-prefix before creating a new one
- If >=5 items with the same prefix exist, suppress and log the suppression (do not create handoff)
- Single commit with message: "Add INBOX suppression enforcement — dedup by slug-prefix to prevent queue saturation (synthesis C135)"
- Completion report filed to `runtime/.handoff/general-supervisor-synthesis-p3a-complete-<iso>.md`
