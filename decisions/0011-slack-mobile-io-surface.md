# ADR-0011: Slack as the principal's mobile I/O surface

Date: 2026-04-14
Status: accepted

## Context

The principal operates across laptop, desktop, and phone. The existing
affordances for interacting with the workspace from mobile are unreliable:
terminal-over-SSH is tolerable on laptops but painful on phones, and the
browser-based command surface is intermittently reachable. There is no
always-available way to watch the governance loop move (synthesis landed,
ADR added, host health degraded) or drop a quick observation into the
system without opening a full session.

The workspace already has the durable machinery: telemetry, reflection
loop, synthesis loop, idea ledger, ADRs, handoff INBOX. What's missing is
a phone-friendly view/note surface on top of them.

An earlier draft of this plan (see IDEA-0004) proposed a seven-channel
Slack intake taxonomy with six maintenance-agent roles and a parallel
policy-candidate state machine. That design was rejected on pressure-test
grounds: it duplicated the existing reflection/synthesis loops and
pre-declared structure for a problem that does not exist yet. The current
design is scoped to the actual principal use case.

The full design spec is
`supervisor/docs/slack-signal-intake-and-policy-automation-plan.md`.

## Decision

Adopt Slack as the principal's mobile I/O surface with the following
governance invariants:

1. **Slack is a view and a note-drop, not a source of truth.** The context
   repo answers "what is true now?" Slack is never consulted for that.
2. **Two services only**: a notifier (workspace → Slack) and a normalizer
   (Slack → workspace). Both are systemd-supervised on the control-plane
   host.
3. **Agents never write to Slack.** The notifier is the only writer; the
   normalizer is the only reader. The Slack bot token lives in the
   workspace secret store and is never exposed to Claude or Codex sessions.
4. **Inbound routing is deterministic and tag-driven.** Tags map to
   existing substrates:
   - `idea:` → idea ledger via `workspace.sh idea new` (status `captured`,
     proposer `human`, source `slack:<channel>:<ts>`)
   - `handoff:` → `supervisor/handoffs/INBOX/`
   - `issue:` → `supervisor/system/active-issues.md` staging section
   - untagged → `supervisor/notes/TRIAGE/` (see ADR-0010)
5. **Principal posts are not direct instruction.** Nothing written in
   Slack amends `CLAUDE.md`, writes an ADR, or bypasses the idea
   pressure-test playbook. The highest-privilege destination reachable
   from Slack is `handoffs/INBOX/`.
6. **Silence must be unambiguous.** A daily digest post doubles as
   heartbeat; three missed digests trigger an ops alert. On notifier
   restart, gap detection catches up missed events or posts a summary
   card for large gaps.
7. **Idempotency is explicit.** Normalizer uses `channel_id:message_ts`
   as the idempotency key; the `slack-inbound.jsonl` telemetry log is
   the processing checkpoint. Edits update in place via `edited_ts`,
   never duplicate artifacts.
8. **Attachments become durable workspace state** under
   `/opt/workspace/runtime/.slack-attachments/<yyyy-mm>/`. Artifacts
   reference the local path, never the Slack URL.

Two-stage rollout with concrete SLOs (details in the plan doc):

- **Stage 1 (outbound only)**: notifier ships, measured over 2 weeks on
  latency p95, digest reliability, volume bounds, coverage across event
  types, and gap-recovery behavior.
- **Stage 2 (inbound minimal)**: normalizer ships after this ADR and
  ADR-0010 are accepted, measured on round-trip latency, duplicate rate,
  route coverage, attachment durability, and edit handling.

Further expansion (additional channels, clustering, candidate schemas) is
out of scope. It may only be adopted by inflating already-declared
structure in a future ADR, not by ad hoc growth.

## Consequences

### Positive

- Principal gains an always-available mobile surface for watching the
  governance loop and dropping observations without opening a full
  session.
- Inbound capture paths route into existing substrates, preserving
  governance invariants mechanically rather than aspirationally.
- The Slack token stays out of agent environments, maintaining the
  "no ambient credentials" charter rule.
- Provenance is preserved end-to-end: every Slack-originated artifact
  carries `source: slack:<channel>:<ts>` back to the originating message.

### Costs

- Two new services to operate, monitor, and keep within Slack API rate
  limits.
- A new dependency on an external SaaS for the primary mobile view.
  Workspace functions without Slack, but the mobile affordance degrades
  to "none" when Slack is unavailable.
- Attachment retention creates a new disk-pressure vector, bounded for
  now, revisitable later.
- The supervisor inherits a weekly TRIAGE pass commitment (via ADR-0010)
  that Slack inbound will exercise continuously.

## Alternatives considered

1. **Extend the existing browser command surface for mobile.** Rejected:
   the principal reports it is hit-or-miss and the failure mode is exactly
   the availability problem Slack solves. Improving the browser surface
   does not address the "always-available" requirement on mobile networks.

2. **Build a lightweight CLI-over-SSH mobile app.** Rejected: higher
   friction than Slack for the note-drop case, does not help the passive
   view case at all.

3. **Use email as the I/O surface.** Rejected: push notifications on
   mobile email are less reliable than Slack's, and threading/reactions
   give Slack a richer confirmation channel for the normalizer.

4. **Build the full seven-channel intake taxonomy from the earlier draft.**
   Rejected on pressure-test grounds. See IDEA-0004 and the rewritten plan
   doc for the full reasoning; in short, it duplicated the reflection
   loop and pre-declared structure without corresponding evidence of need.

5. **Let agents post directly to Slack.** Rejected: Slack messages are
   lossier than structured telemetry, and giving agents Slack credentials
   violates the "no ambient credentials" charter rule. The notifier is
   the governed translation layer.
