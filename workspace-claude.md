# Workspace — /opt/workspace

## Read first

Before anything else, read `supervisor/ESSENCE.md`. It is the worldview
this system operates under. Everything that follows — topology, tier
model, Active Decisions, operational rules — exists to serve that
worldview. If anything below conflicts with the essence, the essence
wins; the rules are wrong and subject to supersession.

The essence is not a rule. It is the frame in which rules are
interpreted. Rules are temporary scaffolding for progress; the essence is
the thing they scaffold toward. When you find yourself reaching for a
strict rule to enforce consistency, treat that as signal the worldview is
not yet embedded, not that more rules are needed.

Canonical workspace root is `/opt/workspace`.

Topology:
- `/opt/workspace/supervisor` — durable control plane
- `/opt/workspace/projects` — managed repos only
- `/opt/workspace/runtime` — generated state, telemetry, handoffs, worktrees

`/opt/projects` is now a compatibility surface with symlinks for legacy paths.

This is Evan's development workspace. Managed repos now live under `/opt/workspace/projects/`. Agent sessions run against individual projects but inherit this shared context from the workspace root.

## Topology (reframed by ADR-0027; supersedes ADR-0023's tier model)

Under ADR-0027, synaplex.ai is *the system itself* — the productized form
of the methodology. What was previously framed as a "two-tier product
system" with atlas and skillfoundry as sibling products is reframed:

- **synaplex.ai** — the system. The methodology-as-product. Public face
  at `synaplex.ai` (human-readable, early surface); operator face at
  `command.synaplex.ai`; agent-addressable face at a protocol surface
  (long-term). Codebase lives at `projects/synaplex/` (rename from
  `projects/agentstack/` pending; see the active-issues entry).
- **atlas** (pod) — systematic crypto trading/investment system. A
  domain application of the same methodology that drives synaplex. Not a
  sibling product; a projection into a specific domain. Pod lifecycle
  applies — it may emerge, refine, contribute invariants, graduate, or
  deprecate.
- **skillfoundry** (pod) — venture foundry with Stage-1 commercial
  discovery. Another domain application of the same methodology. Same
  lifecycle caveats.
- **context-repository** — hosts the L1 canon (obligations model,
  validator rules). Canon is the formal substrate that lets a
  methodology this alive be shippable; itself provisional.
- **command** — the operator surface of synaplex. The principal's
  internal view into the same system the public sees externally at
  synaplex.ai.

ADR-0023's two-tier framing (Products vs. System) is retained in git
history for context but is no longer the canonical shape. The synaplex
reframe is in ADR-0027.

`mentor` and `recruiter` were removed from this server on 2026-04-18. They remain in GitHub (`evanfollis/mentor`, `evanfollis/recruiter`) as personal side projects; the principal develops them locally on other machines when time permits. They are not in the persistent reflection / tick loop and should not compete for workspace attention.

## Session-start context load (M4 / ADR-0021)

The `SessionStart` hook at `/root/.claude/hooks/session-start-context-load.sh` auto-injects the files below into every Claude Code session opened at this cwd. Keep these small and current — stale files (per `updated:` frontmatter older than 7 days) are injected with a loud STALE banner, not silently trusted.

```yaml
context-always-load:
  # Ordered stable → volatile for prompt-cache prefix stability.
  # Claude API auto-caches the longest stable prefix; any file whose contents
  # change invalidates the cache for everything *after* it. Keep the most
  # dynamic files (verified-state, regenerated every tick) at the tail so
  # they don't bust the cache on ESSENCE, synthesis, and pressure files.
  - supervisor/ESSENCE.md                           # ~immutable (worldview)
  - runtime/intake/synthesis/agent-platforms-latest.md  # weekly (Layer 1 intake)
  - supervisor/system/paid-services.md              # monthly
  - supervisor/pressure-queue.md                    # curated, weekly-ish
  - supervisor/system/status.md                     # daily
  - supervisor/system/active-issues.md              # daily, highest churn
  - supervisor/system/verified-state.md             # regenerated every tick
```

The synaplex intake synthesis sits second (right after ESSENCE) so the
AI-landscape briefing for executive sessions is guaranteed to inject
even when downstream files blow the 30KB aggregate cap. The synaplex
Layer 1 intake loop (ADR-0029) produces a weekly synthesis of the
agent-platforms beat and refreshes `agent-platforms-latest.md` as a
symlink to the most recent ISO-week file. The 7-day STALE banner fires
automatically if the synthesis cron has failed. `systematic-trading`
(atlas) and `venture-discovery` (skillfoundry) follow this pattern when
those beats ship. Do not fork into a parallel `supervisor/briefings/`
surface — the synthesis file IS the briefing.

