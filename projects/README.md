# Project State Surfaces

This directory holds one small current-state file per governed project.

Each file should answer, quickly:

- why the project matters to the control plane right now
- what is currently misaligned, active, or blocked
- what the next supervisor-relevant step is
- which durable artifacts matter most

## Rules

- Prefer one file per project, not project-local ledgers inside the supervisor.
- One file exists only for a project currently under supervisor attention.
  Absence means the project remains primarily a project-session responsibility.
- Keep these summaries current rather than comprehensive.
- Link out to project repos, handoffs, or ideas when deeper detail is needed.
- Remove stale concerns once they stop affecting supervisor behavior.
