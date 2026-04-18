# Active Issues

## Immediate

### Kernel reboot needed — kernel 6.8.0-110 pending activation

- Nightly maintenance (2026-04-18T01:24Z) reports a new kernel (6.8.0-110) installed but not yet booted.
- **Action**: Schedule one planned reboot during next maintenance window.
- Maintenance report: `/opt/workspace/runtime/.meta/server-maintenance-2026-04-18T01-24-45Z.md`
- Source: `runtime/.handoff/general-server-maintenance-2026-04-18T01-24-45Z.md` (consumed 2026-04-18T02:49Z)

### Context-repository mechanics — M4 + M5 SHIPPED 2026-04-18 attended (ADR-0021 accepted, ADR-0022 accepted)

**M4 (session-start context auto-load)** shipped 2026-04-18 attended.
`/root/.claude/hooks/session-start-context-load.sh` reads `$CWD/CLAUDE.md`
for `context-always-load:` and injects listed files as `additionalContext`.
Freshness gate: files whose `updated:` frontmatter is older than 7 days are
injected with a loud STALE banner. Registered in `/root/.claude/settings.json`.
Tested end-to-end on 4 cwds. See `supervisor/decisions/0021-*` (accepted).

**M5 phase-1 (session-end CURRENT_STATE detect-and-report)** shipped in
the same session. `/root/.claude/hooks/session-end-current-state-check.sh`
fires on SessionEnd; if cwd opted into always-load, had ≥20 transcript
lines, and `CURRENT_STATE.md` mtime is >24h old, it routes a low-priority
handoff to `general` and emits a telemetry event. No auto-commit —
phase 2 (writer/retriever) is deferred pending C1/C2/C3 resolution. See
`supervisor/decisions/0022-*` (accepted).

**context-always-load declarations added**:
- `/opt/workspace/CLAUDE.md` (workspace root)
- `/opt/workspace/supervisor/AGENT.md` (supervisor)
- `/opt/workspace/projects/atlas/CLAUDE.md`
- `/opt/workspace/projects/command/CLAUDE.md`
- (pre-existing) context-repository, skillfoundry root

**Still open for pass 2 (deferred, not blocking)**:
- Skillfoundry sub-repos (researcher, valuation, builder, designer,
  growth, pricing, products, agents) — 7 of 9 lack `CURRENT_STATE.md`.
  Skillfoundry PM-owned retrofit; tracked separately.
- `docs/agent-context-repo-pattern.md` adversarial review via
  `adversarial-review.sh` — still owed.
- Mentor and recruiter are no longer pass-2 targets — demoted to
  personal side projects and removed from this server 2026-04-18
  (ADR-0023). Any `mentor` / `recruiter` references elsewhere in this
  file should be treated as historical.

### Skillfoundry deployment credentials blocked — principal decision required

Three deploy blockers require Evan's credentials or decisions (escalated 2026-04-17T20:38Z):

- **Preflight landing page + sourceType deploy**: `wrangler deploy` required. `wrangler` not installed; needs Cloudflare API token. Commands once available: `npm install -g wrangler && CLOUDFLARE_API_TOKEN=<token> wrangler deploy` from `skillfoundry-products/products/preflight/`.
- **Watcher IGNORE_RE restart**: `systemctl restart preflight-watcher` blocked by sandbox. Needs Evan or attended session with sudo.
- **LCI intake form + hosting**: Evan must choose intake tool (Tally/Typeform/Cal.com), set price ($49/$99/contact), and decide hosting path (nginx route vs Cloudflare Pages). Once decided, agent can build + deploy in one tick.
- **Launchpad-lint**: NOT a deploy blocker. Already live on Hetzner at `https://skillfoundry.synaplex.ai/products/launchpad-lint/` (systemd `launchpad-lint.service`, uvicorn :8010 behind CF tunnel). Canonical deploy target per `deploy/REMOTE_DEPLOY.md` is Hetzner. The `render.yaml` / `railway.toml` / `fly.toml` in that directory are portability artifacts, not the active deploy. Earlier "confirm Render auto-deploy" framing was based on stale assumption — corrected 2026-04-18T12:48Z.
- **Blog publishing**: Content ready for all 3 probes. Publish path needs Medium Integration Token (agent-executable) or Cloudflare Pages (one-time setup).