Cap note: the aggregate was already over the 30KB budget before this
amendment (active-issues.md alone is ~24KB, which truncated
paid-services + pressure-queue before synthesis was added). The
reorder does not change which files truncate under the existing cap —
active-issues is still the dominant consumer. Addressing the cap
collision is tracked via URGENT handoff
`synaplex-always-load-cap-collision` to principal.

`ESSENCE.md` is first because everything downstream is interpreted in its
light. Current-state files describe what is; the essence describes how we
see and work. Without the essence loaded first, the state files get
interpreted through whatever framing the reading session arrives with —
which is the failure mode this file is here to prevent.

### Workspace-root default
- A session whose cwd is `/opt/workspace` is acting as the workspace executive unless the user explicitly and narrowly redirects it.
- `/opt/workspace` is the executive launch root.
- `/opt/workspace/supervisor/` is the durable control-plane repo and charter surface.
- `/opt/workspace/runtime/` is the executive/supervisor generated state, telemetry, and handoff surface.
- The canonical persistent embodiment of that role is the `general` session rooted at `/opt/workspace`.
- Workspace-root sessions should start with capability attestation (`workspace.sh capabilities` or `workspace.sh context`) and classify themselves honestly.
- Workspace-root sessions should not edit project code directly. They should govern, delegate, and codify policy; project repos remain project-session responsibility.

## Active Decisions

These apply across all projects. Don't re-derive them — they're settled.

### Code Philosophy
- **Finish before you polish.** Wire up existing backend logic before writing new abstractions. The codebase has half-built features — completing them is higher priority than improving what already works.
- **No speculative infrastructure.** Don't add error handling, config layers, or abstractions for scenarios that aren't happening yet. Build for the current use case.
- **Minimal diffs.** When fixing a bug or adding a feature, touch only what's necessary. Don't refactor adjacent code, add docstrings to functions you didn't change, or "improve" imports.
- **Two write paths to the same store require explicit reconciliation (S1-P3).** If two code paths both write to the same state store (DB table, file, index), they must share an ID generation contract. Divergent ID schemes (e.g. `[:12]` vs `[:16]` on the same hash) silently corrupt cross-path queries and promotion gates. Adding a second write path is ADR-class — name both paths, verify the ID contract, and check every consumer that joins across them.

### Agent Behavior
- **Don't summarize what you just did.** Evan reads diffs. End with the next decision point, not a recap.
- **Don't ask permission for reversible actions.** Read files, edit code, run tests — just do it. Ask before pushes, deploys, or destructive operations.
- **Action-default contract (ADR-0020).** Every agent surface in this workspace — executive threads, PM sessions, scheduled ticks — defaults to reversible action, not advice. If the work is in-scope and reversible, take it and report with commits + front-door updates. Reserve "you should..." and "want me to...?" for decisions only the principal can make (novel strategy, irreversible external commitments, legal/FINRA scope, personal-identity credentials). Assessment questions still warrant diagnostic answers — action-default is not action-forced. See `supervisor/decisions/0020-action-default-contract-across-agents.md`.
- **Commit messages: imperative mood, explain why not what.** "Add card review endpoint" not "Added card review endpoint". "Fix streak reset on timezone boundary" not "Updated streak logic".
- **Default to Sonnet.** Only escalate to Opus for architectural decisions, complex debugging, or evaluation tasks.

