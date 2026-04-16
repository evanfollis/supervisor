# Project State Surfaces

This directory holds one small current-state file per governed project.

Each file should answer, quickly:

- why the project matters to the control plane right now
- what is currently misaligned, active, or blocked
- what the next supervisor-relevant step is
- which durable artifacts matter most

Taken together, these files are the executive's running shaping status across
the governed project set. They should make it obvious, at a glance, which
projects are under active pressure, which are monitor-only, and why.

## Rules

- Prefer one file per governed project, not project-local ledgers inside the
  supervisor.
- Files may describe either active pressure/shaping or deliberate monitor-only
  status.
- Keep these summaries current rather than comprehensive.
- Link out to project repos, handoffs, or ideas when deeper detail is needed.
- Remove stale concerns once they stop affecting supervisor behavior.
