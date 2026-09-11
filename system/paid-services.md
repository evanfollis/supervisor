---
name: External service administrative register
description: Administrative record of external accounts and their intended role. Runtime status must be verified from primary sources; this file is not a live-status projection.
updated: 2026-09-11
owner: executive
---

# External services register

These accounts may carry cost, credentials, or external ownership. Before
proposing a new service, check whether one already covers the need. Do not infer
live deployment, billing tier, registrar state, or credential validity from
this administrative record; use primary provider, host, and endpoint evidence.
The register is not guaranteed complete: absence is a search lead, not evidence
that no account exists.

Credential values must never appear here. Paths may be recorded; validate only
non-secret presence, permissions, and authentication status in operational
receipts.

## Known external accounts (billing status not host-verified)

### Hetzner — CPX31 at 5.78.185.6 (Hillsboro, OR)

- Purpose: primary workspace host. Runs persistent sessions, the Supervisor
  control plane, Command, Skillfoundry services, Synaplex operational jobs, and
  the Cloudflare tunnel.
- SSH: `/home/evan/.ssh/hetzner` (local) → server
- Project deployment paths are project-owned and vary by surface; there is no
  generic host webhook autodeployer.
- Billed: monthly, Hetzner account

### Cloudflare — DNS, tunnel, Pages, and Workers

- Purpose: public routing for Synaplex, Command, Skillfoundry, and Preflight.
  The intended host tunnel routes are Command (including the private inbox)
  and Skillfoundry; verify `/etc/cloudflared/config.yml` and the live endpoints.
  Synaplex Pages and the Preflight Worker have separate deployment contracts.
- API token: `/opt/workspace/runtime/.secrets/cloudflare_api_token`
  (root-owned runtime secret; never print its contents).
- Billing and registrar state require provider-side verification.

### Namecheap — historical domain registrar

- Historical purpose: `synaplex.ai` registration. A move to Cloudflare
  Registrar was intended in 2026-04; completion and current billing are
  unverified from this host. Do not claim either without provider evidence.

### Render — account holds `launchpad-lint` MCP on agenticmarket

- Historical purpose: deploy `launchpad-lint` to the **agenticmarket** MCP
  marketplace for distribution. The principal confirmed that placement on
  2026-04-18; its current marketplace state and tier are not host-verifiable.
- Why it's not redundant with Hetzner: the Hetzner deploy at
  `skillfoundry.synaplex.ai/products/launchpad-lint/` is the owned-web
  surface. The Render deploy reaches the MCP marketplace audience, which is
  a different distribution channel.
- Deploy source: `projects/skillfoundry/skillfoundry-products/products/launchpad-lint/render.yaml`
- Credentials: Render account login (principal). Do not initiate a deploy or
  infer auto-build state without current provider evidence.
- Billing tier is unknown and requires provider-side verification.

### Anthropic / Claude

- Purpose: Claude subscription CLI for agent sessions and governed evaluation.
- Check non-secret login readiness with `verify-state.sh`; account
  tier and billing require provider-side verification.
- ADR-0036 prohibits silently substituting metered model API credentials for
  authorized subscription-CLI work.

### OpenAI / Codex

- Purpose: `codex exec --sandbox read-only` is the live adversarial-review
  path per `supervisor/scripts/lib/adversarial-review.sh` (since `/review`
  skill is EROFS-broken, FR-0021).
- Check non-secret login readiness with `verify-state.sh`; account
  tier and billing require provider-side verification.

## Retired / off-this-host

### mentor / recruiter hosting

- Removed from this server 2026-04-18 per ADR-0023. They remain as personal
  side projects under the principal's personal accounts, off-workspace.

## How to use this register

- **Before proposing any paid-service provisioning**: read this file. Confirm
  no existing account covers the need.
- **Before walking the principal through a signup flow**: check the relevant
  row here, then verify current provider and deployment state.
- **When provider evidence requires principal-only login or 2FA**: label the
  state unverified and do not guess. Ask the principal only if that fact blocks
  a concrete current decision or authorized change.
- **When the principal mentions a new paid account**: update this file in the
  same turn. See FR-0032 for why.
