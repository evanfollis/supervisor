---
name: compress-policy-from-repetition
description: Turn repeated lower-level resolutions into explicit policy candidates, with boundaries and non-applications.
applies_to: supervisor
---

# Compress Policy From Repetition

## When to use

Use when a maintenance agent or the supervisor sees the same underlying
judgment resolved multiple times across sessions, projects, or escalations.

## What it does

- identifies the stable underlying pattern
- separates the repeated judgment from incidental context
- proposes the narrowest policy artifact that can carry the rule
- states where the proposed policy does not apply

## Invocation

Use as an analysis method over traces, ideas, decisions, and reflections.

Required output shape:

- pattern
- evidence
- proposed policy target
- non-applications
- rollback or exception rule

## Agent notes

- Claude Code: keep the output artifact-oriented, not essay-shaped.
- Codex: prefer durable artifact recommendations over conversational summaries.