### Architecture Governance
- **The substrate is the stable layer.** Treat model harnesses as replaceable. Durable sessions, truth sources, events, artifacts, decisions, outcomes, and reentry semantics are the real architecture.
- **Prompt context is not durable memory.** Any long-running workflow must have state outside the prompt window.
- **Truth and planning are separate.** Only declared truth sources may create durable facts. Strategy or planning documents may guide prioritization but may not become claim sources.
- **Control plane and execution plane must stay separate.** Orchestration, credential brokerage, and review logic should not collapse into unrestricted execution environments.
- **No ambient credentials by default.** Generated code and execution environments should receive only scoped inputs, never inherited full-process secrets unless explicitly declared and justified.
- **Every governed repo must declare its session unit, event model, reentry path, environment classes, and review path.** Use `context-repository` as the canonical contract source.
- **Well-designed feedback loops are mandatory.** Systems should record when they get stuck, fail, surprise us, or work unexpectedly well.
- **Meta observations must compound.** Recurrent issues or wins should feed an offline synthesis loop that looks for better explanations and cleaner architectural responses, not just more patches.
- **Structured telemetry is required for active runtime systems.** Emit append-only operational events for startup, task/session state changes, failures, review activity, and environment boundaries.
- **Telemetry events must use a `sourceType` field (S1-P2).** Values: `user` (real user action), `system` (internal automation), `smoke` (test/smoke run), `cron` (scheduled job). This is the only way to distinguish real incidents from noise in meta-scan. Minimum event shape: `{ project, source, eventType, level, timestamp, sourceType }`. `timestamp` is epoch milliseconds (integer) — both command (`src/lib/telemetry.ts`) and atlas (`runner.py::_emit_telemetry`) emit this form; the spec was reconciled to match reality on 2026-04-17 after a 3-cycle carry-forward.
- **Self-monitoring systems must self-report stuck states (S3-P2).** A monitor that only emits on the happy path is indistinguishable from a stuck monitor. Any automated loop (supervisor tick, meta-scan, executive dispatch) must emit a named `escalated` event after N consecutive skips or silent failures. The threshold for the tick is 3 consecutive same-reason skips.
- **Measurement systems co-located with their subject must discriminate self-generated traffic (ADR-0019).** A watcher, probe, or monitor running on the same host as the service it observes must apply at least one of: latency floor (sub-2ms round-trips are loopback on the local host), `sourceType`/source-class tagging, or explicit IGNORE patterns for known automated UAs and internal callers. Counting self-traffic as organic signal is worse than having no measurement — it produces false confidence. When in doubt, assume localhost traffic is self-generated and require positive evidence (novel UA, non-loopback origin, latency consistent with a real network path) to classify an event as external. Reason: valuation preflight watcher counted 161 of 162 `Mozilla/0ms` loopback sessions as `REAL-USER` until this rule was written.

### Quality: Root-Cause Discipline
- **No bandaid fixes.** If a bug can only be "fixed" by asking the user to clear their cache, switch browsers, retry, or change settings, you haven't found the bug — those are diagnostic hints, not fixes. The real fix lives in code, response headers, or infrastructure config. Find it.
- **Read primary evidence literally before theorizing.** A screenshot, error message, or log line is a complete answer until proven otherwise. Don't stack speculation on top of evidence you haven't finished reading.
- **Eliminate failure classes, not instances.** Helpers that paper over one symptom (e.g. `buildOrigin()` to reconstruct a public URL) are inferior to changes that make the symptom impossible (e.g. relative `Location` headers). Prefer fixes that remove the ability to fail this way again.
- **"Works on my machine" is not verification.** Curl from the server doesn't replay browser caches, service workers, SameSite enforcement, ITP, mobile network paths, or CDN edge behavior. When a fix depends on client-side behavior, verify from the actual failing client context or state explicitly why the server path matches the client path.
- **Behind a reverse proxy (cloudflared, nginx, CF tunnel), never derive public URLs from `req.url` / `Host` / `new URL(p, req.url)`.** The internal origin is not the public origin. Use relative URLs in `Location` headers, or pin the public origin in config. Same rule for emails, webhooks, OAuth callbacks, any server-generated link.
- **Understand the causal chain before proposing a fix.** Articulate: where does the bad behavior originate, what assumption is violated, what's the smallest change that restores the invariant. If you can't state this, you don't understand the bug yet — don't ship a guess.
- **Speed is not a goal. Quality and emergence are.** Evan has said this explicitly. Slow down, call advisor(), re-read the logs. Fake confidence on a shaky fix is worse than admitting you're stuck.

### Quality: Adversarial Review
- **Use `/review` after completing any significant feature, refactor, or architectural change.** This sends your recent work to a different AI agent (Codex or Claude) that challenges your design decisions, assumptions, and failure modes. It is not a style check — it's a pressure test.
- **Route to the opposing agent.** If you are Claude Code, review with Codex. If you are Codex, review with Claude. The value is in the different perspective.
- **Act on the findings.** If the review identifies a real failure mode, fix it before shipping. If it's a valid tradeoff you already considered, note why you chose this path.
- **Don't skip it for "small" changes.** Small changes in auth, data mutation, or concurrency are exactly where hidden assumptions live.

