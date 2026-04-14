# Slack as the Principal's Mobile I/O Surface

Slack exists in this workspace for one reason: the principal operates across
laptop, desktop, and phone, and needs an always-available surface to watch the
governance loop move and drop observations into it without opening a terminal.

Slack is not an agent bus. It is not a new source of truth. It is not a parallel
policy pipeline. It is a thin mobile affordance layered on top of the
governance primitives that already exist.

## What this document is and is not

This is a scoped integration plan for a principal-facing I/O surface. It is
deliberately narrower than the original draft, which pre-declared a full
seven-channel intake taxonomy, six maintenance agents, and a candidate/pattern
state machine parallel to the existing reflection loop. That scaffolding was
solving a problem this workspace does not have: it already has telemetry, a
reflection loop, a synthesis loop, an idea ledger, ADRs, and a handoff INBOX.
The job is to make those visible and writable from a phone, not to rebuild
them behind a Slack facade.

This plan introduces one new workspace-level surface (`supervisor/notes/TRIAGE/`)
to preserve a governance boundary that inbound traffic would otherwise violate.
That addition requires an accepted ADR before Stage 2 ships. This document is
the design input; the ADR is a follow-on.

## Design stance

1. Outbound is primary. The principal's core use case is watching the loop
   move. Notifications earn their keep before intake does.
2. Inbound is minimal. One channel. No new pipelines. All routing goes into
   substrates that already exist, plus one new triage surface required to keep
   a governance boundary intact.
3. No agent posts to Slack. Agents emit telemetry. A notifier translates
   telemetry into Slack messages. Slack is never an agent's primary output.
4. Slack messages and threads are not durable state. Content surfaced from
   Slack (attachments, pasted text) may become durable when the normalizer
   writes it into the workspace, but the Slack object itself is never a
   truth source.
5. Principal posts flow through governance. They are high-signal, not direct
   instruction. The routing rules below make this boundary mechanical, not
   aspirational.
6. Silence on Slack must be unambiguous. A quiet feed must be distinguishable
   from a broken notifier.

## Outbound: workspace to Slack

This is the half that justifies the integration. A notifier service reads
existing workspace surfaces and posts to Slack when state transitions the
principal should see occur.

### Sources the notifier reads

All already exist. The notifier is a reader, not a producer.

- `/opt/workspace/runtime/.telemetry/events.jsonl` — control-plane events
- `/opt/workspace/runtime/.telemetry/session-trace.jsonl` — session traces
- `/opt/workspace/runtime/.meta/LATEST_SYNTHESIS` — cross-cutting synthesis
- `/opt/workspace/runtime/.meta/*-reflection-*.md` — per-project reflections
- `/opt/workspace/runtime/.meta/LATEST_SERVER_HEALTH` — host snapshot pointer
- `/opt/workspace/runtime/.meta/LATEST_SERVER_MAINTENANCE` — maintenance report pointer
- `/opt/workspace/runtime/.meta/LATEST_IDEA_FOCUS` — idea-focus pointer
- `supervisor/events/supervisor-events.jsonl` — supervisor-scoped events
- `supervisor/decisions/*.md` — new or status-changed ADRs
- `supervisor/ideas/*.json` — new or disposition-changed idea records

### Channels

Two to start. Add more only when a specific recurring item is drowning out
signal in an existing channel.

- `#supervisor-loop` — governance activity: new synthesis, new/changed ADRs,
  new/changed ideas, escalations, handoffs received, policy notifications
- `#workspace-ops` — operational activity: host health alerts, maintenance
  actions required, session-supervisor failures, reflection/synthesis job
  failures, deploy outcomes

### Post contract: the status card

Every outbound post is a status card, not a raw event echo. The card is
phone-legible first, desktop-followable second.

Top-level (visible on phone preview):

- **Status glyph**: single emoji encoding severity (`:large_green_circle:` /
  `:large_yellow_circle:` / `:red_circle:` / `:information_source:`)
- **Headline**: 6–10 words, plain English, no paths. E.g.
  "New synthesis: three projects show deploy-env drift."
- **Summary**: 1–2 sentences naming what changed and why the principal might
  care. No jargon, no absolute paths.
- **Action hint** (when applicable): one short imperative if the principal
  can do something useful from the phone — "Tap :eyes: to have general pick
  this up on next reentry." Otherwise omitted.

Thread reply (for desktop follow-up, not part of phone preview):

