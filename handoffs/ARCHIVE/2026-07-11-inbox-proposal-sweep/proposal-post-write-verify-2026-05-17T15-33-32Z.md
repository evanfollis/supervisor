---
from: synthesis-translator
to: general
date: 2026-05-17T15:33:32Z
priority: high
task_id: synthesis-post-write-verify
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-17T15-27-50Z.md
source_proposal: Proposal 1 — Post-write verification primitive for tick and reflection sessions
---

# Post-write verification primitive for tick and reflection sessions

## Proposal

The tick and reflection sessions both emit events or claims about file writes without verifying the write landed. This proposal adds a shared shell function that any automated session can source.

**Type:** New shared primitive — `supervisor/scripts/lib/verify-write.sh`

**5-line sketch:**
```bash
verify_write() {
  local target="$1" event_type="$2"
  if [[ ! -f "$target" ]]; then
    echo "[VERIFY-WRITE] FAILED: $target does not exist after claimed write" >&2
    return 1
  fi
}
```

The tick's FR-filing code and the reflection's event-emission path should call `verify_write "$file" "friction_filed"` before emitting any `*_filed` or `*_written` event. A failed verification must emit `eventType: "write_verification_failed"` instead of the success event.

**Blast radius:** Tick and reflection jobs (automatic, opt-in per call site). Does not change existing behavior — only adds a verification step.

## Rationale

Two independent instances surfaced this cycle of automated sessions operating under write restrictions that emit success claims without verifying the write landed:

1. **Event stream false-positive (supervisor).** The 04:48Z tick emitted `friction_filed` events claiming FR-0042, FR-0043, and FR-0044 were filed. Disk verification at 14:27Z confirms: these files do not exist. This is the 7th+ window of ghost-FR non-existence with confident false completion claims now in the event stream.

2. **Reflection safety net bypass (context-repository).** A supervisor reflection session advanced HEAD despite `--disallowedTools`, creating unverified writes.

**Underlying failure class:** Write-claim-without-verification. The automation layer has no `stat`-after-write check, so a failed write is indistinguishable from a successful one in the event stream. Every downstream consumer inherits the false positive.

## Verification before action (required)

- Check that `supervisor/scripts/lib/verify-write.sh` does not already exist.
- Verify the tick's FR-filing code path (around `supervisor-tick.sh` friction-file emission) and the reflection's event emission. Note which call sites should be instrumented.
- Read `URGENT-supervisor-event-stream-false-positive-2026-05-17.md` in the INBOX for the current false-positive state.

## Acceptance criteria

- New file `supervisor/scripts/lib/verify-write.sh` created with the `verify_write()` function and accompanying documentation.
- Tick FR-filing code sourced the verify-write.sh and calls `verify_write` before emitting `friction_filed` events.
- Reflection event-emission code sourced verify-write.sh and calls `verify_write` before emitting `*_written` or `*_filed` events.
- A failed verification results in `eventType: "write_verification_failed"` instead of success.
- Changes committed with message explaining the verification-gate addition.
- Completion report at `runtime/.handoff/general-supervisor-proposal-post-write-verify-complete-<iso>.md` pointing to this handoff and the synthesis source.

## Escalation

URGENT if:
- The proposal is superseded by a newer decision (check `decisions/` for ADR-0020 or later authority clarifications on write verification).
- Tick or reflection jobs cannot be modified to source this library due to environment/permission constraints not captured here.
