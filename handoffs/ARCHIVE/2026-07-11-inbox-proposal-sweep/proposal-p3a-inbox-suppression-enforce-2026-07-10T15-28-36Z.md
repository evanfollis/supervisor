---
from: synthesis-translator
to: general
date: 2026-07-10T15:28:36Z
priority: high
task_id: synthesis-p3a-inbox-suppression-enforce
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-10T15-24-51Z.md
source_proposal: P3a (CARRY — C126, 11th cycle): INBOX suppression enforcement
---

# P3a: INBOX suppression enforcement

**Type:** Synthesis translator script amendment. Count existing INBOX items with same slug-prefix before depositing. Suppress if >=5. Log.

**Blast radius:** Supervisor INBOX only.

## Background

Per CLAUDE.md section "Automated Self-Reflection Loop", the INBOX saturation exception rule states:

"When INBOX holds >5 unconsumed items sharing the same root cause, the synthesis job may suppress additional URGENT writes for that root cause and record the suppression in the synthesis file itself."

Currently, the synthesis-translator.sh script writes handoff files without checking whether 5+ items already exist for the same root cause. This means noise-generating URGENTs can accumulate.

## Verification before action (required)

- Location: `/opt/workspace/supervisor/scripts/lib/synthesis-translator.sh`
- Current behavior: writes all handoff files unconditionally
- Target behavior: before writing, count existing INBOX files matching the same slug-prefix; suppress if count >= 5 and log the suppression

## Implementation notes

1. Extract slug-prefix from handoff filename (e.g., `proposal-dispatch-sla-*` → `dispatch-sla`)
2. Count existing files in `/opt/workspace/supervisor/handoffs/INBOX/` matching `*<slug>*.md`
3. If count >= 5, skip writing the handoff and log: `"INBOX suppression: <slug> already at 5+ items, suppressing"`
4. This is a soft suppression — the individual proposal is still acknowledged in the completion report, but no new INBOX file is created

## Acceptance criteria

- Amendment to synthesis-translator.sh slug-extraction and count logic
- Suppression rules correctly implement ">=5 existing items = suppress new writes"
- Log messages go to stderr for visibility during synthesis run
- Change committed with message: "Suppress duplicate INBOX items when root cause already has 5+ entries"
- Completion report filed at `runtime/.handoff/general-inbox-suppression-complete-<iso>.md`

## Escalation

If determining "same root cause" from filenames is ambiguous (e.g., does `dispatch-sla` match `dispatch-sla-relax` vs `dispatch-obligation`?), clarify the slug-matching strategy before implementing.
