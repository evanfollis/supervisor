---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-04
---

# Active issues

## Critical (unattended-loop cannot fix — principal/operator required)

- **Atlas runner frozen 42h+** (6th consecutive reflection window, 2026-05-02T~14Z) — `atlas-runner.service` stopped; evidence store stuck at 239; signal→hypothesis pipeline halted. Fix: `sudo systemctl restart atlas-runner.service`. URGENT in runtime/.handoff/ unconsumed. **One command.**
- **reflect.sh Write bypass cycle 10** — reflection sessions can call Write tool despite propose-only contract; CURRENT_STATE mutations bypass safety net. Fix is adding `"Write"` to `--disallowedTools` in `scripts/lib/reflect.sh:112`. INBOX: `reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`. Tier-C from ticks; requires attended session or Tier-B-auto authority.
- **Ghost-write telemetry corruption** — ticks emit false state claims into `events.jsonl` (e.g. "active-issues updated on main" when writes landed on a tick branch). Telemetry truth source is degraded. Root cause: ticks run on tick branches, not main. FR-0038 pending (see friction harvest this tick).
- **Tick branch accumulation** — 21 branches >24h unmerged (doctor FAIL); 12 commits diverged from remote. All governance writes from ticks (FR, active-issues updates) are ephemeral until merged. `active-issues.md` was 9 days stale on main before this tick.
- **INBOX saturation: 39 proposals, 0/25 landed in 16 cycles** — URGENT-inbox-proposal-saturation from 2026-04-28 still unconsumed. Terminal-consumer bottleneck: no attended session processes Tier-B proposals. Structural unblock: Tier-B-auto authority decision (pending principal).
- **LCI outreach blocked 22+ days** — 10 drafts at `drafted` since 2026-04-11; zero external evidence for LCI commercial assumption. 3-cycle escalation threshold crossed. Principal decision required: unblock channel, park explicitly, or kill. INBOX: `URGENT-lci-outreach-blocked-22-days-2026-05-02.md`.
- **Synaplex cap policy doc/code diverge** — ADR-0029 §6 says "max 200 per source/day"; implementation does "max 200 per fetch + union accumulation" (HN at ~400/day). 3rd-cycle escalation. Decision: truncate-by-score, truncate-by-recency, or ratify per-fetch + amend ADR. INBOX: `URGENT-synaplex-cap-policy-3rd-cycle-2026-05-01T14-42Z.md`.
- **Tier-B-auto authority decision** — 16 synthesis cycles × 0 proposals landed. Without authority for ticks to edit `scripts/lib/`, the reflect.sh bypass, LATEST_SYNTHESIS pointer, rotation-blind telemetry, and ~8 other standing fixes cannot land autonomously. Key unblock for the workspace self-repair loop.

## Currently live

- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap. Old principal FR-0015 escalation archived; replacement handoff is `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session (scope now spans `/opt/workspace/projects/skillfoundry/` root).
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.

## Pending principal (people-or-money only)

- None currently. External-service setup should first be converted to a
  machine-owned fallback path before being treated as principal work.

## Structural / background

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
