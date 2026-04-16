# Role State Surfaces

This directory describes the current operating roles that shape supervisor
behavior.

These are not long theoretical essays. They are small summaries of:

- what a role is for
- what it should load by default
- what it should ignore by default
- what authority boundaries matter right now

Current top-level split:

- `executive` — principal-facing top-level partner
- `supervisor` — governance / policy / reflection
- `operator` — host-control when capability is actually present

## Rules

- Keep role files short and behavioral.
- Put durable theory in `docs/`.
- Put declared future-state structures in `maintenance-agents/`.
- Use these files to keep runtime behavior aligned without forcing archive
  layers into every session start.
