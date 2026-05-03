---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-03
---

# Active issues

## URGENT — operator/principal action required

- **Atlas runner restart** — P1 (TESTING orphan re-eval, commit `71224e9`) and S3-P2 gate (commit `39b6d2f`) are both in `main` but service was last restarted 14:25Z May 2 (pre-P1). One command: `sudo systemctl restart atlas-runner.service`. After restart, 7 orphaned TESTING hypotheses are immediately re-evaluated. FR-0042.
- **Synaplex cap policy** — ADR-0029 §6 says "max 200/source/day"; implementation does "max 200/fetch" → HN reaches ~400/day. Recommend Option C: ratify per-fetch semantic, amend ADR-0029 wording (0 code change). INBOX: `URGENT-synaplex-cap-policy-3rd-cycle-2026-05-01T14-42Z.md`. Score cron cadence also wasteful (9/12 daily runs re-score unchanged corpus).
- **LCI outreach** — 10 drafts at `drafted` status since 2026-04-11 (22+ days). Needs principal decision: unblock (Tally form + channel), park explicitly, or kill. INBOX: `URGENT-lci-outreach-blocked-22-days-2026-05-02.md`.
- **Tier-B-auto authority** — 11 synthesis cycles, 0 proposals landed. Reflect.sh Write bypass + dedup gate + size gate all require `scripts/lib/` edits (Tier-C from tick). Principal decision: approve Tier-B-auto classification for additive, 2+ cycle infra-only changes. INBOX: `proposal-tier-b-auto-authority-2026-05-02T18-50Z.md`.
- **Server maintenance** — p2: repair LATEST_SYNTHESIS pointer (symlink bug corrupting synthesis artifacts); p3: apply routine OS/kernel package updates. Operator-path work. See `runtime/.meta/server-maintenance-2026-05-03T01-24-42Z.md`.

## Currently live

- **Ghost-write structural fix** — FR-0038 through FR-0042 finally written to disk (2026-05-03T02:47Z attended tick, first time in 11 cycles). Root cause confirmed: headless `claude -p` tick sessions have different write-path behavior. Fix pending: post-action state verification in `supervisor-tick.sh` wrapper. FR-0038.
- **reflect.sh Write bypass** — `Write` not in `--disallowedTools`; reflections write CURRENT_STATE.md causing uncommitted drift + covert commit channel via embedded shell commands. Fix: add `"Write"` to disallowedTools; capture reflection output via stdout. FR-0040; INBOX: `reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`.
- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean; rebrand landed; deploy still pending. IA reshape decision open (ADR-0027).
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live and clean; L2/L3/L4 follow ADR-0029 bootstrap throttle.
- **Skillfoundry agentic inbound deploy** — Preflight + sourceType + watcher in flight. Migrate telemetry now emitting (commit `531946f`). LCI outreach blocked (see URGENT above).
- **Discovery adapter post-fix findings** — Finding B shipped; Finding A drafting; Finding C ADR accepted-pending-scheduling.
- **Canon schema polarity surface** — holistic audit dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — atlas landed (`49c24df`); skillfoundry-valuation retrofit awaiting pickup.
- **INBOX saturation** — down from 50 → 30 items (2026-05-03 bulk archive of superseded duplicates). Still 4 URGENT + 26 proposals. FR-0041.

## Pending principal (people-or-money only)

- See URGENT section above (synaplex cap policy, LCI outreach decision, Tier-B-auto authority).

## Structural / background

- **Operator authority loop** — host-control (tmux/systemd) unavailable from tick sessions. Repeated host-only needs (atlas restart, server maintenance) must become an explicit operator bridge/tool.
- **Executive boundary discipline** — FR-0018 and follow-ons; reinforced by ADR-0020.
- **ADR-0028 post-landing artifact hygiene** — browser-layer proof still pending.
- **Workspace CLAUDE.md versioned** — symlink `supervisor/workspace-claude.md`. Autonomous-exec loop demonstrated.
- **Cowork secondary surface** — ADR-0032 durable contract; not a gate or priority escalator.
- **Tick branches aging** — 48 branches >72h (doctor FAIL), 22 more >24h. Merge-tick-branches playbook needed.

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
