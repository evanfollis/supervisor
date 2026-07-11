---
from: synthesis-translator
to: general
date: 2026-06-17T03:29:34Z
priority: high
task_id: synthesis-escalation-routing-fix
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-17T03-26-25Z.md
source_proposal: "Proposal 2: P-escalation-routing-fix (NEW — addresses Pattern 3)"
---

# P-escalation-routing-fix — make URGENT escalations discoverable

**Type:** CLAUDE.md amendment + session script amendment.
**Section:** "Session Awareness" in `/opt/workspace/CLAUDE.md`.
**Blast radius:** General session only. Behavioral guidance. Low risk.
**Status:** NEW. Addresses split-brain escalation routing (Pattern 3 in synthesis).

## Full proposal

This is a newly-diagnosed architecture bug discovered in C103. The synthesis states:

> **Rank: 3 (escalated from C102 rank 5).**
>
> Atlas 02:19Z O2 makes the causal claim explicit:
>
> > "The 126h breach is not simply neglect — the general session has likely
> > never seen this URGENT. This is a routing architecture bug, not a
> > process failure."
>
> Two distinct escalation write paths exist:
> - **Atlas runner / reflection jobs** → `runtime/.handoff/URGENT-*`
> - **Synthesis translator** → `supervisor/handoffs/INBOX/`
>
> The general session startup checks `supervisor/handoffs/INBOX/` (per
> CLAUDE.md). It does NOT check `runtime/.handoff/URGENT-*`. The runner
> writes to the latter. Result: runner-originated URGENTs are structurally
> undeliverable to the general session.

**Failure class:** Split-brain escalation routing — two write paths, one read path.

## Current problem

Seven URGENT files exist in `runtime/.handoff/` (ages 126h–~192h), all structurally invisible to the general session:
- URGENT-atlas-frozen-loop (~126h unconsumed)
- URGENT-atlas-unpushed-commits (stale, resolved Jun 11, never cleaned up)
- URGENT-context-repository-structural-abandonment (~192h unconsumed)
- URGENT-supervisor-event-stream-false-positive (age unknown)
- URGENT-supervisor-reflection-dirty-tree (age unknown)
- URGENT-supervisor-reflection-mutated-head (age unknown)
- URGENT-synaplex-reflection-mutated-head (age unknown)

## Proposed CLAUDE.md delta

In `/opt/workspace/CLAUDE.md`, **Session Awareness** section (currently at line ~182), amend the `general` session instructions:

**Add this line after the existing handoff-checking instructions:**

```markdown
- Also check for URGENT files in `runtime/.handoff/`:
  `ls /opt/workspace/runtime/.handoff/URGENT-* 2>/dev/null`
  Process these with the same priority as `supervisor/handoffs/INBOX/` URGENTs.
  Delete each URGENT file after processing to prevent re-escalation.
```

Location: after the line about checking `supervisor/handoffs/INBOX/`, before the "Carry-forward escalation (Proposal 4)" section.

## Verification before action (required)

- Check `/opt/workspace/CLAUDE.md` line ~182. Verify that the "Session Awareness" section for `general` sessions does NOT already mention checking `runtime/.handoff/URGENT-*`.
- List `runtime/.handoff/URGENT-*` files: `ls /opt/workspace/runtime/.handoff/URGENT-* 2>/dev/null` — verify at least some exist.
- If the amendment is already present in CLAUDE.md, write a completion report "already landed" and close.

## Acceptance criteria

- The text specified above is added to `/opt/workspace/CLAUDE.md` in the "Session Awareness" section.
- Change committed with message: "Extend URGENT escalation read path to runtime/.handoff/ (Pattern 3 fix)"
- No adversarial review required for this guidance amendment.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-escalation-routing-fix-complete-<iso>.md` pointing back to this handoff.

## Impact

- Immediately makes 7 existing URGENT files visible to the general session on next session start.
- Eliminates the architectural split-brain that kept runner-originated URGENTs invisible.
- Low risk: purely additive guidance, no breaking changes.

## Escalation

None expected. This is a read-path amendment with no code changes.
