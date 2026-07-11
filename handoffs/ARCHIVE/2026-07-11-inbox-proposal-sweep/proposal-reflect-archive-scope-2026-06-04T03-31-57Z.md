---
from: synthesis-translator
to: general
date: 2026-06-04T03:31:57Z
priority: high
task_id: synthesis-reflect-archive-scope
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-04T03-27-25Z.md
source_proposal: "P-fpreflect — Scope reflect.sh HEAD check to exclude archive operations"
---

# P-fpreflect — Scope reflect.sh HEAD check to exclude archive operations (3 cycles in INBOX)

**Type:** Shared primitive update — `reflect.sh`

**Sketch:** Narrow the dirty-tree and HEAD mutation checks to exclude `handoffs/ARCHIVE/` directory:

```bash
# Current (check all changed files):
changed=$(git diff --name-only HEAD)

# New (exclude archive directory):
changed=$(git diff --name-only HEAD | grep -v '^handoffs/ARCHIVE/')
```

**Blast radius:** Supervisor only (automatic). Eliminates both `dirty-tree` and `mutated-head` false-positive URGENTs.

**Rationale (from synthesis):** The reflect.sh script includes safety checks to prevent reflection from running against a dirty tree or mutated HEAD state (lines that emit `dirty-tree` and `mutated-head` URGENTs). These are correct in intent — preventing reflection from running during active edits or corrupted state. However, handoff archival operations (moving completed handoffs to `handoffs/ARCHIVE/`) trigger these checks even though archival is a safe, post-hoc operation. Adding an exclusion for `handoffs/ARCHIVE/` prevents false-positive URGENTs while maintaining the safety net for genuine dirty/corrupted states.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` to locate the dirty-tree and HEAD mutation checks and the `git diff --name-only HEAD` invocation.
- Verify the exact line number and current state of this check.
- Review recent URGENTs in supervisor-reflection files to confirm they include `dirty-tree` or `mutated-head` entries tied to `handoffs/ARCHIVE/` changes.
- Confirm `handoffs/ARCHIVE/` is the correct path for archived handoffs (check supervisor/handoffs/ structure).

## Acceptance criteria

- The `git diff --name-only HEAD` invocation is updated to exclude `handoffs/ARCHIVE/` via `grep -v '^handoffs/ARCHIVE/'`.
- Both the dirty-tree check and HEAD mutation check use the filtered `changed` variable.
- Change committed with message: "Exclude handoffs/ARCHIVE/ from reflect.sh dirty-tree checks — eliminate false-positive URGENTs on archival (C77 synthesis P-fpreflect)"
- After landing: verify that archival operations no longer trigger `dirty-tree` or `mutated-head` URGENTs in supervisor reflections.
- Confirm the safety net still fires for genuine dirty-state conditions (edits to non-archive files).

## Escalation

URGENT if:
- The file or check structure does not match the description (reflect.sh may have changed).
- The change is already present (write completion report "already landed at commit <SHA>" and close).
- The `handoffs/ARCHIVE/` path does not exist or is named differently (adjust the grep pattern and escalate if the archive structure is unknown).
