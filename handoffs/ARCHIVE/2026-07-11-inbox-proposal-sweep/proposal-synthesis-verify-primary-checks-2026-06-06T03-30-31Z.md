---
from: synthesis-translator
to: general
date: 2026-06-06T03:30:31Z
priority: high
task_id: synthesis-verify-primary-checks
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-06T03-25-20Z.md
source_proposal: "P-synthesis-verify — Primary verification in synthesis prompt (3 cycles open)"
---

# P-synthesis-verify — Primary verification in synthesis prompt

**Type:** Shared primitive update — synthesis prompt.

Add a verification step before asserting any factual claim derived from a prior synthesis counter: run the actual check (e.g., `ls -lt *.jsonl`, `git status`, `stat`). Do not publish counter-derived claims as primary evidence.

**Blast radius:** Synthesis only (automatic). Prevents the false-claim failure class identified in C79.

## Context

C79 synthesis report counter-derived claims without live verification. Example: counter stated "skip events in URGENT file" but actual `git status` showed the event file was modified. The synthesis prompt was generating factual statements based on stale counter state.

The fix is to move from counter-derived assertions to live primary verification:
- Before claiming "INBOX has N items", run `ls /opt/workspace/supervisor/handoffs/INBOX/ | wc -l`
- Before claiming "files are X days old", run `find ... -mtime` or `stat`
- Before claiming "synthesis_reviewed events are N", run the actual grep on the event stream
- Before claiming "dirty-tree files are X", run `git status --short`

This ensures the synthesis report reflects actual live state, not potentially-stale counter history.

## Verification before action (required)

- Locate the synthesis job script (likely `/opt/workspace/supervisor/scripts/lib/synthesize.sh` or similar)
- Check the current prompt to see how it derives counter values
- Verify the prompt does not already include live verification steps

## Acceptance criteria

- The synthesis prompt is updated to include pre-flight checks for all factual assertions:
  - File counts use `ls` + `wc -l` or `find -type f`
  - Dates use `find -mtime` or `stat -c %y`
  - Event counts use `grep` on the actual event stream file (`events/supervisor-events.jsonl`)
  - Git state uses `git status --short` directly
- The prompt explicitly documents the fallback: if a live check fails, report the error rather than using stale counter
- Change committed with message explaining the synthesis source and the C79 failure class
- Test: run a single synthesis cycle and verify it produces live-verified facts (not counter-derived)

## Escalation

URGENT if:
- The synthesis script does not have an accessible prompt to update (it may be in a config file or API request). Surface the exact location.
- Adding live verification checks would significantly extend synthesis runtime. Document the runtime impact with before/after times.
