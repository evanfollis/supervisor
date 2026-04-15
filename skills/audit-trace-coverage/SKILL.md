---
name: audit-trace-coverage
description: Check whether the control plane can actually see enough to govern without reconstructing local context.
applies_to: supervisor
---

# Audit Trace Coverage

## When to use

Use when validating the workspace telemetry stack or when governance decisions
feel under-informed despite significant activity.

## What it does

- checks whether intended surfaces are represented in telemetry
- looks for blind spots between canonical sources and derived indexes
- flags where direct intervention or role behavior is not sufficiently legible

## Invocation

Use over transcript indexes, workspace telemetry, supervisor events, and queue
artifacts.

Required output shape:

- missing or weakly covered surface
- evidence
- governance consequence
- recommended instrumentation or index fix

## Agent notes

- Claude Code: focus on auditability, not observability as a vanity metric.
- Codex: prefer concrete trace gaps and control-plane fixes.
