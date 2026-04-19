---
name: Agentstack shaping surface
description: Executive shaping file for agentstack — the publication + evaluation lab sibling to atlas and skillfoundry. Third canon instance. Product tier per ADR-0023.
updated: 2026-04-19
tier: product
owner: executive
---

# agentstack — shaping surface

## What this is

Publication + evaluation lab at `agentstack.dev` (domain registration pending principal confirmation). Two tracks: editorial (daily scan + weekly synthesis) and lab (systematic canonical evaluations). Third canon instance after atlas (crypto) and skillfoundry (commercial discovery). See ADR-0026 and approved plan at `/root/.claude/plans/calm-squishing-peacock.md`.

## Current status

- **Scaffold phase (Week 0)**. Project skeleton + governance landed 2026-04-19. Canon adapter work in flight for atlas. Site + domain + first eval pre-registration are next.
- **Tier**: Product (external-facing, commercial-compounding).
- **Operating model**: PM-layer delegated via handoffs under `runtime/.handoff/agentstack-*.md`. Executive shapes; does not edit lab code directly.
- **Session**: `workspace-session@agentstack.service` to be installed once the lab has a working dir under active use.

## What "better" looks like

- First lab eval (memory systems) ships with a valid canon envelope AND a reader-facing writeup — together, not sequentially. Week 6–8 target.
- Atlas + skillfoundry canon adapters land in parallel; all three domains emit canon envelopes passing validator rules.
- Editorial cadence stable: daily scan ≥21 consecutive unattended days; weekly synthesis publishing on schedule.
- Sponsor pipeline opens by Week 12 via agent-drafted + principal-click-send outreach.
- L2 runtime extraction (`discovery-runtime` package) evaluated at Week 20–24 once all three adapters have ≥50 envelopes each.

## Active pressure points

- **Canon adapter → third-instance rule**. The lab must not emit into a diverged epistemic format. Every envelope passes the L1 validator or it doesn't ship.
- **Pre-registration discipline**. Claims land in `lab/.canon/` BEFORE eval runs. No after-the-fact claim synthesis.
- **Methodology credibility**. Every eval adversarially reviewed (Codex) before publish.
- **Commoditized revenue only**. Per `user_revenue_preference_commoditized.md` — no 1:1 audit offerings regardless of inbound demand.
- **FINRA guardrail**. Sponsor outreach is editorial-business, not securities-business. Human-click-send gate on every outbound until a separate legal entity is evaluated (flagged when first sponsor invoice appears).

## Boundaries

- Supervisor does not edit lab code directly; delegate via handoff.
- Lab does not mutate atlas's `.atlas/` or skillfoundry's `memory/venture/` stores. Adapters in those projects produce canon envelopes; the lab reads its own `.canon/`.
- Canon spec changes (v0.1.0 → v0.2.0+) route through context-repository adversarial review, not agentstack unilaterally.
- Revenue surfaces that involve 1:1 delivery are out of scope. Any such proposal should surface the commoditized alternative instead.

## Truth sources (authoritative for this project)

1. `/opt/workspace/projects/context-repository/spec/discovery-framework/` — L1 canon.
2. `projects/agentstack/lab/.canon/` — the lab's canonical envelope store (once populated).
3. `supervisor/decisions/0026-agentstack-lab-third-canon-instance.md` — governance ADR.
4. `projects/agentstack/CURRENT_STATE.md` — front door.
5. Git history of `projects/agentstack/`.

## Interdependencies

- **atlas**: contributes the reference StateStore + models via local-editable install; writes canon adapter that proves the pattern.
- **skillfoundry**: writes canon adapter that finally operationalizes the markdown ontology; adapter pattern learned from atlas's work.
- **command**: gains `/portfolio` view reading all three `.canon/` stores once stable.
- **context-repository**: owns canon spec; any gaps found during adapter work escalate via its adversarial-review process.

## Decision gates (principal)

- **Domain registration ~$12/yr** — pending principal go-ahead (flagged separately).
- **Legal entity for sponsor revenue** — flag when first sponsor invoice appears (month 5+).
- **Paid tier public launch threshold** — verify metrics gate before opening the billing flow (month 4–5).
