# ADR-0025: Principal input durable capture

Date: 2026-04-18
Status: proposed
Author: executive, session 847b6afa-1693-46c8-948d-af85a892017a
Triggered by: FR-0032 (three instances of principal-input-dropped in ~1 week)

## Context

The workspace has no structural mechanism to ensure that statements the
principal makes in chat — decisions, credentials, factual corrections — become
durable state. FR-0032 enumerates three instances in one week where principal
inputs were silently dropped or (worse) reversed by a later tick. Security,
money, and trust have all been hit.

Transcripts are intentionally not a truth source for general state (they
contain dead ends and superseded thinking). But the specific subclass of
"principal-delivered durable fact, decision, or credential" needs a capture
path that does not depend on the receiving session's attention span.

A regex-only pattern matcher on user turns is brittle and will miss future
phrasings. The fix needs to be request-response-shaped: the executive knows
*when it asked* for input, and can reconcile against the principal's
subsequent turns for that specific request.

## Decision

Introduce a two-file ledger at the `system/` tier (always-loaded):

- `system/principal-inputs-pending.md` — open requests the executive has
  escalated to the principal. One entry per request, with a request-ID, the
  question, the session that asked, and timestamp.
- `system/principal-inputs-captured.md` — answered requests that still need
  to be promoted into durable state (ADR, active-issues edit, secrets
  path). One entry per request, with the answer, the session that captured
  it, and the promotion action required.

Both files are always-loaded via the M4 `context-always-load` hook.

### Write path — when the executive asks for principal input

When the executive (or any delegated session) writes any of the following:

- "Evan must…"
- "Principal decision required"
- "Awaiting…" (for a principal response)
- An URGENT handoff to principal

…it MUST also append a request entry to `principal-inputs-pending.md`:

```
## REQ-<YYYYMMDD>-<NN> — <one-line summary>
- Asked: <ISO timestamp>
- Session: <session-id>
- Question: <verbatim>
- Expected answer shape: <decision | credential | factual-clarification>
- Surface to update on capture: <ADR path | active-issues section | secrets path>
```

### Reconcile path — SessionEnd hook + supervisor-tick

A reconcile step runs in two places:

1. **SessionEnd hook** (`/root/.claude/hooks/session-end-principal-input-reconcile.sh`):
   scans the just-ended JSONL for user turns newer than the oldest pending
   request. For each pending REQ-ID, checks whether any user turn contains a
   plausible answer (numbered answers, explicit responses, credential-shaped
   strings). On match, moves the entry to `principal-inputs-captured.md` and
   writes a handoff to `supervisor/handoffs/INBOX/` asking the next session
   to promote the answer.

2. **Supervisor-tick**: runs the same reconciliation across ALL pending
   requests, not just the current session's. Catches answers given in
   sibling sessions that the SessionEnd hook missed.

### Credential-shaped string detector (IMMEDIATE escalation)

Independent of the request ledger, any user turn containing a high-entropy
string ≥20 chars that looks like a credential (regex:
`(api|token|secret|key|bearer|auth)[-_]?(token)?[=:\s]\s*[A-Za-z0-9_\-]{20,}`)
triggers an IMMEDIATE URGENT handoff to `supervisor/handoffs/INBOX/`:

```
URGENT — credential detected in chat transcript
Session: <id>
Turn: <iso>
Match: <pattern name, NOT the credential value>
Action: rotate the credential and write the replacement to
        /opt/workspace/runtime/.secrets/<name> via
        `install -m 0600 /dev/stdin …` + Ctrl-D.
```

The handoff does NOT contain the credential value. The credential stays in
the JSONL (it can't be removed), but the handoff points at it without
re-broadcasting.

### Policy delta to `/opt/workspace/CLAUDE.md`

Add to §Agent Behavior:

- **Principal-input capture is non-optional.** When the principal pastes a
  decision, credential, or factual correction, the receiving session MUST
  capture it into the appropriate durable surface (ADR, active-issues edit,
  secrets path) before the session turn ends. "I'll do it next session"
  doesn't exist.
- **Never paste credentials into chat.** Credentials go directly from
  principal's clipboard to `/opt/workspace/runtime/.secrets/<name>` via
  `install -m 0600 /dev/stdin …` + Ctrl-D. Agent sessions read from that
  path; they never receive credentials in chat. If a credential appears in
  chat, it is considered burned and must be rotated.
- **Tick sessions may not reverse principal statements.** If a tick finds
  evidence appearing to contradict `active-issues.md`, it must check
  whether the contradicted line originated from a principal statement in
  the last 72h (via JSONL scan for user-turn matches) before overwriting.
  If yes, escalate rather than overwrite.

## Consequences

- Principal inputs become visible at the `system/` tier the same way
  `active-issues.md` is — any session opening in the workspace sees them
  immediately via the M4 hook.
- Credentials stop sitting plaintext in transcripts silently. They still
  land there if pasted (can't be prevented at the harness level), but they
  trigger an immediate escalation rather than being absorbed.
- Adds an always-loaded file surface. Keep entries terse and age out
  promoted ones quickly.
- Tick sessions gain a new pre-check before overwriting `active-issues.md`;
  slight slowdown, but stops the reverse-the-principal failure class.

## Alternatives considered

- **Pure regex-on-user-turns scanner** — rejected. Too brittle; next
  phrasing variation will miss.
- **No action, rely on session discipline** — rejected. Three instances in
  one week proves discipline is not sufficient.
- **Treat JSONL as a truth source** — rejected. Transcripts contain dead
  ends; elevating the whole file corrupts the truth stack. The ledger is the
  right granularity: only declared requests and their answers get promoted.
- **Per-project mini-ledgers** — rejected for now. Workspace-level covers
  every surface the principal touches; splitting it adds coordination cost.

## Implementation pre-requisites (attended)

- SessionEnd hook install — requires attended `update-config` / `settings.json` edit.
- CLAUDE.md policy amendment — requires attended edit (agent-managed).
- Supervisor-tick reconcile step — requires `scripts/lib/supervisor-tick.sh` edit.
- Add `principal-inputs-pending.md` and `principal-inputs-captured.md` to
  `context-always-load` in `/opt/workspace/CLAUDE.md`.

All four are reversible. None require principal decision beyond "adopt
ADR-0025."

## Adversarial review

Required before acceptance per the `/review` enforcement gate.
Path: `supervisor/scripts/lib/adversarial-review.sh` (Codex, read-only
sandbox). Artifact: `.reviews/adr-0025-*.md`.

session_id: 847b6afa-1693-46c8-948d-af85a892017a
