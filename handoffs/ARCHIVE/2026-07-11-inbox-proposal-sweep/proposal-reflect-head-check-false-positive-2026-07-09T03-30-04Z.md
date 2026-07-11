---
from: synthesis-translator
to: general
date: 2026-07-09T03:30:04Z
priority: high
task_id: synthesis-reflect-head-check-fp
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-09T03-26-11Z.md
source_proposal: P5 — Patch reflect.sh HEAD-check false positive
---

# P5: Patch reflect.sh HEAD-check false positive

**Type:** `reflect.sh` — whitelist autocommit SHAs in HEAD comparison.

**Blast radius:** Supervisor, synaplex. ~15 min.

---

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` to locate the HEAD comparison check (likely a guard that prevents reflection if HEAD hasn't changed).
- Check for existing SHA-whitelist logic. If it already exists, write completion report "already landed in-file" and close.
- Understand the false-positive case: `reflect: auto-update CURRENT_STATE.md` commits should not trigger "HEAD changed, skip reflection" guards. These autocommits are mechanical state updates, not substantive project activity.
- Locate the autocommit message pattern (likely in supervisor and synaplex automation).

## Acceptance criteria

- `reflect.sh` HEAD comparison whitelists commits with message pattern `reflect: auto-update` (or similar mechanical autocommit signature).
- Whitelisted commits are not considered "real work" for the purpose of deciding whether to run a reflection.
- Unwhitelisted (actual project work) commits trigger normal reflection flow.
- Change committed with clear message: "Whitelist autocommit SHAs in HEAD check per synthesis #133"
- Document the whitelist pattern in a comment above the logic (e.g., "Autocommits like 'reflect: auto-update CURRENT_STATE.md' are mechanical state refreshes, not substantive project work").
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-supervisor-synthesis-reflect-head-check-fp-complete-<iso>.md`.

## Escalation

URGENT if:
- The autocommit message pattern is inconsistent across projects (different message formats in supervisor vs. synaplex). List the patterns found and clarify the whitelist before landing.
- The HEAD check is interleaved with other logic that makes whitelisting complex. Flag the structural issue.
