# Active Issues

## Immediate

### URGENT routing dead-letter bug — FR-0033 (fix requires attended scripts/lib/ edit)

`dispatch-handoffs.sh` silently marks `URGENT-*`-prefixed files as dispatched without delivering them, because no session name starts with `URGENT-`. 5 URGENT files were dead-lettered for 1–26h before the 2026-04-20T16:49Z tick re-routed them via properly-named copies. Executive reentry step 8 also only reads `general-*` globs — URGENTs are invisible there too.

**Fix options** (both require attended `scripts/lib/` edit):
1. `dispatch-handoffs.sh`: strip `URGENT-` prefix, extract project token, route to that session.
2. Add `runtime/.handoff/URGENT-*` to executive reentry step 8 glob (simpler).

See `friction/FR-0033-urgent-handoff-routing-dead-letter.md`. Workaround applied: tick now creates `<project>-urgent-*.md` copies when re-routing.

### Adversarial review owed on tick-fix commit 5618ef1

`5618ef1` (supervisor tick reorder + reflect.sh CURRENT_STATE auto-commit, 2026-04-20) has not been adversarially reviewed. Per charter, code-touching supervisor commits need review.
- Run: `supervisor/scripts/lib/adversarial-review.sh 5618ef1` (Codex, read-only sandbox)
- Non-blocking for daily operation; review is owed before next attended structural change.

### ADR-0028 (command artifact inbox contract) — review required before accepting

Command PM self-marked `accepted` without adversarial review. Demoted to `proposed` (commit c894b40). Run `supervisor/scripts/lib/adversarial-review.sh` against `decisions/0028-*.md` before promoting to `accepted`.

### Synaplex V1 rebrand + deploy — awaiting attended implementation session

ADR-0027 accepted. Principal authorized V1 CF Pages deploy. Full spec at `runtime/.handoff/general-synaplex-rebrand-deploy-prep-2026-04-20T13-15Z.md`. Work is project-code territory — delegate to feature session or attended pass. Not blocking.

### Context-repository mechanics — M4 + M5 SHIPPED 2026-04-18 attended (ADR-0021 accepted, ADR-0022 accepted) — M4 + M5 SHIPPED 2026-04-18 attended (ADR-0021 accepted, ADR-0022 accepted)

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

### synaplex.ai — architecture accepted (ADR-0027 accepted 2026-04-20); deploy pending

**Supersedes the "agentstack" framing.** In a workspace-root session on 2026-04-19, the principal articulated that synaplex.ai is not a parent brand over portfolio products but **the system itself** — a self-evolving knowledge system with a public face at `synaplex.ai` and an operator face at `command.synaplex.ai`. Atlas and skillfoundry are pods (exploratory probes) with bidirectional obligations to the knowledge system. The lab is a load-bearing layer of synaplex, not a third sibling product. The publication is topology-not-timeline; education is a natural projection surface; strange-loop structure is architectural. See `decisions/0027-synaplex-is-the-system.md` (proposed, adversarial review pending).

**Work preserved from the retired agentstack framing (all landed 2026-04-19):**
- **Canon adapters on atlas + skillfoundry** — atlas 253 envelopes (47+123+82+1) valid under canon v0.1.0; skillfoundry 11 (3+3+4+1). Tests: atlas 97/97, skillfoundry 51/51.
- **First lab Claim pre-registered** for memory-systems-v1 at `projects/agentstack/lab/.canon/claims/b7ff216f4eec6e58.json` (path will migrate with the project-dir rename).
- **Astro site scaffold** builds clean at `projects/agentstack/site/dist/` (6 pages + sitemap). Needs rebrand from agentstack → synaplex and IA reshape away from default-blog toward concept-map topology before V1 deploy.

**Retired in ADR-0027:**
- `agentstack` as a brand name (any external reference retires).
- `agentstack.dev` / `agentstack.pages.dev` as deploy targets.
- `projects/agentstack/` directory name (rename to `projects/synaplex/` pending; handoff written to project PM).
- `supervisor/projects/products/agentstack.md` shaping file (superseded by `products/synaplex.md`; old file archived as `.superseded`).
- `handoff/synaplex-*.md` naming convention (formerly `agentstack-*`).

