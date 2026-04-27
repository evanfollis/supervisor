---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-04-27
---

# Active issues

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

- **Ghost FRs on tick branches (FR-0038, CRITICAL)** — tick sessions write FR files and active-issues updates on tick branches that are never merged to main. Main friction/ ends at FR-0037; FRs 0038–0041 were ghost files until this tick fixed them on main. Root cause is Tier-A writes landing on tick branches. ADR-class decision required. See `friction/FR-0038-ghost-frs-on-tick-branches.md`.
- **Synthesis dispatch execution gap (FR-0039, HIGH)** — 0/8 synthesis proposals landed across 2 cycles (Apr 26 03:26Z and 15:25Z). Ticks correctly defer Tier-C edits; no attended session has materialized. INBOX holds 14 items; saturation suppression active. 15:25Z synthesis deadline ~15:25Z today. See `friction/FR-0039-synthesis-dispatch-execution-gap.md`.
- **Reflection-commit gate silent failure (FR-0040, HIGH)** — `reflect.sh:186-202` auto-commit of CURRENT_STATE.md has silently failed for 3+ cycles on synaplex and command. Diagnostic logging needed; Tier-C fix. See `friction/FR-0040-reflection-commit-gate-silent-failure.md`.
- **Adversarial review debt (FR-0041, HIGH)** — Atlas `90bd5fc` at 3rd carry-forward; ADR-0031/0032 both unreviewed at 8+/6+ reflection windows. No systematic detection. See `friction/FR-0041-adversarial-review-debt.md`.
- **Remote push gap** — 36 commits ahead of origin/main as of 2026-04-27T08:49Z. Growing monotonically (was 35 at 03:24Z synthesis, 29 two windows ago). Requires attended session with push authorization.
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
