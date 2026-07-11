---
from: synthesis-translator
to: supervisor
date: 2026-05-18T03:30:49Z
priority: high
task_id: synthesis-verify-write-primitive-2nd-cycle
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-18T03-26-35Z.md
source_proposal: Proposal 3 — Post-write verification primitive
---

# Post-write verification primitive

**Type:** New shared primitive — `supervisor/scripts/lib/verify-write.sh`

**Evidence:** The ghost-FR false-positive pattern (Pattern 4, this synthesis) requires a stat-after-write check. Without it, `friction_filed` events are emitted for files that don't exist, poisoning the event stream. False records remain indefinitely because no correction mechanism exists.

**Problem:** Code that runs `friction_filed` events (tick, reflection, and other automation) writes files and emits success events without verifying the write actually landed on disk. If the write fails silently (permission denied, disk full, interrupted), the event stream records success while the file is missing.

**Proposal (unchanged from cycle 42):**

Create `/opt/workspace/supervisor/scripts/lib/verify-write.sh`:

```bash
#!/usr/bin/env bash
# Verify that a file exists after an operation claims to have written it.
# Usage: verify_write <file_path> [timeout_seconds]
#
# Returns 0 if file exists and is readable within timeout.
# Returns 1 if file does not exist after timeout.
# Emits a calibration message to stderr if verification takes >100ms.

set -euo pipefail

FILE="${1:?file path required}"
TIMEOUT="${2:-1}"  # seconds

start=$(date +%s%N)
elapsed=0
while [[ $elapsed -lt $(( TIMEOUT * 1000000000 )) ]]; do
  if [[ -e "$FILE" ]] && [[ -r "$FILE" ]]; then
    elapsed_ms=$(( ($(date +%s%N) - start) / 1000000 ))
    if [[ $elapsed_ms -gt 100 ]]; then
      echo "verify_write: $FILE verified in ${elapsed_ms}ms" >&2
    fi
    exit 0
  fi
  sleep 0.01
  elapsed=$(( $(date +%s%N) - start ))
done

echo "verify_write: FAILED — $FILE does not exist after ${TIMEOUT}s" >&2
exit 1
```

**Deployment / callsites:**

After writing a durable artifact (handoff, friction, state file), call:

```bash
verify_write "$OUTPUT_FILE" 1 || { echo "write failed: $OUTPUT_FILE" >&2; exit 2; }
```

Start with supervisor-tick.sh and reflect.sh. Extend to any other automation that emits events based on file writes.

**Rationale:**

The event stream is the source of truth for supervisor pressure and dispatch. False events (claiming success when the write failed) corrupt the meta-loop's ability to detect stuck states. This primitive prevents ghost records and catches write failures early.

**Blast radius:** Tick and reflection jobs (automatic, opt-in per call site). No change to existing output; only adds early-exit on write failure.

**Cycles open:** 2.

## Verification before action (required)

- Check if `supervisor/scripts/lib/verify-write.sh` already exists (if so, verify it matches the proposal)
- Search git log for evidence that this pattern has been implemented elsewhere

## Acceptance criteria

- `verify-write.sh` created with the logic above
- Script is executable and sources correctly from calling scripts
- At minimum two callsites updated: supervisor-tick.sh and reflect.sh (after writing friction/output files)
- Test: intentionally trigger a write-failure scenario (e.g. read-only directory) and verify the script detects it
- Change committed with message referencing the ghost-FR pattern and the 2-cycle carry-forward

## Escalation

URGENT if:
- Primary verification shows this pattern already exists under a different name (check `scripts/lib/` for similar utilities)
- Implementation details conflict with an existing error-handling strategy in tick or reflect