**Open in the synaplex architecture (ADR-0027 §Open design questions):**
1. Knowledge system physical home (IDEA-0004 to be created).
2. Site IA beyond "not default-blog" — minimum-viable topology shape for V1.
3. First publication piece editorial voice.
4. Education surface shape.
5. Review methodologies as first-class canon artifacts (requires context-repository adversarial review before spec bump).

**Still pending principal (carried forward, reframed):**
- Deploy authorization for `synaplex.ai` (V1 to CF Pages; reversible).
- Kernel reboot (6.8.0-107 → 6.8.0-110; 3-day-plus pending; unchanged).
- Tally form for Preflight Pro waitlist (unchanged; unrelated to synaplex).

**Adversarial review complete**: Codex review artifact at `.reviews/adr-0027-2026-04-19T15-42Z.md`. Status promoted `proposed → accepted` 2026-04-20T12:xxZ.

### Skillfoundry deployment — CLOSED 2026-04-19T00:22Z

**All three supposed blockers were already resolved or misdiagnosed.** Verified by primary-source sweep 2026-04-19T00:15–00:22Z (session `847b6afa`):

- **Blog**: `skillfoundry-blog.pages.dev/` = 200. Already deployed via CF Pages 2026-04-18T12:43Z (commit `6d4b9d9`). Three posts live.
- **LCI landing**: `lci.pages.dev/` = 200. Already deployed in the same commit. **Only remaining input**: your Tally form embed ID (you decided Tally/$99/CF Pages per ADR-0024; need the form itself created so we can swap the embed placeholder).
- **Preflight landing + sourceType**: was the only real gap. `dist/serve.js` on Hetzner was built 2026-04-17T09:16Z, **before** the sourceType commit (`4907d26`, 16:47Z) and SEO landing commit (`8e9bf50`, 20:51Z). Rebuilt dist + `systemctl restart preflight.service` at 2026-04-19T00:22Z. Verified: landing HTML now served with `<title>`/schema.org block, MCP endpoint returns 200, `dist/index.js` contains 3 sourceType references. This was a **Hetzner build+restart**, never a `wrangler deploy` — the active-issues line that said otherwise was tick-generated drift.

**CF token**: principal decided 2026-04-19T~00:15Z to keep the existing `cfut_cAt4F3J…` token rather than rotate. Recorded. Token is at `/opt/workspace/runtime/.secrets/cloudflare_api_token` (0600). URGENT rotation handoff archived.

**launchpad-lint**: two live targets, both real (Hetzner + agenticmarket/Render). See `paid-services.md`.

All code landed. See ADR-0024 (decisions), FR-0032 (principal-input capture failure class), `system/verified-state.md` (primary-source snapshot).

### Aged tick branches and push backlog — CLOSED 2026-04-18 attended

- 15-commit main backlog pushed to origin 2026-04-18T~11Z.
- `ticks/2026-04-16-12` and `ticks/2026-04-17-02` merged to main (2 merge commits, conflicts in FR-0021 + active-issues.md resolved in favor of HEAD — tick-branch content was stale).
- **P1 (push guard) not implemented as proposed.** The synthesis targeted `scripts/lib/supervisor-autocommit.sh`, but that script's contract is Tier-A rewind-main (never pushes main). The 15-commit backlog was attended-session commits, not tick commits. Automation target needs rethinking: either a post-commit hook in the repo, a periodic reconcile job, or accept that attended sessions own the push. Flagged to principal for decision — see notes below.

### `/review` EROFS broken — adversarial review path partially mitigated

- The `/review` skill fails with `EROFS: read-only file system, open '/root/.claude.json'` in all project sessions.
- Root cause: sandboxed sessions mount `/root/` read-only; the skill writes `.claude.json`.
- **Workaround available**: `adversarial-review.sh` wrapping `codex exec --sandbox read-only` is validated (atlas ingest review ran cleanly via this path, 2026-04-17). Tick sessions should use this for substantial commits.
- **ADR review debt resolved** — artifacts at `.reviews/adr-review-001{5,6,7}-2026-04-17T14-55Z.md`. FR-0025 marked `Status: resolved` (tick 2026-04-18T06-48Z).
- **Remaining unreviewed**: atlas dedup/telemetry (2 cycles) + atlas claim-hash migration commit `040c053` (1 cycle). Command `84b38dc` review completed 2026-04-18T16:54Z — artifact at `.reviews/84b38dc-review-2026-04-18T16-54Z.md`.
- See: FR-0021 `supervisor/friction/FR-0021-review-skill-broken-erofs.md`

