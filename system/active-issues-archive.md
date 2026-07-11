---
name: Active issues — historical archive
description: Archive of resolved + closed items that used to live in active-issues.md. Load on demand, not in context-always-load. Preserves the narrative history that git log carries but that humans and agents may want to browse contiguously.
updated: 2026-04-23
---

# Active issues — historical archive

This file holds items that were previously tracked in `active-issues.md` and are now closed, superseded, or low-leverage enough that they do not belong in a session's auto-loaded context.

The ordering here is reverse-chronological (most-recently-closed first). For the narrative of exactly how each item was closed, `git log` on the source files is authoritative; this archive carries the prose summary that was written when the item still felt current-state-shaped.

See `active-issues.md` for items currently live.

---

## Closed 2026-04-23 during execution-burst

**URGENT routing dead-letter bug (FR-0033 + FR-0034)** — resolved. `dispatch-handoffs.sh` target_session_for() now strips the `URGENT-` prefix before session-prefix match (supervisor `a3a174c`). Skillfoundry session cwd moved from `skillfoundry-harness` to `skillfoundry` root (supervisor `c9775f0`) so dispatched handoffs no longer over-capture or miss-route. Stale `URGENT-skillfoundry-valuation-no-session` handoff in supervisor INBOX deleted (primary verification: all sub-asks landed via 8a5f1ff + 251adf4 + 2f63ae5 + 5008cfb).

**ADR-0028 (command artifact inbox) accepted** — supervisor `a91204c`. Adversarial review at `.reviews/4b5261c-artifacts-review-2026-04-20T16-49Z.md` clean. Artifact inbox live at `/artifacts` in command.

**Tick outage (92h) resolved** — positioning-test.md committed (`fb5901e`); dirty-tree guard now excludes `??` entries (`cee8af6`); 29 tick-escalation URGENTs archived to `handoffs/ARCHIVE/2026-04/` (`589bae1`); S3-P2 writer dedupes by reason-hash so future outages produce one file with a counter not N files (`79fae2f`); supervisor charter reentry step 9 scans `runtime/.handoff/URGENT-*` (same commit). FR-0039 closed; FR-0043 closed.

**Synaplex L1 intake subsystem shipped** — rebrand complete (projects/agentstack → projects/synaplex, supervisor `5008cfb`). Adapter code + systemd timers committed by the synaplex session. Timers enabled today: synaplex-intake, synaplex-score, synaplex-digest, synaplex-synthesize, synaplex-integrity. First daily digest for `agent-platforms` beat rendered at `runtime/intake/digests/agent-platforms-2026-04-23.md`. L2 (reasoning) + L3 (validation) + L4 (presentation) deferred to follow-on builds per ADR-0029.

**Atlas canon gap closure** — `2f63ae5` shipped the 4-finding fix the Codex review identified (emit_decision loop, non-transactional migration reorder, sources parameter, SOL min-bars guard). Tests 107/107. Re-run canon backfill landed. Adversarial review of the reorder clean.

**ADR-0029 accepted** — the synaplex five-layer loop pipeline (intake → reasoning → validation → presentation → friction) codified in `supervisor/decisions/0029-*`. 3-finding Codex review addressed in-ADR with concrete operational controls (per-source trust tracking, scoring accuracy auto-pause, reasoning_note write-time requirement, 4-week bootstrap throttle, candidate TTL + quarantine). `4cdc50a` + `906825c` added the synthesis-translator primitive that closes the "perfect diagnosis, zero execution" loop end-to-end; first autonomous synthesis → handoff → commit chain completed at `d09d2be` (version-controlled `/opt/workspace/CLAUDE.md` via supervisor/workspace-claude.md symlink).

**Synaplex rebrand landed** — `projects/agentstack/` → `projects/synaplex/` filesystem move with git history preserved. Supervisor surfaces updated (sessions.conf, projects.conf, supervisor/projects/products/, dispatch-handoffs.sh KNOWN_SESSIONS). In-project site rebrand + CLAUDE.md rewrite landed via synaplex session.

**Supervised `general-codex` session provisioned** — per ADR-0029 Phase B=c hybrid. `workspace-session@general-codex.service` running; tmux session with codex REPL at gpt-5.4 high reasoning, cwd /opt/workspace. Sessions.conf updated (`4e64137`); dispatcher KNOWN_SESSIONS updated.

---

## Closed earlier in April 2026

