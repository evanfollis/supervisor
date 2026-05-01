---
name: Ghost-write event claims
status: Open
created: 2026-05-01
source: cross-cutting-synthesis-2026-05-01T03-27-05Z / supervisor-tick observations
severity: high
---

# FR-0038: Supervisor tick events claim files written that don't exist on disk

## What happened

Supervisor tick events have repeatedly claimed to write FR friction files and
update `active-issues.md`, but the writes either never execute or execute to
the wrong path. Example: ticks from 2026-04-30 through 2026-05-01 all emitted
events claiming FR-0038 and FR-0039 were written; `ls friction/` showed FR-0037
as the highest number across 7+ consecutive synthesis cycles.

The same pattern extends to `active-issues.md` (claimed "refreshed" in multiple
tick events while the file's `updated:` frontmatter remained at 2026-04-25) and
to project tick wrapper URGENT files (command/context-repo tick wrappers emitted
events claiming INBOX URGENT files were written; the files did not exist).

## Why it matters

The event model is no longer a reliable truth source. Any consumer that trusts
event claims without primary verification (e.g., `ls`, `grep`) will draw false
conclusions about workspace state. This degrades monitoring, meta-scan, and
executive dispatch.

## Root cause candidates

- File writes executed against paths that don't resolve to Tier-A writable
  surfaces (e.g., OS-level sandbox rejecting writes silently without error)
- Variable interpolation failures producing wrong paths
- Write tool returning success before the filesystem confirms the write

## Remediation

Tick sessions must verify each claimed write by reading the written file before
emitting the corresponding event. An event without primary-source verification
is a ghost claim and cannot be trusted.
