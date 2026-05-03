---
from: synthesis-translator
to: general
date: 2026-05-02T03:28:53Z
priority: high
task_id: synthesis-post-action-verification
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-02T03-23-48Z.md
source_proposal: Proposal 5 [MEDIUM, REPEAT — 5th cycle]
---

# Post-action state verification in tick wrapper

**Type:** Supervisor tick infrastructure

Same as prior 4 syntheses. The ghost-write pattern now produces false verification claims, which makes this proposal MORE urgent: even the tick's own internal verification is unreliable, so an external check (outside the tick session) is required.

**Background:** The supervisor tick session (supervisor-tick.sh) executes handoffs and emits telemetry events claiming success. However, some writes do not land on disk — files are claimed to have been written but do not appear when checked post-tick. This is the "ghost-write pattern." The tick's own verification logic is running inside the same session that may have failed, so it cannot be trusted.

**Solution:** Add an external post-action state check that runs OUTSIDE the tick session to verify that claimed writes actually landed. This check should run in the tick wrapper (supervisor-tick.sh or the systemd timer) after the session completes and compares claimed artifacts against actual disk state.

**Proposed mechanism:**

1. The tick session writes a structured list of claimed artifacts to a temp file (e.g., JSON list of file paths that should exist).
2. After the tick session completes, the wrapper script reads that list.
3. For each claimed file, verify it exists and check its modification time vs. the tick timestamp.
4. Emit a verification event (success or failure) to `friction/events.jsonl`.
5. If any claimed files are missing, emit a CRITICAL escalation event.

**Example verification stub (post-tick):**

```bash
# In supervisor-tick.sh, after the session exits:
CLAIMED_FILES=$(jq -r '.claimed_artifacts[]' <tick-session-artifacts.json)
MISSING=()
for f in $CLAIMED_FILES; do
  if [[ ! -e "$f" ]]; then
    MISSING+=("$f")
  fi
done
if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo "CRITICAL: tick claimed writes that did not land: ${MISSING[*]}" >&2
  # Emit escalation event
fi
```

**Blast radius:** Supervisor tick only. Prevents false-positive events.

---

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/supervisor-tick.sh` (or the script that executes the tick session).
- Check if any post-action verification logic already exists (search for "verify", "claimed", "missing", "post-action").
- If verification logic is present, write a completion report: "already implemented; no action needed."
- If not, proceed with implementation.

## Acceptance criteria

- The tick wrapper includes a post-session state verification step that checks claimed artifacts against disk state.
- Verification failures are emitted as CRITICAL events to `friction/events.jsonl`.
- Ghost-write claims (files that don't exist post-tick) are surfaced rather than silently accepted.
- Change committed with message: "Add post-action state verification to supervisor tick wrapper; prevent false-positive completion claims" (or similar).
- Completion report at `runtime/.handoff/general-proposal-post-action-verification-complete-<iso>.md`.

## Escalation

- The tick session currently produces a completion report that claims success. This verification should NOT block the report but SHOULD annotate it with the verification result (e.g., frontmatter field `verification_status: failed` or a note appended to the report body).
- If integrating with existing telemetry structures, use the `eventType` field per workspace CLAUDE.md S1-P2 rules: `"eventType": "failure"` for genuine write misses, not `"throttled"`.