**Skillfoundry deployment (2026-04-19T00:22Z)** — verified-primary-source sweep found all three "blockers" were resolved or misdiagnosed: blog + LCI already deployed via CF Pages commit `6d4b9d9`; Preflight landing was a Hetzner build+restart gap, fixed at `systemctl restart preflight.service` after rebuild. CF token kept per principal decision. Launchpad Lint has two real live targets (Hetzner + agenticmarket/Render).

**Aged tick branches and push backlog (2026-04-18 attended)** — 15-commit main backlog pushed. `ticks/2026-04-16-12` and `ticks/2026-04-17-02` merged to main. P1 push guard from synthesis not implemented as originally proposed; the automation target needs rethinking (attended sessions own the push; see ADR follow-on).

**Atlas URGENT escalations (2026-04-18)** — claim-hash migration complete (`040c053` re-keyed 42→47 hypotheses); live path validated (`ea44220` ran `atlas run --once`); both items addressed.

**`/review` skill EROFS** — context-scoped to tick sessions only. Attended sessions can run Codex adversarial review via `supervisor/scripts/lib/adversarial-review.sh`. See `feedback_dont_generalize_intermittent_failures.md` memory for the tick-vs-attended distinction.

**Context-repository mechanics M4 + M5 shipped (2026-04-18 attended)** — ADR-0021 and ADR-0022 both accepted. Session-start auto-load hook at `/root/.claude/hooks/session-start-context-load.sh` fires on every Claude Code session with a `context-always-load:` declaration. M5 phase-1 (session-end detect-and-report) fires on SessionEnd. Freshness gate (7-day STALE banner) live.

**Command consolidation and thread frame (2026-04-17)** — command.synaplex.ai consolidated to three jobs (executive chat, portfolio, operator tools). Native Claude/Codex session threading with CLI resumability. Thread-opening frame (ADR-0020) addresses the advice-vs-action gap. Codex review clean; FR-0016 closed.

**`/review` enforcement gate live (2026-04-17)** — `scripts/lib/preflight-deploy.sh` fails deploys lacking review artifacts for code-touching commits (supervisor `668c7b0`). Command is on main with full git history; gate applies.

**S3-P1 supervisor dirty-tree escalation to INBOX** — landed via `bd5a854` (original S3 stack) plus `79fae2f` today (dedup by reason-hash). Resolved.

**S4-P3 telemetry rotation** — `supervisor/scripts/lib/telemetry-rotate.sh` committed and running. Resolved.

**Supervisor 401 escalation hook dead code (2026-04-17T19:28Z)** — `$SUP` was undefined under `set -u`; hook was inert. Fixed with correct `$WORKSPACE_SUPERVISOR_HANDOFF_INBOX` variable + S1-P2 `tick.escalated` event. 8-assertion test added.

**Command terminal 16ms false alarm (2026-04-17T16:56Z)** — telemetry misidentification; smoke test connections tagged `sourceType: 'user'` made 21ms smoke sessions look like broken user sessions. Fixed in `c2eb4f2`: server reads `X-Source-Type: smoke` header; smoke events now correctly tagged.

**Telemetry schema gap — `sourceType` field (2026-04-17)** — S1-P2 deployed in command + atlas; CLAUDE.md reconciled to the epoch-ms `timestamp` shape. Verified live via `events.jsonl` entries.

**Tick handoff consumption gate (2026-04-17)** — `supervisor-project-tick-prompt.md` L38–45 contains the handoff-check step (`d29891b`).

**Deploy gate: "pushed" ≠ "deployed" (2026-04-17)** — `supervisor-project-tick-prompt.md` L103 contains the `Delivery state` section requirement. CLAUDE.md §Quality: Radical Truth carries the matching rule.

**reflect-all.sh stdin bug (2026-04-15)** — fixed in `6c91398` by redirecting the reflect.sh subprocess's stdin from `/dev/null`.

**workspace.sh doctor broken (2026-04-15)** — fixed in `6c91398`: resolve `$0` with `readlink -f` so invocation via the `/opt/workspace/workspace.sh` symlink finds the real `scripts/lib/`. FR-0008.

**Server patch + reboot (2026-04-15)** — 45 upgradable packages applied, kernel 6.8.0-107 installed; reboot executed same session. FR-0009.

**FR-0020 naming collision (2026-04-18T18:49Z)** — three files shared the `FR-0020` prefix after tick-branch merge conflict. Renamed: `FR-0020-ghost-fr-claimed-in-events.md` → FR-0029, `FR-0020-supervisor-remote-drift.md` → FR-0030. `FR-0020-tick-branch-governance-gap.md` remains canonical FR-0020.

---

## Deferred / structural items that left this surface without closure

