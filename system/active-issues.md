---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-05
---

# Active issues

## Currently live

- **LATEST_SYNTHESIS corruption** — symlink points to a 67-byte stub file; cross-cutting synthesis dispatch is blind. Fix is in `scripts/lib/synthesize.sh` (Tier C). Proposal at `handoffs/INBOX/proposal-latest-synthesis-pointer-2026-05-05T03-26-47Z.md` (2nd cycle). Attended operator session required.
- **reflect.sh disallow-list gap (FR-0040)** — `Write` tool not blocked; reflection sessions can mutate project files. One inadvertent commit already landed (fdbc781, 2026-05-01). Fix: add `"Write"` at `scripts/lib/reflect.sh:112`. Routing at `handoffs/INBOX/reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md` (Tier C, 83h in INBOX).
- **Ghost-write telemetry corruption (FR-0038)** — tick sessions emit `friction_captured` events for files that only exist on tick branches, not on main. 8+ false events before FR-0038/0039/0040 actually landed (2026-05-05T04-49Z this tick). Event pre-verification proposal at `handoffs/INBOX/proposal-event-emission-preverification-2026-05-05T03-26-47Z.md` (Tier C).
- **Atlas orphaned TESTING hypotheses** — A+C+D2 promoted 7 FORMULATED→TESTING; no path re-evaluates TESTING. Loop ran one productive cycle then went to 0 hypotheses/cycle. P1 fix (add `_include_orphaned_testing`) requires principal authorization. Handoff: `runtime/.handoff/general-atlas-orphaned-testing-failure-mode-2026-05-02T14-26Z.md` (62h stale).
- **Context-repo tick 401 auth failure** — all unattended context-repo ticks silently failing since 2026-05-01T00:38Z. Handoff: `runtime/.handoff/general-context-repo-tick-auth-failure-2026-05-01.md` (98h stale). Credential or harness config issue; attended diagnosis needed.
- **INBOX proposal saturation** — 44+ proposals in INBOX (oldest 229h); Tier C prevents tick execution. Attended session needed for bulk disposition. URGENT: `handoffs/INBOX/URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md` (163h).
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
