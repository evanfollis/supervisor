---
from: synthesis-translator
to: general
date: 2026-07-09T03:30:04Z
priority: medium
task_id: synthesis-cycle-count-guidance
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-09T03-26-11Z.md
source_proposal: P6 — Add rotation-aware cycle-count guidance
---

# P6: Add rotation-aware cycle-count guidance

**Type:** CLAUDE.md amendment or reflection template note.

**Blast radius:** Atlas reflections. Low-risk, informational.

---

## Verification before action (required)

- Read the synthesis file at line 161 to understand the full context. This is a low-priority informational proposal.
- Check if any cycle-count guidance already exists in atlas-specific CLAUDE.md or reflection template.
- Determine whether the guidance should live in `/root/.claude/CLAUDE.md` (global), `/opt/workspace/CLAUDE.md` (workspace), or project-specific documentation for atlas.

## Acceptance criteria

- Add guidance that cycle counts (C1, C2, ..., T1, T2, ...) should account for rotation when interpreting age (e.g., "23 cycles open" may span 12 days of real time if cycles run every 12h, or 1 day if 2h apart).
- Guidance is added as a comment or note accessible to reflection authors (so they interpret "cycles open" correctly in future syntheses).
- Keep guidance brief and non-intrusive (this is informational, not a structural change).
- Change committed with clear message: "Add rotation-aware cycle-count guidance per synthesis #133"
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-supervisor-synthesis-cycle-count-guidance-complete-<iso>.md`.

## Escalation

URGENT if:
- No consensus on where this guidance should live (global vs. workspace vs. project). Clarify scope before landing.