**Tick branch governance gap (FR-0020)** — tick sessions commit friction/ and system/ changes to tick branches; subsequent main-branch sessions don't see them. ADR-class decision needed; not acute.

**`AGENT.md` duplicates `system/status.md`** — two sources of truth for "how the supervisor operates" will drift. Open; candidate for next pass.

**Idea JSON carries inline `history[]` log** — per-file append state duplicates git and events. `scripts/lib/idea-ledger.py` touches this.

**Breach detector false positives FR-0031** — detector does not distinguish the session's own commits from concurrent attended-session commits. Fix requires `scripts/lib/` edit.

**CURRENT_STATE.md auto-commit in reflect.sh** — reflect.sh updates CURRENT_STATE.md but cannot commit (--disallowedTools). Files sit as unstaged working-tree changes. Proposal 2, cross-cutting-2026-04-20T15-28-05Z. Tracked in friction; may be superseded by Anthropic memory-tool adoption.


## Snapshot archived 2026-07-11T22:42Z (was 32 days stale; superseded by live rewrite, ADR-0037 session)


# Active issues

## CRITICAL (blocks autonomous repair)

- **Ghost-write cascade — 224 commits ahead of origin/main, 2 behind** — Tick/autocommit branches claim writes that do not consistently merge to main. Requires a deliberate merge/triage playbook before origin sync. Primary receipt: `git -C /opt/workspace/supervisor status -sb` on 2026-06-09.
- **Synthesis dispatch obligation — INBOX at 156 items, general handoffs at 10 by verified-state filter** — INBOX saturation is still active, but runtime handoff root was reduced by archiving done/superseded breadcrumbs on 2026-06-09. Requires INBOX triage next. Primary receipt: verified-state generated 2026-06-09T15:52:47Z.

## Currently live