### Quality: Radical Truth
- **Separate what you verified from what you believe.** "Tests pass" means you ran them and saw the output. "I think X works" is a belief. Label them differently. In completion reports, evidence is non-negotiable — paste the actual output, not a description of it.
- **An overconfident report is worse than an escalation.** False signal propagates through the stack. If the executive makes decisions based on a completion report that papered over uncertainty, the error compounds silently. Escalate when uncertain. Escalation is the honest move, not a failure.
- **Disagreement is mandatory, not optional.** If a handoff spec is wrong, underdefined, or in tension with the project's design, say so in your completion report. Silent execution of a bad spec is not compliance — it's a failure to communicate.
- **Self-assessment must be adversarial.** Before marking a task complete: what would a skeptic say about this? What didn't you test? What assumptions are you making? Write the answers. An empty Uncertainty section on a non-trivial task is a red flag.
- **Every project maintains a `CURRENT_STATE.md`.** Updated every tick and every reflection pass. This is the breadcrumb system that prevents agents from starting cold. Accuracy over completeness — a short honest file beats a long stale one. See `/opt/workspace/supervisor/scripts/lib/CURRENT_STATE_TEMPLATE.md` for the format.
- **This applies at every layer.** The executive must be as honest with the principal as project PMs are with the executive. There is no level of the stack at which comfortable-sounding uncertainty becomes acceptable.
- **"Pushed" is not "deployed."** A tick that commits and pushes code to a project with a running service must either deploy the change or explicitly note the deployment gap in its completion report under a required `Delivery state` section (`code_landed`, `deployed`, and the deployment step needed if they diverge). The disposition ledger must not mark `verified:true` until the change is live in the target environment. Reason: S1-P2 (`sourceType`) landed in `eb18e35` but command was never redeployed — `grep -c sourceType events.jsonl` = 0 while the disposition read "verified." Conflating the two states silently closes carry-forward loops on work that is not actually live.
- **Credential-blocked work must escalate on first occurrence, not accumulate.** If a tick produces code that requires external credentials, API tokens, or manual deployment steps to become live, the completion report must include a `Credential blocker` section naming the specific credential and the exact command needed once it's available. If the same credential blocks work in 2+ consecutive ticks, the second tick must write an URGENT escalation — the blocker is structural, not transient, and silent accumulation produces a backlog no one sees. Reason: skillfoundry accumulated 5 credential-blocked deploys across 3 ticks before being surfaced; the "pushed is not deployed" rule catches individual instances but does not force early escalation of the blocker itself.

### Deployment & Operations
- **Deploy path: git push → webhook → autodeploy.** Don't SSH in to manually deploy. Push to main and let the pipeline handle it.

### Session Awareness
- You are one of several Claude Code sessions running on this server. Other sessions may be working on other projects simultaneously. Don't make assumptions about the state of projects you're not currently working in.
- If you discover something that affects another project, write a handoff note to `/opt/workspace/runtime/.handoff/<target-session>-<topic>.md` with your session name, date, and what you found.
- At the start of a conversation, check for handoffs addressed to you: `ls /opt/workspace/runtime/.handoff/<your-session>-* 2>/dev/null`
- After reading and acting on a handoff, delete the file.
- Today's health status is at `/opt/workspace/runtime/.health-status.txt` — read it if you need server context.
- Rich server-health artifacts live at `/opt/workspace/runtime/.meta/LATEST_SERVER_HEALTH`, nightly maintenance reports at `/opt/workspace/runtime/.meta/LATEST_SERVER_MAINTENANCE`, and weekly schedules at `/opt/workspace/runtime/.meta/LATEST_SERVER_MAINTENANCE_SCHEDULE`.
- **If you are the `general` session**, you are the workspace **executive**. Your launch root is `/opt/workspace`; your durable governance substrate is `/opt/workspace/supervisor/` (agent-agnostic — works under Claude or Codex). On session start, read `supervisor/AGENT.md`, run capability attestation, then process `supervisor/handoffs/INBOX/` before anything else. Carry the `supervisor` posture by default; claim the `operator` posture only when capability attestation proves host-control access. Promote durable decisions to `supervisor/decisions/` and recurring procedures to `supervisor/playbooks/`. Do not write project code; delegate to project sessions via `/opt/workspace/runtime/.handoff/<project>-*.md`.