- full artifact path under `/opt/workspace/...`
- originating runtime (`claude`, `codex`, `system`)
- event ID or telemetry ref
- any additional structured context too verbose for the card

### Daily digest

Once per day at a configured time, the notifier posts a state-of-workspace
digest to `#supervisor-loop`:

- count of open items in `handoffs/INBOX/`
- count of ideas by status (`captured`, `framed`, `sandboxed`, `deferred`, etc.)
- count of ADRs added in the last 24h
- last synthesis timestamp and whether it's been consumed
- host health glyph
- notifier heartbeat timestamp

The digest doubles as the heartbeat (see failure semantics below).

### Throttling

- Collapse bursts of the same event type within a 60-second window into one card.
- Routine events (reflection completion, periodic health snapshots) appear
  only in the digest, never as real-time posts.
- Real-time posts only for: synthesis ready, ADR added, idea status changed,
  escalation raised, host health degraded, maintenance action required,
  session-supervisor failure.

## Inbound: Slack to workspace

One channel. No clustering, no candidate schema, no pattern queues. Routing
rules are tag-driven and deterministic.

### Channel

- `#principal-notes`

### Routing rules

For each new message, the normalizer captures it and routes based on the
leading tag or keyword:

| Trigger | Destination | Substrate |
|---|---|---|
| `idea:` or `#idea` | idea ledger | new `IDEA-NNNN` record via `workspace.sh idea new`, `status: captured`, `proposer: human`, `source: slack:<channel_id>:<message_ts>` |
| `handoff:` or `#handoff` | supervisor handoff INBOX | `supervisor/handoffs/INBOX/<iso>-slack-<slug>.md` |
| `issue:` or `#issue` | active issues | dated entry appended to `supervisor/system/active-issues.md` |
| anything else (untagged) | triage surface | `supervisor/notes/TRIAGE/<iso>-<slug>.md` |

Three things this corrects from the previous draft:

1. **Ideas enter the real ledger.** ADR-0005 established the idea ledger as a
   JSON-backed substrate with stable `IDEA-*` IDs, disposition lifecycle, and
   pressure-test playbook. Markdown files dropped into `supervisor/ideas/`
   would sit beside that system, not inside it. The normalizer shells out to
   the ledger CLI so every Slack-captured idea is a first-class ledger object
   and enters the pressure-test loop like any other idea. The `source` field
   carries Slack provenance.

   **Dedupe discipline**: because `idea new` mints a fresh `IDEA-NNNN` on each
   invocation, idempotency cannot rely on path collision. Before calling the
   ledger CLI, the normalizer scans existing ledger records for a `source`
   field matching the current `slack:<channel_id>:<message_ts>`. On match,
   it skips the create and reuses the existing ID. The ledger CLI gains a
   `--idempotency-source <value>` flag that performs the same check atomically
   server-side; the normalizer passes this flag so a crash between pre-scan
   and create cannot produce a duplicate. Stage 2 blocks on this CLI flag
   landing. Same discipline applies to any other substrate mutation that
   mints IDs (currently only the ledger; if `issue:` ever gains IDs, it
   inherits the rule).

2. **Untagged notes do not land in INBOX.** `handoffs/INBOX/` is charter-level
   priority work: the supervisor must process it on every reentry. Routing
   free-form phone notes there would make Slack a command queue and break the
   "not direct instruction" boundary. Untagged notes go to a new
   `supervisor/notes/TRIAGE/` surface that the supervisor triages lazily (see
   below). This is the governance-load-bearing change in this plan and
   requires its own ADR.

3. **`issue:` appends to a staging section of `active-issues.md`**, not the
   canonical body. The supervisor promotes staged entries into the body after
   reviewing them; this keeps the canonical issue list curated rather than
   append-from-phone.

### Triage surface contract

`supervisor/notes/TRIAGE/` is explicitly *not* a drain-on-every-reentry queue.
The supervisor triages it:

- opportunistically during reentry if time permits
- on an explicit triage pass scheduled no less often than weekly
- when the principal references a specific note

Triage means: classify each note and move it to the right substrate (ideas
ledger, handoff INBOX, active-issues body, ADR, playbook, or archive if no
action warranted). Notes that sit in TRIAGE longer than 14 days without
movement produce a `stale_triage` event the next reflection surfaces.

### Attachments

Slack messages with attachments are real — phone screenshots, voice memos,
photos — and the integration must handle them first-class.