- **`synthesis_reviewed` event regression — dropped for cycles 55+56, root cause identified (C57 P1)** — C56 tick commit `63ec5b0` (question-promotion fix) dropped the implicit `synthesis_reviewed` event emit. Event was model-inferred through cycle-54; new code path doesn't trigger it. Fix: add explicit emit instruction to tick prompt template step 6 (Tier B — draft only, needs attended session).
- **Reflection/review repair follow-through** — 2026-06-09 attended repair patched `reflect.sh` to block `Write`/`MultiEdit`, fixed `CURRENT_STATE.md` auto-commit argument ordering, deleted the two EROFS test artifacts, and PATH-hardened `adversarial-review.sh`. Next tick must verify those findings stop reappearing rather than carry them forward.
- **Harness migration — researcher-context mismatch** — `migrate --dry-run` exits rc=2 for researcher-context: `memory/venture/` missing by design (researcher is discovery/research, not Stage-1 controller). The synthesis acceptance criterion "exits 0 for valuation + researcher" was architecturally wrong. Valuation dry-run now exits 0 (fixed `9b87438`). Researcher cannot satisfy this criterion without redesigning the repo. `migrate.failure events:1 bad` root cause also resolved (`9b87438` — preflight-distribution-signal.md reformatted). Harness dep `referencing` was already present in `pyproject.toml` since `5ad37e7`; venv issue resolved. Residual: `skillfoundry migrate` CLI subcommand does not exist yet.
- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap. Old principal FR-0015 escalation archived; replacement handoff is `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Synaplex cap policy doc/code divergence** — ADR-0029 says "max 200/source/day"; implementation does "max 200/fetch with union accumulation" (HN reaches 277+/day). Dispatched to synaplex session this tick. INBOX URGENT archived.
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session (scope now spans `/opt/workspace/projects/skillfoundry/` root).
- **LCI outreach blocked** — 10 outreach drafts at `drafted` since 2026-04-11 (30+ days). Channel decision required from principal (Tally form, outreach method, or explicit park/kill). INBOX: `URGENT-aged-lci-outreach-blocked-2026-05-09T02-49Z.md` (61h old).
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.
- **Atlas causal-map residuals after ADR-0035** — Implementation commit `8249acc` deployed: graph now has 69 refuted nodes and runner is active on graph-derived hypotheses. Residuals: historical/manual-validation active cycles still make `atlas status` ambiguous, graph edges remain 0, forward-prediction ledger not built, adversarial review flagged broader data-validity risks.
- **Server maintenance p2** — reboot completed 2026-06-09; post-boot kernel `6.8.0-124-generic`, no reboot-required flag, core services active. Keep next maintenance pass focused on residual service checks, especially `api.synaplex.ai` DNS/API reachability.
- **Reflection accuracy gap (cycle 36 NEW)** — Reflection jobs read CURRENT_STATE.md instead of live sources (task stores, git HEAD, service status), propagating stale derivatives across cycles. Command reported "1 task" for multiple cycles while live store had 11. Proposals 1+4 from cycle-36 synthesis in INBOX propose CLAUDE.md amendment + reflect-prompt.md fix.
- **Synaplex arxiv API degradation (cycle 36 NEW)** — Two concurrent failure modes in one 12h window (429 rate-limit + TimeoutError on arxiv). Neither synaplex nor atlas has backoff logic. `skip_next_run` primitive proposed in cycle-36 synthesis Proposal 5. Dispatching to synaplex session.

## Pending principal (decisions, not provisioning)

- **LCI channel decision** — park, kill, or unblock the 33+ day stalled outreach track. INBOX URGENT `URGENT-aged-lci-outreach-blocked-2026-05-09T02-49Z.md` (133h old, no response).
- **Skillfoundry recommerce Phase 1 authorization** — Phase 1 (source-access outreach to GovDeals/B-Stock/GSA) was never authorized. No emails sent (correct per ADR-0020). Verdict remains: authorize / defer / reframe / kill. If authorized now, the 14-day schedule resets from authorization date. Status: `general-recommerce-status-2026-05-26.md`.
- **Tier-B-auto authority** — grant or deny ticks authority to implement additive `scripts/lib/` changes without attended gating. Structural unblock for ~10 standing synthesis proposals. 8-cycle carry-forward (cycle-20 Q1). Without it, workspace remains diagnosis-complete and action-incomplete.
- **Adversarial review independence decision** — Codex CLI is installed and the wrapper now launches it from known nvm paths, but the review remains same-workspace Codex output, not a truly independent control. Decide later whether that is sufficient or whether a separate review surface is required.
- **[Cycle 56] Should tick auto-promote synthesis "Questions for the human" to active-issues Pending principal?** — Cycle-55 had Q1 (repair ordering) and Q2 (adversarial review route); neither reached this section because the tick absorbed content without escalating. Proposal 1 in C56 synthesis fixes this structurally in `supervisor-tick.sh`. If you prefer synthesis questions stay in synthesis files only, withdraw Proposal 1. Otherwise: attended session should implement C56 Proposal 1.

## Structural / background

- **Synthesis aging gate (C58 P1 / C59 P3 — 2 cycles)** — Synthesis proposals that go un-landed for >2 cycles must be classified by root cause (attended-blocked, Tier-B-blocked, principal-blocked, or withdrawn). Proposals blocked for >4 cycles escalate to URGENT (subject to saturation rules). CLAUDE.md amendment proposed by C58+C59; attended-session-blocked.
- **Reflection question aging rule (C59 P1 — NEW)** — Unanswered meta-reflection questions re-stated in a 2nd cycle must be converted to URGENT handoffs rather than re-asked. Formalizes behavior already emerging in supervisor + atlas reflections. CLAUDE.md amendment; attended-session-blocked.
- **Carry-forward re-verification gap — 4 documented false URGENTs (C58 P4)** — Reflection loop re-asserts prior-cycle observations without re-running the diagnostic. Four instances: Codex PATH, preflight watcher, migrate.failure, LCI bandwidth. Fix: add "re-verify before carry-forward" gate to reflect prompt template. C57 Proposal 3 / C58 Proposal 4 (Tier B).
- **Operator authority loop** — attached sessions can be executive/supervisor
  with repo write but no tmux/systemd host control. ADR-0015 amendment now
  forbids routing Evan to another "full admin" agent; repeated host-only needs
  must become an explicit operator bridge/tool.
- **Executive boundary discipline** — FR-0018 and follow-ons name the pattern where the executive session patches project code instead of shaping the PM layer. Ongoing; reinforced by ADR-0020 action-default + the people-or-money rubric memory.
- **ADR-0028 post-landing artifact hygiene** — artifact inbox still needs owned browser-layer proof before retiring the old `/_inbox` stopgap. Do not ask the principal for the proof path by default.
- **Workspace CLAUDE.md versioned as of `d09d2be`** — symlink from `/opt/workspace/CLAUDE.md` → `supervisor/workspace-claude.md`. All future workspace-charter edits land in git history via the supervisor repo. Autonomous-exec loop demonstrated for this change (synthesis → translator → INBOX handoff → executive commit).
- **Cowork is a secondary friction surface** — external commentary only; not a gate, validator, or backlog priority escalator. Phase D Cowork UI remains downstream of command Phase C and broader system backlog pressure. Durable contract: ADR-0032.

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
