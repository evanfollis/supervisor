---
id: FR-0034
title: skillfoundry-harness session captures skillfoundry-valuation-* handoffs via broad glob
Status: open
opened: 2026-04-20T18:49Z
source: tick 2026-04-20T18-49-00Z; escalation general-skillfoundry-tick-escalation-2026-04-20T17-02-19Z.md
---

# FR-0034 — Dispatch glob overcapture: harness swallows valuation handoffs

## What happened

The prior tick (16:49Z) re-routed a dead-lettered URGENT as
`skillfoundry-valuation-urgent-carry-forwards-2026-04-20T16-49Z.md`. The
harness tmux session is named `skillfoundry` — `dispatch-handoffs.sh`
matched `skillfoundry-valuation-*` against the `skillfoundry-` prefix and
delivered the handoff to the harness session.

The harness session correctly refused to execute it (files are in
`skillfoundry-valuation-context/`, outside its mandate) and escalated via
`general-skillfoundry-tick-escalation-2026-04-20T17-02-19Z.md`. No harm done,
but the valuation carry-forward work remains unactioned.

## Root cause

Two interacting gaps:

1. **FR-0033**: `dispatch-handoffs.sh` cannot route `URGENT-`-prefixed files
   natively, forcing the tick workaround of creating renamed copies.

2. **No session for `skillfoundry-valuation`**: `sessions.conf` registers only
   `skillfoundry` (harness). The valuation project exists in
   `skillfoundry-valuation-context/` and is in `projects.conf`, but has no
   named tmux session. Any `skillfoundry-*` handoff gets delivered to the
   harness session — the only session that matches.

## Impact

Valuation carry-forward work has been blocked for 2 days (Items 1 and 2 of
the re-routed handoff). Each re-routing attempt lands in the wrong session.

## Fix options (all require attended session)

1. **Register a `skillfoundry-valuation` tmux session** in `sessions.conf`
   pointing at `skillfoundry/skillfoundry-valuation-context/`. This gives
   the dispatch a real target.

2. **Rename handoffs for the harness session** to `skillfoundry-harness-*`
   (and treat `skillfoundry-valuation-*` as a separate namespace). Requires
   updating sessions.conf and any tooling that generates harness handoffs.

3. **Short-term only**: Attended session directly runs valuation tick to clear
   the 2-item carry-forward backlog, bypassing the dispatch entirely.

## Workaround

Attended session must manually route
`/opt/workspace/runtime/.handoff/skillfoundry-valuation-urgent-carry-forwards-2026-04-20T16-49Z.md`
to a valuation-context session (or run the work directly in an attended pass).
