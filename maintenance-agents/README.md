# Maintenance Agents

Declared asynchronous maintenance roles operating under the workspace
supervisor.

These are durable role manifests, not necessarily active processes.

## Purpose

This directory exists so the system can grow into a clean maintenance-agent
structure instead of accumulating ad hoc loops around immediate pain points.

## Manifest shape

One JSON file per role:

`<role-id>.json`

Minimum fields:

- `id`
- `title`
- `status`
- `owner_layer`
- `purpose`
- `trigger`
- `cadence`
- `inputs`
- `outputs`
- `escalate_when`
- `shared_skills`

## Status values

- `planned`
- `inactive`
- `active`
- `superseded`

## Rule

Declaring a role here does not mean it is running. It means the structure is
explicit and ready to be inflated over time without redesigning the control
plane.
