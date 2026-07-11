---
from: synthesis-translator
to: general
date: 2026-07-09T03:30:04Z
priority: high
task_id: synthesis-inbox-suppression-enforcement
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-09T03-26-11Z.md
source_proposal: P3a — INBOX suppression enforcement
---

# P3a: INBOX suppression enforcement

**Type:** Synthesis translator script amendment. Before depositing a new INBOX item, count existing items with the same slug-prefix. Suppress if ≥5. Log the suppression.

**Rationale:** INBOX at 295 and growing ~12/day. The CLAUDE.md policy is stated but unimplemented. Without enforcement, each synthesis cycle adds ~6 items indefinitely.

**Blast radius:** Supervisor INBOX only. Reduces per-cycle growth. Does not address existing 295-item backlog.

---

## Verification before action (required)

- Locate the synthesis translator script (likely in `/opt/workspace/supervisor/scripts/lib/` or embedded in synthesis job).
- Search for the section that writes INBOX handoff files (code that creates `.md` files in `/opt/workspace/supervisor/handoffs/INBOX/`).
- Check if slug-prefix dedup already exists. If yes, write completion report "already landed in-file" and close.
- Read CLAUDE.md "Automated Self-Reflection Loop" section for the suppression policy statement (line ~95 in the synthesis references it).

## Acceptance criteria

- Before depositing a handoff to `supervisor/handoffs/INBOX/`, the translator counts existing items with matching root-cause prefix.
- If count ≥5: skip deposit, log suppression with reason: "suppressed: 5+ existing items with prefix '{prefix}'".
- Suppression logged to `/opt/workspace/runtime/.meta/synthesis-suppression-log-<iso>.jsonl` (or similar append-only sink) with fields: `{ prefix, count, suppressed_at, proposed_file }`.
- Change committed with clear message: "Implement INBOX suppression enforcement per synthesis #133"
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-supervisor-synthesis-inbox-suppression-enforcement-complete-<iso>.md`.

## Escalation

URGENT if:
- The suppression log sink doesn't exist and cannot be created (permission issue).
- Identifying "same slug-prefix" is ambiguous. Define the prefix-matching algorithm clearly before landing.
