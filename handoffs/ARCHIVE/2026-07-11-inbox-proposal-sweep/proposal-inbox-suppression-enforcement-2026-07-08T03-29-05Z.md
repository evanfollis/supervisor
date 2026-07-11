---
from: synthesis-translator
to: general
date: 2026-07-08T03:29:05Z
priority: medium
task_id: synthesis-inbox-suppression-enforcement
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-08T03-24-41Z.md
source_proposal: P3a — INBOX suppression enforcement
---

# P3a: INBOX suppression enforcement

**Type:** Synthesis translator script amendment. Before depositing a new INBOX item, count existing items with the same slug-prefix. Suppress if ≥5. Log the suppression.

**Current behavior:** Synthesis translator (which is this translator tool, run after synthesis generation) writes all INBOX proposals without dedup or saturation gating.

**Proposed behavior:** 
1. Before writing a new handoff to `/opt/workspace/supervisor/handoffs/INBOX/`, extract the slug (e.g. `relax-dispatch-sla` from `proposal-relax-dispatch-sla-<iso>.md`)
2. Count existing files in INBOX with matching slug-prefix
3. If count ≥ 5, suppress the new handoff and log the suppression to a `synthesis-translator-suppressions-<iso>.log`
4. Update the synthesis file itself to note the suppression

**Rationale:** INBOX grew from 272 to 278 in this window (+6 from C130 synthesis translator deposits). At ~6 per synthesis cycle, the queue grows ~12 per day indefinitely. The suppression logic is specified in `/opt/workspace/CLAUDE.md` ("INBOX saturation exception") as policy but has never been enforced in code.

**Blast radius:** Supervisor INBOX only. Reduces per-cycle growth from ~6 to near-zero once saturation is hit.

**Carry history:** Proposal from C126 (6th cycle). 6 cycles open as of C131.

## Verification before action (required)

- Check `/opt/workspace/supervisor/handoffs/INBOX/` for existing items with slug-prefixes (e.g. count of `*relax-dispatch*`, `*dirty-tree*`)
- Verify the suppression policy is documented in `/opt/workspace/CLAUDE.md` around line 127–135
- Confirm this translation tool (`synthesis-translator.sh` or equivalent) is running synchronously after synthesis generation

## Acceptance criteria

- Synthesis translator amended to check INBOX saturation before writing
- Suppression threshold: 5 items with matching slug-prefix
- Suppression logged to `/opt/workspace/runtime/.meta/synthesis-translator-suppressions-<iso>.log`
- Synthesis source file annotated with suppression note (e.g. "Proposal P7 suppressed (5 existing relax-* items in INBOX)")
- Change committed with message "Enforce INBOX saturation cap per CLAUDE.md policy"
- Completion report written to `/opt/workspace/runtime/.handoff/general-supervisor-synthesis-inbox-suppression-enforcement-complete-<iso>.md`

## Escalation

URGENT if:
- The suppression mechanism breaks the synthesis → handoff translation loop (e.g. causes synthesis translator to exit)
- Existing handoff count becomes unreliable (e.g. due to archival or cleanup operations between runs)
