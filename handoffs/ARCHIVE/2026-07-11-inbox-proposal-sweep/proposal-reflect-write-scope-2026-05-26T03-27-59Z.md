---
from: synthesis-translator
to: general
date: 2026-05-26T03:27:59Z
priority: high
task_id: synthesis-reflect-write-scope
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-26T03-23-30Z.md
source_proposal: Proposal 2 — Clarify that reflect.sh sessions may delete untracked workspace infrastructure files
---

# Proposal 2: Clarify that reflect.sh sessions may delete untracked workspace infrastructure files

**Type:** CLAUDE.md amendment or `reflect-supervisor-prompt.md` clarification.

**What:** Add explicit language that the "no project code modification" constraint in reflection jobs does not apply to untracked files under `supervisor/scripts/lib/` that are test artifacts (zero-byte, no functional content). Reflection sessions may delete such files without committing.

```markdown
### Reflection write scope
The "do not modify project code" constraint applies to functional code
in project repos. Untracked zero-byte test artifacts under
`supervisor/scripts/lib/` are workspace infrastructure, not project
code, and may be deleted by reflection sessions to maintain working-tree
hygiene.
```

**Why:** This eliminates the 34-cycle FR-0043 false-positive cascade immediately. The charter already permits supervisor sessions to edit `scripts/lib/` — the misreading is specific to reflection jobs interpreting their constraint too broadly. A one-sentence clarification in the reflection prompt or CLAUDE.md unblocks the fix without granting any new authority.

**Blast radius:** Supervisor reflection job only (automatic). Does not affect project reflections.

## Verification before action (required)

- Run `grep -c "Reflection write scope" /opt/workspace/CLAUDE.md` to verify this clarification is not already present.
- Read the "Automated Self-Reflection Loop" section in `/opt/workspace/CLAUDE.md` to confirm placement target.
- Verify the test artifacts still exist: `ls -la /opt/workspace/supervisor/scripts/lib/.erofs-test-meta-reflection /opt/workspace/supervisor/scripts/lib/TEST_WRITE_2951547 2>/dev/null`

## Acceptance criteria

- New subsection "### Reflection write scope" is added to the "Automated Self-Reflection Loop" section in `/opt/workspace/CLAUDE.md`.
- The exact text above (or equivalent formulation) is added to the file.
- Change committed with message: "Clarify reflect.sh write scope for workspace infrastructure (C59 P2)"
- Completion report at `/opt/workspace/runtime/.handoff/general-synthesis-reflect-write-scope-complete-<iso>.md` pointing to this handoff and source synthesis.

## Escalation

URGENT if:
- The clarification is already present in `/opt/workspace/CLAUDE.md` (primary-verify via grep). Write "already landed" completion report instead.
- The test artifacts have already been deleted by a prior supervisor reflection. Write "artifact cleanup already executed by prior cycle" completion report instead.
- The proposed rule conflicts with a more recent decision. Surface the conflict.
