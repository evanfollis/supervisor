---
from: synthesis-translator
to: general
date: 2026-05-01T15:32:17Z
priority: high
task_id: synthesis-post-action-verification
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-01T15-28-00Z.md
source_proposal: "Proposal 4 [MEDIUM, REPEAT — 4th cycle]: Post-action state verification in tick wrapper"
---

# Post-action state verification in tick wrapper

## Summary

Add post-action verification to `supervisor/scripts/lib/supervisor-tick.sh` to validate that file writes actually succeeded before emitting telemetry events claiming they did. The current "ghost-write" pattern (Pattern 2 in the synthesis) has persisted for 9 windows — events assert file writes that contradict primary evidence on disk.

## The problem

Supervisor ticks emit telemetry events claiming successful file writes (e.g., "FR-0038 written to friction/", "active-issues.md updated"). However, primary file-system checks (ls, test -f) reveal the files do not actually exist or are not updated. This is now the 9th synthesis window with this pattern.

**Evidence:**
- Three ticks (04:49Z, 06:49Z, 08:49Z) claimed FR-0038/0039 written to friction/ but `ls friction/` shows files ending at FR-0037
- active-issues.md is dated 2026-04-25 (6 days stale) but ticks claim it was updated
- The 08:49Z tick stated "verified on disk after write" — empirically false

This breaks the trust model: any consumer (meta-scan, executive dispatch, carry-forward gate, this synthesis job) that trusts event claims without file verification draws false conclusions.

## Implementation sketch

After any `Write` tool call that targets a file path in supervisor-tick.sh, verify the write succeeded before emitting a telemetry event claiming success:

```bash
# Example: after writing a file via the Write tool
target_file="$1"
# ... Write tool call to create/update $target_file ...

# Post-action verification before event emission
if ! test -f "$target_file"; then
  echo "supervisor-tick: WRITE FAILED — $target_file does not exist after Write tool call" >&2
  emit_event "failure" "write_verification_failed" "$target_file"
  exit 1
fi

# File exists; safe to emit success event
emit_event "success" "file_written" "$target_file"
```

Apply this pattern to every file-write operation in supervisor-tick.sh that currently emits a success event without verifying.

## Scope

This verification should cover:
- FR (friction) file writes to `supervisor/friction/` 
- active-issues.md updates
- Any other supervisor-generated files written during the tick

The verification is a blocking gate: if the Write fails, the tick should emit a failure event and not proceed to claim success.

## Status

- 4th cycle of this proposal being raised
- 3 existing INBOX copies from prior synthesis cycles
- Root cause still undiagnosed (whether Write tool is silently failing, paths are wrong, or permissions block writes)

## Verification before action (required)

- Read `supervisor/scripts/lib/supervisor-tick.sh`
- Search for `Write` tool invocations and subsequent event emissions
- Check if any post-write `test -f` verification already exists
- Run `git log --oneline -10` on supervisor/ to see if this has been landed via another path

## Acceptance criteria

- Identify all file-write operations in supervisor-tick.sh that currently emit success events
- Add `test -f <file>` verification immediately after each Write call
- If verification fails, emit `eventType: "failure"` with reason "write_verification_failed"
- If verification succeeds, proceed with original success event
- Single commit with message: "Add post-action state verification to supervisor-tick (Proposal 4, 4th cycle)"
- Commit message explains: prevents ghost-write events; verifies actual filesystem state before claiming success

## Testing

After implementation, the next supervisor tick run should either:
1. Emit verified success events for actual file writes, OR
2. Emit failure events and diagnostic info if Write fails

You can manually test by running a tick and checking that:
- Files claimed as written actually exist on disk
- Event log shows matching file paths
- No "verified on disk" event contradicts filesystem reality

## Escalation

URGENT if:
- Post-write verification is already implemented in supervisor-tick.sh from a prior commit. Write completion report saying "already landed at commit <SHA>" and close.
- Investigation of the failing Write calls reveals the root cause (e.g., incorrect file paths, permission issues, tool behavior). Include the diagnosis in the completion report.
- A recent supervisor-tick run has created fresh ghost-write evidence since the synthesis was generated. Include that evidence and propose whether this fix is sufficient or whether deeper instrumentation is needed.
