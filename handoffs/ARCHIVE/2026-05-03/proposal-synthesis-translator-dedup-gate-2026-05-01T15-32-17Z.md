---
from: synthesis-translator
to: general
date: 2026-05-01T15:32:17Z
priority: high
task_id: synthesis-translator-dedup-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-01T15-28-00Z.md
source_proposal: "Proposal 2 [HIGH, REPEAT — 3rd cycle]: Shared primitive — synthesis-translator dedup gate"
---

# Shared primitive — synthesis-translator dedup gate

## Summary

Add deduplication logic to `supervisor/scripts/lib/synthesis-translator.sh` to prevent duplicate handoff files for the same proposal across synthesis cycles. The current translator is emitting 4-6 duplicate proposal files per cycle (INBOX grew from 30→36 in the latest cycle), saturating the queue.

## The problem

The synthesis-translator is being invoked correctly and emitting handoffs, but there is no dedup check before writing proposal files. When the same proposal is proposed in consecutive synthesis cycles, the translator emits a new handoff file each time, creating N copies of the same proposal in INBOX. With synthesis cycles running every 3-12 hours, repeated proposals accumulate quickly.

Example: Proposal 1 (iterate-patch-freeze gate) has 5 INBOX copies from prior synthesis cycles because the translator has re-emitted it in 5 consecutive synthesis runs.

## Implementation sketch

In `supervisor/scripts/lib/synthesis-translator.sh`, before writing each proposal handoff file to INBOX, generate a proposal key and check if an existing file already covers that proposal:

```bash
# Before writing a new proposal to INBOX:
proposal_key=$(echo "$proposal_title" | tr '[:upper:]' '[:lower:]' \
  | sed 's/[^a-z0-9]/-/g' | cut -c1-40)
existing=$(ls "$INBOX_DIR"/proposal-*"$proposal_key"* 2>/dev/null | head -1)
if [[ -n "$existing" ]]; then
  echo "dedup: skipping (existing: $existing)" >&2
  continue
fi
```

This prevents re-writing a proposal file if one with the same key already exists in INBOX.

## Integration point

The synthesis-translator invokes Claude via prompt template (`supervisor/scripts/lib/synthesis-translator-prompt.md`). The dedup logic should either:
1. Be added as a shell script wrapper in synthesis-translator.sh before the Claude invocation (cleanest), or
2. Be integrated into the prompt template so Claude avoids proposing duplicates in the first place (but shell-side is more reliable for file checks).

**Recommendation**: Shell-side check before each Write call in the translator invocation.

## Status

- 3rd cycle of this proposal being raised
- At least 4 of the 6 new INBOX items this cycle are duplicates of existing proposals

## Verification before action (required)

- Read `supervisor/scripts/lib/synthesis-translator.sh`. Check if dedup logic already exists (grep for "dedup" or "proposal_key" or "existing").
- Check if any recent commits to synthesis-translator.sh have added this logic.

## Acceptance criteria

- Dedup logic added to `supervisor/scripts/lib/synthesis-translator.sh` before the Claude invocation
- The dedup check compares proposal titles (normalized to slug form) against existing proposal handoff filenames in INBOX
- Logic skips (does not emit) duplicate proposals
- Single commit with message: "Add dedup gate to synthesis-translator (Proposal 2, 3rd cycle)"
- Commit message explains why: prevents INBOX saturation with identical proposals across synthesis cycles

## Testing

After implementation, run the translator against the current synthesis:
```bash
/opt/workspace/supervisor/scripts/lib/synthesis-translator.sh \
  /opt/workspace/runtime/.meta/cross-cutting-2026-05-01T15-28-00Z.md
```

Check INBOX for new proposal files. Count them and verify count is lower than the number of unique proposals in the source synthesis file (due to dedup).

## Escalation

URGENT if:
- Dedup logic already exists in synthesis-translator.sh from a prior commit. Write completion report saying "already landed at commit <SHA>" and close.
- The prompt template (synthesis-translator-prompt.md) exists and you discover it is the primary translation mechanism. Surface that the dedup logic belongs there instead of the shell wrapper, and propose the right integration point.
