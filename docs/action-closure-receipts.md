# Action closure receipts

`done` is a verified lifecycle state, not an agent assertion. Close an action
only with an absolute path to a schema-versioned JSON receipt:

```bash
python3 /opt/workspace/supervisor/scripts/lib/action-ledger.py transition ACT-NNNN \
  --to done \
  --completion-receipt /opt/workspace/runtime/.meta/action-closure-receipts/ACT-NNNN.json
```

The ledger validates the receipt under its lock, proves pushed code is reachable
from the declared remote ref, verifies hashes for artifacts and transcripts,
archives the action's source artifact without clobbering, and publishes the
terminal transition through a crash-recoverable journal. `action-ledger.py
check` revalidates typed receipts and recovers any prepared transaction before
reporting state.

## Schema version 1

Every dimension is required. Its `status` is either `complete` or
`not_applicable`; `not_applicable` requires a specific `reason`. The schema also
recognizes `deferred` in drafts, but a receipt containing any deferred dimension
cannot close an action.

```json
{
  "schema_version": 1,
  "action_id": "ACT-NNNN",
  "completed_at": "2026-07-20T12:00:00Z",
  "code_landed": {
    "status": "complete",
    "landings": [
      {
        "repository": "/opt/workspace/supervisor",
        "commit": "FULL_40_CHARACTER_LOWERCASE_GIT_SHA",
        "remote_ref": "origin/main"
      },
      {
        "repository": "/opt/workspace/projects/example",
        "commit": "FULL_40_CHARACTER_LOWERCASE_GIT_SHA",
        "remote_ref": "origin/main"
      }
    ]
  },
  "verification_passed": {
    "status": "complete",
    "evidence": [
      {
        "kind": "command",
        "command": "python3 scripts/lib/tests/test_action_ledger.py",
        "exit_code": 0,
        "observed_at": "2026-07-20T12:00:00Z",
        "transcript_path": "/absolute/path/to/full-verification-output.txt",
        "transcript_sha256": "64_CHARACTER_LOWERCASE_SHA256"
      }
    ]
  },
  "deployed": {
    "status": "not_applicable",
    "reason": "This change has no independently deployed runtime."
  },
  "state_projection_refreshed": {
    "status": "complete",
    "path": "/absolute/path/to/refreshed/state.json",
    "sha256": "64_CHARACTER_LOWERCASE_SHA256"
  },
  "source_artifact_dispositioned": {
    "status": "complete",
    "source_path": "/opt/workspace/supervisor/handoffs/INBOX/source.md",
    "archive_path": "/opt/workspace/runtime/.meta/handoff-archive/2026-07-20/source.md",
    "sha256": "64_CHARACTER_LOWERCASE_SHA256"
  }
}
```

For a one-repository action, `code_landed` may retain the backward-compatible
singular `repository`, `commit`, and `remote_ref` fields. A multi-repository
action must use the non-empty `landings` list; mixing the two forms is rejected.
Every listed commit is independently proven reachable from its declared remote.

### Evidence kinds

- `path`: `value` and `sha256` for a regular, owned, non-symlink file.
- `command`: `command`, zero `exit_code`, `observed_at`, and hashed full
  `transcript_path`.
- `service`: `unit`, `result` (`active` or `success`), `observed_at`, and hashed
  full `transcript_path`.
- `url`: HTTP(S) `value`, status in `200..399`, `observed_at`, and hashed full
  `transcript_path`.

Receipts and referenced files must be absolute, owned by the current effective
user, regular non-symlink files, and not group/world writable. The source path
must match the action's declared source. Archives must remain under
`/opt/workspace/runtime/.meta/handoff-archive/` and share a filesystem with the
source so the no-clobber disposition remains crash-safe.

The state-projection hash is verified when the action closes and embedded in the
terminal ledger record. Later `check` runs require the receipt to remain byte-for-
byte equivalent to that embedded closure, but do not require the living projection
file to retain its old hash. A subsequent truthful refresh must not invalidate
historical completion evidence.

## Honest use

- Preserve full command, service, or URL output; do not summarize it into the
  transcript.
- Use `not_applicable` only when the lifecycle dimension genuinely does not
  exist for the action. It is not a substitute for unfinished work.
- A pushed commit is not a deployment. Represent the two dimensions
  independently.
- If any required work is deferred, keep the action non-terminal and record the
  concrete blocker or next owner in the ledger.
