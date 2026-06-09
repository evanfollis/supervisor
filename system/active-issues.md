---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-06-09T16:22Z
---

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
- **Atlas causal-market-map intent mismatch** — Principal clarified 2026-06-09 that Atlas should remain a running falsifiable crypto-market mapping loop using conjecture/criticism, causal implications, and confounder search (Pearl-style). Live post-reboot runner is active, but latest telemetry reported `hypotheses_evaluated: 0`, `graph_nodes: 0`, `graph_edges: 0`. Audit/realign implementation before any stop/park recommendation.
- **Server maintenance p2** — reboot completed 2026-06-09; post-boot kernel `6.8.0-124-generic`, no reboot-required flag, core services active. Keep next maintenance pass focused on residual service checks, especially `api.synaplex.ai` DNS/API reachability.
- **Reflection accuracy gap (cycle 36 NEW)** — Reflection jobs read CURRENT_STATE.md instead of live sources (task stores, git HEAD, service status), propagating stale derivatives across cycles. Command reported "1 task" for multiple cycles while live store had 11. Proposals 1+4 from cycle-36 synthesis in INBOX propose CLAUDE.md amendment + reflect-prompt.md fix.
- **Synaplex arxiv API degradation (cycle 36 NEW)** — Two concurrent failure modes in one 12h window (429 rate-limit + TimeoutError on arxiv). Neither synaplex nor atlas has backoff logic. `skip_next_run` primitive proposed in cycle-36 synthesis Proposal 5. Dispatching to synaplex session.

## Pending principal (people-or-money only)

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
