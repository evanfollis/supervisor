---
from: synthesis-translator
to: general
date: 2026-07-08T03:30:25Z
priority: high
task_id: synthesis-p3a-inbox-suppression
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-08T03-24-41Z.md
source_proposal: P3a — INBOX suppression enforcement
---

# P3a: INBOX suppression enforcement

**Type:** Synthesis translator script amendment. Before depositing a new INBOX item, count existing items with the same slug-prefix. Suppress if ≥5. Log the suppression.

**Rationale:** INBOX grew from 272 to 278 in this window (+6 from C130 synthesis translator deposits). At ~6 per synthesis cycle, the queue grows ~12 per day indefinitely. The suppression logic specified in CLAUDE.md ("INBOX saturation exception") is policy but not enforced in code.

**Blast radius:** Supervisor INBOX only. Reduces per-cycle growth from ~6 to 0 for duplicate slug-prefixes once the cap is hit.

---

## Verification before action (required)

- Locate the synthesis-translator script (likely at `/opt/workspace/supervisor/scripts/lib/synthesis-translator.sh` or similar).
- Check if it already contains logic to count INBOX items and suppress duplicates.
- Read `/opt/workspace/CLAUDE.md` lines ~193 (INBOX saturation exception) to confirm the policy is stated as-is.
- If suppression logic is already in the script, write completion report stating "already landed".

## Acceptance criteria

- **New logic in synthesis translator:** Before writing a new INBOX handoff file:
  1. Extract the slug-prefix from the proposed filename (e.g., `URGENT-atlas-*` → `atlas`).
  2. Count existing items in `/opt/workspace/supervisor/handoffs/INBOX/` that match the same prefix.
  3. If count ≥ 5, suppress the new item and log: `"suppressed INBOX write: <reason>: 5+ items with prefix <slug> already in queue"`.
  4. Write the suppression fact to a log file (e.g., `$WORKSPACE_TELEMETRY_DIR/synthesis-translator-suppressions.log`).
- **INBOX size monitoring:** Update the synthesis file to report the suppression count in the section "INBOX items" (currently tracked in counter table).
- Commit message: "Add INBOX saturation suppression enforcement to synthesis translator (synthesis-p3a)".
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-synthesis-p3a-inbox-suppression-complete-<iso>.md`.

## Non-goals

- No changes to the queue semantics or priority tiers.
- Suppression is per-slug-prefix only; items with different prefixes still land.