### Automated Self-Reflection Loop
- Every 12h (02:17 and 14:17 UTC) `workspace-reflect.timer` fires per-project reflections via `/opt/workspace/supervisor/scripts/lib/reflect.sh`. Each project gets a Sonnet session that reads git log, telemetry, prior reflections, CLAUDE.md, **and the session JSONL transcripts at `/root/.claude/projects/<encoded-cwd>/*.jsonl`**, then writes findings to `/opt/workspace/runtime/.meta/<project>-reflection-<iso>.md`. **Read-only and propose-only — never commits project code.** A HEAD-and-dirty-tree safety net in `reflect.sh` aborts + drops a handoff if the session mutates the repo despite `--disallowedTools`. Short-circuits on inactivity.
- ~1h later (03:23 and 15:23 UTC) `workspace-synthesize.timer` fires a single Opus session that reads all recent reflections and proposes cross-cutting changes (CLAUDE.md amendments, new shared gates, enforcement hooks) to `/opt/workspace/runtime/.meta/cross-cutting-<iso>.md`. On completion it notifies the `general` tmux session via `tmux display-message` and drops a pointer at `/opt/workspace/runtime/.meta/LATEST_SYNTHESIS`.
- Nightly at 01:11 UTC `server-health-capture.timer` writes a rich host snapshot to `/opt/workspace/runtime/.meta/server-health-<iso>.md` and refreshes `/opt/workspace/runtime/.health-status.txt`.
- Nightly at 01:23 UTC `server-maintenance.timer` launches `codex exec` in read-only mode against the latest host snapshot and writes `/opt/workspace/runtime/.meta/server-maintenance-<iso>.md`. If action is required, it creates a handoff under `/opt/workspace/runtime/.handoff/` for the `general` session.
- Weekly on Sunday at 02:05 UTC `server-maintenance-schedule.timer` synthesizes the last week of maintenance reports into `/opt/workspace/runtime/.meta/server-maintenance-schedule-<iso>.md` and drops a matching handoff when work should be scheduled.
- Neither job touches project repos. When you next open a session, **check `/opt/workspace/runtime/.meta/` for unread reflections and synthesis files** — they are the accumulated diagnosis of what this workspace is doing wrong and right.
- Add a project to the reflection loop by appending to `/opt/workspace/supervisor/scripts/lib/projects.conf`.
- **Carry-forward escalation (Proposal 4).** A synthesis observation that has been reported in 3+ consecutive reflection cycles without a corresponding fix commit, decision verdict, or `verified` pointer in `dispositions.jsonl` must trigger an URGENT handoff to `supervisor/handoffs/INBOX/`. The synthesis job owns this gate. An observation that recurs silently is not a low-priority item — it is evidence the stack has lost pressure on it.
- **INBOX saturation exception.** When INBOX holds >5 unconsumed items sharing the same root cause, the synthesis job may suppress additional URGENT writes for that root cause and record the suppression in the synthesis file itself. The synthesis file + `LATEST_SYNTHESIS` pointer become the escalation surface. Suppression must be explicitly noted, not silently skipped. This exists because adding noise to an unread queue is not escalation — it degrades the signal the queue was designed to carry. The tick's S3-P2 writer also dedupes URGENTs by reason-hash (one file per root cause, with an updated counter; supervisor-tick.sh FR-0043 patch).
- **Dispatch obligation.** When a synthesis proposal lands in `runtime/.meta/cross-cutting-*.md`, the executive must dispatch a delegated project session within 24h — via `runtime/.handoff/<project>-*.md` handoff — or record an explicit deferral reason in `supervisor/decisions/` or `runtime/.meta/`. Synthesis proposals sitting >24h without dispatched action or recorded deferral escalate as FR-class structural issues. The reflection/synthesis loop is a work queue, not a diagnostic archive; treating proposals as read-and-file produces the "80h perfect-diagnosis-zero-execution" failure class the loop was designed to prevent.
- Shared preflight gates live at `/opt/workspace/supervisor/scripts/lib/preflight-deploy.sh` — every project's deploy script should source/call this. Proposed new gates from synthesis land here.

### Session Supervision
- The 7 persistent tmux sessions (general + 6 projects) are each supervised by a systemd template unit: `workspace-session@<name>.service`. The `general` session is the canonical executive session and should be rooted at `/opt/workspace`; project sessions remain rooted in their repos. If a session dies (crash, accidental `tmux kill-session`), systemd respawns it within ~5s via `/opt/workspace/supervisor/scripts/lib/session-supervisor.sh`. The Claude JSONL transcript persists on disk across restarts — the conversation context in the model doesn't, but next-cycle reflection reads the JSONL.
- Session inventory lives at `/opt/workspace/supervisor/scripts/lib/sessions.conf` (`<name>|<cwd>|<agent>|<role>`). `ws start|stop|restart|status|add|recover|capabilities` is the intended operator surface.
- `KillMode=process` on the unit means `systemctl restart` only restarts the supervisor, not the tmux session — safe against accidentally killing live chats.