### Atlas — URGENT escalations — CLOSED 2026-04-18

Both items resolved:
- **Claim-hash migration complete** — principal decided "migrate"; `040c053` re-keyed 42→47 hypotheses under canonical form (tick 2026-04-18T12:14Z). Review artifact still owed (see EROFS section above).
- **Live path validated** — `ea44220` ran `atlas run --once`; all hypotheses returned "continue" (4h data too short for signal). Path is exercised; next step is switch to 1h data window.

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
- **4-cycle carry-forwards cleared 2026-04-18T17:00Z** (command PM tick `c3aac72`): deploy gap closed (20/20 smoke), `84b38dc` adversarial review done, `page.tsx` confirm dialog committed, `check-patterns.ts` stale carry-forward was already covered (line 16 `EXTRA_FILES`). Remaining open: FR-0015 Layer-3 real-device proof, metrics producer key scheme doc.

### S3-P1: Supervisor dirty-tree escalation writes to INBOX (not yet implemented)

- Accepted in dispositions (`/opt/workspace/runtime/.meta/dispositions.jsonl`).
- Current state: `skip_with_reason()` emits an `escalated` event after 3 consecutive
  same-reason skips, but events are invisible to attended sessions. An INBOX handoff
  is needed so the escalation is actually seen.
- Blocked on `scripts/lib/supervisor-tick.sh` edit — requires attended session.
- Tracked in: `handoffs/ARCHIVE/2026-04/2026-04-16T13-00Z-pending-supervisor-items.md` (archived; requires attended `scripts/lib/` edit)

### S4-P3: Telemetry rotation script not yet implemented

- Accepted in dispositions. `events.jsonl` and `session-trace.jsonl` have no rotation.
- Requires new `scripts/lib/` rotation script + systemd timer.
- Tracked in: `handoffs/ARCHIVE/2026-04/2026-04-16T13-00Z-pending-supervisor-items.md` (archived; requires attended `scripts/lib/` edit)

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

### Synthesis proposals (cross-cutting-2026-04-18T15-26Z) — pending acceptance

Three proposals from the 15:26Z synthesis await principal decision:

- **P1 — Post-commit review check hook** (`PostToolUse(Bash)` soft gate): fires when a commit touches ≥3 files or ≥100 lines; prints ⚠ reminder that `/review` is required. Draft at synthesis. Blast radius: all sessions. Low risk (display-only). Requires attended `update-config` / hook install.
- **P2 — Tick trivial carry-forward closure**: CLAUDE.md addition permitting tick sessions to fix items that are (a) unblocked, (b) fixable in ≤5 min single commit, (c) open 2+ cycles. Requires CLAUDE.md amendment (attended session).
- **P3 — ADR acceptance gate**: supervisor-tick.sh check — when an ADR lands at `Status: accepted` in the last 48h git log, verify a `.reviews/adr-<NNNN>-*.md` exists; warn to active-issues if absent. Requires `scripts/lib/` edit (attended session).

All three are Tier-B drafts; tick cannot accept or implement.

### Aged tick branches — attended merge needed

- `ticks/2026-04-16-12`: 53h as of 18:49Z tick (>24h threshold)
- `ticks/2026-04-17-02`: 39h as of 18:49Z tick (>24h threshold)
- Both flagged by `workspace.sh doctor` (WARN, not FAIL). Attended session should merge or confirm branches are stale and delete.

### Breach detector false positives on concurrent sessions — FR-0031

Two URGENT handoffs in the same window were false positives (tick 16:49Z boundary breach, reflection 14:32Z HEAD advance). Root cause: the detector does not distinguish the session's own commits from concurrent attended-session commits. See `friction/FR-0031-breach-detector-false-positive-concurrent-sessions.md`. Fix requires `scripts/lib/` edit (attended session).

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

- *FR-0020 naming collision* (closed tick 2026-04-18T18:49Z) — three files shared the `FR-0020` prefix after tick-branch merge conflict. Renamed: `FR-0020-ghost-fr-claimed-in-events.md` → FR-0029, `FR-0020-supervisor-remote-drift.md` → FR-0030. `FR-0020-tick-branch-governance-gap.md` remains canonical FR-0020.
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
