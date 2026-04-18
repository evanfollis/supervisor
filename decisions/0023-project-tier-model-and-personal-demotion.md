# ADR-0023: Project tier model and personal-project demotion

Date: 2026-04-18
Status: accepted
Accepted: 2026-04-18 (principal directive: "two-tier product/system setup; personal projects off-server")

## Context

The workspace had accumulated seven project surfaces as peers:
`atlas`, `command`, `context-repository`, `skillfoundry` (with 9
sub-repos), `mentor`, `recruiter`, and `supervisor` itself. Reflection,
synthesis, tick dispatch, and the 12h project loop treated them all
roughly equally, which meant attention was diluted across projects with
radically different roles:

- `atlas` and `skillfoundry` — external-facing, compounding toward
  commercial outcomes.
- `context-repository` and `command` — infrastructure; leveraged by
  other projects and for the principal's operator work.
- `mentor` and `recruiter` — personal projects, parked for most of
  2026-04, receiving automation attention disproportionate to their
  priority.

The workspace charter's "pressure discipline" section explicitly states
the executive should not hold pressure on items that aren't load-bearing
for the principal's actual goals. Treating mentor and recruiter as peers
of atlas/skillfoundry violated that.

The principal explicitly stated the goal: "a commercial/epistemic
product-focused system with a now dual setup with products and systems
that support them." Two tiers. Personal work happens elsewhere.

## Decision

**Adopt a two-tier project model:**

- **Products** (external compounding):
  - `atlas` — systematic crypto trading/investment. Epistemic-first
    now (build + validate causal market model); systematic investing
    once a threshold is passed.
  - `skillfoundry` — venture foundry with Stage-1 commercial discovery.
    Externally-evidenced only.

- **System** (infrastructure for products + operator surface for principal):
  - `context-repository` — pattern lab. Defines the front-door /
    frontmatter / always-load / M4+M5 hook contract everything else
    consumes.
  - `command` — executive control plane and portfolio surface. Live
    conversation threads, portfolio cards, operator tools.

**Remove `mentor` and `recruiter` from this server entirely.** They
remain in GitHub (`evanfollis/mentor`, `evanfollis/recruiter`) with
uncommitted WIP preserved on three archive branches
(`archive/mentor-dev-wip-2026-04-18`, `archive/mentor-deploy-wip-2026-04-18`,
`archive/recruiter-wip-2026-04-18`). The principal will develop them
on local machines when time allows. They receive no workspace-level
attention — no reflection, no tick, no systemd, no tmux, no CF tunnel,
no domain, no Docker deployment.

## What was done in the accepting session

**Code preservation (GitHub holds everything):**
- `mentor` dev clone: 2 clean ahead-of-main commits pushed to
  `origin/main`. Dirty tree (13 files) + untracked captured on
  `archive/mentor-dev-wip-2026-04-18`.
- `mentor` deploy clone (was at `/opt/mentor`): dirty tree (13 files)
  captured on `archive/mentor-deploy-wip-2026-04-18`.
- `recruiter`: 2 clean ahead-of-main commits pushed to `origin/main`.
  Dirty tree (4 files) captured on `archive/recruiter-wip-2026-04-18`.

**Data preservation:**
- Postgres dump of `mentor_pgdata` saved to
  `/opt/workspace/runtime/backups/mentor-pgdata-2026-04-18.sql.gz`
  (9.4 KB, gzipped). Low-cost insurance if the principal wants to
  restore learning-progress history locally.

**Runtime teardown:**
- `/opt/mentor/` Docker Compose stack torn down
  (`docker compose down -v`) — containers + `mentor_pgdata` volume
  removed.
- Systemd units disabled and de-linked:
  `workspace-session@mentor.service`,
  `workspace-session@recruiter.service`,
  `workspace-project-tick@mentor.timer`,
  `workspace-project-tick@recruiter.timer`,
  `autodeploy.service` (was mentor-only; unit file archived to
  `runtime/backups/autodeploy.service.bak-2026-04-18`, unit file
  removed from `/etc/systemd/system/`).
- Tmux sessions killed: `mentor`, `recruiter`.
- Cloudflare tunnel routes removed from `/etc/cloudflared/config.yml`:
  `mentor.synaplex.ai`, `api.synaplex.ai`, `deploy.synaplex.ai`.
  Cloudflared restarted; verified `mentor.synaplex.ai` and
  `deploy.synaplex.ai` return 404 externally while
  `command.synaplex.ai` continues to serve.