- Normalizer downloads attachment bytes to
  `/opt/workspace/runtime/.slack-attachments/<yyyy-mm>/<message_ts>-<sanitized-filename>`
- Generated artifact (idea record, handoff, issue, triage note) references
  the local path, never the Slack URL
- The Slack message itself remains non-durable; the attachment bytes become
  durable because they land in workspace-managed storage under the normal
  file-system trust boundary

Concrete limits (Stage 2 ships with these enforced, not aspirational):

- **Per-file size cap**: 50 MB. Files above the cap are rejected; the message
  is still processed for text content, and an `attachment_rejected` event
  names the file and reason.
- **Per-message total cap**: 200 MB across attachments. Same rejection
  semantics.
- **Content-type allowlist**: `image/*`, `audio/*`, `video/*`, `application/pdf`,
  `text/*`, and Slack-native snippet types. Anything else is rejected.
- **Filename denylist**: reject on match against common secret patterns —
  `*.key`, `*.pem`, `id_rsa*`, `.env*`, `*credentials*`, `*secret*`,
  `*.pfx`, `*.p12`. The principal can override per-message by adding a
  `#allow-sensitive` tag (writes a `sensitive_override` event for audit).
- **Storage quota**: 10 GB soft, 20 GB hard. On soft-cap crossing, emit a
  `slack_attachment_quota_warning` event and post a card to `#workspace-ops`.
  On hard-cap, reject new attachments until cleanup (rotation policy deferred
  until a quota event actually fires).

All rejections produce a Slack reaction naming the reason so the principal
sees immediately what happened without tailing logs.

### Idempotency and recovery

The normalizer must be safe under restart, message edits, and delivery
duplicates. Concrete rules:

- **Idempotency key**: `channel_id:message_ts`. The key is stable across
  retries; `message_ts` does not change when a message is edited.
- **Primary transport is the Slack Events API**, not polling. Events deliver
  new messages, edits, and deletions as distinct event types
  (`message`, `message_changed`, `message_deleted`) with retry semantics,
  so edits to arbitrarily old messages surface without depending on
  polling discovering them. Slack's delivery guarantees are at-least-once;
  the idempotency key handles the duplication.
- **Edit handling**: `message_changed` events include both the original
  `ts` and the new `edited_ts`. The normalizer locates the existing
  artifact by idempotency key and updates it in place, appending an
  `edit_log` entry with the new `edited_ts` and a content-hash of the
  previous body. No duplicate artifact is created. For `idea:` routes
  where the artifact is a ledger record, the normalizer calls
  `workspace.sh idea update <id>` with the new summary; the ledger's
  own `updated_at` and internal history track the change.
- **Deletion handling**: `message_deleted` events mark the corresponding
  artifact with a `deleted_at` frontmatter field and a `source_deleted`
  event. Artifacts are not physically removed — deletion in Slack is a
  signal, not an authoritative retraction of workspace state.
- **Processing order**: for each event the normalizer performs, in order:
  1. check idempotency (telemetry log + ledger-source scan for `idea:`)
  2. write the artifact (atomic rename from tmp) or update existing
  3. persist attachments
  4. append a record to `/opt/workspace/runtime/.telemetry/slack-inbound.jsonl`
     keyed by idempotency key, with current processing state and event type
  5. post Slack reaction confirming destination
- **Restart recovery**: on notifier/normalizer startup, in addition to
  Events-API reconnection, the normalizer issues a bounded backfill call
  to `conversations.history` with a **6-hour overlap window** behind its
  last processed `ts`. Every returned message is passed through the full
  idempotency check; already-processed messages are no-ops. This closes
  two gaps: (a) events that the Events API dropped during downtime, and
  (b) messages posted/edited in the restart window.
- **Crash recovery**: before writing, the normalizer checks the telemetry
  log for the idempotency key. If present and state is `complete`, skip.
  If present and state is partial, resume from the failed step. Artifact
  writes are idempotent on (key + destination path); ledger creates are
  idempotent via the `--idempotency-source` flag described above.
- **Reaction failures are non-fatal.** If the reaction step fails, the
  telemetry log still records `complete`. A missing reaction is a UX
  imperfection, not a correctness bug; the next heartbeat surfaces it.

### Principal posts are not direct instruction

