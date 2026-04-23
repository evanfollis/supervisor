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
