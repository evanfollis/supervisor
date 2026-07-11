---
from: synthesis-translator
to: general
date: 2026-07-03T03:26:51Z
priority: high
task_id: synthesis-reflect-sha-whitelist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-03T03-23-57Z.md
source_proposal: P5 (CARRY — C120, 2nd cycle): Patch reflect.sh HEAD-check false positive
---

# P5: Patch reflect.sh HEAD-check false positive

Type: `reflect.sh` — whitelist autocommit SHAs in HEAD comparison.

Location: `/opt/workspace/supervisor/scripts/lib/reflect.sh`

Problem: reflect.sh validates that the agent did not mutate the HEAD of the repo by comparing the current HEAD SHA against a baseline. However, supervisor-autocommit.sh legitimately updates HEAD as part of its normal operation. This causes reflect.sh to emit a false-positive `URGENT-supervisor-reflection-mutated-head.md` file even though no unauthorized mutation occurred.

Current behavior: reflect.sh compares the working directory HEAD against an initial baseline. If they differ, it raises an URGENT file.

Required fix: When reflect.sh runs in a context where supervisor-autocommit.sh is active (supervisor project only), maintain a whitelist of "known good" autocommit SHAs that performed legitimate HEAD updates. Check the current HEAD against this whitelist before raising the URGENT.

Implementation sketch from C120:
1. In reflect.sh's HEAD-check section, after detecting a HEAD mismatch
2. Check if the new HEAD SHA matches the most recent autocommit SHA from supervisor-autocommit.sh (either via `git log --oneline -1` for autocommit commits, or a recorded state file)
3. If it matches, log an info event and skip the URGENT escalation
4. If it doesn't match, proceed with the false-positive alert as before

Rationale from C121: This is Pattern 4 in the C121 synthesis — the false-positive `URGENT-supervisor-reflection-mutated-head.md` is still present, and it recurs because reflect.sh doesn't know about autocommit-driven HEAD updates. The false positive should be eliminated without removing the legitimate safety check.

Effort: ~15 minutes

Blast radius: All reflected projects with concurrent autocommit (currently: supervisor only).

## Verification before action (required)

- `grep -n "URGENT-.*mutated-head\|HEAD.*mutated\|HEAD comparison" /opt/workspace/supervisor/scripts/lib/reflect.sh` to find the current HEAD-check code
- Verify that no whitelist logic currently exists
- List `runtime/.handoff/URGENT-supervisor-reflection-mutated-head.md` to confirm the false-positive file exists

## Acceptance criteria

- reflect.sh HEAD-check code is enhanced to whitelist autocommit SHAs for the supervisor project
- The false-positive URGENT file at `runtime/.handoff/URGENT-supervisor-reflection-mutated-head.md` is deleted (as part of the fix verification)
- A test run of reflect.sh confirms it no longer raises the false-positive URGENT when HEAD has been legitimately updated by autocommit
- Commit with message: "Whitelist autocommit SHAs in reflect.sh HEAD-check to eliminate false-positive URGENT (synthesis C121)"
- Completion report at `runtime/.handoff/general-proposal-reflect-sha-whitelist-complete-<iso>.md`

## Escalation

URGENT if:
- The whitelist logic is already in place (use completion report "already landed" path)
- The HEAD-check code structure differs significantly from what's described (may require additional implementation context from C120 or earlier synthesis cycles)
