---
name: analyze-recurring-friction
description: Distinguish noise from real recurring workflow drag and propose simplifications at the right layer.
applies_to: supervisor
---

# Analyze Recurring Friction

## When to use

Use when there are repeated retries, stalls, re-explanations, or handoff churn.

## What it does

- identifies repeated friction patterns
- distinguishes user-specific, project-local, and cross-project drag
- estimates whether the best intervention is local workflow change, policy
  change, or no action

## Invocation

Use over session traces, telemetry, and project reflections.

Required output shape:

- friction pattern
- likely root layer
- evidence
- proposed simplification
- why the simplification belongs at that layer

## Agent notes

- Claude Code: treat "annoying but acceptable" as distinct from true friction.
- Codex: prefer layer placement clarity over speculative root-cause language.