**Directory removal:**
- `/opt/mentor/` — removed (was deploy clone).
- `/opt/workspace/projects/career-os/` — removed (was dev clones +
  parent docs).

**Reference cleanup:**
- `supervisor/scripts/lib/projects.conf` — removed `mentor` and
  `recruiter` from reflection loop. Reorganized remaining entries by
  product / system tier with inline comment.
- `supervisor/scripts/lib/sessions.conf` — removed `mentor` and
  `recruiter` tmux session declarations; now 1 executive + 2 product + 2
  system sessions.
- `supervisor/scripts/lib/metrics-rollup.py` — removed `mentor` and
  `recruiter` cwd attribution + Claude-dir mapping entries.
- `supervisor/autodeploy.py` — deleted (only mentor was configured).
- `supervisor/sessions/mentor.json` and `recruiter.json` — deleted (gitignored on-disk session records).
- `supervisor/projects/mentor.md` and `recruiter.md` — deleted.
- `/opt/workspace/CLAUDE.md` — added tier-model §, removed
  mentor-directory bullet and Docker-Compose-for-mentor bullet.

**Tier reorganization:**
- `supervisor/projects/` split into `products/` (atlas,
  skillfoundry-harness) and `system/` (command, context-repo), with a
  README describing the tiers.

**Not touched (deliberate):**
- Historical reflection/synthesis artifacts in `runtime/.meta/` that
  mention mentor/recruiter. They record past state correctly — not
  rewriting history.
- The `ADR-0016-per-project-execution-tick.md` references to mentor
  remain. ADRs are immutable once written per ADR-0014 conventions;
  this ADR supersedes their applicability without editing them.
- GitHub repos `evanfollis/mentor` and `evanfollis/recruiter` themselves
  are preserved; only the server-side copies are gone.
- The principal must remove `mentor.synaplex.ai`, `api.synaplex.ai`, and
  `deploy.synaplex.ai` DNS records from the Cloudflare dashboard if he
  wants the domains fully retired. The cloudflared config no longer
  routes them, so they are inert either way.

## Consequences

**Positive:**

- Reflection/synthesis budget concentrates on 4 active projects + supervisor instead of 6 + supervisor. ~30% token reduction in per-cycle reflection cost (fewer projects × same cost each).
- The persistent-tmux session fleet shrinks from 7 sessions to 5, reducing host resource overhead and making `ws status` legible.
- The workspace narrative is now compatible with what it actually is: a product-focused system. Future agents starting cold see two product targets and two system projects; no confused peer-relationship with personal repos.
- `autodeploy.service` removal closes the last webhook-listener surface that was mentor-specific. If future products need autodeploy, they declare it explicitly (not speculatively scaffold for it).

**Makes harder:**

- If the principal wants to resume mentor on this server, he has to redeploy (clone, restore postgres from the backup dump or start fresh, re-add cloudflared routes, re-declare in projects.conf/sessions.conf). That is the cost of demotion and is acceptable per principal direction.
- Metrics history that grouped old mentor/recruiter sessions still references them in past snapshots; going forward, those attributions fall under "admin" (the default bucket). This is cosmetic and does not break analytics.

**Foreclosed:**

- The "everything is a project" implicit peer relationship. Tier boundaries are explicit now.

## Alternatives considered

**Leave mentor + recruiter on-server but skip them in the reflection loop.** Rejected — still costs disk + tmux + systemd slots + cloudflared routes for no active use. If not in the loop, also not on the server.

**Move mentor/recruiter to a separate `personal/` subtree under projects/ but keep the repos.** Rejected — the principal's stated direction was to free attention, and keeping them on-disk creates ambient recovery temptation. Clean cut is better.

**Keep autodeploy.py but nullify DEPLOY_COMMANDS.** Rejected — no-op scaffold for hypothetical future use is speculative infrastructure. Delete now; reintroduce with a concrete need.

## References

- `/opt/workspace/CLAUDE.md` §Project tier model
- `supervisor/projects/README.md` (new, this ADR)
- `supervisor/scripts/lib/projects.conf` (edited)
- `supervisor/scripts/lib/sessions.conf` (edited)
- `supervisor/scripts/lib/metrics-rollup.py` (edited)
- `/opt/workspace/runtime/backups/mentor-pgdata-2026-04-18.sql.gz`
- `/opt/workspace/runtime/backups/autodeploy.service.bak-2026-04-18`
- GitHub: `archive/mentor-dev-wip-2026-04-18`, `archive/mentor-deploy-wip-2026-04-18`, `archive/recruiter-wip-2026-04-18` branches
