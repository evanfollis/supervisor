# FR-0032 — Principal inputs (facts, decisions, credentials) dropped or reversed between sessions

Status: open
Severity: high
Opened: 2026-04-18T23:~15Z
Session: 847b6afa-1693-46c8-948d-af85a892017a

## Failure class

Principal statements of fact or decision, pasted into an executive session,
do not reliably become durable state. They are acted on (or not) within the
session that receives them and then vanish. Subsequent sessions either:

- ask the same question again (as if the principal never answered), or
- worse, write the opposite of what the principal said into governance
  surfaces (`active-issues.md`, tick commits), as if the principal's statement
  had never occurred.

The JSONL transcript is the only surviving record, and nothing in the stack
reads it for principal-input capture. This is load-bearing: credentials,
product-level decisions, and paid-service state all move through the chat
surface, and all three have now been dropped.

## Evidence — three concrete instances in the same failure class

### Instance A — LCI + blog host + CF token paste dropped (2026-04-18T12:32:24Z)

Principal pasted five numbered answers in one message in session `40788ae9`:

1. Cloudflare API token `cfut_cAt4F3J…9994b`
2. Confirmation that the watcher restart was already done
3. LCI stack: Tally + $99 + Cloudflare Pages
4. Render: new account made, asking for setup info
5. Blog host: Cloudflare Pages ("Medium doesn't issue tokens anymore")

**What happened:** the receiving session acted on none of them in a durable
way. 11 hours later session `847b6afa` was still reporting "Evan must choose
intake tool, set price, decide hosting path" verbatim. The CF token was never
moved from the transcript into a secret path. The LCI decisions were never
captured as an ADR. Closed by ADR-0024 + token-rotation handoff.

### Instance B — agenticmarket deploy statement reversed (2026-04-18T12:47Z)

Principal said: "I already have launchpad-lint on agenticmarket."

**What happened:** a later tick (same day) wrote into `active-issues.md`:
"Canonical deploy target per `deploy/REMOTE_DEPLOY.md` is Hetzner. The
`render.yaml` / `railway.toml` / `fly.toml` in that directory are portability
artifacts, not the active deploy." That directly contradicts what the
principal said. The tick read the deploy docs and ignored the principal's
primary statement. Corrected in the same pass as this FR.

This is also the reason a paid **Render account** provisioned last week was
not tracked anywhere in governance — it was mentioned in chat, never recorded.

### Instance C — Render Blueprint walkthrough (2026-04-18, earlier)

Documented in `feedback_verify_deploy_state_first.md` auto-memory. An executive
session walked the principal through a 5-step Render setup for launchpad-lint,
reaching the payment screen, before noticing the service was already live on
Hetzner. Same class: secondary sources trusted over primary state (including
the principal's own prior statements in chat).

## Why this keeps happening

- Transcripts are **not** in the truth-source stack (see `supervisor/CLAUDE.md`
  §Truth sources). This is correct for general state — conversation is full of
  dead ends — but it leaves a hole at the specific subclass of "principal
  delivered a durable fact/decision/credential."
- No surface scans user-turn content for pasted decisions, numbered answers,
  credential-shaped strings, or factual corrections of active-issues state.
- Sessions end without a reconcile step against "what did the principal hand
  me this session that needs to become durable state?"
- The executive's own output contract (§Output contract in `supervisor/CLAUDE.md`)
  requires "what only the principal can decide or unblock" — but there's no
  symmetric contract for "what the principal already decided or unblocked."

## Why it matters

- **Security**: credentials pasted in chat sit in plaintext JSONL files
  readable by every session and reflection job. The CF token in Instance A was
  exposed for 11h+ before anyone noticed.
- **Money**: the Render account in Instance B was not tracked anywhere. A
  paid service not in governance is a service that can be duplicated,
  forgotten, or cancelled by accident.
- **Trust**: asking the principal the same question they already answered is
  exactly the "stack doesn't hold pressure" failure mode §Stack progression is
  trying to eliminate.

## Proposed structural fix

**ADR-class, not tick-class.** Do NOT attempt a tick-session regex hook; the
principal's phrasing varies and a brittle matcher will miss the next instance.

Draft at `supervisor/decisions/0025-principal-input-durable-capture.md`
(Status: proposed). The broad shape:

- When the executive surface asks the principal for input (decision,
  credential, factual clarification), it writes an open-ledger entry to
  `supervisor/system/principal-inputs-pending.md` with a request-ID and the
  question.
- A SessionEnd hook + the supervisor-tick both reconcile that file against
  JSONL user turns. If a request-ID's answer appears in the transcript, the
  hook moves the entry into `principal-inputs-captured.md` and writes a
  handoff asking the next session to promote the answer into durable state
  (ADR, active-issues edit, secrets path).
- Credential-shaped strings (regex: `(api|token|secret|key)` followed by
  high-entropy span ≥20 chars) in user turns emit an IMMEDIATE URGENT
  handoff: "credential detected in chat; rotate and route to secrets path."
- `principal-inputs-pending.md` becomes always-loaded via the M4 hook.

This makes the principal's durable statements visible at the same tier as
`active-issues.md` and forces reconciliation before the loop can close.

Full design: ADR-0025 (proposed).

## Policy delta (take now, no structural work needed)

1. **No credentials in chat, ever.** Principal writes them to
   `runtime/.secrets/<name>` via `install -m 0600 /dev/stdin …` + Ctrl-D.
   This is a durable rule, not a one-off. Carried as an amendment candidate
   to `/opt/workspace/CLAUDE.md`.
2. **When the principal states a fact about deploy state, paid services, or
   product decisions, the receiving session MUST capture it** into an ADR
   (decisions) or the relevant `projects/` or `system/` surface before the
   session turn ends. Not "eventually" — in-session.
3. **Tick sessions may not reverse principal statements.** If a tick finds
   evidence that appears to contradict `active-issues.md`, it must check
   whether the `active-issues` line originated from a principal statement in
   the last 72h (via JSONL scan) before overwriting. If yes, escalate rather
   than overwrite.

## Cross-references

- ADR-0024 (decisions captured from the dropped paste)
- ADR-0025 draft (proposed structural fix)
- `feedback_verify_deploy_state_first.md` (prior instance in same class)
- `feedback_evan_above_system.md` (why this class matters)
- Pressure-queue §"Executive must preserve latent structure, not mirror literal phrasing"

session_id: 847b6afa-1693-46c8-948d-af85a892017a
