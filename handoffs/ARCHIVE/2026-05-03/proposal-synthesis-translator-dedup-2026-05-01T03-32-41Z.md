---
from: synthesis-translator
to: general
date: 2026-05-01T03:32:41Z
priority: high
task_id: synthesis-translator-dedup-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-01T03-27-05Z.md
source_proposal: Proposal 2 — Synthesis-translator dedup gate (HIGH, REPEAT — now more urgent)
---

# Synthesis-translator dedup gate

**Pattern:** INBOX has grown from 27 → 30 items this cycle (+3 new proposals, all duplicates). The synthesis-translator itself created 2 copies of its own dedup-gate proposal. Duplicate proposals accumulate without detection.

**Proposed implementation** (add to `/opt/workspace/supervisor/scripts/lib/synthesis-translator.sh` before any `echo ... > "$INBOX_DIR"/proposal-*` statement):

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

**Blast radius:** Supervisor project only (synthesis-translator.sh). Automatic. Would stop ~3 duplicate files per 12h cycle.

**Why now:** High urgency driven by Pattern 4 (INBOX saturation growing ~3/cycle, effective queue obscured by duplicates). This is the single mechanical fix that prevents the dedup-gate proposal itself from appearing twice in the next synthesis.

## Verification before action (required)

- Run `ls -la /opt/workspace/supervisor/scripts/lib/synthesis-translator.sh`.
- Run `grep -n "proposal_key=" synthesis-translator.sh` — should return empty (dedup not yet implemented).
- If grep returns non-empty, skip and report "already landed at line <N>".

## Acceptance criteria

- Dedup check added before any INBOX proposal write statement in synthesis-translator.sh.
- Variable names (`proposal_key`, `existing`, `INBOX_DIR`) must match the surrounding code.
- Commit message: "Add dedup gate to synthesis-translator to prevent duplicate proposals in INBOX" (imperative, explains why not what).
- Commit includes cite to synthesis source.

## Adversarial review

This is a defensive shell script patch. Run via `supervisor/scripts/lib/adversarial-review.sh /opt/workspace/supervisor/scripts/lib/synthesis-translator.sh` to validate:
- Dedup key is stable across synthesis runs.
- Early `continue` doesn't skip other proposal processing.
- Edge cases: whitespace/punctuation in proposal titles, existing handoff filenames.

## Completion report

After commit, write `/opt/workspace/runtime/.handoff/general-supervisor-synthesis-translator-dedup-complete-<iso>.md` with:
- Commit SHA
- Confirmation that grep shows dedup code in synthesis-translator.sh at line <N>
- Link back to this handoff