The routing table above is the mechanism. Nothing the principal writes in
Slack amends `CLAUDE.md`, writes an ADR, changes a policy, or bypasses the
idea pressure-test playbook. The highest-privilege destination reachable from
Slack is `handoffs/INBOX/`, which is already the charter-defined mechanism
for human-to-supervisor handoff. The governance contract is preserved.

## Operational model

The notifier and the normalizer are two small services on the same host as
the rest of the control plane. Both are systemd-supervised.

### Auth and credentials

- One Slack bot token, scoped to the specific channels it reads and writes.
- Stored in the workspace secret store used by existing services, not in any
  agent environment.
- Neither Claude nor Codex sessions receive the Slack token. They cannot post
  to Slack directly. The notifier is the only writer; the normalizer is the
  only reader.

### Failure semantics

Outbound is load-bearing, not vanity. A silent Slack must be distinguishable
from a quiet workspace. Liveness is layered:

- **Slack bot presence**: the notifier maintains `presence: auto` while
  healthy and explicitly sets `presence: away` on degradation (heartbeat
  failure, source-read errors, Slack API errors sustained >5 min). The
  presence indicator is the principal's fastest at-a-glance liveness
  signal — no post required.
- **Hourly internal liveness file**: every hour on the wall clock the
  notifier writes its current state to
  `/opt/workspace/runtime/.slack-notifier-heartbeat` (timestamp, last
  successful post, last error, queue depth). The nightly server-health
  capture reads this; a stale heartbeat (>90 min) triggers a
  `slack_notifier_stale` health event.
- **On-demand liveness probe**: the principal may post `status:` or
  `#status` in `#principal-notes`. The normalizer responds within 30
  seconds by reading the heartbeat file and posting a threaded reply
  summarizing health. If no reply arrives, the principal knows the
  normalizer specifically is down.
- **Daily digest**: the digest post serves as passive liveness confirmation
  for the notifier path. A missed digest is an incident on the first miss
  (not the third), because the hourly internal check already tolerates
  short blips — a missed digest means a sustained notifier-path failure.
- **Gap detection on restart**: on notifier startup, it scans event
  sources for entries newer than its last successful post. If the gap
  contains fewer than 10 events, it posts them individually with a
  `[catch-up]` prefix. If larger, it posts a single `gap detected: X
  events between T1 and T2` card with paths to the relevant logs.
- **Inbound never loses messages**. Normalizer down = events queue in
  Slack's Events API delivery plus the 6-hour overlap backfill on
  restart. Slack's own history retention is the only residual failure
  mode, and that's a workspace-wide cap not a normalizer property.
- **Rate limits**: both services respect Slack API limits with exponential
  backoff. Outbound under pressure drops low-priority cards (routine
  events) before high-priority (escalations, health-degraded). Inbound
  never drops.

### Accepted risk: SaaS dependency

If Slack itself is unavailable (regional outage, account suspension,
ToS dispute), the mobile I/O surface degrades to none. The workspace
continues to function — telemetry, reflection, synthesis, and the
idea ledger all remain authoritative and reachable from terminal —
but the principal loses the phone affordance until Slack recovers.

This is explicitly accepted because:

- the workspace already tolerates browser-command-surface unavailability
- no alternative mobile surface with comparable reliability and push
  notification exists at workspace-appropriate scale
- the governance invariants do not depend on Slack: nothing durable
  lives there

If Slack becomes structurally unreliable, the fallback is to revisit
this ADR, not to accumulate band-aids inside the notifier.

### Runtime artifacts

- `/opt/workspace/runtime/.telemetry/slack-inbound.jsonl` — every inbound message the normalizer processes (the processing checkpoint)
- `/opt/workspace/runtime/.telemetry/slack-outbound.jsonl` — every outbound post the notifier sends, indexed by event source
- `/opt/workspace/runtime/.slack-attachments/` — durable attachment bytes
- No `.meta/` surface for Slack. Slack does not produce synthesis-class state.

## Relationship to existing primitives

- The **reflection loop** still mines per-project patterns. Slack does not.
- The **synthesis loop** still produces cross-cutting candidates. Slack does not.
- The **idea ledger** is the home for novelty. Slack inbound `idea:` posts
  enter it as proper `IDEA-NNNN` records via the ledger CLI.
- The **handoff INBOX** is the supervisor's priority queue. Only tagged
  `handoff:` Slack posts enter it; untagged notes go to TRIAGE.
- The **active-issues** file is the curated current-pressure list. Slack
  `issue:` posts land in a staging section, not the canonical body.
