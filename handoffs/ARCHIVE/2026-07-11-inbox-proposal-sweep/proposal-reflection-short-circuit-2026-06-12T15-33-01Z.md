---
from: synthesis-translator
to: general
date: 2026-06-12T15:33:01Z
priority: medium
task_id: synthesis-reflection-short-circuit
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-12T15-27-51Z.md
source_proposal: Proposal 3 — P-reflection-short-circuit (NEW)
---

# P-reflection-short-circuit — Allow reflections to degrade output after 4 unchanged cycles

## Synthesis proposal (verbatim)

**Type:** Shared primitive amendment.
**File:** `supervisor/scripts/lib/reflect-prompt.md`

**What:** Add guidance allowing reflections to degrade to a single-paragraph status update when all observations are unchanged for N consecutive cycles (proposed: N=4). The short form must include:
(a) count of unchanged observations, (b) age of oldest unresolved item, (c) pointer to the last full reflection, (d) any NEW observations only.

**Sketch (addition to reflect-prompt.md):**
```markdown
## Short-circuit rule

If ALL observations in your prior reflection are unchanged (same items,
same status, no new findings), and this is the 4th+ consecutive cycle
with no change, you MAY reduce your output to a single paragraph:

> **Short-circuit: cycle N.** M observations unchanged since [prior
> reflection path]. Oldest unresolved: [item, age]. No new findings.
> [Any NEW observation gets a full write-up here.]

This prevents context exhaustion from verbose repetition of identical
findings. Resume full analysis when any observation changes status.
```

**Blast radius:** All projects with active reflection loops. Opt-in (guidance, not enforcement — the reflection agent may still write full output if new findings exist).

**Why this matters now:** Context-repository explicitly requested this ("future reflections should hard-skip non-critical sections"). Skillfoundry-harness noted "this entry exists to maintain the cycle counter and timestamp record; it contains no new findings." The reflection loop is spending tokens to say the same thing every 12h without adding information.

---

## Context (from synthesis)

Three projects independently signaled that their reflection loops are producing noise, not signal, after 4+ cycles of unchanged findings. The reflection loop short-circuit rule (currently just inactivity detection) needs extension to handle the "all observations unchanged" case. This is a feedback-loop health amendment, not a structural fix.

---

## Verification before action (required)

- Read `supervisor/scripts/lib/reflect-prompt.md` — does a "Short-circuit rule" section already exist that covers the "observations unchanged for 4+ cycles" scenario?
- Grep for variations: `4.*cycle|unchanged.*observation|reduce.*output` in the file.
- If full proposal is already present, write completion report "already landed" and close.
- If a partial short-circuit rule exists but doesn't cover the observation-unchanged case, verify whether the proposed amendment should extend the existing section or create a separate one.

---

## Acceptance criteria

- Section added to `supervisor/scripts/lib/reflect-prompt.md` (or existing "Short-circuit rule" section extended if present).
- Guidance is framed as opt-in and must explicitly state "MAY reduce" not "MUST reduce" — reflections retain discretion to write full output.
- The short form must require all four elements: (a) count unchanged, (b) age of oldest item, (c) pointer to last full reflection, (d) any NEW observations.
- Commit message: "Add short-circuit guidance for unchanged observations across 4+ cycles to prevent context exhaustion" (or similar).

---

## Escalation

URGENT if:
- Verification surfaces a design conflict with the existing inactivity short-circuit rule. The two rules should compose cleanly (inactivity skips entirely; observation-unchanged produces a minimal paragraph). Flag if they interact unexpectedly.
- A project reflection has already landed a variant of this guidance in its local CURRENT_STATE.md or similar. Dedup guidance before landing workspace-wide amendment.
