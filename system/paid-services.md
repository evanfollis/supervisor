---
name: Paid service asset register
description: Every paid external service the workspace depends on. One row per account. Purpose, provisioned-for, status, who knows the credentials path.
updated: 2026-04-18
owner: executive
---

# Paid services register

The principal pays real money for these accounts. Any agent session that
proposes provisioning a new paid service must first check whether one already
covers the need. Any session that mentions paying for a service must update
this file in the same turn.

This is deliberately in `system/` (always-loaded), not in a decision record:
it's current-state, not a historical choice.

## Active paid services

### Hetzner — CPX31 at 5.78.185.6 (Hillsboro, OR)

- Purpose: primary workspace host. Runs all persistent sessions, systemd
  units, atlas/command/skillfoundry services, cloudflared tunnel.
- SSH: `/home/evan/.ssh/hetzner` (local) → server
- Deploy path: `git push` → webhook → autodeploy
- Billed: monthly, Hetzner account

### Cloudflare — account holds synaplex.ai + tunnel + (soon) Pages

- Purpose: DNS for `synaplex.ai` (migrating from Namecheap 2026-04-18),
  cloudflared tunnel fronting `skillfoundry.synaplex.ai`,
  `command.synaplex.ai`, `mentor.synaplex.ai`, `api.synaplex.ai`, and
  (planned) Cloudflare Pages hosting for preflight landing + blog + LCI
  intake embed (per ADR-0024).
- API token: `/opt/workspace/runtime/.secrets/cloudflare_api_token`
  (0600, gitignored). Principal decided 2026-04-19T~00:15Z to keep the
  existing `cfut_cAt4F3J…` token rather than rotate (risk accepted:
  the token sat plaintext in JSONL transcripts). Future sessions: **do not
  re-propose rotation**; principal has already weighed and declined. If you
  think rotation is again warranted, surface evidence of actual misuse, not
  the historical exposure.
- Billed: pay-as-you-go (DNS is free; domain registration and Pages are paid).

### Namecheap — legacy domain registrar (migrating out)

- Purpose: `synaplex.ai` registration. **Migrating to Cloudflare Registrar
  2026-04-18** (principal decision; cheaper). Any session that sees Namecheap
  state should treat it as transient — the destination of record is
  Cloudflare.
- Billed: annual. Should decrease to zero once migration completes.

### Render — account holds `launchpad-lint` MCP on agenticmarket

- Purpose: deploy `launchpad-lint` to the **agenticmarket** MCP marketplace
  so MCP users discover it. Provisioned ~2026-04-11 (week prior to this
  register) specifically for agenticmarket reach. Principal confirmed
  deploy 2026-04-18T12:47Z: "I already have launchpad-lint on agenticmarket."
- Why it's not redundant with Hetzner: the Hetzner deploy at
  `skillfoundry.synaplex.ai/products/launchpad-lint/` is the owned-web
  surface. The Render deploy reaches the MCP marketplace audience, which is
  a different distribution channel.
- Deploy source: `projects/skillfoundry/skillfoundry-products/products/launchpad-lint/render.yaml`
- Credentials: Render account login (principal). Agent sessions do not need
  Render API credentials for routine work because the marketplace deploy is
  already live; re-deploy goes through Render's git auto-build.
- Billed: Render account, likely free-tier or starter. Confirm tier at
  next attended session.

### Anthropic API — Claude Code harness + programmatic Claude calls

- Purpose: powers every Claude session on this host including the executive.
- Billed: per-token, Anthropic account (principal).

### OpenAI / Codex — adversarial-review path

- Purpose: `codex exec --sandbox read-only` is the live adversarial-review
  path per `supervisor/scripts/lib/adversarial-review.sh` (since `/review`
  skill is EROFS-broken, FR-0021).
- Billed: per-token, OpenAI account (principal).

## Retired / off-this-host

### mentor / recruiter hosting

- Removed from this server 2026-04-18 per ADR-0023. They remain as personal
  side projects under the principal's personal accounts, off-workspace.

## How to use this register

- **Before proposing any paid-service provisioning**: read this file. Confirm
  no existing account covers the need.
- **Before walking the principal through a signup flow**: check the relevant
  row here. If the service is listed, read the deployment state cross-check
  rules in `feedback_verify_deploy_state_first.md`.
- **When the principal mentions a new paid account**: update this file in the
  same turn. See FR-0032 for why.
