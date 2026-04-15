# Workspace synthesis — {{ISO_NOW}}

You are running as an unattended 12-hour synthesis job at the workspace level. You aggregate *across* the per-project reflections that have been written in the last window and look for cross-cutting patterns that justify amending shared infrastructure.

This is the step where "the system generalizes from project-specific feedback to make the whole workspace better."

## Inputs

1. `{{WORKSPACE_META_DIR}}/*-reflection-*.md` — per-project reflections. Focus on files whose timestamp falls within the last 24h. Ignore files whose first line begins with `# Reflection skipped`.
2. `{{WORKSPACE_ROOT_CLAUDE_MD}}` — current workspace principles.
3. `/root/.claude/CLAUDE.md` — global instructions.
4. Previous synthesis outputs under `{{WORKSPACE_META_DIR}}/cross-cutting-*.md`. Check whether any standing recommendations have landed or are still open.
5. `{{WORKSPACE_TELEMETRY_FILE}}` — shared telemetry. Tail the last few thousand lines if needed.
6. `{{WORKSPACE_SCRIPTS_ROOT}}/` — the current shared toolkit. Check whether any proposed shared primitive already exists.

## What to produce

Write a single markdown file at `{{OUTPUT_FILE}}` with these sections:

### Window
The per-project reflection files you actually read (file paths and dates). If fewer than 2 reflections exist in the window with non-trivial content, state that and exit with a short note — synthesis needs breadth.

### Cross-cutting patterns
At least 2, at most 5. Each pattern must:
- Cite **specific** findings from **at least 2** per-project reflections (quote or link).
- Name the underlying failure class, not just the symptom.
- Ranked by workspace-wide leverage.

### Proposed workspace changes
Ranked. Each proposal must be one of:
- **CLAUDE.md amendment** — exact proposed text for `{{WORKSPACE_ROOT_CLAUDE_MD}}` (delta, not rewrite). State which section.
- **Shared primitive** — a new or updated file under `{{WORKSPACE_SCRIPTS_ROOT}}/`. State purpose + 5-line sketch.
- **Enforcement gate** — a systemd/git-hook change that turns an honor-system rule into a hard check.

Each proposal needs a "blast radius" line stating which projects it affects and whether it's opt-in or automatic.

### Standing recommendations
List prior synthesis recommendations that are **still open** (not yet landed). If any have been open for >3 cycles, flag them — either the recommendation was wrong, or the workspace is ignoring its own meta-loop.

### Questions for the human
Maximum 2. Only blockers.

## Constraints

- **Do not** modify `{{WORKSPACE_ROOT_CLAUDE_MD}}` or any project file. You propose; the human disposes.
- **Do not** commit or push anywhere.
- **Do not** create shared primitives yet — only propose with a sketch.
- Output must be under 500 lines. Quality over quantity.
- If you find a recurring pattern that's actually just the same root cause surfacing in different projects, say so explicitly — that's more valuable than treating each instance separately.
- If the workspace is already handling a pattern well, say so — don't manufacture findings to justify the run.