Code is landed and tested. Deploy gap only. See: `runtime/.handoff/general-skillfoundry-agentic-inbound-credential-escalation-2026-04-17T20-38Z.md` (consumed by tick 2026-04-17T22-48-12Z).

### Aged tick branches and push backlog — CLOSED 2026-04-18 attended

- 15-commit main backlog pushed to origin 2026-04-18T~11Z.
- `ticks/2026-04-16-12` and `ticks/2026-04-17-02` merged to main (2 merge commits, conflicts in FR-0021 + active-issues.md resolved in favor of HEAD — tick-branch content was stale).
- **P1 (push guard) not implemented as proposed.** The synthesis targeted `scripts/lib/supervisor-autocommit.sh`, but that script's contract is Tier-A rewind-main (never pushes main). The 15-commit backlog was attended-session commits, not tick commits. Automation target needs rethinking: either a post-commit hook in the repo, a periodic reconcile job, or accept that attended sessions own the push. Flagged to principal for decision — see notes below.

### `/review` EROFS broken — adversarial review path partially mitigated

- The `/review` skill fails with `EROFS: read-only file system, open '/root/.claude.json'` in all project sessions.
- Root cause: sandboxed sessions mount `/root/` read-only; the skill writes `.claude.json`.
- **Workaround available**: `adversarial-review.sh` wrapping `codex exec --sandbox read-only` is validated (atlas ingest review ran cleanly via this path, 2026-04-17). Tick sessions should use this for substantial commits.
- **ADR review debt resolved** — artifacts at `.reviews/adr-review-001{5,6,7}-2026-04-17T14-55Z.md`. FR-0025 marked `Status: resolved` (tick 2026-04-18T06-48Z).
- **Remaining unreviewed**: atlas dedup/telemetry (1 cycle).
- See: FR-0021 `supervisor/friction/FR-0021-review-skill-broken-erofs.md`

### Atlas — two URGENT escalations (3rd-cycle carry-forward) — principal decisions required

**Escalated 2026-04-18T02:26Z** by reflection job after 3 consecutive cycles without resolution. Both sat unconsumed for 6.5h until tick 2026-04-18T08-49Z surfaced them (see FR-0028).

**1. Claim-hash identity: migrate or reset?** Atlas ingest uses `claim_hash[:16]` as hypothesis identity; case/whitespace drift silently forks hypotheses. Migration script is ready (`scripts/migrate_claim_hash.py`). Principal must decide: migrate (re-link 42 hypotheses) or reset. Both paths are low-risk. Silence is the risk.

**2. Live autonomous path unvalidated.** `atlas run --once` has never executed under the current evidence-ID contract. Zero atlas telemetry events in workspace events.jsonl. Requires `ATLAS_EXCHANGE_API_KEY` + `ATLAS_EXCHANGE_SECRET`. If credentials available, run from atlas session. If blocked, record explicitly in atlas `CURRENT_STATE.md`.

- INBOX handoff: `handoffs/INBOX/URGENT-2026-04-18T08-49Z-atlas-escalations.md`
- Source handoffs: `runtime/.handoff/URGENT-atlas-claim-hash-decision-needed.md`, `runtime/.handoff/URGENT-atlas-live-path-unvalidated.md`

### Tick branch governance gap — FR-0020

- Tick sessions commit friction/ and system/ changes to tick branches, not main.
- Friction records and active-issues.md updates from tick sessions are invisible to subsequent main-branch sessions.
- ADR-class decision: merge tick branches, or move governance surfaces to runtime (not git).
- See: `supervisor/friction/FR-0020-tick-branch-governance-gap.md`

### Context repository mismatch

- The `context-repository` project is currently chartered as an abstract spec
  layer with no operational state.
- Intended design is the opposite: current compressed state in-repo, logs and
  transcripts elsewhere, git history as the state-change narrative.
- A first opposite-agent redesign attempt drifted further toward canonical
  schemas and abstract governance docs instead of implementing current-state
  context surfaces.
- Active control-plane item: `IDEA-0003`.
- Routed via handoff: `/opt/workspace/runtime/.handoff/context-repo-context-repo-redesign.md`
- **Watch for second-signal drift**: if the redesign proposal comes back
  oriented around new abstract schemas, that's the same failure class
  repeating and warrants escalation.

### Interaction-derived signal triage

- The system can now capture and prioritize novelty, but it still lacks a
  deterministic signal taxonomy for noise, local friction, policy candidates,
  and compoundable value.
