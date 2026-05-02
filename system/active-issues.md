---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-02
---

# Active issues

## Currently live

- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap. Old principal FR-0015 escalation archived; replacement handoff is `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Synaplex cap policy / scoring cron** — ADR-0029 §6 says "max 200 per source per day"; implementation does "max 200 per fetch" → HN at 277+/day. Recommendation: C (ratify per-fetch semantic, amend §6). Score cron fires 12×/day on unchanged corpus — wasteful once Sonnet scoring activates. Principal decision pending. INBOX: `synaplex-cap-policy-decision-2026-04-30T14-49Z.md` (3rd-cycle URGENT).
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session (scope now spans `/opt/workspace/projects/skillfoundry/` root).
- **Skillfoundry researcher outreach blocker** — No external outreach activity for 21+ days. Approaching 3rd-cycle carry-forward threshold. Researcher session needs unblocking or explicit suspension.
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.
- **Atlas runner frozen** — Pool rotation gate triggered; runner frozen 90h+. Atlas decision handoff `runtime/.handoff/atlas-pool-rotation-decision.md` processed; atlas PM to act. 401 auth also blocking atlas tick.
- **Workspace adversarial review gap** — codex binary not installed; EROFS in tick envs. All projects shipping without cross-model review for 5+ consecutive cycles. FR-0038 through FR-0040 finally written 2026-05-02T00:48Z after 9 ghost-write windows. Structural fix needed in operator surface.
- **reflect.sh disallow-list gap** — Write + Bash(python3) not in --disallowedTools; one commit already auto-executed from CURRENT_STATE.md. Two fixes needed in scripts/lib/ (Tier-C). FR-0040. Routed to attended session: `handoffs/INBOX/reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`.

## Pending principal (people-or-money only)

- **Synaplex cap policy decision** — A/B/C choice (recommend C: ratify per-fetch semantic, amend ADR-0029 §6). Synaplex score cron cadence also needs decision before Sonnet key lands. No code change required for C. INBOX: `synaplex-cap-policy-decision-2026-04-30T14-49Z.md`.

## Structural / background

- **401 auth intermittent — headless tick execution path** — Ticks fail with 401 while reflection jobs succeed. Root cause: credential path divergence between workspace-reflect.timer and project tick scripts. FR-0039. Requires operator access to diagnose. INBOX: `URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md`.
- **INBOX proposal saturation** — 30+ proposals aged 24h–153h without attended disposition. Saturation exception active (>5 items, same root cause). Requires attended session to bulk-accept, defer, or close. INBOX: `URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md`.
- **Ghost-write pattern in tick sessions** — Ticks emit events claiming writes that don't persist. FR-0038. Fix: post-action verification in tick wrapper (proposal: `proposal-post-action-state-verification-2026-05-01T15-32-17Z.md`). Tier-C gate for headless tick.
- **24 aged tick branches** — `ticks/2026-04-29-02` through `ticks/2026-05-01-00` aged >24h. Merge playbook needed (INBOX: `proposal-merge-tick-branches-playbook-2026-04-26T03-37-07Z.md`). Doctor: FAIL.
- **Operator authority loop** — Attached sessions can be executive/supervisor with repo write but no tmux/systemd host control. ADR-0015 amendment now forbids routing Evan to another "full admin" agent; repeated host-only needs must become an explicit operator bridge/tool.
- **Executive boundary discipline** — FR-0018 and follow-ons name the pattern where the executive session patches project code instead of shaping the PM layer. Ongoing; reinforced by ADR-0020 action-default + the people-or-money rubric memory.
- **ADR-0028 post-landing artifact hygiene** — artifact inbox still needs owned browser-layer proof before retiring the old `/_inbox` stopgap. Do not ask the principal for the proof path by default.
- **Workspace CLAUDE.md versioned as of `d09d2be`** — symlink from `/opt/workspace/CLAUDE.md` → `supervisor/workspace-claude.md`. All future workspace-charter edits land in git history via the supervisor repo. Autonomous-exec loop demonstrated for this change (synthesis → translator → INBOX handoff → executive commit).
- **Cowork is a secondary friction surface** — external commentary only; not a gate, validator, or backlog priority escalator. Phase D Cowork UI remains downstream of command Phase C and broader system backlog pressure. Durable contract: ADR-0032.

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
