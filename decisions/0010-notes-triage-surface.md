# ADR-0010: notes/TRIAGE/ as a lazy-triage capture surface

Date: 2026-04-14
Status: accepted

## Context

The supervisor has two high-privilege inbound surfaces for human input:

- `handoffs/INBOX/` — charter-mandated priority work, drained every reentry
- idea ledger (`ideas/`) — novelty pipeline with pressure-test playbook
- `system/active-issues.md` — curated current-pressure list

Nothing between "priority action" and "nowhere." Every capture path that wants
to accept untagged, low-ceremony input from the principal (Slack being the
immediate driver, but not the last) faces the same choice: drop it into INBOX
and make it priority by default, or silently lose it.

Routing untagged input to INBOX breaks the governance contract. INBOX items
are interpreted as "do this next." A free-form phone note like "the mentor
homepage looked weird this morning" should not preempt session planning.
Routing it to the idea ledger is also wrong — not every observation is a
novel idea, and the ledger's lifecycle (captured → framed → pressure_tested)
implies commitment to the proposal. Routing it nowhere loses it.

The missing surface is a low-ceremony capture queue whose contract is
explicitly *classify later*, not *act now*.

## Decision

Introduce `supervisor/notes/TRIAGE/` as a first-class control-plane surface
with lazy-triage semantics.

Contract:

- **Writable** only by capture paths that meet the writability gate below.
  TRIAGE is not a generic dumping ground; a path that does not meet the
  gate must either find a correct substrate or escalate via handoff.
- **Not priority work.** The supervisor does not drain TRIAGE on every
  reentry. Leaving a TRIAGE note untouched for a session is normal.
- **Triage cadence**: opportunistically during reentry when time allows;
  an explicit triage pass scheduled no less often than weekly; or on
  principal reference to a specific note.
- **Triage action**: classify and move. Each note resolves to one of:
  - promote to idea ledger via `workspace.sh idea new`
  - promote to `handoffs/INBOX/` with supervisor-added context
  - promote to `system/active-issues.md` body
  - become input to an ADR or playbook
  - archive under `notes/ARCHIVE/YYYY-MM/` with a one-line disposition
- **Backlog cap**: 50 untriaged notes. Writes above the cap are refused
  at the capture path with an immediate `triage_cap_reached` event and
  a visible signal back to the submitter (for Slack, a reaction emoji
  naming the cap). The cap forces the supervisor to drain before further
  accumulation rather than letting the queue grow unbounded.
- **Staleness enforcement**: a note untouched for 14 days emits a
  `stale_triage` event. Each stale event requires disposition within
  **7 days** — triage, explicit defer (with a one-line reason recorded
  in the note's frontmatter), or bulk-archive. Unresolved stale events
  at day 21 after original capture compound into the next reflection
  and synthesis surface as a `triage_neglect` signal. The reflection loop
  is expected to flag this to the principal when it sees the pattern
  repeat. Staleness is not just *detectable* — it is *costly* to ignore.

File shape:

```
supervisor/notes/TRIAGE/<iso>-<slug>.md
```

Frontmatter fields: `captured_at`, `source` (e.g. `slack:C01234:1712345678`),
`author` (`human` or agent name), `tags` (optional, free-form),
`attempted_classification` (required, see gate below), `deferred_reason`
(present only after an explicit defer during triage).

### Writability gate

A capture path may write to TRIAGE only if it:

1. **Attempted classification against existing substrates first.** The note's
   `attempted_classification` frontmatter field must enumerate which
   substrates the path considered (idea ledger, handoffs/INBOX,
   active-issues, ADR, playbook) and a one-line reason each was rejected.
   An empty or boilerplate value fails the gate; the write is refused.
2. **Records the reason classification failed.** "Untagged phone note with
   no structural signal" is a valid reason. "Unknown" is not.
3. **Carries enough provenance for the supervisor to route it later.**
   At minimum: source, author, captured_at, original content reference.
   A capture path that cannot supply these must escalate via handoff,
   not drop into TRIAGE.

The Slack normalizer's untagged route already satisfies (1) by stating
"no leading tag matched idea:/handoff:/issue:" and (3) by the
`source: slack:<channel>:<ts>` convention. Future capture paths must
demonstrate the same before being authorized to write here. This is a
design-time gate, not a runtime check — the supervisor verifies it
when approving a new capture path, and non-conforming paths are rejected
at ADR review.

Event emissions:

- `note_captured` on write
- `note_triaged` on move/archive, with destination
- `stale_triage` on 14-day boundary (once per note)
- `triage_neglect` on 21-day boundary when stale was not dispositioned
- `triage_cap_reached` on a refused write due to backlog cap

## Consequences

### Positive

- Untagged capture paths gain a correct destination that does not violate
  INBOX semantics.
- Staleness is mechanically surfaced, so the queue cannot rot silently.
- Future capture channels (email, webhook, CLI quick-note) route here
  instead of each reinventing a drop point.

### Costs

- One more surface for the supervisor to attend to on triage passes.
- Principal must learn the tag convention to avoid over-TRIAGE: `idea:`,
  `handoff:`, `issue:` route directly to their substrates; anything else
  is TRIAGE. This is a UX cost paid once.
- Weekly-triage commitment is a new recurring supervisor responsibility.
  If it slips, staleness events will flag it, but it will still reduce
  the value of the capture path.

## Alternatives considered

1. **Route untagged input to `handoffs/INBOX/` anyway.** Rejected: breaks
   the "not direct instruction" boundary that the governance contract
   depends on. INBOX means "do this next" and the charter enforces that at
   reentry.

2. **Route everything to the idea ledger as `captured`.** Rejected: the
   ledger is for proposals, not observations. Mixing free-form notes with
   pressure-test candidates dilutes both.

3. **Route to `active-issues.md` directly.** Rejected: that file is a
   curated supervisor artifact, not an inbox. Direct append would let
   low-quality capture degrade a high-quality surface.

4. **Drop untagged input with a Slack reaction asking for a tag.**
   Rejected: friction exactly where the design is trying to remove it.
   The principal is already on a phone; asking him to retag is the
   interaction we are specifically avoiding.

5. **Name the surface `INBOX-LOW` or `INBOX-TRIAGE`.** Rejected: co-locates
   with the priority queue and invites the same confusion the priority
   queue's contract was designed to prevent. A distinct directory with a
   distinct name keeps the contract legible.