- Active control-plane item: `IDEA-0002`.

### `/review` enforcement gate → live

- `scripts/lib/preflight-deploy.sh` now fails deploys lacking review
  artifacts for code-touching commits (supervisor commit `668c7b0`,
  cross-cutting-2026-04-14 Proposal 1).
- **Closed 2026-04-17**: `command` is on `main` at `c2eb4f2` with ~20+
  commits of real history. The "no git repo" blocker is resolved; the
  gate applies to command like any other project.

### Command — consolidation + thread frame complete (2026-04-17)

- `command.synaplex.ai` consolidated to three jobs: executive chat, portfolio,
  operator tools. Deleted: `/orchestrate`, `/terminal`, `/telemetry`, `/meta`,
  `/sessions` index. Native Claude/Codex session threading with CLI resumability.
- Thread-opening frame (ADR-0020) closes the advice-vs-action gap: agents in
  executive threads now default to reversible action. Two self-tests confirmed
  (Claude commit `90c6b64`, Codex commits `47f4fab`/`3eade29`).
- Adversarial review (Codex, 2026-04-17T19:24Z): no architectural or security
  failures. Findings (Codex session ID race, no failed-turn marker,
  in-process-only lock) are accepted single-process tradeoffs.
- **FR-0016 closed.** All three named symptoms addressed. See closure evidence
  in `supervisor/friction/FR-0016-command-still-behaves-like-ui-over-sessions.md`.

### S3-P1: Supervisor dirty-tree escalation writes to INBOX (not yet implemented)

- Accepted in dispositions (`/opt/workspace/runtime/.meta/dispositions.jsonl`).
- Current state: `skip_with_reason()` emits an `escalated` event after 3 consecutive
  same-reason skips, but events are invisible to attended sessions. An INBOX handoff
  is needed so the escalation is actually seen.
- Blocked on `scripts/lib/supervisor-tick.sh` edit — requires attended session.
- Tracked in: `/opt/workspace/supervisor/handoffs/INBOX/2026-04-16T13-00Z-pending-supervisor-items.md`

### S4-P3: Telemetry rotation script not yet implemented

- Accepted in dispositions. `events.jsonl` and `session-trace.jsonl` have no rotation.
- Requires new `scripts/lib/` rotation script + systemd timer.
- Tracked in: `/opt/workspace/supervisor/handoffs/INBOX/2026-04-16T13-00Z-pending-supervisor-items.md`

### Executive relapsed into implementation instead of shaping the `command` PM

- The principal correctly called out that the executive was still trying to be
  a do-it-all surface instead of operating at the PM-shaping level.
- This was not just a tone issue. Workspace-root executive sessions directly
  touched `command` repeatedly while the real need was clearer PM pressure,
  product architecture, and acceptance criteria for the browser control plane.
- Immediate correction: treat `command` as a PM/product-system problem and hold
  the next pass there, rather than continuing to patch it from the executive
  lane.
- See friction record:
  `/opt/workspace/supervisor/friction/FR-0018-executive-relapsed-into-project-implementation.md`

## Structural (supervisor self-alignment)

These items concern the supervisor repo matching its own current-state
model. Resolved items are removed; remaining items are tracked to an ADR.

- **Events live inside the repo.** Charter §Event model locates
  `events/supervisor-events.jsonl` in-repo. Should be in
  `/opt/workspace/runtime/.telemetry/` with a pointer here. Addressed
  by **ADR-0012 (accepted)**; migration queued as a separate execution
  task.
- **`handoffs/ARCHIVE/` is a log.** Resolution is already in git.
  Addressed by **ADR-0012 (accepted)**; migration queued with events.
- **`AGENT.md` duplicates `system/status.md`** on reentry order and
  operating model. Two sources of truth for "how the supervisor operates"
  will drift. **Open — needs ADR or direct compression.** Candidate for
  next pass.
- **Idea JSON carries inline `history[]` log.** Per-file append state
  duplicates git and events. Strip history; rely on `git log -- ideas/…`
  and `idea_*` events. **Open — touches `scripts/lib/idea-ledger.py`.**
- **Supervisor pressure was implicit, not surfaced.** `pressure-queue.md`
  now exists to make dropped pressure visible. The discipline still needs to
  prove itself in live use.

## Structural (workspace-wide)