- The **context repo** is the answer to "what is true now?" Slack is never
  consulted for that.

If a pattern emerges from Slack inbound that the reflection loop is not
catching, the fix is to improve the reflection loop's inputs, not to build
a parallel pipeline inside the normalizer.

## Failure modes to avoid

1. Slack becomes the durable source of truth.
2. Agents start posting to Slack directly, making it a lossy telemetry mirror.
3. Principal posts bypass ADRs and become direct instruction.
4. Untagged phone notes become a de-facto priority work queue via INBOX.
5. Ideas created from Slack sit outside the ledger instead of inside it.
6. The normalizer grows clustering and candidate logic, duplicating the
   reflection loop.
7. Channel count grows without a specific observed signal-to-noise problem.
8. Outbound throttling is too loose; Slack becomes noisy and the principal
   mutes the channel.
9. Outbound throttling is too tight; the feedback loop goes dark without
   anyone noticing.
10. Notifier silence is indistinguishable from workspace silence.
11. The TRIAGE surface fills up and is never drained, becoming a second
    invisible graveyard.

## Rollout

### Stage 0: Governance precondition

- Accept an ADR establishing `supervisor/notes/TRIAGE/` as a workspace-level
  substrate with the contract above (lazy-triage, not priority queue).
- Accept an ADR (may be the same one) specifying the Slack integration scope,
  auth model, and failure semantics.

Without these ADRs, Stage 2 does not ship. Stage 1 can proceed because
outbound does not alter workspace substrates.

### Stage 1: Outbound only

Provision Slack app, bot token, two channels. Ship the notifier reading
existing artifacts and posting status cards.

Exit SLOs (measured over a 2-week observation window):

- **Latency**: real-time events appear as Slack cards within 120 seconds of
  the underlying event's `captured_at` timestamp, p95.
- **Digest reliability**: daily digest posts within 5 minutes of configured
  time, ≥95% of days. Three consecutive misses = incident.
- **Volume**: real-time card rate ≤20 per day per channel under normal
  operation; sustained >40/day triggers a throttling review.
- **Coverage**: the principal confirms, from phone alone, correct
  situational awareness on at least one instance each of: new synthesis
  landed, ADR added, host health degraded, escalation raised.
- **Gap recovery**: one planned notifier restart is exercised and the
  catch-up/gap-card behavior fires correctly.

### Stage 2: Inbound minimal

Provision `#principal-notes`. Ship the normalizer with the routing table,
attachment handling, idempotency spec, and reaction confirmation.

Exit SLOs (measured over a 2-week observation window):

- **Round-trip latency**: post in `#principal-notes` → Slack reaction with
  destination within 30 seconds, p95.
- **Correctness**: zero duplicate artifacts across the window, verified by
  scanning `slack-inbound.jsonl` for idempotency-key collisions producing
  distinct artifact paths.
- **Route coverage**: at least one real message of each type (`idea:`,
  `handoff:`, `issue:`, untagged) produces a correctly shaped artifact that
  the supervisor picks up on next reentry (for INBOX) or by next weekly
  triage pass (for TRIAGE). "Correctly shaped" means the idea ledger record
  validates against its JSON schema, the handoff matches the handoff
  contract, the issue lands in the staging section, and the triage note
  includes Slack provenance.
- **Attachment durability**: an attachment posted from phone is present in
  `runtime/.slack-attachments/` and referenced by local path from its
  generated artifact.
- **Edit handling**: one principal-edited message is processed correctly,
  updating the existing artifact and appending an `edit_log` entry, not
  creating a duplicate.

### Stage 3: Only if needed

Add channels, tags, or routing rules only in response to a specific observed
problem. Do not pre-declare more structure. The charter rule applies:
novelty expands the system by inflating declared structure, not by adopting
ad hoc loops under pressure.

## Out of scope

Explicitly deferred, not forgotten:

- per-category intake channels (`#signals-friction`, etc.)
- clustering, recurrence keys, severity math inside the normalizer
- policy candidate schemas or a Slack-driven ratification pipeline
- a meta-policy synthesizer fed by accepted policy adjustments
- automatic project-local routing of inbound messages
- Slack threads as durable task state

## Decision rule

If a proposed Slack feature duplicates something the reflection, synthesis,
idea, or handoff systems already do, the feature belongs in those systems,
not in Slack. Slack stays a view, a note-drop, and a heartbeat. That is the
whole contract.
