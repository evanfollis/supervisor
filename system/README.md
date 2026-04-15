# System State Surfaces

This directory is the top-level working memory for the supervisor context
repository.

These files should stay:

- small
- current
- overwrite-friendly
- easy to diff
- safe to load in full at session start

## Files

- `status.md` — best current understanding of the control plane and its rules
- `active-issues.md` — current problems requiring attention
- `active-ideas.md` — current novelty worth active consideration

## Rules

- Do not turn these files into append-only logs.
- Do not duplicate transcript or telemetry detail here.
- If raw evidence matters, link to the runtime artifact instead of copying it.
- If a rationale must persist beyond current state, promote it to `decisions/`
  or `docs/` and keep only the current implication here.
