# Docs

Reference material for concepts that remain useful after they stop belonging in
the current-state bundle.

## Purpose

`docs/` is not working memory. It is a subordinate reference layer for:

- durable explanatory models
- architecture notes still relevant to current decisions
- operating concepts not yet absorbed into a concise ADR or state file

## Promotion and retirement

- If a concept becomes load-bearing policy, promote it to `decisions/`.
- If a concept becomes part of day-to-day operating state, compress its current
  implication into `system/`, `projects/`, or `roles/`.
- If a document reflects completed migration or one-time transition work and is
  no longer referenced by current-state surfaces, let git history carry it and
  remove it from `docs/`.

## Rule

Do not treat `docs/` as ambient session-start context. Open it when the
current-state bundle points at it or when a live issue requires deeper
reference material.
