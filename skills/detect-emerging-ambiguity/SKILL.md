---
name: detect-emerging-ambiguity
description: Identify recurring uncertainty, contract confusion, and boundary hesitation before they become workflow drift.
applies_to: supervisor
---

# Detect Emerging Ambiguity

## When to use

Use when traces, reflections, or maintenance outputs suggest repeated
uncertainty about ownership, policy, or allowed action.

## What it does

- groups similar ambiguity signals
- distinguishes local confusion from systemic ambiguity
- identifies the contract or policy surface most likely to need clarification
- produces a concise ambiguity report

## Invocation

Use over session traces, reflections, idea records, and escalations.

Required output shape:

- ambiguity pattern
- likely affected boundary
- evidence
- local/systemic classification
- recommended clarification path

## Agent notes

- Claude Code: avoid broad taxonomies; compress to the smallest useful set.
- Codex: bias toward concrete artifact changes over abstract commentary.
