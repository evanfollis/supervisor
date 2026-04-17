# Playbook update proposal: deploy gate in completion reports

**Written**: 2026-04-17T04:47Z (supervisor tick)
**Source**: cross-cutting-2026-04-17T03-23-27Z.md Proposal 4
**Requires**: attended session — editing `scripts/lib/supervisor-project-tick-prompt.md` and `/opt/workspace/CLAUDE.md` (Tier C for ticks)

## What to add

**To `supervisor-project-tick-prompt.md` completion report template**:

> **Completion report must distinguish:**
> - `code_landed: true/false` — committed and pushed to remote
> - `deployed: true/false/not-applicable` — running in production (for projects with a deployed service)
> - If `code_landed: true` and `deployed: false`, the completion report must state what deployment step is needed

**To `/opt/workspace/CLAUDE.md` §Quality: Radical Truth**:

> - **"Pushed" is not "deployed."** A tick that commits and pushes code to a project with a running service must either deploy or explicitly note the deployment gap in its completion report. The disposition ledger must not mark `verified:true` until the change is live in the target environment.

## Why

S1-P2 (`sourceType` field) was dispositioned as `verified:true` after eb18e35 was committed and pushed. But the command service was never redeployed — `grep -c sourceType events.jsonl` = 0. The disposed item closed the carry-forward loop on something that wasn't actually live. This conflation of "pushed" and "deployed" will repeat on every deployed-service project (command, mentor, launchpad-lint).

## Reference

- Synthesis: `/opt/workspace/runtime/.meta/cross-cutting-2026-04-17T03-23-27Z.md` §Proposal 4
- Evidence: S1-P2 in dispositions.jsonl vs. events.jsonl grep
