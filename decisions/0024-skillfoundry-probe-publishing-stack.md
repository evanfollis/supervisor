# ADR-0024: Skillfoundry probe publishing stack (LCI intake + blog host)

Date: 2026-04-18
Status: accepted
Decided by: principal (Evan), paste 2026-04-18T12:32:24Z, session `40788ae9-1924-485e-b63d-e2d80f8b125c`
Recorded into ADRs: 2026-04-18T23:~15Z, session `847b6afa-...` (11 hours late — see FR-0032)

## Context

Skillfoundry Stage-1 probes need a commercial discovery loop: intake form +
priced offer + a publishing surface for the three probe posts. The implementation
was complete and tested; only three decisions were outstanding:

1. Which intake tool? (Tally / Typeform / Cal.com)
2. What price? ($49 / $99 / contact-to-quote)
3. Which hosting surface? (nginx route on Hetzner / Cloudflare Pages)

And a parallel decision on blog host:

4. Medium (agent-executable via Integration Token) or Cloudflare Pages (one-time setup)?

The principal answered all four in a single numbered paste on 2026-04-18T12:32:24Z.
The receiving session did not capture those answers into governance. 11 hours later a
subsequent executive session was still reporting these items as "principal decision
required." This ADR closes the gap.

## Decision

**LCI intake stack**:
- Intake tool: **Tally** (hosted form, embeddable, agent-deployable)
- Price: **$99** (single price point; no contact-to-quote tier)
- Host: **Cloudflare Pages** (static + Tally embed; no nginx route needed)

**Blog publishing**:
- Host: **Cloudflare Pages** (owned surface, no third-party token dependency)
- Rationale from principal: "Medium doesn't issue tokens anymore" (see
  `reference_medium_no_tokens.md` auto-memory)

Both surfaces share the Cloudflare Pages host; one CF account covers them.

## Consequences

- Probe deploy unblocks as soon as the rotated Cloudflare API token lands in
  `/opt/workspace/runtime/.secrets/cloudflare_api_token`.
- The Medium publishing path is dead (separately recorded in
  `feedback_state_cost_before_signup.md` memory and `reference_medium_no_tokens.md`).
- Tally pricing page integration lives in `skillfoundry-products/products/preflight/`
  build output; no separate hosting infra.

## Alternatives considered

- **Typeform**: more polished UX; rejected on cost and agent-deployability.
- **Cal.com**: scheduling, not form intake; wrong tool for LCI.
- **nginx route on Hetzner**: adds cross-host coupling; rejected in favor of CF Pages.
- **Medium**: API keys no longer issued; removed from consideration.

## Session provenance

- Principal paste: session `40788ae9-1924-485e-b63d-e2d80f8b125c`, 2026-04-18T12:32:24Z
- Recording session: `847b6afa-1693-46c8-948d-af85a892017a`, 2026-04-18T23:~15Z

session_id: 847b6afa-1693-46c8-948d-af85a892017a
