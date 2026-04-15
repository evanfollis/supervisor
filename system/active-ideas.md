# Active Ideas

## IDEA-0004 — Slack signal intake and friction-to-policy automation

- Status: `adopted` (Stage 1 deployed 2026-04-15)
- Why it matters: gives the principal a mobile I/O surface into the
  governance loop without collapsing governance boundaries.
- Stage 1 state: `workspace-slack-notifier.timer` active on 60s
  cadence, posting status cards to `#supervisor-loop` and
  `#workspace-ops` in the Signal Foundry workspace via the
  `workspace-supervisor` bot (token in `config/slack.env`).
- Stage 1 exit gaps: daily digest post, throttling, heartbeat/health
  integration. Track before declaring SLO window complete.
- Stage 2 (inbound `#principal-notes` normalizer): deferred. Requires
  a public Events API endpoint.
- Plan: `/opt/workspace/supervisor/docs/slack-signal-intake-and-policy-automation-plan.md`
- ADRs: `0010` (notes/TRIAGE surface), `0011` (Slack integration
  contract).

## IDEA-0003 — Redesign context-repository around current-state context surfaces

- Status: `pressure_tested`
- Why it matters: fixes a control-plane mismatch between intended and
  actual use of the context repository
- Next step: have the `context-repo` project session produce and begin
  applying a redesign proposal centered on `system/`, `projects/`, and
  `roles/` current state files plus `session_id` provenance in commit
  messages
- Handoff out: `/opt/workspace/runtime/.handoff/context-repo-context-repo-redesign.md`

## IDEA-0002 — Interaction-derived signal triage for compoundable value

- Status: `framed`
- Why it matters: determines whether the system can distinguish noise
  from genuinely compounding signals across ordinary interaction
- Next step: define a signal taxonomy and identify the first source
  surfaces to classify
