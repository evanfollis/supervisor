---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-03
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

## Pending principal

- **Atlas runner restart** — `sudo systemctl restart atlas-runner.service`. P1 (TESTING orphan re-evaluation, `71224e9`) + S3-P2 gate (`39b6d2f`) both in main since ~May 2 17:05Z; service last restarted May 2 14:25Z. One command deploys both. Evidence frozen at 239.
- **Synaplex cap policy** — ADR-0029 §6 says "200/source/day"; implementation does "200/fetch" + union (HN ~400/day). Recommendation: Option C — amend ADR wording to match implementation (zero code change). 5th carry-forward cycle. See `URGENT-synaplex-cap-policy-3rd-cycle-2026-05-01T14-42Z.md`.
- **LCI outreach decision** — 10 drafts at `drafted` status since 2026-04-11 (22+ days). Three options: unblock (channel decision), park explicitly (ADR), or kill. See `URGENT-lci-outreach-blocked-22-days-2026-05-02.md`.
- **Tier-B-auto authority** — 13 cycles × 0 synthesis proposals landed. Approving Tier-B-auto for additive `scripts/lib/` changes proposed 2+ cycles immediately unblocks reflect.sh fix (FR-0040), synthesis-translator dedup, and ~8 other stale INBOX proposals. See `proposal-tier-b-auto-authority-2026-05-02T18-50Z.md` and `2026-05-03T02-47Z-principal-decisions-pending.md`.

## Structural / background

- **Tick-branch isolation (FR-0038)** — tick wrapper creates `ticks/YYYY-MM-DD-HH` branches; all writes commit there and never merge to main. Governance surfaces (friction/, active-issues, verified-state) updated by ticks are effectively orphaned. Merge playbook in INBOX since Apr 26; structural fix needs attended session or Tier-B-auto approval.
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
