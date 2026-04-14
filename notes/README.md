# Notes

Lazy-triage capture surface. See ADR-0010.

## Directories

- `TRIAGE/` — untagged captures awaiting classification. Not a priority queue.
  The supervisor triages opportunistically, at least weekly, or on principal
  reference.
- `ARCHIVE/YYYY-MM/` — triaged notes that resolved to "no action warranted."
  Kept for provenance, not for reprocessing.

## What goes here

Only inputs that have been classified against existing substrates and found
to fit none of them. The classifying capture path must record its reasoning
in frontmatter (see below).

Inputs that *do* fit a substrate belong there directly, not here:

- novel proposal → idea ledger (`workspace.sh idea new`)
- priority work for the supervisor → `handoffs/INBOX/`
- current pressure on the workspace → `system/active-issues.md`
- durable architectural decision → `decisions/` (ADR)
- recurring procedure → `playbooks/`

## File shape

```
supervisor/notes/TRIAGE/<iso>-<slug>.md
```

Frontmatter (all fields required unless noted):

```yaml
---
captured_at: 2026-04-14T21:45:00Z
source: slack:C01234:1712345678.123456
author: human            # or agent name
tags: []                 # optional, free-form
attempted_classification: |
  idea ledger: no proposal — observation only
  handoffs/INBOX: not a supervisor action request
  active-issues: not a current-pressure item, no severity
deferred_reason: null    # populated only after an explicit triage defer
---
```

A capture path that cannot populate `attempted_classification` with concrete
per-substrate reasoning fails the writability gate and must either find the
right substrate or escalate via `handoffs/INBOX/` with an explicit context.

## Backlog cap

50 untriaged notes. Writes above the cap are refused with a
`triage_cap_reached` event. The cap is a forcing function: it makes the
supervisor drain before further accumulation.

## Staleness and neglect

- 14 days untouched → `stale_triage` event (once per note)
- 21 days untouched → `triage_neglect` event, compounds into reflection
- Each stale event requires disposition within 7 days: triage, explicit
  defer (with `deferred_reason` recorded), or bulk-archive

## Events

Emitted to `supervisor/events/supervisor-events.jsonl`:

- `note_captured` — write
- `note_triaged` — move to real substrate or archive
- `stale_triage` — 14-day boundary
- `triage_neglect` — 21-day boundary without disposition
- `triage_cap_reached` — refused write due to backlog cap
