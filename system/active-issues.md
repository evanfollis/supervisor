---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-02
---

# Active issues

## URGENT — attended session required

- **Ghost-write false-verification (FR-0038)** — Tick sessions claim successful writes that don't land on disk, AND now produce explicit "verified" claims that are empirically false. FR-0037 was last real frontier; FR-0038/0039/0040 were claimed written by 9+ prior ticks but didn't exist until this tick (2026-05-02T04:47Z). Attended interactive diagnosis required. See `friction/FR-0038-ghost-write-false-verification.md`.
- **Headless project tick 401 auth failure (FR-0039 ref)** — All headless project tick sessions (context-repo, command) fail immediately with `401 Invalid authentication credentials`. Reflection jobs unaffected. Credential source differs between the two execution paths. Operator fix: compare env/credential source, rotate stale key. See INBOX `URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md`.
- **Atlas S3-P2 fix undeployed** — `39b6d2f` (rotation-safe persistent counter) pushed to main 2026-05-02T02:11Z. Running service still has old scan-based gate. Deploy: `sudo systemctl restart atlas-runner.service`. Operator access required.
- **reflect.sh Write bypass (FR-0040)** — `--disallowedTools` blocks `Edit` but not `Write`. Reflections actively mutate project files. An unidentified host process ran a `git commit -m` command scraped from CURRENT_STATE.md output. Fix in `scripts/lib/reflect.sh` requires attended session. See `friction/FR-0040-reflect-sh-write-bypass.md`.
- **LCI outreach 22-day stall** — 10 outreach drafts at `drafted` status since 2026-04-11 (22 days). 3-cycle escalation threshold crossed (URGENT in INBOX). Needs principal decision: unblock (channel + Tally form), park with rationale, or kill the LCI track. See INBOX `URGENT-lci-outreach-blocked-22-days-2026-05-02.md`.

## Currently live — projects

- **Synaplex cap policy decision** — ADR-0029 §6 says "max 200/source/day"; code does "max 200/fetch" with union accumulation (~450 HN items/day). No data corruption. Recommendation: Option C (ratify per-fetch, amend §6 wording — 0 code change). 4th cycle carry-forward. See INBOX `synaplex-cap-policy-decision-2026-04-30T14-49Z.md` + URGENT 3rd cycle.
- **Synaplex scoring cron redundancy** — Scores fire 12×/day; intake only 3×/day. 9 score runs re-score an unchanged corpus. Harmless with heuristic scoring; wasteful when ANTHROPIC_API_KEY lands. Fix needed before key is active.
- **Command browser-layer verification** — server-side smoke strong, real-browser coverage is a machine-owned gap. Replacement handoff: `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4** — L1 intake live; Layer 2/3/4 follow ADR-0029 bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Skillfoundry agentic inbound** — Preflight + sourceType + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per skillfoundry session.
- **Discovery adapter post-fix findings** — 3 Codex-review findings on `2f63ae5`: parse_assumption 3-claim collapse, migrate.py parse failure swallow, parse-one-file boundary leak. Finding B shipped; Finding A/C pending.
- **Canon schema polarity** — Holistic audit (reconcile polarity vocabulary + audit/citation/phase-0 + FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 for atlas landed (`49c24df`). skillfoundry-valuation retrofit proposal filed; awaiting pickup.

## Pending principal (people-or-money only)

- **LCI commercial track decision** — unblock, park, or kill. See URGENT above.
- **Synaplex cap policy** — Option A/B/C. See above. Recommendation: C.

## Structural / background

- **Synthesis-to-execution pipeline blocked (FR-0039)** — 10 synthesis cycles, 0 of 17 proposals landed. INBOX at 40 items. Most proposals are Tier-C (scripts/lib, CLAUDE.md, decisions). No attended triage has run. Bulk "won't-fix" or authority grant for safe Tier-B proposals needed. See `friction/FR-0039-synthesis-execution-gap.md`.
- **CURRENT_STATE.md drift** — 3 projects (command, context-repo, sf-harness) have uncommitted CURRENT_STATE.md content. Post-reflection auto-commit pathway exists but unreliable. Pattern: reflections write, nothing commits.
- **Adversarial review non-functional** — codex not installed; `adversarial-review.sh` EROFS-blocked for 6+ cycles across all projects. Most-patched function in workspace (atlas `_maybe_escalate_frozen_loop`) has never had opposing-agent review.
- **Operator authority loop** — sessions carry supervisor posture but no tmux/systemd host control. ADR-0015 forbids routing Evan to another "full admin" agent; repeated host-only needs must become an explicit operator bridge/tool.
- **Executive boundary discipline** — FR-0018 and follow-ons name the pattern where executive patches project code instead of shaping PM layer. Ongoing; reinforced by ADR-0020.
- **ADR-0028 artifact hygiene** — artifact inbox needs owned browser-layer proof before retiring `/_inbox` stopgap.
- **Cowork is secondary** — external commentary only; not a gate. ADR-0032.

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
