---
from: synthesis-translator
to: general
date: 2026-06-05T15:29:43Z
priority: medium
task_id: synthesis-synthesis-verify
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-05T15-26-05Z.md
source_proposal: P-synthesis-verify — Primary verification in synthesis prompt (2 cycles open)
---

# P-synthesis-verify — Primary verification in synthesis prompt

**Type:** Shared primitive update — `synthesize-prompt.md` or `synthesize.sh`.

**Pattern:** Synthesis makes assertions about principal activity status without primary verification. C79 self-applied this ad hoc; it is not yet systematic in the synthesis prompt.

**Failure class:** Counter-derived claims without primary evidence. Synthesis reports can state conclusions based on arithmetic (e.g., "no principal session in the C20 window because the JSONL count is N") without verifying against actual session files.

**Proposed change:**
Add to the synthesis prompt (in `synthesize-prompt.md` or directly in `synthesize.sh`):
```
Before asserting principal activity status, run:
  ls -lt /root/.claude/projects/-opt-workspace/*.jsonl | head -5
Do not publish principal-absence claims derived solely from counter arithmetic.
```

**Rationale:** C79 manually verified session files before claiming principal absence. This prevented a false-confidence report that would have cascaded to the executive. The check must be systematic, not ad hoc.

**Blast radius:** Synthesis only (automatic). Prevents counter-derived-claim failure class. Currently 0% blocked by this, but systematic verification prevents future occurrence.

**Evidence:** C80 section "No principal session this window" (lines 52–56) notes C79 applied this check ad hoc. Synthesis now states: "Primary verification applied: Checked `ls -lt /root/.claude/projects/-opt-workspace/*.jsonl | head -5` directly." This must be encoded into the synthesis prompt so every cycle applies it automatically.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/synthesize-prompt.md` or the synthesis job script to locate where prompt instructions are defined
- Check if primary verification checks already exist in the prompt
- Verify this change has not already landed (check recent commits and prompt content)
- If already landed, write completion report noting "already landed at commit <SHA>" and exit

## Acceptance criteria

- The synthesis prompt includes an instruction to verify session file state before asserting principal activity
- The instruction specifies the exact command to run: `ls -lt /root/.claude/projects/-opt-workspace/*.jsonl | head -5`
- The prompt explicitly forbids counter-derived principal-absence claims without file verification
- Commit message explains the synthesis source and why ad hoc verification must be systematic
- Completion report at `/opt/workspace/runtime/.handoff/general-synthesis-synthesis-verify-complete-<iso>.md` pointing back to this handoff and source synthesis

## Escalation

URGENT if:
- Verification reveals this check has already landed by another path — write brief completion saying "obsolete — already landed" and close
- The synthesis prompt structure has changed significantly since C80 — surface the structural mismatch
