---
name: FR-0039
slug: automated-adr-commit-on-handoff-trigger
status: Open
filed: 2026-05-07T02:54Z
source: supervisor-tick-2026-05-07T02-48-05Z
severity: critical
---

# FR-0039: Automated process committed Tier-C ADR in response to tick handoff

Captured: 2026-05-07T02:54Z
Source: supervisor-tick-2026-05-07T02-48-05Z
Status: open

## Observed behavior

At 2026-05-07T02:53:35Z (during the 02:48Z tick), commit `7a718ac` ("Amend
ADR-0029 §6 cap policy: per-fetch, not per-day") landed on main branch with
author "Evan Follis". This commit:

1. Modified `decisions/0029-synaplex-loop-five-layer-pipeline.md` (Tier-C: immutable once accepted)
2. Appeared ~90s after this tick wrote `runtime/.handoff/synaplex-cap-policy-divergence-2026-05-07T02-48Z.md`
3. References that handoff explicitly in the commit message and amendment provenance
4. Was committed while the tick session was still running

No attended session or interactive agent was present. The tick session did
NOT write this commit — it was produced by an external automated mechanism.

## Why this is critical

**ADR files are Tier-C — immutable once written.** The tier model exists
specifically to prevent unilateral modification of governance decisions. An
automated mechanism that can trigger ADR commits based on handoff file
creation bypasses the governance contract entirely.

The amendment content appears substantively correct (per-fetch vs per-day
cap semantics are accurately described). But correctness does not authorize
the mechanism. A correct unauthorized commit is still unauthorized, and the
mechanism that produced it can produce incorrect commits with equal ease.

## What mechanism triggered this?

Unknown. Candidates:
1. A hook watching `runtime/.handoff/` for new files that auto-processes them
2. A cron job or systemd timer that runs agent sessions against handoff files
3. The "something on the host that scrapes and executes shell commands from
   CURRENT_STATE.md" mechanism (documented in reflect.sh FR-0040 investigation)
   generalized to handoff files

The commit author "Evan Follis" matches the workspace git config. The
commit message quality and reasoning are consistent with a capable agent
session. Timing (~90s) is consistent with a triggered agent invocation.

## Required investigation

1. `systemctl list-timers --all` — check for timers that could trigger on
   new files in runtime/.handoff/
2. `inotifywait -r /opt/workspace/runtime/.handoff/` — check if file watches
   are active
3. Check `/root/.claude/hooks/` and `/root/.codex/hooks/` for handoff-processing hooks
4. `git log --author="Evan Follis" --since="2026-04-01" --oneline` — check
   for prior automated commits with this author pattern

## Required action

1. Identify the trigger mechanism
2. Either authorize it explicitly (add to workspace CLAUDE.md as a declared
   automation) or disable it
3. If the mechanism can commit to main without attended-session oversight,
   it must be scoped to Tier-A files only or gated behind the Tier-B-auto
   authority decision

## Related

- reflect.sh Write bypass: FR-0040 (execution of agent sessions without proper tooling gates)
- CURRENT_STATE.md shell-command execution: documented in `runtime/.handoff/general-skillfoundry-harness-reflection-mutated-head-investigation-2026-05-01T14-35Z.md`
- Ghost-write cascade: FR-0038 (tick events claiming main commits that land on branches)
- Tier-B-auto authority: synthesis Proposal #18, cycle-20 Q1
