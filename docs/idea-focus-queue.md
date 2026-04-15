# Idea Focus Queue

The idea ledger is the archive. The idea-focus queue is the working surface.

## Purpose

This queue exists so the supervisor can absorb novelty without rereading the
entire archive and without letting active ideas disappear into durable storage.

## Canonical rule

The queue is derived.

- `supervisor/ideas/` is canonical for idea state
- `runtime/.meta/idea-focus-*.md` is canonical for the current compressed view

## Active statuses

The queue should consider these ideas active:

- `captured`
- `framed`
- `pressure_tested`
- `sandboxed`
- `deferred`

These ideas still require governance attention, even if not immediate action.

## Closed statuses

These are not part of the active queue except as recent context:

- `adopted`
- `rejected`

## Priority fields

Idea records may carry these optional prioritization hints:

- `priority`: `low`, `medium`, `high`
- `compoundability`: `low`, `medium`, `high`
- `risk`: `low`, `medium`, `high`
- `review_after`: ISO date or timestamp

These do not replace judgment. They bias the queue so compoundable and urgent
ideas stay visible while low-value noise recedes.

## Reentry rule

On supervisor reentry, read the latest idea-focus artifact first. Use the full
idea record only when one item in the queue needs deeper review.
