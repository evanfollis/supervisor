---
from: synthesis-translator
to: general
date: 2026-06-28T03:27:59Z
priority: high
task_id: synthesis-escalation-routing-fix-supervisor
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-28T03-24-11Z.md
source_proposal: P-escalation-routing-fix (carry from C103) — Unify handoff scan paths — Supervisor Part
---

# P-escalation-routing-fix (Part 1/2): AGENT.md reentry amendment

**Type:** Charter amendment — `supervisor/AGENT.md` reentry step 9.

**Status (at synthesis time):** Unchanged since C103. Two independent changes needed; this handoff covers the supervisor/AGENT.md part only. See matching atlas handoff for the runner.py fix.

## Proposal body (from synthesis)

The diagnostic infrastructure writes escalation handoffs to two different paths:
- Project runners and local scripts write to `runtime/.handoff/URGENT-*`
- The executive reentry procedure reads from `supervisor/handoffs/INBOX/`

This routing fragmentation makes 8 URGENT files invisible to the executive — they land in `runtime/.handoff/` but reentry doesn't scan that path.

**Patch to apply** to `supervisor/AGENT.md` reentry step 9:

Current text likely reads something like:
```
9. List handoffs addressed to `general`: `ls /opt/workspace/runtime/.handoff/general-* 2>/dev/null`.
```

Add a new scan for URGENT project files:
```
9. List handoffs addressed to `general`: `ls /opt/workspace/runtime/.handoff/general-* 2>/dev/null`.
   Also check for project-level URGENTs: `ls /opt/workspace/runtime/.handoff/URGENT-* 2>/dev/null`.
```

The charter already documents this dual-path reentry in a later section ("List project-level URGENTs..."), but it is not in the main reentry flow. This amendment moves it into the primary reentry sequence.

**Blast radius:** Executive reentry only. Purely informational — no state change, no automation affected.

**Effort:** <2 min. One-line amendment to charter.

**Coordination note:** The matching atlas runner.py fix (Part 2 of this proposal) directs future escalations to `supervisor/handoffs/INBOX/` instead of `runtime/.handoff/`, which will further reduce need for this dual scan. However, both changes are needed: the AGENT.md amendment catches existing orphaned URGENTs, while the runner.py fix prevents new ones.

## Verification before action (required)

- Read the current `supervisor/AGENT.md` reentry section to confirm step 9 does not already include the `ls .../URGENT-*` scan.
- If already present, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- `supervisor/AGENT.md` reentry step 9 (or the next numbered reentry step if numbering has changed) includes explicit `ls /opt/workspace/runtime/.handoff/URGENT-* 2>/dev/null` scan.
- Change committed with message explaining the routing fix.
- No need for adversarial review — the change is purely informational and additive to the reentry procedure.

## Escalation

None. This is a straightforward charter amendment with no dependencies.
