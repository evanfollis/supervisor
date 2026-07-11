---
from: synthesis-translator
to: general
date: 2026-05-28T03:27:57Z
priority: high
task_id: synthesis-dispatch-deadline-enforcement
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-28T03-24-25Z.md
source_proposal: C61 Proposal 4 (STRUCTURAL — synthesis survivability)
---

# Dispatch-deadline enforcement at reentry

**Status:** Open, **3 cycles**. CLAUDE.md amendment. Adds attended-session fallback for synthesis dispatch when tick is down. Three consecutive breaches confirm the gap this was designed to fill.

## Context

CLAUDE.md specifies a 24-hour dispatch obligation: when a synthesis proposes a change, an attended session must dispatch a delegated project session within 24 hours or record an explicit deferral reason.

Since C60 (cycle 60), three consecutive synthesis cycles have breached this deadline:
- C60 (expired ~15:32Z May 27)
- C61 (expired ~03:28Z May 28)
- C62 (expired ~15:27Z May 28 — within this synthesis's write window)

Root cause: The tick halt prevents tick from executing dispatch logic, and no attended session arrived to manually dispatch. The rule is correct and identified the scenario it's meant to prevent. The enforcement path has no fallback when both tick and attended session are absent.

The fix: Add language to CLAUDE.md that designates reentry by an attended session as a secondary dispatch trigger. When the general session starts a new conversation (reentry), it must check synthesis dispatch obligations and resolve them before proceeding to other work.

## Verification before action (required)

- Read current CLAUDE.md and verify the 24-hour dispatch rule exists
- Check `supervisor/system/verified-state.md` for the current dispatch obligation count
- If dispatch obligations have already been manually resolved, write completion report "already actioned" and skip

## Acceptance criteria

- CLAUDE.md includes explicit language making reentry by an attended session a secondary enforcement trigger for dispatch obligations
- The language clarifies that "dispatch" means either: tick executes the handoff, OR attended session manually processes it before starting other work
- Change committed with message explaining the fallback enforcement path
- Completion report includes a count of currently open dispatch obligations needing resolution

## Escalation

URGENT if:
- The amendment creates ambiguity about which session bears responsibility for dispatch
- Attended reentry flow becomes unclear or adds friction
