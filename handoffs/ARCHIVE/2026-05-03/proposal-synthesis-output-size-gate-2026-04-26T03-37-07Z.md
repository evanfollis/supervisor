---
from: synthesis-translator
to: general
date: 2026-04-26T03:37:07Z
priority: high
task_id: synthesis-output-size-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-26T03-26-05Z.md
source_proposal: Proposal 2 [HIGH] — Guard synthesis output size before updating LATEST_SYNTHESIS
---

# Proposal 2 [HIGH]: Guard synthesis output size before updating LATEST_SYNTHESIS

**Type:** `synthesize.sh` amendment.

Two consecutive synthesis runs produced 67-byte stubs that poisoned `LATEST_SYNTHESIS` and triggered the translator on empty input, producing INBOX proposals from cached knowledge. The fix is a 3-line size gate.

**Proposed change:**

```bash
# After claude -p completes, before updating LATEST_SYNTHESIS:
OUTPUT_SIZE=$(wc -c < "$OUTPUT_FILE")
if [[ "$OUTPUT_SIZE" -lt 1024 ]]; then
  echo "synthesize: WARNING — output too small (${OUTPUT_SIZE}B), not updating LATEST_SYNTHESIS" >&2
  # Do NOT run translator on stub output
  exit 2
fi
```

**Blast radius:** Synthesis loop only. Automatic. Low risk — prevents stub output from poisoning downstream consumers. Does not affect the synthesis session itself, only the pointer and translator invocation.

## Verification before action (required)

- Run `git log --oneline -20` on `supervisor/scripts/lib/synthesize.sh`. Check if this proposal has already landed via another path.
- Read the file. Check if the OUTPUT_SIZE gate already exists.
- If either is true, write a completion report stating "already landed at commit <SHA> / verified in-file" rather than re-applying.

## Acceptance criteria

- The size gate is added to `synthesize.sh` after the `claude` invocation completes and before `LATEST_SYNTHESIS` is updated.
- The gate exits with code 2 and prints a warning if output is <1024 bytes.
- The translator is not invoked on stub output.
- Change committed with clear message explaining the synthesis source.
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh`.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-output-size-gate-complete-<iso>.md`.

## Escalation

URGENT if:
- Primary verification reveals the proposal is based on stale state.
- The proposal conflicts with a more recent decision.