### Current-state bundle discipline must hold

- `workspace.sh context` now emits the canonical current-state bundle.
- Reentry should continue to prefer `system/status.md`,
  `system/active-issues.md`, `system/active-ideas.md`, and relevant
  `projects/` / `roles/` state files.
- Reference and archive layers should be opened only when the state
  surfaces point at them.

### Cross-agent project transport is still soft

- Runtime handoffs exist and are the intended project-session routing
  surface.
- Direct opposite-agent CLI invocation from the supervisor is unreliable
  in the current sandbox: local `claude -p` calls hang without returning
  usable output.
- The control plane should not assume that ad hoc CLI invocation is a
  reliable substitute for a proper session-to-session transport and
  acknowledgment path.

## Resolved (removed from this surface; see git history for detail)

Previously-listed items that have been closed:

- *Supervisor 401 escalation hook dead code* (closed 2026-04-17T19:28Z) — `$SUP` was undefined under `set -u`; hook was inert. Fixed with correct `$WORKSPACE_SUPERVISOR_HANDOFF_INBOX` variable + S1-P2 `tick.escalated` event. 8-assertion test added. S3-P1 fully landed.
- *Command terminal 16ms false alarm* (closed 2026-04-17T16:56Z) — root cause was telemetry misidentification: smoke test connections tagged `sourceType: 'user'` made 21ms smoke sessions look like broken user sessions. Fixed in `c2eb4f2`: server reads `X-Source-Type: smoke` header; smoke events now correctly tagged. Real terminal verified working over both localhost and cloudflared WS. SMOKE PASSED (15/15).
- *Telemetry schema gap — `sourceType` field* (closed 2026-04-17) —
  S1-P2 deployed in both command (`src/lib/telemetry.ts`) and atlas
  (`runner.py::_emit_telemetry`); CLAUDE.md reconciled to the epoch-ms
  `timestamp` shape. Verified live: recent `events.jsonl` entries from
  both projects carry `sourceType`, atlas has emitted 35+ events, and
  `command.api.sessions.listed` is tagged `sourceType:"system"` so
  meta-scan can now filter self-traffic. Older pre-deployment events in
  the file lack the field by design (append-only). Proposal 2 of
  cross-cutting-2026-04-14 is satisfied.
- *Tick handoff consumption gate* (2026-04-17) — `supervisor-project-tick-prompt.md` L38–45 now contains the handoff-check step (commit `d29891b`). Handoff archived to `handoffs/ARCHIVE/2026-04/`. Next cycle's reflection measures whether the runtime handoff queue drains.
- *Deploy gate: "pushed" ≠ "deployed"* (2026-04-17) — `supervisor-project-tick-prompt.md` L103 now contains the `Delivery state` section requirement (commit `d29891b`). CLAUDE.md §Quality: Radical Truth carries the matching rule.
- *reflect-all.sh stdin bug* (2026-04-15) — fixed in commit 6c91398 by
  redirecting the `reflect.sh` subprocess's stdin from `/dev/null`. Next
  12h reflection cycle (14:17 UTC) will validate all 7 projects produce
  artifacts. Source: FR (pending), synthesis 2026-04-15T03:26 Pattern #1.
- *workspace.sh doctor broken* (2026-04-15) — fixed in commit 6c91398:
  resolve `$0` with `readlink -f` so invocation via the
  `/opt/workspace/workspace.sh` symlink finds the real `scripts/lib/`.
  FR-0008.
- *Server patch + reboot overdue* (2026-04-15) — 45 upgradable packages
  applied, kernel 6.8.0-107 installed; reboot executed same session.
  FR-0009.
- *Supervisor tick paused by hold file* (2026-04-15) — resolved in attended
  session by removing `/opt/workspace/runtime/.locks/supervisor-tick.hold`.
- *Post-reboot runtime health surfaces stale* (2026-04-15) — resolved in
  attended session; latest snapshot is
  `/opt/workspace/runtime/.meta/server-health-2026-04-15T12-57-45Z.md`.
- *session_id in commit trailers* — ADR-0009 accepted; all supervisor
  commits from 2026-04-14 onward carry the trailer.
- *`docs/` promotion/retirement rule* — `docs/README.md` already
  defines it.
- *`projects/` retention rule* — `projects/README.md` already defines
  it.
- *`sessions/` retention rule* — `sessions/README.md` already defines it.
